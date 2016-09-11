import os

import logbook

from .base import SubsystemBase

_logger = logbook.Logger(__name__)



class StaticSubsystem(SubsystemBase):

    NAME = 'static'

    def configure_module(self, module, app): # pylint: disable=unused-argument
        cfg = module.config
        root = os.path.join(module.path, cfg['root'])
        self.project.add_static_location(cfg['mountpoint'], root)
