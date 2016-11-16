Using Migrations
================

Cob makes it easy for you to create migrations for your data, and will help you to execute them during deployment and testing, as we will see later on.

Cob uses `Alembic <http://alembic.zzzcomputing.com/en/latest/>`_ for database migration management - for more information please refer to Alembic's docs.

Initializing the Migrations Directory
-------------------------------------

You will first need to create your migrations directory (this is a one-time operation)

.. code-block:: bash

       $ cob migrate init

This will create a ``migrations`` directory, and within it ``versions``, which will contain your migration scripts.

Create a  Revision
------------------

.. code-block:: bash

       $ cob migrate revision -m "My revision name"

This will compare the needed changes to bring your DB up-to-date. Please make sure to run it with a database that is already migrated to the latest revision.

Upgrade/Downgrade
-----------------

Migrating up and down the revision tree is done via ``migrate up`` and ``migrate down``:

.. code-block:: bash

       $ cob migrate up

.. code-block:: bash

       $ cob migrate down
