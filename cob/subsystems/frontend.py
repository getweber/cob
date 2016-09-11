import os

from .base import SubsystemBase

class FrontendSubsystem(SubsystemBase):

    pass

class EmberSubsystem(FrontendSubsystem):

    NAME = 'frontend-ember'

    def configure_module(self, module, flask_app): # pylint: disable=unused-argument
        self.project.add_static_location('/assets', os.path.join(module.path, 'dist/assets'))
        self.project.add_static_file_alias('/', os.path.join(module.path, 'dist/index.html'))
