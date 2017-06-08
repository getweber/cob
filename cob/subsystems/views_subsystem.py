import logbook

from .base import SubsystemBase
from ..locations import Location

from flask import Blueprint

_logger = logbook.Logger(__name__)

class ViewsSubsystem(SubsystemBase):

    NAME = 'views'

    def configure_grain(self, grain, flask_app):
        _logger.trace('Found views grain: {}', grain)
        main = grain.load()
        blueprint = Blueprint(main.__name__, main.__name__, url_prefix=grain.config['mountpoint'])
        for deferred_route in getattr(main, '__cob_routes__', []):
            deferred_route.register(blueprint)
        flask_app.register_blueprint(blueprint)

    def iter_locations(self):
        assert self.grains
        for grain in self.grains:
            yield Location(grain.mountpoint)
