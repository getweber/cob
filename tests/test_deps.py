import os
import subprocess
import sys

import pytest


def test_adding_deps(tmpdir):
    assert 'COB_NO_REENTRY' not in os.environ
    with pytest.raises(ImportError):
        import pact

    projdir = tmpdir.join('proj')
    yaml = projdir.join('.cob-project.yml')
    python = str(projdir.join('.cob/env/bin/python'))


    with yaml.open('a', ensure=True) as f:
        print('name: testproj', file=f)
    _run_cob(projdir, 'bootstrap')

    assert os.path.exists(python)

    assert subprocess.call([python, '-c', 'import pact']) == 1

    with yaml.open('a') as f:
        print('deps:', file=f)
        print('  - pact', file=f)

    _run_cob(projdir, 'bootstrap')
    assert subprocess.call([python, '-c', 'import pact']) == 0


def _run_cob(cwd, cmd):

    subprocess.check_call(
        [sys.executable, '-m', 'cob.cli.main', '-vvvvv', str(cmd)],
        cwd=str(cwd),
        env={**os.environ, 'COB_DEVELOP': '1'},
    )
