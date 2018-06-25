import pytest

from .project import Project

@pytest.mark.parametrize('blueprint_type', ['directory', 'file'])
def test_blueprints(blueprint_type):
    with Project('basics').server_context() as app:
        assert app.get(f'blueprints/{blueprint_type}/test').content.decode('utf-8') == f'this is {blueprint_type}'


def test_default_config_no_track_modifications():
    with Project('basics').server_context() as app:
        assert app.get('config').json()['flask_config']['SQLALCHEMY_TRACK_MODIFICATIONS'] == False
