from .utils.url import Mountpoint


class Location:

    def __init__(self, mountpoint, is_frontend_app=False, is_static=False, fs_paths=()):
        assert isinstance(mountpoint, Mountpoint)
        self.mountpoint = mountpoint
        self._is_frontend_app = is_frontend_app
        self._is_static = is_static
        self.fs_paths = list(fs_paths)

    def is_frontend_app(self):
        return self._is_frontend_app

    def is_static(self):
        return self._is_static

    def __repr__(self):
        return f'<Location {self.mountpoint!r} ({self.fs_paths})>'
