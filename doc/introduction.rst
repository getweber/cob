Introduction
============

What is Cob?
------------


Everyone knows how to build a web application in theory. Most resources and tutorials go as far as a basic "hello world" webapp, and leave many details up for the developer to find out. Almost all serious webapps need to take care of deployment, configuration, background tasks, DB models/connections/migrations, static files location and configuration, and much much more.

Cob is a utility for building a solid scaffold for your webapps, and takes care of intertwining the various parts of a robust webapp for you. It also tries to leave as much as the glue code inside Cob itself, so you can avoid as much boilerplate code in your own project as possible.

Cob is relatively opinionated about how projects should be structured, and provides utilities for generating the various components out of well-known templates.

Cob is greatly inspired by *Ember CLI*, which also aimed at solving a similar problem.

Cob in 5 Minutes
----------------

Install Cob
~~~~~~~~~~~

.. code-block:: bash

       $ pip install cob

Generate a project
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

       $ cob generate project myproj
       $ cd myproj
