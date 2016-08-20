import requests

import pytest


from .project import Project


def test_static_files_same_root():
    pytest.skip('Not implemented yet')


def test_static_files():
    p = Project('staticfiles')
    with p.server_context() as url:
        assert requests.get(url.add_path('static1/file')).text == 'this is #1\n'
        assert requests.get(url.add_path('static2/file')).text == 'this is #2\n'
