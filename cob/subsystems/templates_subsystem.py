import logbook

from .base import SubsystemBase

_logger = logbook.Logger(__name__)

class FlaskBlueprintSubsystem(SubsystemBase):

    NAME = 'templates'

    def configure_grain(self, grain, app):
        if app.template_folder is not None:
            raise RuntimeError('Multiple template dirs not supported yet')

        app.template_folder = grain.path
