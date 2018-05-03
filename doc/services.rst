Services
========

Cob allows you to work with additional services, in a way that makes them available to your app and
automatically set up during deployment.


Redis
-----

To use redis in your app, include the following in your ``services`` key of your
``.cob-project.yml``::

  # .cob-project.yml
  ...
  services:
    - redis

Then in your app, you can use ``cob.services.redis`` to obtain a working Redis client:

.. code-block:: python

                from cob import services
                ...
                @cob.route('/')
                def index():
                    value = services.redis.get('key')
                    ...
.. note:: During development, the Redis server is not started for you. Cob relies on the existence
          of a running Cob server on your local machine
