from uuid import uuid4

import functools


def task(_func=None, *, every=None, schedule=None, schedule_name=None, use_app_context=False, **kwargs):
    from .app import celery_app

    if _func is None:
        return functools.partial(task, every=every, schedule=schedule, schedule_name=schedule_name, use_app_context=use_app_context, **kwargs)


    if use_app_context:
        _func = _wrap_with_app_context(_func)

    returned = celery_app.task(**kwargs)(_func)


    if every is not None or schedule is not None:
        if every is not None and schedule is not None:
            raise RuntimeError("'every' can't be provided along with 'schedule'")

        if schedule_name is None:
            schedule_name = str(uuid4())

        celery_app.conf.beat_schedule[schedule_name] = { # pylint: disable=no-member
            'task': returned.name,
            'schedule': every if every is not None else schedule,
        }

    return returned


def _wrap_with_app_context(func):

    @functools.wraps(func)
    def new_func(*args, **kwargs):
        from cob.app import build_app

        app = build_app(use_cached=True)
        with app.app_context():
            return func(*args, **kwargs)
    return new_func
