from celery import Celery
from kombu import Queue
from cob.project import get_project
import logbook
cobcelery = Celery('cobtasks')

# crontab celery schedule syntax:
# http://docs.celeryproject.org/en/latest/userguide/periodic-tasks.html#crontab-schedules

################################3
# TURN IT TO CLASS
################################

_logger = logbook.Logger(__name__)

cobcelery.config_from_object('celeryconfig')

def task(*args, **kwargs):
    def task_wrap(func):
        kwargs.update(non_periodic_task_update_conf(func, kwargs))
        parse_general_task_args(kwargs)
        return cobcelery.task(func, **kwargs)
    return task_wrap


def periodic_task(*args, **kwargs):
    def periodic_task_wrap(func):
        kwargs.update(parse_simple_periodic_args(func, kwargs))
        parse_general_task_args(kwargs)
        return cobcelery.task(func, **kwargs)
    return periodic_task_wrap


def non_periodic_task_update_conf(func, *args, **kwargs):
    if 'name' not in kwargs:
        return {'name':'_cob.tasks.%s' % func.__name__}
    else:
        return {}

def parse_simple_periodic_args(func, kwargs):
    '''
    for simple cases where the user
    provided "every" and "args" for the periodic task
    we'll parse manually and create the beat_schedule dict update
    in all other cases, the user will have to provide a full
    beat schedule dict that will be updated in cobcelery.conf
    '''
    global cobcelery
    kwargs.update(non_periodic_task_update_conf(func, kwargs))
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

def parse_general_task_args(kwargs):
    '''
    applicable for non periodic and periodic tasks
    for args like queue=.. we would like to gather inforamtion
    and keep it in mind for different reasons like:
    1. when running cob develop ,running celery worker command states which queues
       to monitor and if we know which queues are targeted in all tasks, we know automatically
       which on to monitor.

    '''
    global cobcelery
    if 'queue' in kwargs:
        get_project().config.setdefault('celery_queues',[]).append(kwargs.get('queue'))
        _logger.info("Adding celery consumer")
        cobcelery.control.add_consumer(kwargs.get('queue'))
        # consumers_data = cobcelery.control.inspect().ping()
        # for c in consumers_data:
            # cobcelery.control.add_consumer(c)
        # import pudb;pudb.set_trace()
