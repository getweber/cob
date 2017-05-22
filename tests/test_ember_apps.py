import re

from .project import Project


def test_ember_assets():
    with Project('ember').server_context() as app:
        for asset_uri in _iter_assets(app):
            assert app.get(asset_uri)

def _iter_assets(app):
    page = app.get('/').text
    yield from re.findall(r'<link rel="stylesheet" href="([^"]*)">', page)
    yield from re.findall(r'<script src="([^"]*)">', page)
