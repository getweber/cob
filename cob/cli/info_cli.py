import click
from ..project import get_project


@click.group()
def info():
    pass

@info.command(name='project-name')
def project_name():
    """Prints out the name of the current project"""
    print(get_project().name)
