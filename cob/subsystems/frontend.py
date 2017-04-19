import os

from .base import SubsystemBase
from ..utils.url import ensure_trailing_slash

class FrontendSubsystem(SubsystemBase): # pylint: disable=abstract-method
    pass

class EmberSubsystem(FrontendSubsystem):

    NAME = 'frontend-ember'

    def configure_grain(self, grain, flask_app): # pylint: disable=unused-argument
        mountpoint = ensure_trailing_slash(grain.config.get('mountpoint', '/'))
        self.project.add_static_location(mountpoint + 'assets', os.path.join(grain.path, 'dist/assets'))
        self.project.add_static_location(mountpoint, os.path.join(grain.path, 'dist/index.html'), frontend_app=self._is_location_type_auto(grain))

    def _is_location_type_auto(self, grain):
        config_filename = os.path.join(grain.path, 'config', 'environment.js')
        if not os.path.isfile(config_filename):
            return False

        with open(config_filename) as f:
            for line in f:
                if 'locationType' in line:
                    return line.split(':', 1)[1].strip()[1:].lower().startswith('auto')
        return False

    def configure_tmux_window(self, windows):
        for grain in self.grains:
            windows.append({
                'window_name': 'frontend({})'.format(os.path.basename(grain.path)),
                'panes': [
                    'cd "{}" && ember build --watch'.format(grain.path),
                ],
            })
