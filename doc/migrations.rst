Using Migrations
================

Once you have created your basic set of models, you may want to start using migrations to manage db revisions.

Initializing the Migrations Directory
-------------------------------------

.. code-block:: bash

       $ cob migrate init

Create a  Revision
------------------

.. code-block:: bash

       $ cob migrate revision -m "My revision name"

Upgrade/Downgrade
-----------------

.. code-block:: bash

       $ cob migrate up

.. code-block:: bash

       $ cob migrate down
