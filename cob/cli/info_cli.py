import click
from ..project import get_project


@click.group()
def info():
    pass

@info.command(name='project-name')
def project_name():
    """Prints out the name of the current project"""
    print(get_project().name)


@info.command(name='docker-image-name')
def docker_image_name():
    """Prints out the name of the docker image to use for this project"""
    print(get_project().get_docker_image_name())
