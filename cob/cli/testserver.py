import click
import logbook

from ..app import build_app
from ..bootstrapping import ensure_project_bootstrapped

_logger = logbook.Logger(__name__)


@click.command()
@click.option('-p', '--port', type=int, default=5000)
def testserver(port):
    ensure_project_bootstrapped()
    flask_app = build_app()
    flask_app.run(port=port)
