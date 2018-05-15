import os

import yaml
import logbook

from .base import SubsystemBase
from ..exceptions import MountpointConflict, UnknownSubsystem
from ..utils.parsing import parse_front_matter

_logger = logbook.Logger(__name__)


class SubsystemsManager(object):

    def __init__(self, project):
        super(SubsystemsManager, self).__init__()
        self.project = project
        self._subsystems = {}
        self._load_project_subsystems()
        self._validate_config()


    def _validate_config(self):
        mountpoints_to_grains = {}
        for subsystem in self._subsystems.values():
            for grain in subsystem.grains:
                if grain.mountpoint is not None:
                    mountpoints_to_grains.setdefault(grain.mountpoint, []).append(grain)

        for mountpoint, grains in mountpoints_to_grains.items():
            assert len(grains) > 0 # pylint: disable=len-as-condition
            if len(grains) == 1:
                continue
            subsystems = {grain.subsystem for grain in grains}
            if len(subsystems) > 1 or not grains[0].subsystem.SUPPORTS_OVERLAYS:
                raise MountpointConflict(f'Mount point {mountpoint} used more than once')

    def _load_project_subsystems(self):
        roots = [self.project.root]
        while roots:
            root = roots.pop()
            for name in os.listdir(root):
                if os.path.isfile(name) and (name.startswith('.') or not name.endswith('.py')):
                    continue
                _logger.trace('Examining {}...', name)
                path = os.path.join(root, name)
                config = self._try_get_config(path)
                if config is None:
                    _logger.trace('{} does not seem to be a cob grain. Skipping...', name)
                    continue
                grain_type = config.setdefault('type', 'views')
                _logger.trace(
                    'Detected grain in {} (subsystem: {})', name, grain_type)
                if grain_type == 'bundle':
                    _logger.trace('Will traverse into bundle {}', path)
                    roots.append(path)
                    continue
                try:
                    subsystem_cls = self._get_subsystem_by_grain_type(grain_type)
                except UnknownSubsystem:
                    raise UnknownSubsystem(f'Grain {path} uses an unknown subsystem type: {grain_type!r}') from None
                subsystem = self._subsystems.get(subsystem_cls.NAME)
                if subsystem is None:
                    subsystem = self._subsystems[
                        subsystem_cls.NAME] = subsystem_cls(self)
                subsystem.add_grain(os.path.abspath(path), config)
        _logger.trace('Grain loading complete')

    def _try_get_config(self, path):
        yml = os.path.join(path, '.cob.yml')
        if os.path.isfile(yml):
            with open(yml) as f:
                return yaml.load(f.read())

        if os.path.isfile(path):
            with open(path) as f:
                return parse_front_matter(f)

        _logger.trace('No cob config detected ({}). Skipping...', path)
        return None

    def configure_app(self, flask_app):
        for subsystem in self:
            subsystem.activate(flask_app)

        for subsystem in self:
            subsystem.configure_app(flask_app)

    def _get_subsystem_by_grain_type(self, grain_type):
        try:
            return SubsystemBase.SUBSYSTEM_BY_NAME[grain_type]
        except KeyError:
            raise UnknownSubsystem(f'Unknown subsystem type: {grain_type!r}')

    def __iter__(self):
        return iter(self._subsystems.values())

    def __getattr__(self, subsystem_name):
        try:
            return self[subsystem_name]
        except LookupError:
            raise AttributeError(subsystem_name) from None

    def __getitem__(self, subsystem_name):
        if subsystem_name not in self._subsystems:
            raise LookupError(subsystem_name)
        return self._subsystems[subsystem_name]

    def has_subsystem(self, name_or_cls):
        if name_or_cls in self._subsystems:
            return True

        if isinstance(name_or_cls, type):
            for subsystem in self._subsystems.values():
                if isinstance(subsystem, name_or_cls):
                    return True
        return False

    def has_database(self):
        return self.has_subsystem('models')

    def has_tasks(self):
        return self.has_subsystem('tasks')


##########################################################################
# import all known subsystems to ensure registration
from . import flask_blueprint_subsystem  # pylint: disable=unused-import
from . import static_subsystem  # pylint: disable=unused-import
from . import models_subsystem  # pylint: disable=unused-import
from . import views_subsystem  # pylint: disable=unused-import
from . import templates_subsystem  # pylint: disable=unused-import
from . import tasks_subsystem # pylint: disable=unused-import
from . import frontend  # pylint: disable=unused-import
from . import unittests  # pylint: disable=unused-import
