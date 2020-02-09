.. _deployment:

Deployment
==========

Deploying Cob applications is easy and straightforward. Cob uses Docker for deployment -- it helps you build a dockerized version of your app, which you can then push to a repository or deploy directly to the local machine.


Deployment Requirements
-----------------------

.. _deployment_deps:

Cob has several requirements in order to be successfully deployed on your system/machine.

Python Version
~~~~~~~~~~~~~~

Cob requires Python 3.6 or newer in order to install and run correctly. If you are deploying on Ubuntu 18.04 or newer, this should already be the case for your system.

For Ubuntu 16.04 or older, it is recommended to use the *deadsnakes* PPA for installing 3.6::

  $ sudo apt-get install -y software-properties-common
  $ sudo add-apt-repository ppa:deadsnakes/ppa
  $ sudo apt-get update
  $ sudo apt-get install -y python3.6

Docker and Docker-Compose
~~~~~~~~~~~~~~~~~~~~~~~~~

Deploying a cob app requires *docker* to be installed. In addition, ``docker-compose`` is needed.

.. note:: In some cases docker-compose is bundled with ``docker`` on your platform. However, due to a compatibility issue of the docker-compose format, Cob requires version 1.13 and above, which might not be the case for your installation.

          In any case, it is recommended to follow the `official guide <https://docs.docker.com/compose/install/>`_ for setting up ``docker-compose``.


Building a Docker Image
-----------------------

First, you'll need to build the Docker image for your project. This is done by running::

  $ cob docker build

This command builds a docker image labeled ``<your project name>>:dev`` by default. This means that if your project is named "todos",
the image would be named ``todos:dev``.


Testing Dockerized Apps
-----------------------

To make sure no new issues get introduced as a result of packaging your app through Docker, you can run your tests
inside the docker containers comprising your app, meaning it will run very similarly to how it would run in production.

This is done by running ``cob docker test``.

Tagging and Pushing Images
--------------------------

In most cases you would probably like to tag your released images and upload them to a Docker registry. This can be done by setting the *image name* for your project before building images.

Under ``.cob-project.yml``, add the ``docker.image_name`` configuration::

  # .cob-project.yml
  ...
  docker:
      image_name: "your.server.com:4567/myproject"

Now when you build or test your project, the docker image created will be ``your.server.com:4567/myproject:dev``

Once you're satisfied with a built image, you can tag it directly through docker as your "latest" version::

  $ cob docker tag-latest

Then you can push your image to the repository with a standard ``docker push`` command::

  $ cob docker push

.. note:: both ``cob docker tag-latest`` and ``cob docker push`` take the image name from the project's configuration, and are intended as shortcuts for ``docker tag`` and ``docker push``.


Deploying on Systemd-based Systems
----------------------------------

If your target machine is based on *systemd* (e.g. recent Ubuntu Server releases, CentOS 7.x etc.), you can deploy a dockerized cob project by running::

  $ cob docker deploy your.server.com:4567/myproject:latest

This will pull off the needed information from the Docker image and create appropriate unit files to run your project.



.. note:: cob uses docker-compose for deployment. a docker-compose-override yml file can be provided which is then used as described in `docker-compose overview <https://docs.docker.com/compose/reference/overview/>`_.

To use the above capability, add ``--compose-override <full path to override file>`` to the above ``cob docker deploy`` command.
You can use more than one compose-override files by repeating the flag for each file.
