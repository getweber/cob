import functools

from ..app import build_app
from ..bootstrapping import ensure_project_bootstrapped


def appcontext_command(func):
    @functools.wraps(func)
    def new_func(*args, **kwargs):
        ensure_project_bootstrapped()
        with build_app().app_context():
            return func(*args, **kwargs)

    return new_func
