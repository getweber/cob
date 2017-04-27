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
        assert len(app.get('/index/list_models').json()) > 0
        assert int(subprocess.check_output(
            "docker exec {0}_db_1 psql {1} -A -t -U {1}  -c 'select count(*) from person'".format(
                project_name.replace('_', ''), project_name).strip(), shell=True)) == 1
