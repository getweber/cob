import pytest
from cob.app import build_app
from cob.utils.unittests import Webapp


@pytest.fixture
def webapp(request):
    returned = Webapp()
    returned.activate()
    request.addfinalizer(returned.deactivate)
    return returned
