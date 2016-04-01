import os
from uuid import uuid4

import pytest
import yaml


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
        with open(os.path.join(self.path, '.weber.yml'), 'w') as f:
            f.write(yaml.dump({
                'name': self.name,
            }))
