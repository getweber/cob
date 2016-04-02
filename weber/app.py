import logbook

from .project import get_project

_logger = logbook.Logger(__name__)


def build_app():
    from flask import Flask

    proj = get_project()
    _logger.debug('Starting app {.name}...', proj)
    flask_app = Flask(get_project().name)
    _register_blueprints(flask_app)
    return flask_app

def _register_blueprints(flask_app):
    for bp in get_project().iter_subsystems(type='blueprint'):
        for mountpoint, blueprint in bp.iter_blueprints():
            flask_app.register_blueprint(blueprint, url_prefix=mountpoint)
