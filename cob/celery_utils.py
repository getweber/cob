from uuid import uuid4
from .app import build_app

from celery import Celery
from celery.loaders.base import BaseLoader


# Cob's loader. Used to correctly locate tasks

class CobLoader(BaseLoader):

    def on_worker_init(self):
        # this will make the tasks grains to be properly loaded and discovered
        build_app()


celery_app = Celery('cob-celery', backend='rpc://', loader=CobLoader)


def task(*, every=None, schedule=None, schedule_name=None, **kwargs):
    if every is None and schedule is None:
        return celery_app.task(**kwargs)

    if every is not None and schedule is not None:
        raise RuntimeError("'every' can't be provided along with 'schedule'")

    if schedule_name is None:
        schedule_name = str(uuid4())

    def decorator(func):
        returned = celery_app.task(**kwargs)(func)
        celery_app.conf.beat_schedule[schedule_name] = { # pylint: disable=no-member
            'task': returned.name,
            'schedule': every if every is not None else schedule,
        }
        return returned

    return decorator
