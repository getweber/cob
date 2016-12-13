import logbook
import gossip

from .project import get_project

_logger = logbook.Logger(__name__)


_cached_app = None

def build_app(*, use_cached=False):
    from flask import Flask

    global _cached_app  # pylint: disable=global-statement
    if use_cached and _cached_app is not None:
        return _cached_app


    proj = get_project()
    _logger.debug('Starting app {.name}...', proj)
    _cached_app = Flask(get_project().name, static_folder=None, template_folder=None)
    proj.configure_app(_cached_app)
    gossip.trigger_with_tags('cob.after_configure_app', {'app': _cached_app})
    _logger.trace('URL map: {}', _cached_app.url_map)
    return _cached_app
