import os
import click
import flask_migrate
import logbook
import multiprocessing
import random
import shutil
import string
import subprocess
from tempfile import mkdtemp

import gunicorn.app.base
from werkzeug.contrib.fixers import ProxyFix
import yaml


from ..ctx import context
from ..app import build_app
from ..bootstrapping import ensure_project_bootstrapped
from ..exceptions import MissingDependency, TestsFailed
from ..utils.config import get_etc_config_path
from ..utils.docker import get_full_commmand as get_full_docker_command
from ..utils.develop import is_develop, cob_root
from ..utils.network import wait_for_app_services, wait_for_tcp
from ..utils.templates import load_template
from ..project import get_project

import pkg_resources


_COB_VERSION = pkg_resources.get_distribution('cob').version  # pylint: disable=no-member

_logger = logbook.Logger(__name__)
_CUSTOM_DOCKERFILE = "custom.docker"

def _get_user_steps():
    if not os.path.isfile(_CUSTOM_DOCKERFILE):
        return ''

    with open(_CUSTOM_DOCKERFILE) as f:
        return f.read()


@click.group()
def docker():
    pass


@docker.command()
def generate():
    proj = get_project()
    template = load_template('Dockerfile')

    if is_develop():
        sdist_file_name = os.path.join(proj.root, '.cob-sdist.tar.gz')
        _build_cob_sdist(filename=sdist_file_name)
    else:
        sdist_file_name = None

    with open(".Dockerfile", "w") as f:
        f.write(template.render(
            project=proj,
            deployment_base_image='ubuntu:16.04',
            python_version='3.6',
            is_develop=is_develop(),
            cob_sdist_filename=os.path.basename(sdist_file_name) if sdist_file_name else None,
            cob_root=cob_root() if is_develop() else None,
            user_steps=_get_user_steps()))


def _build_cob_sdist(filename):

    sdist_filename = os.environ.get('COB_SDIST_FILENAME')

    if sdist_filename is not None:
        shutil.copy(sdist_filename, filename)
    else:
        tmpdir = mkdtemp()
        try:
            subprocess.check_call(
                f'python setup.py sdist -d {tmpdir}', cwd=cob_root(), shell=True)
            [distfile] = os.listdir(tmpdir)
            sdist_filename = os.path.join(tmpdir, distfile)
            shutil.move(sdist_filename, str(filename))
        finally:
            shutil.rmtree(tmpdir)


@docker.command(name='build')
@click.option('--sudo/--no-sudo', is_flag=True, default=None, help="Run docker build with sudo")
@click.option('--extra-build-args', '-e', default="", help="Arguments to pass to docker build")
@click.option('--release', is_flag=True, default=False)
def docker_build(sudo, extra_build_args="", use_exec=True, image_name=None, release=False):
    project = get_project()
    if image_name is None:
        image_name = f'{project.name}:{"latest" if release else "dev"}'.format(project.name, 'latest' if release else 'dev')
    generate.callback()
    cmd = get_full_docker_command(['docker', 'build', '-t', image_name, '-f', '.Dockerfile', '.', *extra_build_args.split()],
                                  should_sudo=sudo)
    _logger.debug('Running Command: {}', ' '.join(cmd))
    if use_exec:
        os.execv(cmd[0], cmd)
    else:
        subprocess.check_call(cmd)


@docker.command(name='wsgi-start')
def start_wsgi():
    logbook.StderrHandler(level=logbook.DEBUG).push_application()

    _ensure_secret_config()
    ensure_project_bootstrapped()
    project = get_project()
    app = build_app(config_overrides={'PROPAGATE_EXCEPTIONS': True})
    app.wsgi_app = ProxyFix(app.wsgi_app)

    wait_for_app_services(app)

    if project.subsystems.has_database():
        with app.app_context():
            if project.subsystems.models.has_migrations():
                flask_migrate.upgrade()
            else:
                context.db.create_all()

    workers_count = (multiprocessing.cpu_count() * 2) + 1

    class StandaloneApplication(gunicorn.app.base.BaseApplication):  # pylint: disable=abstract-method

        def __init__(self, app, options=None):
            self.options = options or {}
            self.application = app
            super(StandaloneApplication, self).__init__()

        def load_config(self):
            config = {key: value for key, value in self.options.items()
                      if key in self.cfg.settings and value is not None}

            for key, value in config.items():
                self.cfg.set(key.lower(), value)

        def load(self):
            return self.application

    options = {
        'bind': '0.0.0.0:8000',
        'workers': workers_count,
    }
    options.update(project.config.get('gunicorn', {}))

    StandaloneApplication(app, options).run()


def _ensure_secret_config():
    conf_dir = os.environ.get('COB_CONFIG_DIR')
    if not conf_dir:
        return
    secret_file = os.path.join(conf_dir, '000-cob-private.yml')
    if os.path.isfile(secret_file):
        return

    with open(secret_file, 'w') as f:
        f.write('flask_config:\n')
        for secret_name in ('SECRET_KEY', 'SECURITY_PASSWORD_SALT'):
            f.write(f'  {secret_name}: {_generate_secret_string()!r}\n')


def _generate_secret_string(length=50):
    return "".join([random.choice(string.ascii_letters) for i in range(length)])


