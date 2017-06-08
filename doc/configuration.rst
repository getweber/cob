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


Flask Config
------------

You can easily add configuration to Flask's config by specifying it in the ``flask_config`` key of ``.cob-project.yml``::

  # .cob-project.yml
  ...
  flask_config:
      SQLALCHEMY_DATABASE_URI: sqlite:////path/to/db.db

Deployment Configuration
------------------------

Several aspects of Cob's deployment can be configured via the project's configuration files.

Gunicorn Options
~~~~~~~~~~~~~~~~

By adding a ``gunicorn`` dictionary to your project's YAML file, you can control Gunicorn options directly::

  # .cob-project.yml
  gunicorn:
      max_requests: 20
