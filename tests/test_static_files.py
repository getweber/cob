from .project import Project


def test_static_files_same_root():
    p = Project('basics')
    with p.server_context() as app:
        assert app.get('static1/file').text == 'this is #1\n'
        assert app.get('static1/file3').text == 'this is #3\n'


def test_static_files():
    p = Project('basics')
    with p.server_context() as app:
        assert app.get('static1/file').text == 'this is #1\n'
        assert app.get('static2/file').text == 'this is #2\n'
