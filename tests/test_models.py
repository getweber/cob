import pytest

from .project import Project

@pytest.mark.parametrize('with_migrations', [True, False])
def test_models(with_migrations):
    project_name = 'models_with_migrations' if with_migrations else 'models_no_migrations'
    assert Project(project_name).on('/index/list_models').returns_json([])
