import os
from setuptools import setup, find_packages

with open(os.path.join(os.path.dirname(__file__), "cob", "__version__.py")) as version_file:
    exec(version_file.read()) # pylint: disable=W0122

_INSTALL_REQUIRES = [
    'click',
    'emport',
    'gossip',
    'Flask',
    'Flask-Migrate',
    'Flask-SQLAlchemy',
    'Flask-Loopback',
    'Jinja2',
    'gossip',
    'Logbook',
    'PyYAML',
    'tmuxp',
    'virtualenv',
]

setup(name="cob",
      classifiers = [
          "Programming Language :: Python :: 3.3",
          "Programming Language :: Python :: 3.4",
          "Programming Language :: Python :: 3.5",
          ],
      description="A scaffold for building and deploying powerful and robust webapps",
      license="BSD3",
      author="Rotem Yaari",
      author_email="vmalloc@gmail.com",
      version=__version__, # pylint: disable=E0602
      packages=find_packages(exclude=["tests"]),

      url="https://github.com/getcob/cob-cli",
      entry_points={
          "console_scripts": [
              "cob = cob.cli.main:main",
          ]},
      install_requires=_INSTALL_REQUIRES,
      scripts=[],
      namespace_packages=[],
      package_data={'cob': ['cob/Dockerfile.j2']},
      include_package_data=True,
      zip_safe=False,
      )
