import os
import click
import flask_migrate
import logbook
import multiprocessing
import shutil
import subprocess
from tempfile import mkdtemp


import gunicorn.app.base
import yaml

from ..ctx import context
from ..app import build_app
from ..bootstrapping import ensure_project_bootstrapped
from .utils import exec_or_error
from ..utils.develop import is_develop, cob_root
from ..utils.network import wait_for_tcp
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


@docker.command()
@click.option('--sudo', is_flag=True, help="Run docker build with sudo")
@click.option('--extra-build-args', '-e', default="", help="Arguments to pass to docker build")
def build(sudo, extra_build_args):
    project = get_project()
    generate.callback()

    cmd = "{}docker build -t {} -f .Dockerfile {} .".format(
        "sudo " if sudo else "",
        project.name,
        extra_build_args)

    exec_or_error(cmd, shell=True)


@docker.command(name='wsgi-start')
def start_wsgi():
    ensure_project_bootstrapped()
    project = get_project()
    app = build_app()

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
            config = dict([(key, value) for key, value in self.options.items()
                           if key in self.cfg.settings and value is not None])
            for key, value in config.items():
                self.cfg.set(key.lower(), value)

        def load(self):
            return self.application

    options = {
        'bind': '0.0.0.0:8000',
        'workers': workers_count,
    }
    logbook.StderrHandler(level=logbook.DEBUG).push_application()
    StandaloneApplication(app, options).run()


@docker.command(name='nginx-start')
@click.option('--print-config', is_flag=True, default=False)
def start_nginx(print_config):
    project = get_project()
    template = load_template('nginx_config')
    config = template.render({'use_ssl': False, 'hostname': None, 'project': project})

    if print_config:
        print(config)
        return

    wait_for_tcp('wsgi', 8000, timeout_seconds=30)

    with open('/etc/nginx/conf.d/webapp.conf', 'w') as f:
        f.write(config)

    nginx_path = '/usr/sbin/nginx'
    os.execv(nginx_path, [nginx_path, '-g', 'daemon off; error_log /dev/stdout info;'])


@docker.command()
@click.option('--http-port', default=None)
def run(http_port):
    _exec_docker_compose(['up'], http_port=http_port)


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
    os.execv(docker_compose, [docker_compose, '-f',
                              compose_filename, '-p', project.name] + cmd)


@docker.command()
def compose():
    print(_generate_compose_file())


def _generate_compose_file(*, http_port=None):
    project = get_project()

    config = {
        'version': '3',
        'volumes': {},
    }
    services = config['services'] = {

        'wsgi':  {
            'image': project.name,
            'command': 'cob docker wsgi-start',
        },

        'nginx': {
            'image': project.name,
            'command': 'cob docker nginx-start',
            'ports': ['{}:80'.format(http_port or 8000)],
        }
    }

    if project.subsystems.has_database():
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

    return yaml.safe_dump(config, allow_unicode=True, default_flow_style=False)
