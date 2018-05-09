Background Tasks
================

Cob lets you define background tasks with relative ease. Background tasks use *Celery* by default,
and can be easily triggered from your code. Cob then takes care of setting up a worker and a broker
for you during deployment.

Defining Tasks
--------------

Tasks are defined in Python files which are declared as *task grains*. You can create such a file
yourself very easily - let's call it ``tasks.py`` and put it in your project's root directory. Start
it with the following metadata line:

.. code-block:: python

                # cob: type=tasks

Cob exposes a utility decorator, letting you easily define tasks:

.. code-block:: python

                # cob: type=tasks
                from cob import task

                @task
                def my_first_task():
                    print('task here')

Triggering Tasks
----------------

Triggering a task is easy. Once defined in ``tasks.py``, you can use them through a simple import:

.. code-block:: python

                ### index.py
                # cob: type=views
                from cob import route
                from .tasks import my_first_task

                @route('/')
                def index():
                    my_first_task.delay()

Requiring Application Context
-----------------------------

By default, tasks are not run with an active application context, meaning they cannot interact with
models or rely on the current Flask app. You can opt for having your tasks run with it by passing
``use_app_context=True``:

.. code-block:: python


                # cob: type=tasks
                from cob import task

                @task(use_app_context=True)
                def my_first_task():
                    print('task here')

Configuring Celery
------------------

Queue Names
~~~~~~~~~~~

You can control the queue names which are loaded into the worker by adding ``queue_names`` to your
grain config. For example:

.. code-block:: python

                # cob: type=tasks queue_names=queue1,queue2
                ...


Adding Worker Arguments
~~~~~~~~~~~~~~~~~~~~~~~

You can control arguments to the Celery workers by setting ``celery.worker_args`` in your project's
config::

  # .cob-project.yml
  ...
  celery:
     ...
     worker_args: -c 4
