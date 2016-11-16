import requests

from .project import Project


def test_empty_project():
    assert Project('empty').on('/').returns(requests.codes.not_found)

def test_simple_views():
    assert Project('simple').on('/').returns('hey')
