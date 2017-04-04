import os

import click
import logbook
import yaml

from ..bootstrapping import (ensure_project_bootstrapped,
                             get_virtualenv_binary_path)
from ..app import build_app
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
    _ = build_app() # make sure the tasks subsystem is initialized
    env = ' '.join('{}={}'.format(key, os.environ[key])
                   for key in ('COB_DEVELOP', 'COB_NO_REENTRY')
                   if key in os.environ)

    windows = [
        {
            'window_name': 'Webapp',
            'layout': 'even-horizontal',
            'panes': [
                'cd {} && source .cob/env/bin/activate && {} cob testserver'.format(project.root, env),
            ]
        },
        {
            'window_name': 'Celery',
            'layout': 'even-horizontal',
            'panes': [
                'cd {} && source .cob/env/bin/activate && {} celery -A cob.celery_utils worker --loglevel=DEBUG -E  -B -Q {}'.format(project.root, env, ','.join(_get_queue_names(project))),
            ]
        },
    ]

    for subsystem in get_project().subsystems:
        subsystem.configure_tmux_window(windows)

    return {
        'session_name': 'cob-{}'.format(get_project().name),
        'windows': windows,
    }

def _get_queue_names(project):
    return ['celery', *project.subsystems.tasks.queues]
