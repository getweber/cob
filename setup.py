import os
from setuptools import setup, find_packages

with open(os.path.join(os.path.dirname(__file__), "weber", "__version__.py")) as version_file:
    exec(version_file.read()) # pylint: disable=W0122

_INSTALL_REQUIRES = [
    'click',
    'Logbook',
    'virtualenv',
]

setup(name="weber",
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

      url="https://github.com/getweber/weber-cli",
      entry_points={
          "console_scripts": [
              "weber = weber.cli.main:main",
          ]},
      install_requires=_INSTALL_REQUIRES,
      scripts=[],
      namespace_packages=[]
      )
