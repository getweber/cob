.. _deployment:

Deployment
==========

Deploying Cob applications is easy and straightforward. Cob uses Docker for deployment -- it helps you build a dockerized version of your app, which you can then push to a repository or deploy directly to the local machine.

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

Tagging Images
--------------

Once you're satisfied with a built image, you can tag it directly through docker as your "latest" version::

  $ docker tag myproject:dev myproject:latest


Deploying on Systemd-based Systems
----------------------------------

If your target machine is based on *systemd* (e.g. recent Ubuntu Server releases, CentOS 7.x etc.), you can deploy a dockerized cob project by running::

  $ cob docker deploy myproject:latest

This will pull off the needed information from the Docker image and create appropriate unit files to run your project.
