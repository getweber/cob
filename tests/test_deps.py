import os
import subprocess
import sys

import pytest


def test_adding_deps(tmpdir):
    with pytest.raises(ImportError):
        import sentinels

    projdir = tmpdir.join('proj')
    yaml = projdir.join('.cob-project.yml')
    python = str(projdir.join('.cob/env/bin/python'))


    with yaml.open('a', ensure=True) as f:
        print('name: testproj', file=f)
    _cob_on(projdir, 'bootstrap')

    assert os.path.exists(python)

    assert subprocess.call([python, '-c', 'import sentinels']) == 1

    with yaml.open('a') as f:
        print('deps:', file=f)
        print('  - sentinels', file=f)

    _cob_on(projdir, 'bootstrap')
    assert subprocess.call([python, '-c', 'import sentinels']) == 0


def _cob_on(cwd, cmd):
    x = os.environ.pop('COB_NO_REENTRY')
    try:
        subprocess.check_call([sys.executable, '-m', 'cob.cli.main', '-vvvvv', str(cmd)], cwd=str(cwd))
    finally:
        os.environ['COB_NO_REENTRY'] = x
