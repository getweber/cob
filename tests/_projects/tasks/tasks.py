# cob: type=tasks
from cob import task

from .models import Task, db

@task()
def task_complete(task_id):
    t = Task.query.get(task_id)
    t.completed = True
    db.session.add(t)
    db.session.commit()
