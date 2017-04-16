import pytest
import requests

from .project import Project

@pytest.mark.parametrize('projname', ['blueprints1', 'blueprints2', 'blueprints3'])
def test_blueprints(projname):
    with Project(projname).server_context() as app:
        for name in ('bp1', 'bp2'):
            assert app.get('{}/test'.format(name)).content.decode(
                'utf-8') == 'this is {}'.format(name)
