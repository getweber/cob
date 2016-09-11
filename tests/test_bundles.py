from .project import Project

def test_bundle():
    assert Project('bundles').on('/').returns('hey')
