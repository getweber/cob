import os

import click
import logbook
import yaml

from ..bootstrapping import (ensure_project_bootstrapped,
                             get_virtualenv_binary_path)
from ..project import get_project

_logger = logbook.Logger(__name__)


@click.command()
def develop():
    ensure_project_bootstrapped()
    tmuxp = get_virtualenv_binary_path('tmuxp')
    tmux_config_filename = os.path.abspath('.cob/_frontend.yml')
    with open(tmux_config_filename, 'w') as f:
        yaml.dump(_get_tmux_config(), f)
    os.execve(tmuxp, [tmuxp, 'load', tmux_config_filename], {**os.environ})


def _get_tmux_config():
    project = get_project()

    windows = [
        _window('Webapp', _project_cmd(project, 'cob testserver')),
    ]

    if project.subsystems.has_subsystem('tasks'):
        windows.extend([
            _window('Celery', _project_cmd(project, 'cob celery start-worker')),
        ])

    for subsystem in get_project().subsystems:
        subsystem.configure_tmux_window(windows)

    return {
        'session_name': 'cob-{}'.format(get_project().name),
        'windows': windows,
    }

def _window(window_name, commands, *, layout='even-horizontal'):
    if not isinstance(commands, (list, tuple)):
        commands = [commands]
    return {
        'window_name': window_name,
        'layout': layout,
        'panes': list(commands),
    }

def _project_cmd(proj, cmd):
    env = ' '.join('{}={}'.format(key, os.environ[key])
                   for key in ('COB_DEVELOP', 'COB_NO_REENTRY')
                   if key in os.environ)

    return 'cd {} && source .cob/env/bin/activate && {} {}'.format(proj.root, env, cmd)
