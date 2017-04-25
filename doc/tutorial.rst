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

  $ curl http://127.0.0.1/api/tasks
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
     
     
     @route('/tasks')
     def get_all():
         return jsonify({
            'data': [
                _serialize(task)
                for task in Task.query.all()
            ]})
     
     @route('/tasks', methods=['POST'])
     def create_todo():
         data = request.get_json()['data']
         task = Task(
             description = data['attributes']['description']
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
         

We now have a working, simple TODO app, with a REST API to add and
view tasks.


Testing
-------

Now that our app is beginning to grow some logic, it's time to start
adding tests. Cob makes testing easy with the help of **pytest** and
several related tools.

Let's add our first test -- create a directory called ``tests`` under
your project root, and create your first test file -- let's name it
``test_todo.py``:

.. code-block:: python

    def test_add_todo(webapp):
        message = 'some message'
        webapp.post('/api/tasks', data_json={
            'data': {
                'attributes': {
                    'description': message,
                }
            }})
        all_todos = webapp.get('/api/todos')['data']
        last_todo = all_todos[-1]['attributes']
        assert last_todo['description'] == message

We wrote a single test function for use in **pytest**, with a single
fixture called webapp, which is an instance of
:class:`cob.utils.unittest.Webapp`, a helper Cob exposes for tests.

To run our tests, all we need to do is run ``cob test`` from our
project root.

.. tip:: ``cob test`` is just a shortcut for running **pytest** in
         your project. All options and arguments are forwarded to
         pytest for maximum flexibility.

Adding Third-Party Components
-----------------------------

Cob is aimed at being the backbone of your webapp. Most web
applications eventually need to bring in and use third party
components or libraries, and Cob makes that easy to do.

We are going to improve our Todo app by using a third-part tool for
serialization, `marshmallow
<http://marshmallow.readthedocs.io/en/latest/>`_. The first 
order of business is to get Cob to install this dependency whenever
our project is being bootstrapped. This can be done easily by
appending it to the ``deps`` section of ``.cob-project.yml``::

  # .cob-project.yml
  ...
  deps:
      - marshmallow

Now we can use this library to serialize our data, for instance create
a file named ``schemas.py`` with the following:

.. code-block:: python
       
  from marshmallow import Schema, fields, post_dump, post_load, pre_load
  from .models import Task
  
  
  class JSONAPISchema(Schema):
  
      @post_dump(pass_many=True)
      def wrap_with_envelope(self, data, many): # pylint: disable=unused-argument
          return {'data': data}
  
      @post_dump(pass_many=False)
      def wrap_objet(self, obj):
          return {'id': obj.pop('id'), 'attributes': obj, 'type': self.Meta.model.__name__.lower()}
  
      @post_load
      def make_object(self, data):
          return self.Meta.model(**data)
  
      @pre_load
      def preload_object(self, data):
          data = data.get('data', {})
          returned = dict(data.get('attributes', {}))
          returned['id'] = data.get('id')
          return returned
  
  
  class TaskSchema(JSONAPISchema):
      id = fields.Integer(dump_only=True)
      description = fields.Str(required=True)
      done = fields.Boolean()
  
      class Meta:
          model = Task
  
  tasks = TaskSchema(strict=True)

And use it in ``backend.py``:

.. code-block:: python

  from cob import route
  from flask import jsonify, request
  
  from .models import db, Task
  from .schemas import tasks as tasks_schema
  
  @route('/tasks')
  def get_all():
      return jsonify(tasks_schema.dump(Task.query.all(), many=True).data)
  
  @route('/tasks', methods=['POST'])
  def create_todo():
      json = request.get_json()
      if json is None:
          return "No JSON provided", 400
  
      result = tasks_schema.load(json)
      if result.errors:
          return jsonify(result.errors), 400
      db.session.add(result.data)
      db.session.commit()
      return jsonify(tasks_schema.dump(result.data).data)


Building a UI
-------------

Cob makes it easy to integrate front-end code in the same repository as
your backend, and helps you build, test and deploy it too. 

Setting Up
~~~~~~~~~~

In our example we will be using `Ember <https://www.emberjs.com/>`_ to
use our UI. We'll start by creating our front-end grain::

  $ cob generate grain --type frontend-ember webapp

.. note:: In order for the above to work, you need to have
          `Ember CLI <https://ember-cli.com/>`_ installed on your
          system

This will bootstrap your ``webapp`` subdirectory with our UI code, and
take care of initial setup.

While this looks like black magic, what happens here is quite simple -
Cob creates a directory called ``webapp``, and places a ``.cob.yml``
file inside it, letting Cob know that this is a grain of type
``frontend-ember``::

  # In webapp/.cob.yml
  type: frontend-ember

The ``.cob.yml`` file is just a different way to write the markup we
used in the first comment line of our previous grains. Once we marked
our webapp directory in this way, Cob knows how to treat it as one
containing Ember front-end code.

Writing our Front-end Logic
~~~~~~~~~~~~~~~~~~~~~~~~~~~

We won't dive in to how to develop using Ember, so we'll just create a
minimal front-end app for displaying and adding our TODOs.

.. note:: We won't cover Ember here in depth -- for more information
          you can refer to the excellent `Ember Guides
          <https://guides.emberjs.com/v2.12.0/>`_. For now, just take
          our word for it


.. code-block:: javascript

  // webapp/app/routes/tasks.js
  import Ember from 'ember';
  
  export default Ember.Route.extend({
  
      model() {
          return this.store.findAll('task');
      },
  
      setupController(controller, model) {
          this._super(...arguments);
          controller.set('tasks', model);
      },
  });


.. code-block:: javascript

  // webapp/app/controllers/tasks.js
  import Ember from 'ember';
  
  export default Ember.Controller.extend({
  
      new_task: '',
  
      actions: {
          add_task() {
              let task = this.store.createRecord('task', {
                  description: this.get('new_task'),
              });
              task.save();
          }
      }
  });


.. code-block:: javascript

  // webapp/app/models/task.js  
  import DS from 'ember-data';
  
  export default DS.Model.extend({
  
      description: DS.attr(),
      done: DS.attr('boolean'),
  });

.. code-block:: javascript

  // webapp/app/adapters/application.js
  import DS from 'ember-data';
  
  export default DS.JSONAPIAdapter.extend({
      namespace: '/api',
  });

And finally our template::

  <!-- webapp/app/templates/tasks.hbs -->
  {{#each tasks as |task| }}
    <div class="task">
      <h3>{{task.description}}</h3>
    </div>
  {{/each}}
  
  {{input value=new_task}}
  <button {{action "add_task"}}>Add</button>


Developing Front-end and Backend Simultaneously
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Now that we have multiple components to track during development (our
Flask app and our Front-end compilation) we can make use of yet
another handy tool Cob provides for us: ``cob develop``::

  $ cob develop

This command will fire up ``tmux`` (you'll have to have it installed
beforehand though), with two windows -- one for running the backend
server and the other running ``ember build --watch`` to compile your
front-end. Cool huh?


Deploying your Application
--------------------------

Cob uses **Docker** for deploying apps. It is the best way to
guarantee reproducible, composable setups and also allow reuse between
development and deployment.

Cob separates deployment to two stages: building your deployment image
and running it.

Building your Application Image
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

From your project directory, run::
  
  $ cob docker build

This will create a basic Docker image, labeled ``todos`` by default
(Cob uses the app name from the project's configuration to name to
label its images), and that image will be later on used for running
your app.

Running your Application in Deployment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To run your app via ``docker-compose``, running its various pieces
properly linked, run::

  $ cob docker run

This will start your app in the foreground.

.. seealso:: For more information on deploying your apps with Cob, see
             the :ref:`deployment` section of the docs
