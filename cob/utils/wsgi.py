from ..app import build_app


def app(*args, **kwargs):
    return build_app(use_cached=True)(*args, **kwargs)
