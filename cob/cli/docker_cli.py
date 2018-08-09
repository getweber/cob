import os
import click
import logbook
import multiprocessing
from pathlib import Path
import random
import shutil
import string
import subprocess
import sys
from tempfile import mkdtemp

import gunicorn.app.base
from werkzeug.contrib.fixers import ProxyFix
import yaml


from ..app import build_app
from ..bootstrapping import ensure_project_bootstrapped
from ..exceptions import TestsFailed
from ..utils.config import get_etc_config_path
from ..utils.docker import docker_cmd, docker_compose_cmd
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


@docker.command(name="generate-docker-file")
def generate_dockerfile():
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
            deployment_base_image='python:3.6-jessie',
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
def docker_build(sudo, extra_build_args="", use_exec=True, image_name=None, release=False, use_cache=True):
    project = get_project()
    if image_name is None:
        image_name = f'{project.get_docker_image_name()}:{"latest" if release else "dev"}'.format(project.name, 'latest' if release else 'dev')
    generate_dockerfile.callback()
    cmd = docker_cmd.build(['-t', image_name, '-f', '.Dockerfile', '.', *extra_build_args.split()]).force_sudo(sudo)
    if not use_cache:
        cmd = cmd.args(['--no-cache'])
    _logger.debug('Running Command: {}', cmd)
    cmd.run(use_exec=use_exec)


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
            project.setup_db()

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
@click.option('compose_overrides', '-o', '--overlay-compose-file', default=[], multiple=True)
@click.option('-d', '--detach', is_flag=True, default=False)
@click.option('--image-name', default=None, help='Image to use for the main docker containers')
def run(http_port, build, detach, image_name, compose_overrides):
    project = get_project()
    if build:
        docker_build.callback(sudo=False, use_exec=False)
    if image_name is None:
        image_name = f'{project.get_docker_image_name()}:dev'
    run_image.callback(image_name=image_name, detach=detach, http_port=http_port, compose_overrides=compose_overrides)


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
    cmd = docker_compose_cmd.args(['-f', compose_filename, '-p', project.name, *cmd])
    cmd.execv()


@docker.command(name='generate-docker-compose-file')
@click.option('--image-name', default=None)
@click.option('--http-port', type=int, default=None)
@click.option('--force-config-override', is_flag=True, default=False)
@click.option('--log-driver', default='syslog')
def generate_docker_compose_file(image_name, force_config_override, http_port, log_driver):
    """Prints out a docker-compose.yml for this project"""
    print(_generate_compose_file_string(image_name=image_name, force_config_override=force_config_override, http_port=http_port, log_driver=log_driver))


def _generate_compose_file_dict(*, http_port=None, image_name=None, force_config_override=False, log_driver='syslog'):
    project = get_project()

    if image_name is None:
        image_name = f'{project.get_docker_image_name()}:dev'

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

    config_override_path = get_etc_config_path(project.name).resolve()
    if force_config_override or config_override_path.is_dir():
        for service_config in services.values():
            service_config.setdefault('volumes', []).append('{0}:{0}'.format(config_override_path))

    for service_config in services.values():
        service_config.setdefault('volumes', []).append(
            '/etc/localtime:/etc/localtime:ro',
        )

        service_config.setdefault('logging', {'driver': log_driver})

    for service_name, service_ports in project.config.get('docker', {}).get('exposed_ports', {}).items():
        services[service_name].setdefault('ports', []).extend(service_ports)

    return config


def _generate_compose_file_string(**kwargs):
    config = _generate_compose_file_dict(**kwargs)
    return _dump_yaml(config)


def _dump_yaml(config, *, stream=None):
    return yaml.safe_dump(config, stream, allow_unicode=True, default_flow_style=False)


@docker.command()
@click.option('build_image', '--no-build', is_flag=True, default=True)
@click.option('use_cache', '--no-cache', is_flag=True, default=True)
@click.option('--sudo/--no-sudo', is_flag=True, default=None, help="Run docker build with sudo")
def test(build_image, sudo, use_cache):
    project = get_project()
    image_name = f"{project.get_docker_image_name()}:dev"
    if build_image:
        docker_build.callback(sudo=sudo, use_exec=False, image_name=image_name, use_cache=use_cache)
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
    docker_compose_name = f'{project.name}-test'

    test_cmd = "cob test --migrate"
    if not build_image:
        test_cmd = f'rsync -rvP --delete --exclude .cob /localdir/ /app/ && {test_cmd}'


    cmd_args = ['-f', compose_filename, '-p', docker_compose_name]
    cmd = docker_compose_cmd.args([
        *cmd_args, 'run',
        '-w', '/app', '-v', f'{os.path.abspath(".")}:/localdir',
        'test',
        'bash', '-c', test_cmd])
    try:
        if cmd.popen().wait() != 0:
            raise TestsFailed('Tests failed')
    finally:
        docker_compose_cmd.args([
            *cmd_args, 'stop']).popen().wait()


