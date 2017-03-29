The Cob Tutorial
================

In this section we will explore building a complete webapp with Cob. We will cover the most frequent tasks often tackled when starting an app from scratch, and will also cover how to deploy your app once it's ready for prime time.

Our examples will focus around building a TODO app, which will have all the parts a modern full-stack app has: a modern front-end UI, a backend for API calls, static files and assets, database integration and background tasks.


Getting Started
---------------

Installing Cob
~~~~~~~~~~~~~~

To get started with cob, you will need to have cob installed on your system. Cob is basically a Python package, and as such - is most easily installed via ``pip``::

  $ pip install cob

The remainder of this tutorial will make extensive use of the ``cob`` command, which is the entry point for the various operations we will be using.

Creating your Project
~~~~~~~~~~~~~~~~~~~~~

Any Cob project lives in its own directory with a conventional
structure. Although an empty project is very simple and minimalistic,
Cob helps us create it through the ``cob generate`` command. ``cob
generate`` always receives the type of thing we want to generate (in
this case a *project*), and the name of what we're creating::

  $ cob generate project todos

The above command will create a new project directory called **todos**
which we are going to use for our project. A minimalistic cob project
is just a directory with a special YAML file, called
``.cob-project.yml``.  

We will be returning to this file very soon enough, so don't worry. 

.. tip:: Now would be a good time to start tracking your project with *git*::

          $ cd todos
          $ git init
          $ git add .
          $ git commit -m 'Initial version'

First Steps
-----------

Creating a Simple Backend
~~~~~~~~~~~~~~~~~~~~~~~~~

Our application will need a backend serving our JSON API for fetching
and updating TODO items. Cob is built around the Flask web framework
and leverages its composability, while removing the need for
boilerplate code. 

Let's start by adding our route for serving TODO items. Let's create a
file named ``backend.py``, and add the following content to it: 

.. in ./backend.py
.. code-block:: python
       
   # cob: type=views mountpoint=/api
                
   from cob import route
   from flask import jsonify

   @route('/todos')
   def get_all():
       return jsonify({'data': []})

Let's break down the example to see what's going on. The first line is
a special one, used by cob to let it know how this file should be
dealt with. It tells Cob that the type of this file is "views"
(meaning a collection of Flask view functions), and that it should be
"mounted" under ``/api`` in the resulting webapp.  

Next, we import ``route`` from Cob. This is a shortcut to the
``app.route`` or ``blueprint.route`` in Flask, but is managed by Cob,
and allows it to "discover" the routes that each file provides. 

Running the Test Server
~~~~~~~~~~~~~~~~~~~~~~~

Before we move on, let's give our little app a try. Go into your
project directory and run ``cob testserver``. If this is the first
time you're doing this in your project, Cob will initialize the
private project environment for you first. For more information about
how this works you can read about it :ref:`here <environments>`.

After the setup is done, your server will run on the default port::

  $ curl http://127.0.0.1/api/todos
  { 
      "data": []
  }

.. note:: ``cob testserver`` only runs the Flask backend serving your
          routes. Later on we will see how to set up a more complete
          testing environment 

Interlude -- What Have We Just Created?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Files of the like of ``backend.py`` above are very critical in Cob's
functionality. Cob takes away the boilerplate in your project -- but
in order to do so it needs to know the parts that constitute your
project. Each such part is loaded separately, and its dependencies are
automatically taken care of by cob. 

These "pieces" of your project are called **grains** in cob. Each
grain has a *type* (for instance we have just created a 
:ref:`views grain <views_grain>`), telling Cob how to handle it. As we
move forward we will meet more types of grains that we can use in Cob.

Working with Data
-----------------

Most web applications work on data, usually in the form of records in
a database. This is one of the most "boilerplate"-ish tasks in backend
development, so naturally Cob aims at simplifying it as much as
possible. 

Cob takes care of loading models from your project, and also takes
care of connecting to your database and migrations. Let's take a coser
look at how it's done as we improve our app to actually keep track of
todo tasks. 

Adding Models
~~~~~~~~~~~~~

Our first step will be to add a model for our Todos. We'll use ``cob
generate`` again to generate our models file::

  $ cob generate models

This will create a file named ``models.py`` in our project
directory. The file already imports the db component of cob, onto
which we can define models::

  $ cat models.py
  # cob: type=models
  from cob import db

Models grains use Flask-SQLAlchemy for defining models. Let's create
our task model:

.. code-block:: python

   ...
   class Task(db.Model):

       id = db.Column(db.Integer, primary_key=True)
       description = db.Column(db.Text, nullable=False)
       done = db.Column(db.Boolean, default=False)

Initializing Migrations
~~~~~~~~~~~~~~~~~~~~~~~

We would like Cob to manage migrations for us, which will be useful
when the time comes to modify and evolve our app, even after it's
already deployed. Cob allows us to easily create a migration for our
data. First we will initialize the migrations data (only needs to
happen once)::
  
  $ cob migrate init

Then we will create our automatic migration script::

  $ cob migrate revision -m "initial revision"
  $ cob migrate up

.. note:: ``cob migrate`` uses `Alembic
          <http://alembic.zzzcomputing.com/en/latest/>`_ for migration
          management. you can refer to Alembic's documentation for
          more information on how to customize your migration scripts

.. note:: Cob is configured, by default, to use an sqlite file under
          ``.cob/db.sqlite``. See :ref:`the database section <db>` to
          learn more on how it can be configured

Using Models in our Backend API
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Using models is very simple now that we have defined our model. Let's
go back to our ``backend.py`` file and modify it to load and store our
tasks from the database:

.. code-block:: python

     # cob: type=views mountpoint=/api
     
     from cob import route
     from flask import jsonify, request
     
     from .models import db, Task
     
     
     @route('/todos')
     def get_all():
         return jsonify({
            'data': [
                _serialize(task)
                for task in Task.query.all()
            ]})
     
     @route('/todos', methods=['POST'])
     def create_todo():
         data = request.get_json()['data']
         task = Task(
             description = data['description']
         )
         db.session.add(task)
         db.session.commit()
         return jsonify(_serialize(task))
     
     
     def _serialize(task):
         return {
             'type': 'task',
             'id': task.id,
             'attributes': {
                 'description': task.description,
             }
         }
         
