Using Hooks
===========

Cob offers specific hooks to control what happens during your application's lifecycle. Hooks are implmented through the `gossip <https://gossip.readthedocs.org>`_ library, and are usually defined in a special file located at your project's root, ``project.py``

Configuring your Flask App After Creation
-----------------------------------------

You can use the ``cob.after_configure_app`` hook to add additional features or configurations to your app:

.. code-block:: python

       # project.py

       import gossip


       @gossip.register('cob.after_configure_app')
       def after_configure_app(app):

           @app.before_request
           def before_request():
               ...
