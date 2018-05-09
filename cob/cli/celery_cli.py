import os

import click


@click.group()
def celery():
    pass

@celery.command(name='start-worker')
@click.argument('additional_args', nargs=-1)
def start_worker(additional_args):
    from ..bootstrapping import ensure_project_bootstrapped
    from ..project import get_project
    from ..utils.network import wait_for_app_services

    from ..app import build_app

    ensure_project_bootstrapped()
    project = get_project()
    app = build_app()
    wait_for_app_services(app)
    celery_cmd = project.build_venv_command('celery')
    tasks_subsystem = project.subsystems.tasks
    assert tasks_subsystem.grains
    argv = [celery_cmd]
    argv.extend('-A cob.celery.app worker --loglevel=DEBUG -E -B -Q {}'.format(','.join(tasks_subsystem.get_queue_names())).split())
    argv.extend(tasks_subsystem.config.get('additional_args', '').split())
    argv.extend(additional_args)
    os.execv(celery_cmd, argv)