@docker.command(name="run-image", help='Runs a cob project in a pre-built docker image')
@click.argument('image_name')
@click.option('-d', '--detach', is_flag=True, default=False)
@click.option('compose_overrides', '-o', '--overlay-compose-file', default=[], multiple=True)
@click.option('--http-port', default=None)
def run_image(image_name, detach, compose_overrides, http_port):
    project_name, compose_path = _generate_compose_file_from_image(image_name, http_port=http_port)
    cmd = docker_compose_cmd.args(['-p', project_name, '-f', compose_path])
    for compose_override in compose_overrides:
        cmd.args(['-f', compose_override])
    cmd.args(['up'])
    if detach:
        cmd = cmd.args(['-d'])

    cmd.execv()


@docker.command(name="stop-image")
@click.argument('image_name')
def stop_image(image_name):
    project_name, compose_path = _generate_compose_file_from_image(image_name)
    docker_compose_cmd.args(['-p', project_name, '-f', compose_path, 'down']).execv()


def _generate_compose_file_from_image(image_name, *, http_port=None):
    project_name = _get_project_name_from_image(image_name)
    cmd = docker_cmd.run(['--rm', image_name, 'cob', 'docker', 'generate-docker-compose-file', '--image-name', image_name, '--http-port', '80'])
    if _is_journald_system():
        cmd.args(['--log-driver=journald'])
    if get_etc_config_path(project_name).is_dir():
        cmd.args(['--force-config-override'])
    if http_port is not None:
        cmd.args(['--http-port', str(http_port)])
    compose_file_contents = cmd.check_output()
    compose_path = Path('/tmp') / f"__cob_docker_compose_{image_name.replace(':', '_').replace('/', '_')}.yml"
    with compose_path.open('wb') as f:
        f.write(compose_file_contents)
    return project_name, compose_path


@docker.command(name='deploy', help='Deploys an dockerized cob app image to the local systemd-based machine')
@click.option('--force', is_flag=True, default=False)
@click.argument('image_name')
def deploy_image(image_name, force):
    click.echo(f'Obtaining project information for {image_name}...')
    project_name = _get_project_name_from_image(image_name)
    unit_template = load_template('systemd_unit')
    filename = Path('/etc/systemd/system') / f'{project_name}-docker.service'
    click.echo(f'Writing systemd unit file under {filename}...')
    if filename.exists() and not force:
        click.confirm(f'{filename} already exists. Overwrite?', abort=True)

    tmp_filename = Path(mkdtemp()) / 'systemd-unit'
    with tmp_filename.open('w') as f: # pylint: disable=no-member
        f.write(unit_template.render(project_name=project_name, image_name=image_name, cob=f'{sys.executable} -m cob.cli.main'))

    subprocess.check_call(f'sudo -p "Enter password to deploy service" mv {tmp_filename} {filename}', shell=True)
    click.echo(f'Starting systemd service {filename.stem}...')
    subprocess.check_call('sudo systemctl daemon-reload', shell=True)
    subprocess.check_call(f'sudo systemctl enable --now {filename.name}', shell=True)


def _get_project_name_from_image(image_name):
    return docker_cmd.run(['--rm', image_name, 'cob', 'info', 'project-name']).check_output(encoding='utf-8').strip()


def _is_journald_system():
    return shutil.which('journalctl') is not None


@docker.command(name='tag-latest', help='Tags the latest development image as latest')
def tag_latest():
    project = get_project()
    docker_cmd.tag([
        f'{project.get_docker_image_name()}:dev',
        f'{project.get_docker_image_name()}:latest']
    ).execv()

@docker.command(name='push')
def push():
    project = get_project()
    docker_cmd.push([f'{project.get_docker_image_name()}:latest']).execv()
