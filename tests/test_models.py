from .project import Project

def test_simple_models():
    proj = Project('models1')
    proj.cmd('cob db createall')
    assert proj.on('/index/list_models').returns_json([])
