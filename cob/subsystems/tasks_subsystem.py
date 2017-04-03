import logbook

from .base import SubsystemBase
from ..celery_utils import celery_app

_logger = logbook.Logger(__name__)


class TasksSubsystem(SubsystemBase):

    NAME = 'tasks'


    def configure_grain(self, grain, flask_app):
        _logger.trace('Found tasks grain: {}', grain)
        # celery_app.cobcelery.conf.imports = ('%s' % grain.path.split('/')[-1].split('.')[0])
        m = grain.load()
        celery_app.register_tasks()


    def activate(self, flask_app):
        celery_app.load_config(self.project)
