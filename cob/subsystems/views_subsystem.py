import logbook

from .base import SubsystemBase

from flask import Blueprint

_logger = logbook.Logger(__name__)

class ViewsSubsystem(SubsystemBase):

    NAME = 'views'

    def configure_grain(self, grain, app):
        _logger.trace('Found views grain: {}', grain)
        main = grain.load()
        blueprint = Blueprint(main.__name__, main.__name__, url_prefix=grain.config['mountpoint'])
        for deferred_route in getattr(main, '__cob_routes__', []):
            deferred_route.register(blueprint)
        app.register_blueprint(blueprint)
