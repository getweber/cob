import pytest
from cob.app import build_app
from cob.utils.unittests import Webapp


@pytest.fixture
def webapp(request):
    returned = Webapp(build_app(use_cached=True))
    returned.app.config["SECRET_KEY"] = "testing_key"
    returned.app.config["TESTING"] = True
    returned.activate()
    request.addfinalizer(returned.deactivate)
    return returned
