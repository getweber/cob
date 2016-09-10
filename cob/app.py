import logbook

from .project import get_project

_logger = logbook.Logger(__name__)


def build_app():
    from flask import Flask

    proj = get_project()
    _logger.debug('Starting app {.name}...', proj)
    flask_app = Flask(get_project().name, static_folder=None, template_folder=None)
    proj.configure_app(flask_app)
    _logger.trace('URL map: {}', flask_app.url_map)
    return flask_app
