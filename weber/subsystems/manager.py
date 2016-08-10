import os

import yaml
import logbook

from .base import SubsystemBase

_logger = logbook.Logger(__name__)


class SubsystemsManager(object):

    def __init__(self, project):
        super(SubsystemsManager, self).__init__()
        self.project = project
        self._subsystems = {}
        self._load_project_subsystems()

    def _load_project_subsystems(self):
        for directory in os.listdir(self.project.root):
            path = os.path.join(self.project.root, directory)
            yml = os.path.join(path, '.weber.yml')
            if not os.path.isfile(yml):
                continue
            with open(yml) as f:
                config = yaml.load(f.read())
            _logger.debug(
                'Detected module in {} (subsystem: {[type]}', directory, config)
            subsystem_cls = self._get_subsystem_by_module_type(config['type'])
            subsystem = self._subsystems.get(subsystem_cls.NAME)
            if subsystem is None:
                subsystem = self._subsystems[
                    subsystem_cls.NAME] = subsystem_cls(self)
            subsystem.add_module(path, config)

    def _get_subsystem_by_module_type(self, module_type):
        return SubsystemBase.SUBSYSTEM_BY_NAME[module_type]

    def activate(self):
        for subsystem in self:
            subsystem.activate()

    def __iter__(self):
        return iter(self._subsystems.values())


##########################################################################
# import all known subsystems to ensure registration
from . import flask_blueprint_subsystem  # pylint: disable=unused-import
from . import static_subsystem  # pylint: disable=unused-import
from . import models_subsystem  # pylint: disable=unused-import
