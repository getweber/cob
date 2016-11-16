import click
import logbook

from cob.ctx import context

from .utils import appcontext_command

_logger = logbook.Logger(__name__)


@click.group()
def db():
    pass

@db.command()
@appcontext_command
def createall():
    context.db.create_all()
