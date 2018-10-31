import click
import logbook

from ..app import build_app
from ..bootstrapping import ensure_project_bootstrapped

_logger = logbook.Logger(__name__)


@click.command()
@click.option('-p', '--port', type=int, default=5000)
@click.option('-H', '--host', default='127.0.0.1')
@click.option('--debug/--no-debug', is_flag=True, default=True)
def testserver(port, debug, host):
    ensure_project_bootstrapped()
    flask_app = build_app(config_overrides={'TESTING': True, 'DEBUG': debug})
    logbook.StderrHandler(level=logbook.DEBUG).push_application()
    flask_app.run(port=port, debug=debug, host=host)
