import os

import logbook

from .base import SubsystemBase
_logger = logbook.Logger(__name__)


class TasksSubsystem(SubsystemBase):

    NAME = 'tasks'


    def activate(self, flask_app):
        from ..celery.app import celery_app
        self.config = self.project.config.get('celery', {})

        # ensure critical celery config exists
        self.config.setdefault('broker_url', 'amqp://guest:guest@localhost/')

        override_broker_url = os.environ.get('COB_CELERY_BROKER_URL')
        if override_broker_url is not None:
            self.config['broker_url'] = override_broker_url

        celery_app.conf.update(self.config)
        self.queues = set()

    def get_queue_names(self):
        names = set()
        for grain in self.grains:
            queue_names = grain.config.get('queue_names')
            if not queue_names:
                continue
            if not isinstance(queue_names, list):
                queue_names = queue_names.split(',')
            names.update(queue_names)
        names.add('celery')
        return sorted(names)

    def configure_grain(self, grain, flask_app):
        _ = grain.load()

    def configure_app(self, flask_app):
        super().configure_app(flask_app)

        from ..celery.app import celery_app
        for task in celery_app.tasks.values():
            queue_name = getattr(task, 'queue', None)
            if queue_name is not None:
                self.queues.add(queue_name)

    def iter_locations(self):
        return None
