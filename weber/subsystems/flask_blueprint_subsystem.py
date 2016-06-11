import logbook

import gossip

from .base import SubsystemBase

_logger = logbook.Logger(__name__)

class FlaskBlueprintSubsystem(SubsystemBase):

    NAME = 'blueprint'

    def configure_app(self, app):
        for blueprint_module in self.modules:
            _logger.trace('Found blueprint: {[blueprint]}', blueprint_module.config)
            bp = blueprint_module.load_python_symbol_by_name(
                blueprint_module.config['blueprint'])
            _logger.trace('registering under {.url_prefix}', bp)
            app.register_blueprint(bp)
