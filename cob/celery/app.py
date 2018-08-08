from celery import Celery
from celery.loaders.base import BaseLoader

import logbook
from logbook.compat import LoggingHandler

class CobLoader(BaseLoader):

    def on_worker_init(self):
        from ..app import build_app

        # this will make the tasks grains to be properly loaded and discovered
        LoggingHandler(level=logbook.DEBUG).push_application()
        build_app()


celery_app = Celery('cob-celery', backend='rpc://', loader=CobLoader)
