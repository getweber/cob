from .project import Project

def test_simple_models():
    assert Project('models1').on('/index/list_models').returns_json([])
