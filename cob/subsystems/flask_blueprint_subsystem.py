import logbook

from flask import Blueprint
from .base import SubsystemBase

from ..locations import Location

_logger = logbook.Logger(__name__)

class FlaskBlueprintSubsystem(SubsystemBase):

    NAME = 'blueprint'

    def configure_grain(self, grain, flask_app):
        _logger.trace('Found blueprint: {}', grain)
        main = grain.load()
        name = None
        for name in dir(main):
            if name.startswith('_'):
                continue
            blueprint = getattr(main, name)
            if isinstance(blueprint, Blueprint):
                break
        else:
            raise RuntimeError('Could not find any blueprint in {}'.format(grain.path))
        url_prefix = grain.config.get('mountpoint', '/')
        _logger.trace('registering {}:{} under {}', grain, name, url_prefix)
        flask_app.register_blueprint(blueprint, url_prefix=url_prefix)

    def iter_locations(self):
        assert self.grains
        for grain in self.grains:
            yield Location(grain.mountpoint)
