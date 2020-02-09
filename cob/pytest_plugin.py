import pytest

from cob.app import build_app
from cob.project import is_cob_project
from cob.utils.unittests import Webapp

@pytest.yield_fixture
def webapp(request):  # pylint: disable=unused-argument
    with Webapp() as _webapp, _webapp.app.app_context():
        yield _webapp


def pytest_configure(config):  # pylint: disable=unused-argument
    if is_cob_project():
        build_app(use_cached=True)
