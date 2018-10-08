import os

from .base import SubsystemBase
from ..locations import Location


_DEFAULT_NODE_VERSION = 8

class FrontendSubsystem(SubsystemBase): # pylint: disable=abstract-method
    pass

class EmberSubsystem(FrontendSubsystem):

    NAME = 'frontend-ember'

    def get_docker_preamble_steps(self):
        returned = [
            f'FROM node:{self.project.config.get("frontend", {}).get("node_version", _DEFAULT_NODE_VERSION)} as frontend-builder',
            'RUN npm install -g ember-cli',
        ]

        for grain, path in self._iter_grain_frontend_builder_paths():
            returned.extend([
                f'ADD {grain.relpath} {path}',
                f'RUN cd {path} && yarn install && ember build --environment=production',
            ])
        return returned

    def get_docker_install_steps(self):
        returned = []
        for grain, path in self._iter_grain_frontend_builder_paths():
            returned.append(f'COPY --from=frontend-builder {path}/dist {grain.get_path_from("/app")}/dist')
        return returned

    def _iter_grain_frontend_builder_paths(self):
        for index, grain in enumerate(self.grains, 1):
            path = f'/frontend-{index}'
            yield grain, path

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
                'window_name': f'frontend({os.path.basename(grain.path)})',
                'panes': [
                    f'cd "{grain.path}" && ember build --watch',
                ],
            })
