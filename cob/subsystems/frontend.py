import os

from .base import SubsystemBase
from ..locations import Location

class FrontendSubsystem(SubsystemBase): # pylint: disable=abstract-method
    pass

class EmberSubsystem(FrontendSubsystem):

    NAME = 'frontend-ember'

    def get_docker_pre_install_steps(self):
        return [
            'RUN npm install -g ember-cli bower',
        ]


    def get_docker_install_steps(self):
        return [
            'RUN cd {} && npm install && bower install --allow-root && ember build --environment=production'.format(grain.get_path_from('/app'))
            for grain in self.grains
        ]

    def add_grain(self, path, config):
        config.setdefault('mountpoint', '/')
        return super().add_grain(path, config)

    def configure_grain(self, grain, flask_app):
        pass

    def iter_locations(self):
        assert self.grains
        for grain in self.grains:
            yield Location(
                mountpoint=grain.mountpoint.join('assets'),
                fs_paths=[os.path.join(grain.path, 'dist/assets')],
                is_static=True,
            )
            yield Location(
                mountpoint=grain.mountpoint,
                fs_paths=[os.path.join(grain.path, 'dist/index.html')],
                is_frontend_app=self._is_location_type_auto(grain),
                is_static=True,
            )

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
