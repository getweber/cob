from .project import Project

def test_secret_key_config():
    def _get_secret():
        with Project('basics').server_context() as app:
            return app.get('config').json()['flask_config']['SECRET_KEY']

    secret = _get_secret()

    assert secret
    assert len(secret) > 20

    assert _get_secret() == secret
