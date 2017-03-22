Basic Grains
============

.. _views_grain:

Views Grains
------------

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

.. note::

   You do not have to name your blueprint variable ``blueprint``. Cob will look for your Blueprint instance among the module's globals

Template Grains
---------------

*Template* grains are used to host Flask (Jinja2) templates::

  $ cob generate grain templates --type templates
  ...

You can now create a basic template under ``templates/index.html``. Rendering it is fairly simple::

  $ cat index.py

.. code-block:: python

       # cob: type=views mountpoint=/
       from cob import route
       from flask import render_template

       @route('/')
       def index():
	   return render_template('index.html')

Tasks Grains
-------------

*Tasks* grains are used to run Asyc tasks::

  $ cob generate grain tasks --type tasks
  ...
  $ cat tasks.py

  .. code-block:: python
          # cob: type=tasks mountpoint={{mountpoint}}
          from cob import task, periodic_task
          from celery.schedules import crontab

          ## Your tasks go here

          # use the next syntax for tasks you'll send "manually" through REST API
          @task()
          def task_func1(x,y,z ...):
                  ...

          # use this syntax to set a task binded to an non-default queue ("celery").
          # queue arg can also be used with the periodic_task decorators.
          @task(queue=<queue name>)
          def task_func2(...):
                  ...

          # use this syntax to create a task that will be dispached every predefined period.
          @periodic_task(every=<num of seconds>)
          def periodic_task_func3(...):
                  ...

          schedule_dict = {
              '<choose a name>': {
                       'schedule': crontab(...) or <number of seconds>,
                       'args': <tuple of arguments according to the args your task_func needs>
              }
           }

           # use this syntax to create a more "complex" schedule for the task
           @periodic_task(schedule=schedule_dict)
           def periodic_task_func4(...):
                  ...        
  
Bundle Grains
-------------

In some cases, as we'll see later, you may want to bundle several grains into a single directory. However, Cob only searches for grains in the project root by default.

Luckily you can create a directory and declare it as a bundle to tell Cob it should traverse the top level of that directory as well::

  $ cob generate grain my_addon --type bundle
  $ cat my_addon/.cob.yml
  type: bundle
  $ cob generate grain my_addon/index.py --type views
  ...
