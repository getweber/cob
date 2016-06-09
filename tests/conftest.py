import os
from uuid import uuid4

import logbook

import pytest

from .project import Project
from weber.bootstrapping import _PREVENT_REENTRY_ENV_VAR


@pytest.fixture(scope='session', autouse=True)
def setup_logging():
    logbook.StderrHandler(level=logbook.TRACE).push_application()


@pytest.fixture(scope='session', autouse=True)
def prevent_bootstrapping():
    os.environ[_PREVENT_REENTRY_ENV_VAR] = 'true'


@pytest.fixture
def project_name():
    return 'proj{}'.format(str(uuid4()).replace('-', '_'))


@pytest.fixture
def empty_project(tmpdir, project_name):
    returned = Project(tmpdir, project_name)
    returned.generate_project()
    return returned
