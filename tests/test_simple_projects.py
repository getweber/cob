import requests


def test_empty_project(empty_project):
    with empty_project.server_context() as url:
        assert requests.get(url).status_code == requests.codes.not_found
