from flask_loopback import FlaskLoopback
from sentinels import NOTHING

from ..app import build_app

import json
import requests
import uuid


class Webapp(object):

    def __init__(self):
        super(Webapp, self).__init__()
        self.hostname = str(uuid.uuid1())

    def __enter__(self):
        self.activate()
        return self

    def __exit__(self, *args):
        self.deactivate()

    def activate(self):
        self.app = build_app(use_cached=True)
        self.app.config["SECRET_KEY"] = "testing_key"
        self.app.config["TESTING"] = True

        self.loopback = FlaskLoopback(self.app)
        self.loopback.activate_address((self.hostname, 80))

    def deactivate(self):
        self.loopback.deactivate_address((self.hostname, 80))

    def request(self, method, path, *args, **kwargs):
        """Performs a request against the server app
        All arguments are similar to requests' ``request``, except for a few
        exceptions listed below

        :keyword raw_response: if ``True``, returns the raw response object and avoids checking for success
        :keyword data_json: if provided, sends the value provided serialized to JSON, and sets the content type to be json accordingly
        """
        if not isinstance(path, str):
            path = str(path)
        raw_response = kwargs.pop("raw_response", False)

        data_json = kwargs.pop('data_json', NOTHING)
        if data_json is not NOTHING:
            if 'data' in kwargs:
                raise RuntimeError('`data` is not supported when combined with `data_json`')
            kwargs['data'] = json.dumps(data_json)
            headers = kwargs['headers'] = dict(kwargs.get('headers', ()))
            if not any(k.lower() == 'content-type' for k in headers):
                headers['Content-type'] = 'application/json'

        if path.startswith("/"):
            path = path[1:]
            assert not path.startswith("/")
        returned = requests.request(method, f"http://{self.hostname}/{path}", *args, **kwargs)
        if raw_response:
            return returned

        returned.raise_for_status()
        return returned.json()

    def get(self, *args, **kwargs):
        """Shortcut for self.request('get', ...)
        """
        return self.request("get", *args, **kwargs)

    def post(self, *args, **kwargs):
        """Shortcut for self.request('post', ...)
        """
        return self.request("post", *args, **kwargs)

    def delete(self, *args, **kwargs):
        """Shortcut for self.request('delete', ...)
        """
        return self.request("delete", *args, **kwargs)

    def put(self, *args, **kwargs):
        """Shortcut for self.request('put', ...)
        """
        return self.request("put", *args, **kwargs)
