import os
import sys

import emport
import flask_migrate
from flask.helpers import send_from_directory
from flask import abort
import logbook
import yaml

from .defs import COB_CONFIG_FILE_NAME, PYPI_INDEX_ENV_VAR
from .ctx import context
from .exceptions import NotInProject
from .service_manager import Services
from .subsystems.manager import SubsystemsManager
from .utils.config import merge_config, load_overrides
from .utils.url import sort_paths_specific_to_generic


_projet = None

_logger = logbook.Logger(__name__)


DEFAULT_CONFIG = {
    'flask_config': {
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    },
}


class Project(object):

    def __init__(self, root='.'):
        super(Project, self).__init__()
        self.root = os.path.abspath(root)
        self._static = {}

        config_filename = os.path.join(self.root, COB_CONFIG_FILE_NAME)

        if not os.path.isfile(config_filename):
            raise NotInProject(f'You do not seem to be in a Cob project directory (Currently in {self.root})')

        with open(config_filename) as f:
            config = merge_config(DEFAULT_CONFIG, yaml.full_load(f))

        self.config = load_overrides(config)

        self.name = self.config.get('name', os.path.basename(self.root))
        self.subsystems = SubsystemsManager(self)
        self.services = Services(self)

        self._initialized = False

    def setup_db(self):
        """Either runs migrations or creates all models, if needed
        """
        if self.subsystems.has_subsystem('models'):
            if self.subsystems.models.has_migrations():
                flask_migrate.upgrade()
            else:
                context.db.create_all()

    def get_docker_image_name(self):
        return self.config.get('docker', {}).get('image_name', self.name)

    def is_dockerized(self):
        return bool(os.environ.get('COB_DOCKERIZED'))

    def build_venv_command(self, cmd):
        cmd, *remainder = cmd.split()
        returned = os.path.abspath(os.path.join(self.root, '.cob', 'env', 'bin', cmd))
        return ' '.join([returned, *remainder])

    def get_deps(self):
        return set(self.config.get('deps') or ())

    def get_pypi_index_url(self):
        _index = self.config.get(PYPI_INDEX_ENV_VAR.lower()) or os.environ.get(PYPI_INDEX_ENV_VAR)
        if _index:
            _logger.trace(f'Using PYPI INDEX URL {_index}')
        return _index

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

    def get_sorted_locations(self):
        return sort_paths_specific_to_generic(
            self._iter_all_locations(),
            key=lambda location: location.mountpoint.path)

    def _iter_all_locations(self):
        for subsystem in self.subsystems:
            location_iterator = subsystem.iter_locations()
            if location_iterator is None:
                continue
            yield from location_iterator

    def _configure_static_locations(self, flask_app):

        for location in self.get_sorted_locations():
            if not location.is_static():
                continue

            if location.is_frontend_app():
                for alias in (str(location.mountpoint), f'{location.mountpoint}<path:ignored>'):
                    flask_app.route(alias, defaults={'path': location.fs_paths[0]})(_static_alias_view)
            else:
                flask_app.route(f'{location.mountpoint}<path:filename>',
                                defaults={'search_locations': location.fs_paths})(_static_view)


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
