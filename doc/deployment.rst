.. _deployment:

Deployment
==========

cob relies on Docker to perform deployments.

Building a Docker Image
-----------------------

First, you'll need to generate the Docker image for your project. You do this by running::

  $ cob docker build

This image will later be used to run the various needed containers.

Running your App in Deployment
------------------------------

The easiest way to run the deployment image locally is to run::

  $ cob docker run

The above assumes you already built the deployment image with ``cob
docker build``, and will use it in a ``docker-compose`` configuration.

While this is useful to run in the foreground from within the project
directory, you may want to generate a docker-compose file for later
use in other deployment scripts (such as ``systemd`` services). For
this purpose you can generate the ``docker-compose.yml`` file with::

  $ cob docker compose > /path/to/docker-compose.yml
