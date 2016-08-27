import requests

from .project import Project


def test_templates():
    assert Project('templates').on('/test').returns('hey')
