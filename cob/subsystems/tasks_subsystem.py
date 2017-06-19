import os

import logbook

from .base import SubsystemBase
_logger = logbook.Logger(__name__)


class TasksSubsystem(SubsystemBase):

    NAME = 'tasks'


    def activate(self, flask_app):
        from ..celery.app import celery_app
        self._config = self.project.config.get('celery', {})

        # ensure critical celery config exists
        self._config.setdefault('broker_url', 'amqp://guest:guest@localhost/')

        override_broker_url = os.environ.get('COB_CELERY_BROKER_URL')
        if override_broker_url is not None:
            self._config['broker_url'] = override_broker_url

        celery_app.conf.broker_url = self._config['broker_url']
        self.queues = set()

    def get_queue_names(self):
        names = {queue_name for grain in self.grains for queue_name in grain.config.get('queue_names', [])}
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
