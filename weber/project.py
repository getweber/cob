import os

import yaml

from .defs import WEBER_CONFIG_FILE_NAME
from .subsystems.manager import SubsystemsManager

_projet = None

class Project(object):

    def __init__(self):
        super(Project, self).__init__()
        self.root = os.path.abspath('.')
        with open(os.path.join(self.root, WEBER_CONFIG_FILE_NAME)) as f:
            yaml_config = yaml.load(f)
        self.name = yaml_config.get('name', os.path.basename(self.root))
        self.subsystems = SubsystemsManager(self)




_project = None

def get_project():
    global _project # pylint: disable=global-statement
    if _project is None:
        _project = Project()
        _project.subsystems.activate()

    return _project