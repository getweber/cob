Changelog
=========

* :feature:`76` Support ``celery.additional_args`` to control additional worker arguments through configuration
* :feature:`66` Support the ``--image-name`` parameter in ``cob docker run`` to override the image used
* :feature:`67` Support redis
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
