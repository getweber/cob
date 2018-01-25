.. _db:

Working with Databases
======================

Models Grains
-------------

*Models grains* provide the ability to define your models to be used by your applications. Their structure is very straightforward, and relies on SQLAlchemy::

  $ cob generate grain my_models --type models

Then you can add your models in my_models.py:

.. code-block:: python

       # cob: type=models
       from cob import db

       class Person(db.Model):
	   id = db.Column(db.Integer, primary_key=True)

To direct cob to the database to use, you can add your database URI to ``.cob-project.yml`` under ``flask_config``::

  name: myproj
  flask_config:
      SQLALCHEMY_DATABASE_URI: sqlite:////path/to/db.db


.. note:: By default, Cob uses an SQLite database located in the project's `.cob` directory for development, and switches to use Postgres for production (e.g. when being deployed as a docker container). In some cases you may want to use Postgres during development as well. In such cases, make sure you have a local Postgres instance running, and change the relevant DB URL to point at it (e.g. `postgres://localhost/your_db`)

To quickly create your database and its relations, you can run::

  $ cob db createall

.. warning:: The proper way to initialize your database is through :ref:`migrations`. The ``createall`` command is only intended for quick experimenting if you are not interested in preserving your data for long periods and across revisions
