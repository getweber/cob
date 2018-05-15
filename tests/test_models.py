import subprocess
import pytest

from .project import Project

@pytest.mark.parametrize('with_migrations', [True, False])
def test_models(with_migrations):
    project_name = 'models_with_migrations' if with_migrations else 'models_no_migrations'
    with Project(project_name).server_context() as app:
        app.post('/index/purge')
        assert app.get('/index/list_models').json() == []
        app.post('/index/add_model')
        assert len(app.get('/index/list_models').json()) > 0 # pylint: disable=len-as-condition
        assert int(subprocess.check_output(
            f"docker exec {project_name.replace('_', '')}_db_1 psql {project_name} -A -t -U {project_name}  -c 'select count(*) from person'", shell=True)) == 1
