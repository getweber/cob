Working with Static Files
=========================

Managing static assets can be a pain, especially during deployment and testing. Cob can be instructed to look for static files in several places, including custom locations

Static Grains
-------------

Static grains are just like regular grains, but are used to store static files.

To create static grains::

  $ cob generate grain staticfiles --type static
  $ cat staticfiles/.cob.yml
  type: static
  root: ./root
  mountpoint: /static

This instructs cob to look for static files under the ``root`` subdirectory of the ``staticfiles`` directory, when accessed via the ``/static/`` URL prefix.

.. note:: We can instruct the root directory to become ``.``, instead of ``./root``, but this would expose ``.cob.yml`` itself to be fetched as a static file
