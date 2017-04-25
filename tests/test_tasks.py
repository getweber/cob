import time

from .project import Project

def test_tasks():
    timeout_seconds = 5
    with Project('tasks').server_context() as app:
        task_id = app.get('/start').json()['id']
        end_time = time.time() + timeout_seconds
        while time.time() < end_time:
            status = app.get('/status/{}'.format(task_id)).json()['completed']
            if status:
                break
        else:
            assert False, 'Timeout expired'
