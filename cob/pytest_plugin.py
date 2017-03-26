import pytest
from cob.utils.unittests import Webapp


@pytest.yield_fixture
def webapp(request):  # pylint: disable=unused-argument
    with Webapp() as _webapp, _webapp.app.app_context():
        yield _webapp
