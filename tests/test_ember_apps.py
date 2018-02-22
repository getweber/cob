import re

from .project import Project


def test_ember_apps():
    with Project('ember').server_context() as app:

        for asset_uri in _iter_assets(app):
            assert app.get(asset_uri)

        for uri in ['/', '/items']:
            assert 'vendor' in app.get(uri).text

def test_ember_non_root_uri():
    with Project('ember_non_root_uri').server_context() as app:
        assert app.get('/').text == 'root resource here'
        assert 'link rel="stylesheet"' in app.get('/ui/').text


def _iter_assets(app):
    page = app.get('/').text
    yield from re.findall(r'<link rel="stylesheet" href="([^"]*)">', page)
    yield from re.findall(r'<script src="([^"]*)">', page)
