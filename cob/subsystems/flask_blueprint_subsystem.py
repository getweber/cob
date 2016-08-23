import logbook

from .base import SubsystemBase

_logger = logbook.Logger(__name__)

class FlaskBlueprintSubsystem(SubsystemBase):

    NAME = 'blueprint'

    def configure_module(self, module, app):
        _logger.trace('Found blueprint: {[blueprint]}', module.config)
        bp = module.load_python_symbol_by_name(
            module.config['blueprint'])
        _logger.trace('registering under {.url_prefix}', bp)
        app.register_blueprint(bp)
