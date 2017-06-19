from uuid import uuid4


def task(*, every=None, schedule=None, schedule_name=None, **kwargs):
    from .app import celery_app

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
