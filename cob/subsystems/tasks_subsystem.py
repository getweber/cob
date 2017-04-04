import logbook

from .base import SubsystemBase
_logger = logbook.Logger(__name__)


class TasksSubsystem(SubsystemBase):

    NAME = 'tasks'


    def activate(self, flask_app):
        from ..celery_utils import celery_app
        self._config = self.project.config.get('celery', {})

        # ensure critical celery config exists
        self._config.setdefault('broker_url', 'amqp://guest:guest@localhost/')

        celery_app.conf.broker_url = self._config['broker_url']

    def configure_grain(self, grain, flask_app):
        _ = grain.load()
