from .project import Project

def test_redis_service():
    with Project('services').server_context() as app:
        assert app.get('/test_redis').ok
