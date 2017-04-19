class StaticLocation(object):

    def __init__(self, url_path, frontend_app=False):
        self.url_path = url_path
        self.fs_paths = []
        self.frontend_app = frontend_app

    def add_fs_path(self, fs_path):
        if self.fs_paths and self.frontend_app:
            raise RuntimeError('Multiple locations not supported for frontend apps')
        self.fs_paths.append(fs_path)

    @property
    def url_path_no_trailing_slash(self):
        returned = self.url_path
        while returned.endswith('/'):
            returned = returned[:-1]
        return returned
