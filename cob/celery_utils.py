from celery import Celery
from kombu import Queue
cobcelery = Celery('cobtasks')

# crontab celery schedule syntax:
# http://docs.celeryproject.org/en/latest/userguide/periodic-tasks.html#crontab-schedules


cobcelery.config_from_object('celeryconfig')

def task(*args, **kwargs):
    def task_wrap(func):
        kwargs.update(general_task_update_conf(func, kwargs))
        return cobcelery.task(func, **kwargs)
    return task_wrap


def periodic_task(*args, **kwargs):
    def periodic_task_wrap(func):
        kwargs.update(parse_simple_periodic_args(func, kwargs))
        return cobcelery.task(func, **kwargs)
    return periodic_task_wrap


def general_task_update_conf(func, *args, **kwargs):
    if 'name' not in kwargs:
        return {'name':'_cob.tasks.%s' % func.__name__}
    else:
        return {}

def parse_simple_periodic_args(func, kwargs):
    '''
    for simple cases where the user
    proveded "every" and "args" for the periodic task
    we'll parse manually and create the beat_schedule dict update
    in all other cases, the user will have to provide a full
    beat schedule dict that will be updated in cobcelery.conf
    '''
    global cobcelery
    kwargs.update(general_task_update_conf(func, kwargs))
    if 'every' in kwargs:
            cobcelery.conf.beat_schedule.update({
                'run-every-{}-seconds'.format(kwargs.get('every')): {
                    'task':kwargs.get('name'),
                    'schedule':kwargs.get('every'),
                    'args':kwargs.get('args')
                }
            })
            kwargs.pop('every', None)
            kwargs.pop('args', None)
    elif 'schedule' in kwargs:
        for k in kwargs['schedule'].keys():
            kwargs['schedule'][k]['task'] = kwargs.get('name')
        cobcelery.conf.beat_schedule.update(kwargs.get('schedule'))
        kwargs.pop('schedule', None)

    return kwargs
