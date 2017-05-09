import os
import pytest

from cob.project import Project
from cob.exceptions import MountpointConflict

from .project import PROJECTS_ROOT


def test_conflict(conflicting_project_path): # pylint: disable=redefined-outer-name
    with pytest.raises(MountpointConflict):
        Project(conflicting_project_path)


@pytest.fixture(params=os.listdir(os.path.join(PROJECTS_ROOT, 'conflicts')))
def conflicting_project_path(request):
    return os.path.join(PROJECTS_ROOT, 'conflicts', request.param)
