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
from ..exceptions import MissingDependency
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
        sdist_file_name = _build_cob_sdist()
    else:
        sdist_file_name = None

    with open(".Dockerfile", "w") as f:
        f.write(template.render(
            project=proj,
            deployment_base_image='ubuntu:latest',
            python_version='3.6',
            is_develop=is_develop(),
            cob_sdist_filename=sdist_file_name,
            cob_root=cob_root() if is_develop() else None,
            user_steps=_get_user_steps()))


def _build_cob_sdist():
    tmpdir = mkdtemp()
    try:
        subprocess.check_call(
            'python setup.py sdist -d {}'.format(tmpdir), cwd=cob_root(), shell=True)
        [distfile] = os.listdir(tmpdir)
        returned = '.cob-sdist.tar.gz'
        shutil.move(os.path.join(tmpdir, distfile),
                    os.path.join(get_project().root, returned))
    finally:
        shutil.rmtree(tmpdir)
    return returned


@docker.command(name='build')
@click.option('--sudo/--no-sudo', is_flag=True, default=None, help="Run docker build with sudo")
@click.option('--extra-build-args', '-e', default="", help="Arguments to pass to docker build")
def docker_build(sudo, extra_build_args):
    project = get_project()
    generate.callback()
    cmd = get_full_docker_command(['docker', 'build', '-t', project.name, '-f', '.Dockerfile', '.', *extra_build_args.split()],
                                  should_sudo=sudo)
    _logger.debug('Running Command: {}', ' '.join(cmd))
    os.execv(cmd[0], cmd)


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
            f.write('  {}: {!r}\n'.format(secret_name, _generate_secret_string()))


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
def run(http_port, build, detach):
    if build:
        docker_build.callback(sudo=False, extra_build_args='')
    cmd = ['up']
    if detach:
        cmd.append('-d')
    _exec_docker_compose(cmd, http_port=http_port)


@docker.command()
def stop():
    _exec_docker_compose(['down'])


@docker.command()
def logs():
    _exec_docker_compose(['logs'])


def _exec_docker_compose(cmd, **kwargs):
    project = get_project()
    compose_filename = '/tmp/__{}-docker-compose.yml'.format(project.name)
    with open(compose_filename, 'w') as f:
        f.write(_generate_compose_file(**kwargs))
    docker_compose = shutil.which('docker-compose')
    if not docker_compose:
        raise MissingDependency("docker-compose is not installed in this system. Please install it to use cob")
    cmd = get_full_docker_command([docker_compose, '-f', compose_filename, '-p', project.name, *cmd])
    os.execv(cmd[0], cmd)


@docker.command()
def compose():
    print(_generate_compose_file())


def _generate_compose_file(*, http_port=None):
    project = get_project()

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
            'image': project.name,
            'command': 'cob docker wsgi-start',
            'environment': common_environment,
            'depends_on': [],
            'volumes': [
                'conf:/conf',
            ],
        },

        'nginx': {
            'image': project.name,
            'command': 'cob docker nginx-start',
            'ports': ['{}:80'.format(http_port or 8000)],
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
            'image': project.name,
            'command': 'cob celery start-worker',
            'environment': common_environment,
        }

    return yaml.safe_dump(config, allow_unicode=True, default_flow_style=False)
