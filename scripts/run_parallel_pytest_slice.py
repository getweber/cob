import os
import sys
import yaml
from pathlib import Path


_ROOT = Path(__file__).parent.parent
_TEST_ROOT = _ROOT / 'tests'
_TRAVIS_YML = _ROOT / '.travis.yml'


def main():
    worker_id = int(os.environ['WORKER'])
    assert worker_id > 0

    tests = sorted([test for test in _TEST_ROOT.iterdir() if test.stem.startswith('test_') and test.suffix == '.py'],
                   key = lambda test: test.stem)
    assert tests

    with _TRAVIS_YML.open() as f:
        config = yaml.load(f.read())

    num_workers = len([x for x in config['jobs']['include'] if str(x['script']).strip().startswith('WORKER=')])
    assert num_workers > 0

    tests = [str(test) for index, test in enumerate(tests) if index % num_workers == worker_id - 1]
    print('Running tests:', tests)

    argv = [sys.executable, '-m', 'pytest', *tests, *sys.argv[1:]]
    os.execv(argv[0], argv)

if __name__ == '__main__':
    main()
