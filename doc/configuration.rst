Project Configuration
=====================

Cob puts a strong emphasis on configuration, allowing you to control the various aspects of your project and other 3rd party tools.

Project Config
--------------

Assuming you need a place to store project-specific configuration values, you can use the ``.cob-project.yml`` file located at the root of your project.

Any configuration written in this file will be available to your project via the current project's ``config`` attribute. For instance, for the following contents of ``.cob-project.yml``::

  name: myproj
  some_value: 2

You can access ``some_value`` through the ``config`` project attribute:

.. code-block:: python

  ...
  from cob.project import get_project
  ...
  value = get_project().config['some_value']

.. note:: Some keys in the project config have special meaning, like the project name stored in the ``name`` key or ``flask_config`` described below. To avoid name clashes, it is wise to store all of your specific configuration under a specific key as a nested structure, such as ``config`` or ``project-config``

Cob Config Options
------------------
pypi_index_url - For use with pypi other than https://pypi.org/simple
specific_virtualenv_pkgs - a string of the form 'pip==19.0.1 setuptools==40.6.3'. this will tell cob to udpate pip/setuptools versions inside cob's virtualenv before installing dependencies.


Managing Dependencies
---------------------

Apart from the base dependencies needed by cob itself, which takes care of the facilities your project uses (this includes Flask, SQLAlchemy and Celery for example), you can specify additional dependencies your code relies on. This can be done using the ``deps`` configuration value::

  # .cob-project.yml
  ...
  deps:
      - requests>=1.1.0




Flask Config
------------

You can easily add configuration to Flask's config by specifying it in the ``flask_config`` key of ``.cob-project.yml``::

  # .cob-project.yml
  ...
  flask_config:
      SQLALCHEMY_DATABASE_URI: sqlite:////path/to/db.db

Configuration Loading and Overrides
-----------------------------------

In addition to the current project's ``.cob-project.yml``, Cob looks in other places to load
configuration snippets. This allows you to add overrides and overlays used either locally during
development, or per-server for deployment.

The following locations are scanned for configuration overrides:

* ``/etc/cob/conf.d/<project name>``
* ``~/.config/cob/projects/<project name>``

This means that if you would like a project named ``testme`` to have a private piece of information
in its config loaded during deployment and not stored in the source repository, all you have to do
is add the following::

  SOME_SECRET_CONFIG: 'secret'

In ``/etc/cob/conf.d/testme/000-private.yml`` on your server.

Deployment Configuration
------------------------

Several aspects of Cob's deployment can be configured via the project's configuration files.

Gunicorn Options
~~~~~~~~~~~~~~~~

By adding a ``gunicorn`` dictionary to your project's YAML file, you can control Gunicorn options directly::

  # .cob-project.yml
  gunicorn:
      max_requests: 20

Exposed Ports
~~~~~~~~~~~~~

When deploying via Docker, Cob automatically exposes port 80 for your webapp, but leaves other ports private.

You can customize this behavior using the ``docker.exposed_ports`` configuration. This configuration value is a mapping, containing the list of exposed ports for each service name::

  # .cob-project.yml
  docker:
      exposed_ports:
          wsgi:
             - 443
             - 12345
