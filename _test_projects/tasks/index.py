# cob: type=views mountpoint=/
from cob import route
from .tasks import task_complete
from .models import db, Task

from flask import jsonify

@route('start')
def start():
    task = Task()
    db.session.add(task)
    db.session.commit()
    task_complete.delay((task.id,))
    return jsonify({'id': task.id})

@route('status/<int:task_id>')
def status(task_id):
    return jsonify({'completed': Task.query.get_or_404(task_id).completed})
