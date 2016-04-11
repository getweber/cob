import gossip
from .base import SubsystemBase


class FlaskBlueprintSubsystem(SubsystemBase):

    NAME = 'blueprint'

    def activate(self):
        super(FlaskBlueprintSubsystem, self).activate()

        for module in self.modules:
            for blueprint_config in module.config['blueprints']:
                bp = module.load_python_symbol_by_name(blueprint_config['blueprint'])
                print('blueprint', bp, 'in', blueprint_config['mountpoint'])

        gossip.register(self.configure_app, 'weber.configure_flask_app')

    def configure_app(self, app):
        import pudb
        pudb.set_trace()
