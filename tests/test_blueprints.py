import requests

from .project import Project

def test_blueprints():
    with Project('blueprints').server_context() as url:
        for name in ('bp1', 'bp2'):
            assert requests.get(url.add_path(name).add_path('test')).content.decode(
                'utf-8') == 'this is {}'.format(name)
