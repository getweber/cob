import functools
import os
import subprocess
import sys

import click
import logbook
import yaml

from .defs import COB_CONFIG_FILE_NAME
from .utils.develop import is_develop, cob_root
from .project import get_project

_logger = logbook.Logger(__name__)

_PREVENT_REENTRY_ENV_VAR = 'COB_NO_REENTRY'
_COB_REFRESH_ENV = 'COB_REFRESH_ENV'
_VIRTUALENV_PATH = '.cob/env'
_INSTALLED_DEPS = '.cob/_installed_deps.yml'

def ensure_project_bootstrapped(*, reenter=True):
    if not os.path.isfile(COB_CONFIG_FILE_NAME):
        _logger.trace('Project is not a cob project')
        return
    if _PREVENT_REENTRY_ENV_VAR in os.environ:
        _logger.trace('{} found in environ. Not reentering.', _PREVENT_REENTRY_ENV_VAR)
        return
    _ensure_virtualenv()
    if reenter:
        _reenter()

def get_virtualenv_binary_path(name):
    return os.path.join(_VIRTUALENV_PATH, 'bin', name)

def _is_in_project_virtualenv():
    venv_parent_dir = os.path.dirname(os.path.abspath(_VIRTUALENV_PATH))
    python = os.path.abspath(os.path.join(venv_parent_dir, "env", "bin", "python"))
    return os.path.abspath(sys.executable) == python

def _ensure_virtualenv():
    if not _needs_refresh():
        _logger.trace('Virtualenv already seems bootstrapped. Skipping...')
        return
    venv_parent_dir = os.path.dirname(os.path.abspath(_VIRTUALENV_PATH))
    if not _is_in_project_virtualenv():
        _logger.trace('Creating virtualenv in {}', _VIRTUALENV_PATH)
        if not os.path.isdir(venv_parent_dir):
            os.makedirs(venv_parent_dir)
        _create_virtualenv(_VIRTUALENV_PATH)

    _in_env = functools.partial(os.path.join, _VIRTUALENV_PATH, 'bin')

    if not os.path.isfile(_in_env('pip')):
        subprocess.check_call([_in_env('python'), '-m', 'ensurepip'])
    if is_develop():
        _logger.trace('Using development version of cob')
        sdist_path = os.environ.get('COB_DEVELOP_SDIST')
        if sdist_path is None:
            _virtualenv_pip_install(['-e', cob_root()])
        else:
            _virtualenv_pip_install([sdist_path])
    else:
        _logger.trace('Installing cob form Pypi')
        _virtualenv_pip_install(['-U', 'cob'])

    deps = sorted(get_project().get_deps())
    _virtualenv_pip_install(['-U', *deps])
    with open(_INSTALLED_DEPS, 'w') as f:
        yaml.dump(deps, f)

def _create_virtualenv(path):
    if 'VIRTUAL_ENV' in os.environ:
        click.echo(click.style('You are attempting to use Cob from a virtual environment. Cob will try to locate your global Python installation to avoid '
                               'unintended consequences', fg='yellow'))
        interpreter = _locate_original_interpreter()
    else:
        interpreter = sys.executable

    subprocess.check_call([interpreter, '-m', 'virtualenv', path])

def _locate_original_interpreter():
    if not os.environ.get('COB_FORCE_CURRENT_INTERPRETER'):
        for path in ('/usr/local/bin', '/usr/bin'):
            for option in ('python{0.major}.{0.minor}', 'python{0.major}'):
                optional = os.path.join(path, option.format(sys.version_info))
                if os.path.isfile(optional):
                    return optional
    else:
        click.echo(click.style('Current interpreter is forced (COB_FORCE_CURRENT_INTERPRETER is set)', fg='yellow'))

    click.echo(click.style('Could not locate global Python interpreter. Using current interpreter as fallback', fg='yellow'))
    return sys.executable

def _needs_refresh():
    if _COB_REFRESH_ENV in os.environ:
        click.echo(click.style('Virtualenv refresh forced. This might take a while...', fg='magenta'))
        return True
    if not os.path.exists(os.path.join(_VIRTUALENV_PATH, 'bin', 'python')):
        click.echo(click.style('Creating project environment. This might take a while...', fg='magenta'))
        return True
    if _get_installed_deps() != get_project().get_deps():
        click.echo(click.style('Dependencies have changes - refreshing virtualenv. This might take a while...', fg='magenta'))
        return True
    return False

def _get_installed_deps():
    if not os.path.isfile(_INSTALLED_DEPS):
        return set()
    with open(_INSTALLED_DEPS) as f:
        return set(yaml.load(f.read()))

def _virtualenv_pip_install(argv):
    _logger.trace('Installing cob in virtualenv...')
    subprocess.check_call([os.path.join(_VIRTUALENV_PATH, 'bin', 'python'), '-m', 'pip', 'install', *argv])

def _reenter():
    if _is_in_project_virtualenv():
        return

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
