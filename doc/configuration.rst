Project Configuration
=====================

Flask Config
------------

You can easily add configuration to Flask's config by specifying it in the ``flask_config`` key of ``.cob-project.yml``::

  # .cob-project.yml
  ...
  flask_config:
      SQLALCHEMY_DATABASE_URI: sqlite:////path/to/db.db
