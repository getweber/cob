import logbook

import gossip

from .project import get_project

_logger = logbook.Logger(__name__)


def build_app():
    from flask import Flask

    proj = get_project()
    _logger.debug('Starting app {.name}...', proj)
    flask_app = Flask(get_project().name)
    gossip.trigger('weber.configure_flask_app', app=flask_app)
    return flask_app
