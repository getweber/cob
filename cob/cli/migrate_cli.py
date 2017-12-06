import click
import logbook

from .utils import appcontext_command
from ..ctx import context

import flask_migrate

_logger = logbook.Logger(__name__)


@click.group()
def migrate():
    pass


@migrate.command()
@appcontext_command
def init():
    flask_migrate.init('migrations', False)


@migrate.command()
@click.option('-m', '--message', default=None)
@appcontext_command
def revision(message):
    if not context.db.metadata.tables:
        _logger.warning('No tables loaded!')
    flask_migrate.upgrade()
    flask_migrate.revision(autogenerate=True, message=message)

@migrate.command()
@appcontext_command
def up():
    flask_migrate.upgrade()

@migrate.command()
@appcontext_command
def down():
    flask_migrate.upgrade()
