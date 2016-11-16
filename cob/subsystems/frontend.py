import os

from .base import SubsystemBase

class FrontendSubsystem(SubsystemBase): # pylint: disable=abstract-method
    pass

class EmberSubsystem(FrontendSubsystem):

    NAME = 'frontend-ember'

    def configure_grain(self, grain, flask_app): # pylint: disable=unused-argument
        self.project.add_static_location('/assets', os.path.join(grain.path, 'dist/assets'))
        self.project.add_static_file_alias('/', os.path.join(grain.path, 'dist/index.html'))

    def configure_tmux_window(self, windows):
        for grain in self.grains:
            windows.append({
                'window_name': 'frontend({})'.format(os.path.basename(grain.path)),
                'panes': [
                    'cd "{}" && ember build --watch'.format(grain.path),
                ],
            })
