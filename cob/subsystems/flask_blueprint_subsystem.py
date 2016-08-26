import logbook

from .base import SubsystemBase

_logger = logbook.Logger(__name__)

class FlaskBlueprintSubsystem(SubsystemBase):

    NAME = 'blueprint'

    def configure_module(self, module, app):
        _logger.trace('Found blueprint: {}', module)
        main = module.load()
        bp = getattr(main, module.config.get('blueprint', 'blueprint'))
        _logger.trace('registering under {.url_prefix}', bp)
        app.register_blueprint(bp)
