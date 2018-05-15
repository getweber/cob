Testing
=======

Testing a cob application is easy, and can be done in two modes -- undockerized and dockerized.

Undockerized Testing
--------------------

Cob supports running tests against your project using the ``pytest`` testing framework. Cob exposes
a default *fixture* for using your app called ``webapp``.

To get started, simply create a ``tests`` folder inside your project, and create your first test
file there. There is no extra cob-specific markup required:

.. code-block:: python

                # tests/test_view.py

                def test_index_view(webapp):
                    assert webapp.get('/') == {'some': 'json'}


Since the vast majority of web services use JSON for the response format, Cob parses it for you, and
thus ``get``, ``post`` etc. return a parsed JSON object by default.

You can override this behavior using ``raw_response=True``, getting the actual response object
(provided by the ``requests`` library). Note that in this mode you have to verify the success of
your request yourself:

.. code-block:: python

                # tests/test_view.py
                import requests

                def test_something_fails(webapp):
                    resp = webapp.post('/some/nonexistent/url')
                    assert resp.status_code == requests.codes.not_found

Dockerized Testing
------------------

While the plain, undockerized mode is good for quick API tests and scenarios that don't require an
entire environment set up, some tests do impose some constraints on the testing environment. The
most notorious examples are ones involving background tasks, interaction with other services such as
Redis, etc.

For this purpose Cob supports testing in "dockerized" mode. This mode is slower since it builds your
docker-compose environment for you, but once run, you can rest assured that the tests work as if
they were in production.

To run the tests in this mode, simply run ``cob docker test``.
