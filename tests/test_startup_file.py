from .project import Project

def test_startup_file():
    assert Project('startup_file').on('/').returns('ack')
