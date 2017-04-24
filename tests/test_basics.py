import pytest

from .project import Project

@pytest.mark.parametrize('blueprint_type', ['directory', 'file'])
def test_blueprints(blueprint_type):
    with Project('basics').server_context() as app:
        assert app.get('blueprints/{}/test'.format(blueprint_type)).content.decode('utf-8') == 'this is {}'.format(blueprint_type)
