from .project import Project

def test_bundle():
    assert Project('basics').on('/bundle/index').returns('hey')
