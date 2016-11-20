from flask.ext.loopback import FlaskLoopback  # pylint: disable=import-error, no-name-in-module

from ..app import build_app

import requests
import uuid

class Webapp(object):

    def __init__(self):
        super(Webapp, self).__init__()
        self.hostname = str(uuid.uuid1())

    def activate(self):
        self.app = build_app(use_cached=True)
        self.app.config["SECRET_KEY"] = "testing_key"
        self.app.config["TESTING"] = True

        self.loopback = FlaskLoopback(self.app)
        self.loopback.activate_address((self.hostname, 80))

    def deactivate(self):
        self.loopback.deactivate_address((self.hostname, 80))

    def _request(self, method, path, *args, **kwargs):
        if not isinstance(path, str):
            path = str(path)
        raw_response = kwargs.pop("raw_response", False)
        if path.startswith("/"):
            path = path[1:]
            assert not path.startswith("/")
        returned = requests.request(method, "http://{0}/{1}".format(self.hostname, path), *args, **kwargs)
        if raw_response:
            return returned

        returned.raise_for_status()
        return returned.json()

    def get(self, *args, **kwargs):
        return self._request("get", *args, **kwargs)

    def post(self, *args, **kwargs):
        return self._request("post", *args, **kwargs)

    def delete(self, *args, **kwargs):
        return self._request("delete", *args, **kwargs)

    def put(self, *args, **kwargs):
        return self._request("put", *args, **kwargs)
