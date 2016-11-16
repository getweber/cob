Introduction
============

What is Cob?
------------


Everyone knows how to build a web application in theory. Most resources and tutorials go as far as a basic "hello world" webapp, and leave many details up for the developer to find out. Almost all serious webapps need to take care of deployment, configuration, background tasks, DB models/connections/migrations, static files location and configuration, and much much more.

Cob is a utility for building a solid scaffold for your webapps, and takes care of intertwining the various parts of a robust webapp for you. It also tries to leave as much of the glue code as possible inside Cob itself, so you can avoid as much boilerplate code in your own project as possible.

Cob is relatively opinionated about how projects should be structured, and provides utilities for generating the various components out of well-known templates.

Cob is greatly inspired by *Ember CLI*, which also aimed at solving a similar problem.

Anatomy of a Cob App
--------------------
A Cob App is built from *configuration*, letting cob know how to build, test and deploy your app, and from *grains*. Grains can be individual files or whole directories, and they comprise the individual parts of your app. For example - a grain can be a blueprint binding multiple Flask views, or it can be a whole front-end UI written in JavaScript. Cob has well-defined grain types, and it knows how to deal with them.

Getting Started
---------------

Installation
~~~~~~~~~~~~
You can install cob from ``pip``, just by using::

  $ pip install cob

Generating an Empty Project
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Cob has a utility for generating grains and projects, and it can be used to generate an empty project for us::

  $ cob generate project myproj
  $ tree myproj
  myproj
  └── .cob-project.yml

  0 directories, 1 file

Your project is now created, and already has its base configuration in the ``.cob-project.yml``. By default, it only contains the project name to be used.

The Simplest App - The Views Grain
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Now it's time to populate our app with grains. Grains, as mentioned earlier, are the actual pieces of functionality in your app.

The simplest grain to demonstrate is the **views** grain, and it should be recognizable to anyone familiar with Flask::

  $ cat myproj/index.py

.. code-block:: python

  # cob: type=views mountpoint=/
  from cob import route

  @route('hey')
  def say_hey():
      return 'hey'

Our file contains the mount point (a.k.a the url prefix) for our grain, and indicates it is a views grain, meaning a grain comprising of simple Flask view functions.

Note that we do not mention the Flask app itself here. We only indicate what's indended to be added to it when it is configured. This is the cob philosophy in a nutshell - you don't specify the glue code - only the main logic of your app. Cob tries very hard to perform the gluing operations for you.


Running your App
~~~~~~~~~~~~~~~~

When you're ready to test your app, just hit::

  $ cob testserver

And it will run your app for you to test.
