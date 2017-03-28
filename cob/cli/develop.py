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
    env = ' '.join('{}={}'.format(key, os.environ[key])
                   for key in ('COB_DEVELOP', 'COB_NO_REENTRY')
                   if key in os.environ)
    windows = [
        {
            'window_name': 'flask',
            'layout': 'even-horizontal',
            'panes': [
                'cd {} && sleep 45 && source .cob/env/bin/activate && {} cob testserver'.format(project.root, env),
            ]
        },
        {
            'window_name': 'rabbitmq-server',
            'layout': 'even-horizontal',
            'panes': [
                'cd {} && {} rabbitmq-server'.format(project.root, env),
                ]
        },
        {
            'window_name': 'start celery_workers and beat',
            'layout': 'even-horizontal',
            'panes': [
                'cd {} && source .cob/env/bin/activate && sleep 10 && {} celery -A cob.celery_utils -I tasks worker --loglevel=DEBUG -E -B -Q celery'.format(project.root, env),
            ]
        },
        {
            'window_name': 'just working env',
            'layout': 'even-horizontal',
            'panes': [
                'cd {} && {} && source .cob/env/bin/activate'.format(project.root, env)
                ]
        },


    ]

    for subsystem in get_project().subsystems:
        subsystem.configure_tmux_window(windows)

    return {
        'session_name': 'cob-{}'.format(get_project().name),
        'windows': windows,
    }
