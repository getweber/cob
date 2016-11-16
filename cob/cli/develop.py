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

    windows = [
        {
            'window_name': 'flask',
            'layout': 'even-horizontal',
            'panes': [
                'source .cob/env/bin/activate && cob testserver',
            ]
        },
    ]

    for subsystem in get_project().subsystems:
        subsystem.configure_tmux_window(windows)

    return {
        'session_name': 'cob-{}'.format(get_project().name),
        'windows': windows,
    }
