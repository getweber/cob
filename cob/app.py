import logbook
import gossip

from .project import get_project
# from .celery_utils import celery_app

_logger = logbook.Logger(__name__)


_cached_app = None

_building = False

def build_app(*, use_cached=False, config_overrides=None):
    from flask import Flask

    global _cached_app  # pylint: disable=global-statement
    global _building    # pylint: disable=global-statement
    if use_cached and _cached_app is not None:
        return _cached_app

    if config_overrides is None:
        config_overrides = {}

    if _building:
        raise RuntimeError('Attempted to create an app while an app was already being initialized!')

    _building = True
    try:
        proj = get_project()
        _logger.debug('Starting app {.name}...', proj)
        _cached_app = Flask(get_project().name, static_folder=None, template_folder=None)
        _cached_app.config.update(config_overrides)
        proj.configure_app(_cached_app)
        gossip.trigger_with_tags('cob.after_configure_app', {'app': _cached_app})
        _logger.trace('URL map: {}', _cached_app.url_map)
        return _cached_app
    finally:
        _building = False
