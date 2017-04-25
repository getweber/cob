import os
import sys

import emport
import yaml
import logbook

from .defs import COB_CONFIG_FILE_NAME
from .exceptions import NotInProject
from .subsystems.manager import SubsystemsManager
from .utils.static_files import StaticLocation
from .utils.url import ensure_trailing_slash

from flask.helpers import send_from_directory
from flask import abort

_projet = None

_logger = logbook.Logger(__name__)


class Project(object):

    def __init__(self):
        super(Project, self).__init__()
        self.root = os.path.abspath('.')
        self._static = {}

        config_filename = os.path.join(self.root, COB_CONFIG_FILE_NAME)

        if not os.path.isfile(config_filename):
            raise NotInProject('You do not seem to be in a Cob project directory')

        with open(config_filename) as f:
            self.config = yaml.load(f)
        self.name = self.config.get('name', os.path.basename(self.root))
        self.subsystems = SubsystemsManager(self)

        self._initialized = False

    def build_venv_command(self, cmd):
        cmd, *remainder = cmd.split()
        returned = os.path.abspath(os.path.join(self.root, '.cob', 'env', 'bin', cmd))
        return ' '.join([returned, *remainder])

    def get_deps(self):
        return set(self.config.get('deps') or ())

    def initialize(self):
        if self._initialized:
            return
        assert '_cob' not in sys.modules
        emport.set_package_name(self.root, '_cob')

        project_file_path = os.path.join(self.root, 'project.py')
        if os.path.isfile(project_file_path):
            emport.import_file(project_file_path)
        self._initialized = True

    def configure_app(self, app):
        self.initialize()
        app.config.update(self.config.get('flask_config', {}))
        self.subsystems.configure_app(app)
        self._configure_static_locations(app)

    def add_static_location(self, url_path, fs_path, frontend_app=False):
        self._static.setdefault(url_path, StaticLocation(url_path, frontend_app=frontend_app)).add_fs_path(fs_path)

    def _configure_static_locations(self, flask_app):

        for location in self._static.values():

            url_path = ensure_trailing_slash(location.url_path)

            if location.frontend_app:
                flask_app.route(ensure_trailing_slash(url_path), defaults={'path': location.fs_paths[0]})(
                    _static_alias_view)
            else:
                flask_app.route(url_path + '<path:filename>',
                                defaults={'search_locations': location.fs_paths})(_static_view)


    def iter_static_locations(self):
        yield from self._static.values()

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


def _static_alias_view(path, ignored=None): # pylint: disable=unused-argument
    return send_from_directory(os.path.dirname(path), os.path.basename(path))


_project = None


def get_project():
    global _project  # pylint: disable=global-statement
    if _project is None:
        _project = Project()

    return _project
