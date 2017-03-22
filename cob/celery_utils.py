from celery import Celery
from .defs import CELERY_BACKEND, CELERY_BROKER
from kombu import Queue
cobcelery = Celery('cobtasks')



cobcelery.conf.update(
    enable_utc=True,
    backend=CELERY_BACKEND,
    broker=CELERY_BROKER
    )

# task = cobcelery.task

def task(**kwargs):
    def task_wrap(func):
        if 'name' not in kwargs:  
            kwargs.update({'name':'tasks.add'})
        conf = dict()
        if 'queue' in kwargs:
            conf['task_queues'] = [Queue(name=kwargs.get('queue'))]
        cobcelery.conf.update(conf)
        # print(conf)
        # def update_conf(conf):
        #     cobcelery.conf.update(conf)
        return cobcelery.task(func, **kwargs)
    return task_wrap

