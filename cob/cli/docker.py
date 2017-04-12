import os
import click
import logbook
import shutil
import subprocess
from tempfile import mkdtemp

from jinja2 import Template
from pkg_resources import resource_string

from .utils import exec_or_error
from ..utils.develop import is_develop, cob_root
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
    dockerfile_template = Template(resource_string(
        "cob", "Dockerfile.j2").decode("UTF-8"))

    if is_develop():
        sdist_file_name = _build_cob_sdist()

    with open(".Dockerfile", "w") as f:
        f.write(dockerfile_template.render(
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
        subprocess.check_call('python setup.py sdist -d {}'.format(tmpdir), cwd=cob_root(), shell=True)
        [distfile] = os.listdir(tmpdir)
        returned = '.cob-sdist.tar.gz'
        shutil.move(os.path.join(tmpdir, distfile), os.path.join(get_project().root, returned))
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
