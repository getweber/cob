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


Controlling the Database URI
----------------------------

By default, Cob uses an SQLite database located in the project's `.cob` directory for development. In production (when deployed via docker) - it switches to Postgres.

In some cases, however, you may want to use Postgres during development as well, or move to use a different database altogether. For such cases, Cob supports setting the database URI explicitly
through the following methods:

1. You can set your database URI in the configuration file. Simply set ``SQLALCHEMY_DATABASE_URI`` config value in your ``.cob-project.yml`` file:

   .. code-block:: yaml

      name: myproj
      flask_config:
          SQLALCHEMY_DATABASE_URI: postgres://db-server/your-db

2. You can override the database URI used by Cob through the ``COB_DATABASE_URI`` environment
   variable. This method takes precedence over the local project configuration, and therefore is
   useful for overriding the database connection settings during testing or in CI scenarios.

Database Initialization
-----------------------

Note that Cob, by default, does not initialize any DB structure for you when run. This means that
for your code to work, an extra step is required to make sure the database is properly initialized.

If your project **does not** use migrations, you can quickly create all tables and structures using:: 

  $ cob db createall

However, the recommended practice for long-lasting projects is to use migrations. For projects using
migrations, creating the DB is done via ``cob migrate up``, which is described in the
:ref:`migrations` chapter of this guide.

.. note:: Cob takes care of migrations automatically during deployment - the statement above about
          having to initialize your database hold only for the development phase of your project.
