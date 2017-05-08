import os

import logbook

from .base import SubsystemBase

_logger = logbook.Logger(__name__)



class StaticSubsystem(SubsystemBase):

    NAME = 'static'
    SUPPORTS_OVERLAYS = True

    def add_grain(self, path, config):
        super().add_grain(path, config)
        root = os.path.abspath(os.path.normpath(os.path.join(path, config['root'])))
        self.project.add_static_location(config['mountpoint'], root)

    def configure_grain(self, grain, flask_app):
        pass
