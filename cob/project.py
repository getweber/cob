import os

import emport
import yaml
import logbook

from .defs import COB_CONFIG_FILE_NAME
from .subsystems.manager import SubsystemsManager

from flask.helpers import send_from_directory
from flask import abort

_projet = None

_logger = logbook.Logger(__name__)


class Project(object):

    def __init__(self):
        super(Project, self).__init__()
        self.root = os.path.abspath('.')
        with open(os.path.join(self.root, COB_CONFIG_FILE_NAME)) as f:
            self.config = yaml.load(f)
        self.name = self.config.get('name', os.path.basename(self.root))
        self.subsystems = SubsystemsManager(self)

        self.static_locations = {}
        self.static_aliases = {}
        self._initialized = False

    def get_deps(self):
        return set(self.config.get('deps') or ())

    def initialize(self):
        if self._initialized:
            return
        project_file_path = os.path.join(self.root, 'project.py')
        if os.path.isfile(project_file_path):
            emport.import_file(project_file_path)
        self._initialized = True

    def configure_app(self, app):
        self.initialize()
        app.config.update(self.config.get('flask_config', {}))
        self.subsystems.configure_app(app)
        self._configure_static_locations(app)

    def add_static_location(self, url_path, fs_path):
        self.static_locations.setdefault(url_path, []).append(os.path.abspath(fs_path))

    def add_static_file_alias(self, url_path, fs_path):
        assert url_path not in self.static_aliases
        self.static_aliases[url_path] = os.path.abspath(fs_path)

    def _configure_static_locations(self, flask_app):
        for url_path, fs_paths in self.static_locations.items():
            if not url_path.endswith('/'):
                url_path += '/'
            flask_app.route(url_path + '<path:filename>',
                            defaults={'search_locations': fs_paths})(_static_view)

        for url_path, fs_path in self.static_aliases.items():
            flask_app.route(url_path, defaults={'path': fs_path})(
                _static_alias_view)


def _static_view(filename, search_locations):
    for location in search_locations:
        if not location.endswith('/'):
            location += '/'
        _logger.trace('looking for {!r} in {!r}...', filename, location)
        p = os.path.join(location, filename)
        if os.path.exists(p) and os.path.abspath(p).startswith(location):
            _logger.trace('Found. Serving')
            return send_from_directory(location, filename)
    abort(404)


def _static_alias_view(path):
    return send_from_directory(os.path.dirname(path), os.path.basename(path))


_project = None


def get_project():
    global _project  # pylint: disable=global-statement
    if _project is None:
        _project = Project()

    return _project
