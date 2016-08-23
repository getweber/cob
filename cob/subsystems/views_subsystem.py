import logbook

from .base import SubsystemBase

from flask import Blueprint

_logger = logbook.Logger(__name__)

class ViewsSubsystem(SubsystemBase):

    NAME = 'views'

    def configure_module(self, module, app):
        _logger.trace('Found views module: {}', module)
        main = module.load()
        blueprint = Blueprint(main.__name__, main.__name__, url_prefix=module.config['mountpoint'])
        for deferred_route in main.__cob_routes__:
            deferred_route.register(blueprint)
        app.register_blueprint(blueprint)
