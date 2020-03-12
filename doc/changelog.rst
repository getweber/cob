Changelog
=========

* :release:`0.23.1 <12-03-2020>`
* :bug:`139` Use POSTRES_HOST_AUTH_METHOD for postres configuration
* :release:`0.23.0 <09-02-2020>`
* :bug:`- major` Fix Werkzeug's ProxyFix import
* :feature:`122` Adding docker compose override files to ``cob docker deploy --compose-override``
* :release:`0.22.0 <04-09-2019>`
* :feautre:`121` Improve environment/config customization
* :feature:`116` Update PyAML version
* :feature:`-` Added automation documentaion for commands
* :release:`0.21.4 <10-02-2019>`
* :bug:`-` Pin tmuxp version to < 2.0
* :bug:`-` Pin click version to < 8
* :release:`0.21.3 <13-12-2018>`
* :bug:`-` Use yaspin instead of halo
* :release:`0.21.2 <06-12-2018>`
* :bug:`-` Properly handle pypi index url environment variables
* :release:`0.21.1 <31-10-2018>`
* :feature:`-` Added ``-H`` parameter to ``cob testserver``, specifying the address to bind
* :release:`0.20.0 <08-10-2018>`
* :feature:`105` Allow configuring node versions being used during docker image building
* :release:`0.19.8 <09-08-2018>`
* :bug:`-`: Avoid setting up database if project doesn't have models
* :bug:`104` Clean up containers on docker test end
* :release:`0.19.7 <02-08-2018>`
* :bug:`-` Added ``--no-cache`` option to ``cob docker test`` to support usage in CIs
* :release:`0.19.6 <01-08-2018>`
* :bug:`-` Avoid running ``rsync`` in ``cob docker test`` if an image is built during the process
* :release:`0.19.5 <01-08-2018>`
* :bug:`-` Fix pylint errors
* :release:`0.19.4 <01-08-2018>`
* :bug:`101` Run migrations on cob docker test
* :release:`0.19.3 <26-08-2018>`
* :bug:`-` Add IPython as a dependency
* :release:`0.19.2 <18-08-2018>`
* :bug:`-` Pin pylint dependency
* :release:`0.19.1 <18-07-2018>`
* :bug:`-` Added debug log output to ``cob testserver``
* :release:`0.19.0 <15-07-2018>`
* :feature:`97` Added ``cob shell`` command, allowing users to interactively access their modules and code through IPython or the builtin Python interpreter shell
* :feature:`94` Added ``cob docker tag-latest`` to tag the recent image as latest, and ``cob docker push`` to push the latest image
* :bug:`96 major` Pin Celery dependency to 4.1.x because of 4.2.x regression
* :feature:`92` Use journald logging driver when available during docker execution
* :feature:`88` Add option to specify more compose file to ``cob docker run-image``
* :feature:`89` Add ``--force`` to ``cob docker deploy`` to force overwriting unit files
* :feature:`90` Add ``docker.exposed_ports`` configuration for controlling exposed ports in deployment
* :release:`0.18.5 <09-07-2018>`
* :bug:`-` Fix error formatting when docker could not be located
* :bug:`90` Add ``docker.exposed_ports`` configuration
* :bug:`88` Support additional docker-compose files in ``docker run-image`` with ``-o``
* :release:`0.18.4 <05-07-2018>`
* :bug:`-` Add logging to syslog by default
* :bug:`89` Add --force to cob docker deploy
* :release:`0.18.3 <28-06-2018>`
* :bug:`87` Add "cob version" command
* :bug:`-` Fix escaping of image names
* :release:`0.18.2 <28-06-2018>`
* :bug:`-` Fix escaping of image names when using ``cob docker deploy``
* :bug:`-` Pin PyYaml to 3.x
* :bug:`85` Cob now supports symlinks for /etc/cob/conf.d/PROJNAME
* :bug:`84` Cob now mounts /etc/localtime inside containers to enforce correct time zone
* :release:`0.18.1 <27-06-2018>`
* :bug:`83` Add ``docker.image_name`` project configuration
* :bug:`-` Change default build image to Python3.6-jessie
* :bug:`85` * cob docker test now uses <project name>:dev image name by default
* :bug:`85` * Use port 80 in cob docker deploy
* :bug:`85` * Support \`cob docker deploy\` command (closes #51)
* :bug:`85` * Changelog
* :bug:`85` Cob now supports symlinks for /etc/cob/conf.d/PROJNAME
* :bug:`84` Cob now mounts /etc/localtime inside containers to enforce correct time zone
* :release:`0.18.0 <25-06-2018>`
* :feature:`51` Support `cob docker deploy` command to conveniently deploy dockerized cob projects on systemd
* :feature:`82` Added `cob docker run-image` to run a prebuilt cob image without requiring dependencies
* :feature:`77` Cob now required Python 3.6
* :feature:`50` ``cob docker test`` can now be used to run your tests inside a working
  docker-compose setup
* :feature:`76` Support ``celery.additional_args`` to control additional worker arguments through configuration
* :feature:`66` Support the ``--image-name`` parameter in ``cob docker run`` to override the image used
* :feature:`67` Support redis
* :release:`0.17.0 <05-03-2018>`
* :feature:`-` Allow passing celery configuration in project yaml
* :release:`0.16.0 <25-2-2018>`
* :feature:`21` Cob now uses multi-stage docker building to reduce image size and speed up the build process
* :release:`0.15.0 <19-2-2018>`
* :feature:`59` Front-end ember grains now run npm install
* :feature:`47` Cob now handles cases where docker requires sudo more elegantly
* :feature:`-` Many small fixes and improvements
* :release:`0.14.0 <19-10-2017>`
* :feature:`43` Add option to pass arbitrary arguments to celery start-worker
* :feature:`40` Added ability to make background tasks run in app context
* :feature:`44` Allow specifying cob version to use via `COB_VERSION` environment variable
* :feature:`42` Cob now supports specifying the pypi index URL to use via `COB_INDEX_URL`
* :release:`0.0.1 <16-11-2016>`
* :feature:`-` First operational release
