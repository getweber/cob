import os

import click

from ..bootstrapping import ensure_project_bootstrapped
from ..project import get_project


@click.group()
def celery():
    pass

@celery.command(name='start-worker')
def start_worker():
    ensure_project_bootstrapped(reenter=False)
    project = get_project()
    celery_cmd = project.build_venv_command('celery')
    tasks_subsystem = project.subsystems.tasks
    assert tasks_subsystem.grains
    argv = [celery_cmd]
    argv.extend('-A cob.celery_utils worker --loglevel=DEBUG -E -B -Q {}'.format(','.join(tasks_subsystem.get_queue_names())).split())
    os.execv(celery_cmd, argv)
