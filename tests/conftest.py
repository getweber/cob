import os
from uuid import uuid4

import pytest
import yaml

from .utils import write_template


@pytest.fixture
def empty_project(tmpdir):
    returned = ProjectFixture(tmpdir.strpath)
    returned.write_config()
    return returned


class ProjectFixture(object):

    def __init__(self, path):
        super(ProjectFixture, self).__init__()
        self.path = path
        self.name = str(uuid4())

    def write_config(self):
        with open(os.path.join(self.path, '.weber-project.yml'), 'w') as f:
            f.write(yaml.dump({
                'name': self.name,
            }))

    def add_blueprint(self, name):
        bp_path = os.path.join(self.path, name)
        os.makedirs(bp_path)
        with open(os.path.join(bp_path, '.weber.yml'), 'w') as f:
            f.write(yaml.dump({
                'type': 'blueprint',
                'blueprint': 'module:blueprint',
                'mountpoint': '/{}'.format(name),
            }))
        with open(os.path.join(bp_path, 'module.py'), 'w') as f:
            write_template(f, 'blueprint_module.j2', {'name': name})
