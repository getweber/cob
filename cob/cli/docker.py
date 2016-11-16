import os
import click
import logbook
import subprocess

from jinja2 import Template
from pkg_resources import resource_string
from ..utils.develop import is_develop, cob_branch
from ..project import get_project
from cob.__version__ import __version__


_logger = logbook.Logger(__name__)
_CUSTOM_DOCKERFILE = "custom.docker"


def _get_user_steps():
    if not os.path.isfile(_CUSTOM_DOCKERFILE):
        return ''

    with open(_CUSTOM_DOCKERFILE) as f:
        return f.read()


def _generate_cob_installation():
    if is_develop():
        return "ENV COB_DEVELOP=1\nRUN cd /opt && git clone -b {} https://github.com/getweber/cob && pip install -e cob --no-cache-dir".format(cob_branch())
    else:
        return "RUN pip install cob=={}".format(__version__)


@click.group()
def docker():
    pass


@docker.command()
def generate():
    dockerfile_template = Template(resource_string("cob", "Dockerfile.j2").decode("UTF-8"))
    with open(".Dockerfile", "w") as f:
        f.write(dockerfile_template.render(
            install_cob=_generate_cob_installation(),
            user_steps=_get_user_steps()))


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

    subprocess.check_call(cmd, shell=True)
