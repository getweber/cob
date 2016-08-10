import click
import logbook

from ..app import build_app

_logger = logbook.Logger(__name__)


@click.command()
@click.option('-p', '--port', type=int, default=5000)
def testserver(port):
    flask_app = build_app()
    flask_app.run(port=port)
