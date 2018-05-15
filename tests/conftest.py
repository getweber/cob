import os
from uuid import uuid4

import logbook

import pytest

from .project import Project
from cob.bootstrapping import _PREVENT_REENTRY_ENV_VAR
from cob.utils.develop import _COB_DEVELOP_MODE


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
