import os

import logbook

from .base import SubsystemBase

_logger = logbook.Logger(__name__)



class StaticSubsystem(SubsystemBase):

    NAME = 'static'

    def configure_grain(self, grain, app): # pylint: disable=unused-argument
        cfg = grain.config
        root = os.path.join(grain.path, cfg['root'])
        self.project.add_static_location(cfg['mountpoint'], root)
