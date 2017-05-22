import os

import logbook

from .base import SubsystemBase
from ..locations import Location

_logger = logbook.Logger(__name__)



class StaticSubsystem(SubsystemBase):

    NAME = 'static'
    SUPPORTS_OVERLAYS = True

    def configure_grain(self, grain, flask_app):
        pass

    def iter_locations(self):
        assert self.grains

        mountpoints_to_paths = {}
        for grain in self.grains:
            root = os.path.abspath(os.path.normpath(os.path.join(grain.path, grain.config['root'])))
            mountpoints_to_paths.setdefault(grain.mountpoint, []).append(root)

        for mountpoint, paths in mountpoints_to_paths.items():
            yield Location(mountpoint=mountpoint, fs_paths=paths, is_static=True)
