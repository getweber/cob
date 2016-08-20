import requests

from .project import Project


def test_empty_project():
    with Project('empty').server_context() as url:
        assert requests.get(url).status_code == requests.codes.not_found
