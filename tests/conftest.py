import logbook
from pathlib import Path
import pytest
from uuid import uuid4
import yaml

from .project import Project


config = None


def pytest_addoption(parser):
    parser.addoption("--prebuilt", action="store_true", default=False,
        help="Use prebuilt docker images")


@pytest.fixture(autouse=True)
def configure(request):
    global config # pylint: disable=global-statement
    config = request.config

    @request.addfinalizer
    def cleanup():    # pylint: disable=unused-variable
        global config # pylint: disable=trailing-whitespace, global-statement
        config = None



@pytest.fixture(scope='session', autouse=True)
def setup_logging():
    logbook.StderrHandler(level=logbook.TRACE).push_application()


@pytest.fixture
def project_name():
    return f'proj{str(uuid4()).replace("-", "_")}'


@pytest.fixture
def empty_project(tmpdir, project_name):
    returned = Project(tmpdir, project_name)
    returned.generate_project()
    return returned


class _ProjectFactory:

    def __init__(self, root):
        self.root = root
        self.config = {}

    def build(self):
        from cob.project import Project
        with (self.root / '.cob-project.yml').open('w') as f:
            yaml.dump(self.config, f)
        return Project(self.root)


@pytest.fixture
def project_factory(tmpdir):
    tmpdir = Path(tmpdir)
    return _ProjectFactory(tmpdir)
