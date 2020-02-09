import subprocess
import pytest

from .project import Project


def test_models():
    project = Project('unittests')
    project.test()
