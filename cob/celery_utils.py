from celery import Celery

class CobCelery(object):

    def __init__(self, celery_inst):
        self.cobcelery = celery_inst


    def celery_load_config(self):
        '''
        by default ,a celeryconfig.py file should exist in the
        main cob project dir with some basic configuration:
           - broker url
           - results backend
        this file will be loaded and used as celery config.
        '''
        self.cobcelery.config_from_object('celeryconfig')

    def update_celery_task_name(self, func, kwargs):
        '''
        this will make sure the celery config contains
        a task name so that tasks are registered exactly
        by the name we expect.
        '''
        if not kwargs.get('name'):
            return {'name': '_cob.tasks.%s' % func.__name__}
        else:
            return {}


    def add_queue_consumer(self, kwargs):
        '''
        in cases where the user provided a queue name
        in the task args, we need to assign a worker
        that will consume from this queue.
        '''
        if kwargs.get('queue'):
            self.cobcelery.control.add_consumer(kwargs.get('queue'))


    def periodic_task_parse_scheduling_args(self, func, kwargs):
        '''
        for now we support these args:
        'every': user may add every=100s and the task will be sent every 100s.
        'schedule': user provides a dict

                  'task title': {
                      'schedule': <num of seconds> or crontab(...),
                      'args': (tuple of args),
                  }

             -> this function will just add a 'task': <task name>
                to the dict and update celery.conf.beat_schedule with
                the new task and its schedule
        '''
        # parse 'every' arg
        if kwargs.get('every'):
            self.cobcelery.conf.beat_schedule.update({
                'run-every-{}-seconds'.format(kwargs.get('every')): {
                    'task': kwargs.get('name'),
                    'schedule':kwargs.get('every'),
                    'args':kwargs.get('args'),
                }
            })
            kwargs.pop('every', None)
            kwargs.pop('args', None)

        # parse 'schedule' arg
        if kwargs.get('schedule'):
            for k in kwargs['schedule'].keys():
                kwargs['schedule'][k]['task'] = kwargs.get('name')
                self.cobcelery.conf.beat_schedule.update(kwargs.get('schedule'))
            kwargs.pop('schedule', None)

        return kwargs


celery_inst = Celery('cobtasks')
celery_app = CobCelery(celery_inst)
celery_app.celery_load_config()

def task(*args, **kwargs):
    def task_wrap(func):
        kwargs.update(celery_app.update_celery_task_name(func, kwargs))
        celery_app.add_queue_consumer(kwargs)
        return celery_app.cobcelery.task(func, **kwargs)
    return task_wrap


def periodic_task(*args, **kwargs):
    def periodic_task_wrap(func):
        kwargs.update(celery_app.update_celery_task_name(func, kwargs))
        kwargs.update(celery_app.periodic_task_parse_scheduling_args(func, kwargs))
        celery_app.add_queue_consumer(kwargs)
        return celery_app.cobcelery.task(func, **kwargs)
    return periodic_task_wrap