@docker.command(name='nginx-start')
@click.option('--print-config', is_flag=True, default=False)
def start_nginx(print_config):
    project = get_project()
    template = load_template('nginx_config')
    config = template.render({'use_ssl': False, 'hostname': None, 'project': project, 'os': os})

    if print_config:
        print(config)
        return

    wait_for_tcp('wsgi', 8000)

    with open('/etc/nginx/conf.d/webapp.conf', 'w') as f:
        f.write(config)

    nginx_path = '/usr/sbin/nginx'
    os.execv(nginx_path, [nginx_path, '-g', 'daemon off; error_log /dev/stdout info;'])


@docker.command()
@click.option('--http-port', default=None)
@click.option('--build', is_flag=True, default=False)
@click.option('-d', '--detach', is_flag=True, default=False)
@click.option('--image-name', default=None, help='Image to use for the main docker containers')
def run(http_port, build, detach, image_name):
    if build:
        docker_build.callback(sudo=False, use_exec=False)
    cmd = ['up']
    if detach:
        cmd.append('-d')
    _exec_docker_compose(cmd, http_port=http_port, image_name=image_name)


@docker.command()
def stop():
    _exec_docker_compose(['down'])


@docker.command()
def logs():
    _exec_docker_compose(['logs'])


def _exec_docker_compose(cmd, **kwargs):
    project = get_project()
    compose_filename = f'/tmp/__{project.name}-docker-compose.yml'
    with open(compose_filename, 'w') as f:
        f.write(_generate_compose_file_string(**kwargs))
    docker_compose = _get_docker_compose_executable()
    cmd = get_full_docker_command([docker_compose, '-f', compose_filename, '-p', project.name, *cmd])
    os.execv(cmd[0], cmd)


@docker.command()
@click.option('--image-name', default=None)
def compose(image_name):
    print(_generate_compose_file_string(_generate_compose_file_dict(image_name=image_name)))


def _generate_compose_file_dict(*, http_port=None, image_name=None):
    project = get_project()

    local_override_path = get_etc_config_path(project.name)

    if image_name is None:
        image_name = f'{project.name}:dev'

    config = {
        'version': '3',
        'volumes': {
            'conf': None
        },
    }

    common_environment = {
        'COB_DATABASE_URI': 'postgresql://{0}@db/{0}'.format(project.name),
        'COB_CELERY_BROKER_URL': 'amqp://guest:guest@rabbitmq',
        'COB_CONFIG_DIR': '/conf',
    }

    services = config['services'] = {

        'wsgi':  {
            'image': image_name,
            'command': 'cob docker wsgi-start',
            'environment': common_environment,
            'depends_on': [],
            'volumes': [
                'conf:/conf',
            ],
        },

        'nginx': {
            'image': image_name,
            'command': 'cob docker nginx-start',
            'ports': [f'{http_port or 8000}:80'],
            'depends_on': ['wsgi'],
        }
    }

    if project.subsystems.has_database():
        services['wsgi']['depends_on'].append('db')
        services['db'] = {
            'image': 'postgres:9.6',
            'volumes': [
                'db:/var/lib/postgresql/data'
            ],
            'environment': {
                'POSTGRES_USER': project.name,
                'POSTGRES_DB': project.name,
            }
        }
        config['volumes']['db'] = None

    if project.subsystems.has_tasks():

        services['rabbitmq'] = {
            'image': 'rabbitmq',
            #'command': 'bash -c "sleep 15 && rabbitmq-server"',
        }
        services['worker'] = {
            'image': image_name,
            'command': 'cob celery start-worker',
            'environment': common_environment,
        }

    if project.services.redis:
        services['redis'] = {
            'image': 'redis',
        }

    if local_override_path.is_dir():
        for service_config in services.values():
            service_config.setdefault('volumes', []).append('{0}:{0}'.format(local_override_path))

    return config


def _generate_compose_file_string(*args, **kwargs):
    config = _generate_compose_file_dict(*args, **kwargs)
    return _dump_yaml(config)


def _dump_yaml(config, *, stream=None):
    return yaml.safe_dump(config, stream, allow_unicode=True, default_flow_style=False)


@docker.command()
@click.option('build_image', '--no-build', is_flag=True, default=True)
@click.option('--sudo/--no-sudo', is_flag=True, default=None, help="Run docker build with sudo")
def test(build_image, sudo):
    project = get_project()
    image_name = f"{project.name}:testing"
    if build_image:
        docker_build.callback(sudo=sudo, use_exec=False, image_name=image_name)
    compose_file_dict = _generate_compose_file_dict(image_name=image_name)
    compose_file_dict['services'].pop('nginx')
    test_config = compose_file_dict['services'].pop('wsgi')

    test_config['tty'] = True
    test_config['depends_on'] = sorted(set(compose_file_dict['services']) - {'test'})
    test_config['stdin_open'] = True
    compose_file_dict['services']['test'] = test_config

    compose_filename = f'/tmp/__{project.name}-test-docker-compose.yml'
    with open(compose_filename, 'w') as f:
        _dump_yaml(compose_file_dict, stream=f)
    docker_compose = _get_docker_compose_executable()
    docker_compose_name = f'{project.name}-test'
    cmd = get_full_docker_command([
        docker_compose, '-f', compose_filename, '-p', docker_compose_name, 'run',
        '-w', '/app', '-v', f'{os.path.abspath(".")}:/localdir',
        'test',
        'bash', '-c', "rsync -rvP --delete --exclude .cob /localdir/ /app/ && cob test"])
    p = subprocess.Popen(cmd)
    if p.wait() != 0:
        raise TestsFailed('Tests failed')


def _get_docker_compose_executable():
    returned = shutil.which('docker-compose')
    if not returned:
        raise MissingDependency("docker-compose is not installed in this system. Please install it to use cob")
    return returned
