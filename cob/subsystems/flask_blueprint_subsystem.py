import logbook

from flask import Blueprint
from .base import SubsystemBase

_logger = logbook.Logger(__name__)

class FlaskBlueprintSubsystem(SubsystemBase):

    NAME = 'blueprint'

    def configure_module(self, module, app):
        _logger.trace('Found blueprint: {}', module)
        main = module.load()
        name = None
        for name in dir(main):
            if name.startswith('_'):
                continue
            blueprint = getattr(main, name)
            if isinstance(blueprint, Blueprint):
                break
        else:
            raise RuntimeError('Could not find any blueprint in {}'.format(module.path))
        url_prefix = module.config.get('mountpoint', '/')
        _logger.trace('registering {}:{} under {}', module, name, url_prefix)
        app.register_blueprint(blueprint, url_prefix=url_prefix)
