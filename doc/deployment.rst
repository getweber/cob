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

  $ docker tag your.server.com:4567/myproject:dev your.server.com:4567/myproject:latest

Then you can push your image to the repository with a standard ``docker push`` command::

  $ docker push your.server.com:4567/myproject:latest


Deploying on Systemd-based Systems
-------------------------------

If your target machine is based on *systemd* (e.g. recent Ubuntu Server releases, CentOS 7.x etc.), you can deploy a dockerized cob project by running::

  $ cob docker deploy your.server.com:4567/myproject:latest

This will pull off the needed information from the Docker image and create appropriate unit files to run your project.
