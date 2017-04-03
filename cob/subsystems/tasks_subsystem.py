import logbook

from .base import SubsystemBase
_logger = logbook.Logger(__name__)


class TasksSubsystem(SubsystemBase):

    NAME = 'tasks'


    def activate(self, flask_app):
        from ..celery_utils import celery_app
        celery_app.conf.broker_url = self.project.config['celery']['broker_url']

    def configure_grain(self, grain, flask_app):
        from ..celery_utils import celery_app
        module = grain.load()
        import pudb
        pudb.set_trace()
