import functools

from ..app import build_app


def appcontext_command(func):
    @functools.wraps(func)
    def new_func(*args, **kwargs):
        with build_app().app_context():
            return func(*args, **kwargs)

    return new_func
