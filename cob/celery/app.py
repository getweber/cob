from celery import Celery
from celery.loaders.base import BaseLoader


class CobLoader(BaseLoader):

    def on_worker_init(self):
        from ..app import build_app

        # this will make the tasks grains to be properly loaded and discovered
        build_app()


celery_app = Celery('cob-celery', backend='rpc://', loader=CobLoader)
