from .app import build_app

from celery import Celery
from celery.loaders.base import BaseLoader


# Cob's loader. Used to correctly locate tasks

class CobLoader(BaseLoader):

    def on_worker_init(self):
        # this will make the tasks grains to be properly loaded and discovered
        build_app()


def periodic_task(*args, **kwargs):
    raise NotImplementedError()  # pragma: no cover

celery_app = Celery('cob-celery', loader=CobLoader)


task = celery_app.task
