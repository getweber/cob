Developing Cob Apps
===================

Using Cob inside Virtual Environments
-------------------------------------

Cob works by creating a virtual environment for its applications. This is necessary in order to ensure dependency installation and isolation from external environments. It determines the Python interpter to use for installing the virtual environment based on a set of rules, like trying to see where which Python interpreter is currently running it.

In case your current interpreter is already inside a virtual environment (a.k.a. ``virtualenv``), Cob will attempt to fall back to the global Python interpreter. This is because there are usually multiple issues with trying to create a virtualenv from within another virtualenv. You can override this default behavior by setting the ``COB_FORCE_CURRENT_INTERPRETER`` environment variable to a non-empty value.

``cob develop``
---------------

This mode is slightly more useful for real-world apps including front-end components. ``cob develop`` starts a tmux session (named ``cob-<your project name>`` by default), with a single window for the test server, and additional windows for other components of your app. For instance, projects using *frontend grains*, will set up panes running the build/watch process for your assets.

.. note:: If you wish to test your flask app alone (without the surrounding components started in ``cob develop``, you can run ``cob testserver``. This will only run the backend Flask part of your webapp
