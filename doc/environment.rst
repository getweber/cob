.. _environments:

The Cob Environment
===================

Virtualenv and Dependencies
---------------------------

When you run a cob project, you use the ``cob`` console script belonging to your external environment, but it, in turn, creates an internal virtual environment (through ``virtualenv``) to run your project. This is done automatically for you, and the resulting virtualenv is saved under ``.cob/env`` in your project root.

Cob takes care of only refreshing this environment when needed (e.g. when it is deleted or when new dependencies exist in your configuration, as described below).

.. note::
   You can always use the ``COB_REFRESH_ENV`` environment variable to force cob to refresh your virtualenv:

   .. code:: bash

       $ COB_REFRESH_ENV=1 cob testserver


Additional Dependencies
-----------------------

You can install additional dependencies through the ``deps`` section of the ``.cob-project.yml`` file::

  # .cob-project.yml
  ...
  deps:
    - Flask-Security
    - Flask-SQLAlchemy>=0.1.0
