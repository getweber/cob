import os

import yaml

from .defs import WEBER_CONFIG_FILE_NAME
from .subsystems import Subsystem

_projet = None

class Project(object):

    def __init__(self):
        super(Project, self).__init__()
        self.root = os.path.abspath('.')
        with open(os.path.join(self.root, WEBER_CONFIG_FILE_NAME)) as f:
            yaml_config = yaml.load(f)
        self.name = yaml_config.get('name', os.path.basename(self.root))
        self._subsystems = None

    def iter_subsystems(self, type=None):
        if self._subsystems is None:
            self._load_subsystems()
        for s in self._subsystems:
            if type is not None and s.type != type:
                continue
            yield s

    def _load_subsystems(self):
        subsystems = []
        for directory in os.listdir(self.root):
            path = os.path.join(self.root, directory)
            yml = os.path.join(path, '.weber.yml')
            if not os.path.isfile(yml):
                continue
            with open(yml) as f:
                config = yaml.load(f.read())
            subsystems.append(Subsystem.from_config(path, config))

        self._subsystems = subsystems


_project = None

def get_project():
    global _project # pylint: disable=global-statement
    if _project is None:
        _project = Project()

    return _project
