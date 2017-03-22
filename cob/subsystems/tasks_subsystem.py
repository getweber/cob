import logbook

from .base import SubsystemBase
from celery import Celery

_logger = logbook.Logger(__name__)


class TasksSubsystem(SubsystemBase):

    NAME = 'tasks'


    def configure_grain(self, grain, app):
        _logger.trace('Found tasks grain: {}', grain)
        celery = Celery('tasks', backend='rpc://', broker='amqp://dhcpawn:dhcpawn@localhost/dhcpawn_vhost')

        app.config['capp'] = "test"
        grain.load()


