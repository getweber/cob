Working with Front-end Code
===========================

Creating Front-end Grains
~~~~~~~~~~~~~~~~~~~~~~~~~

Ember
-----
Cob supports front-ends written in Ember (through ember-cli). It even lets you easily generate a new project::

  $ cob generate grain --type frontend-ember ./webapp

This will create the new grain and even, if ember-cli is detected in your environment, run ``ember init`` for you.


Developing
~~~~~~~~~~

Developing back-end and front-end code in tandem requires some additional ergonomics. Cob supports the ``tmux`` command for running a complete development environment inside tmux.

After creating your grains, run ``cob tmux start`` to start your tmux development session.
