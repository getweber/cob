import re


def ensure_trailing_slash(url):
    if not url.endswith('/'):
        url += '/'
    return url


class Mountpoint:

    def __init__(self, path):
        self.path = ensure_trailing_slash(path)

    def join(self, other):
        if not isinstance(other, Mountpoint):
            other = Mountpoint(other)
        other_path = other.path
        if other_path.startswith('/'):
            other_path = other_path[1:]
        return Mountpoint(self.path + other_path)

    def without_trailing_slash(self):
        return self.path[:-1]

    def __str__(self):
        return self.path

    def __hash__(self):
        return hash(self.path)

    def __eq__(self, other):
        if not isinstance(other, Mountpoint):
            other = Mountpoint(other)
        return self.path == other.path


def sort_paths_specific_to_generic(paths, key=None):
    return sorted(paths, key=_get_path_normalizer(key=key), reverse=True)


def _get_path_normalizer(key=None):
    if key is None:
        return _normalize_path

    def normalizer(a):
        return _normalize_path(key(a))
    return normalizer


def _normalize_path(path):

    path = re.sub(r'/+', '/', path)
    if path.startswith('/'):
        path = path[1:]
    if path.endswith('/'):
        path = path[:-1]
    return tuple(path.split('/'))
