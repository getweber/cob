Developing Cob Apps
===================

``cob testserver``
------------------

This is the simplest mode of testing your Flask app, without any of its satellite services. It runs your configured app using the default Flask test server, including the automatic reloader.

``cob develop``
---------------

This mode is slightly more useful for real-world apps including front-end components. ``cob develop`` starts a tmux session (named ``cob-<your project name>`` by default), with a single window for the test server, and additional windows for other components of your app. For instance, projects using *frontend grains*, will set up panes running the build/watch process for your assets.
