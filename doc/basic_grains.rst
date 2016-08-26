Basic Grains
============

Views Grain
-----------

*Views* is the simplest type of grain, and it contains plain Flask route functions.

To generate a new views grain, run::

  $ cob generate grain myview --type views

Views grains normally look like this:

.. code-block:: bash

       $ cat myview.py

.. code-block:: python

       # cob: type=views mountpoint=/

       from cob import route

       @route('/sayhi')
       def hi():
	  return 'hi'

Blueprint Grains
----------------

*Blueprint* grains are very similar to views grains, but allow a more direct control over the blueprint they create::

  $ cob generate grain blueprint --type blueprint
  ...
  $ cat blueprint.py

.. code-block:: python

  # cob: type=blueprint mountpoint='/bp'
  from flask import Blueprint

  blueprint = Blueprint(...)
