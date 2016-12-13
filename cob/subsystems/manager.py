import os

import yaml
import logbook

from .base import SubsystemBase
from ..utils.parsing import parse_front_matter

_logger = logbook.Logger(__name__)


class SubsystemsManager(object):

    def __init__(self, project):
        super(SubsystemsManager, self).__init__()
        self.project = project
        self._subsystems = {}
        self._load_project_subsystems()

    def _load_project_subsystems(self):
        roots = [self.project.root]
        while roots:
            root = roots.pop()
            for name in os.listdir(root):
                _logger.trace('Examining {}...', name)
                path = os.path.join(root, name)
                config = self._try_get_config(path)
                if config is None:
                    _logger.trace('{} does not seem to be a cob grain. Skipping...', name)
                    continue
                _logger.trace(
                    'Detected grain in {} (subsystem: {[type]}', name, config)
                if config['type'] == 'bundle':
                    _logger.trace('Will traverse into bundle {}', path)
                    roots.append(path)
                    continue
                subsystem_cls = self._get_subsystem_by_grain_type(config['type'])
                subsystem = self._subsystems.get(subsystem_cls.NAME)
                if subsystem is None:
                    subsystem = self._subsystems[
                        subsystem_cls.NAME] = subsystem_cls(self)
                subsystem.add_grain(path, config)
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
        return SubsystemBase.SUBSYSTEM_BY_NAME[grain_type]

    def __iter__(self):
        return iter(self._subsystems.values())


##########################################################################
# import all known subsystems to ensure registration
from . import flask_blueprint_subsystem  # pylint: disable=unused-import
from . import static_subsystem  # pylint: disable=unused-import
from . import models_subsystem  # pylint: disable=unused-import
from . import views_subsystem  # pylint: disable=unused-import
from . import templates_subsystem  # pylint: disable=unused-import
from . import frontend  # pylint: disable=unused-import
from . import unittests  # pylint: disable=unused-import
