import click
import logbook

from ..app import build_app

_logger = logbook.Logger(__name__)


@click.command()
def testserver():
    flask_app = build_app()
    flask_app.run()
