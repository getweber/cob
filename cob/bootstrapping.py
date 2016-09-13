import os
import subprocess
import sys

import logbook
import venv

from .defs import COB_CONFIG_FILE_NAME

_logger = logbook.Logger(__name__)

_PREVENT_REENTRY_ENV_VAR = 'COB_NO_REENTRY'
_COB_DEVELOP_MODE = 'COB_DEVELOP'
_COB_REFRESH_ENV = 'COB_REFRESH_ENV'
_VIRTUALENV_PATH = '.cob/env'

def ensure_project_bootstrapped():
    if not os.path.isfile(COB_CONFIG_FILE_NAME):
        _logger.trace('Project is not a cob project')
        return
    if _PREVENT_REENTRY_ENV_VAR in os.environ:
        _logger.trace('{} found in environ. Not reentering.', _PREVENT_REENTRY_ENV_VAR)
        return
    _ensure_virtualenv()
    _reenter()

def _ensure_virtualenv():
    if os.path.exists(os.path.join(_VIRTUALENV_PATH, 'bin', 'python')) and _COB_REFRESH_ENV not in os.environ:
        _logger.trace('Virtualenv already seems bootstrapped. Skipping...')
        return
    _logger.trace('Creating virtualenv in {}', _VIRTUALENV_PATH)
    venv_parent_dir = os.path.dirname(os.path.abspath(_VIRTUALENV_PATH))
    if not os.path.isdir(venv_parent_dir):
        os.makedirs(venv_parent_dir)
    venv.create(_VIRTUALENV_PATH)
    subprocess.check_call([os.path.join(_VIRTUALENV_PATH, 'bin', 'python'), '-m', 'ensurepip'])
    if _COB_DEVELOP_MODE in os.environ:
        _logger.trace('Using development version of cob')
        _virtualenv_pip_install(['-e', os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))])
    else:
        _logger.trace('Installing cob form Pypi')
        _virtualenv_pip_install(['-U', 'cob'])

def _virtualenv_pip_install(argv):
    _logger.trace('Installing cob in virtualenv...')
    subprocess.check_call([os.path.join(_VIRTUALENV_PATH, 'bin', 'python'), '-m', 'pip', 'install', *argv])

def _reenter():
    argv = sys.argv[:]
    argv[:1] = [os.path.abspath(os.path.join(_VIRTUALENV_PATH, 'bin', 'python')), '-m', 'cob.cli.main']
    _logger.trace('Running in {}: {}...', _VIRTUALENV_PATH, argv)
    os.execve(argv[0], argv, {_PREVENT_REENTRY_ENV_VAR: 'true', **os.environ})

def _which(bin):
    for directory in os.environ['PATH'].split(':'):
        full_path = os.path.join(directory, bin)
        if os.path.isfile(full_path):
            return full_path

    raise ValueError('Could not find a python interpreter named {}'.format(bin))
