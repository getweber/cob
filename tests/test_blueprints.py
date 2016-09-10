import pytest
import requests

from .project import Project

@pytest.mark.parametrize('projname', ['blueprints1', 'blueprints2', 'blueprints3'])
def test_blueprints(projname):
    with Project(projname).server_context() as url:
        for name in ('bp1', 'bp2'):
            assert requests.get(url.add_path(name).add_path('test')).content.decode(
                'utf-8') == 'this is {}'.format(name)
