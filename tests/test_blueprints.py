import requests

from .utils import server_context


def test_blueprints(empty_project):
    names = ['bp1', 'bp2']
    for name in names:
        empty_project.add_blueprint(name)
    with server_context(empty_project) as url:
        for name in names:
            assert requests.get(url.add_path(name)).json()['result'] == name
