from contextlib import closing
import time
import socket

import logbook
from urlobject import URLObject as URL


_POSTGRES_TCP_PORT = 5432
_RABBITMQ_TCP_PORT = 5672

_logger = logbook.Logger(__name__)


def wait_for_tcp(hostname, port, timeout_seconds=600):
    end_time = time.time() + timeout_seconds

    with closing(socket.socket()) as sock:
        while True:
            try:
                _logger.debug(
                    'Trying to connect to {!r}:{}...', hostname, port)
                sock.connect((hostname, port))  # pylint: disable=no-member
            except socket.error as e:
                _logger.debug('Could not connect ({})', e)
                if time.time() > end_time:
                    raise IOError(
                        'Could not connect to {}:{}'.format(hostname, port))
                time.sleep(1)
            else:
                return


def wait_for_app_services(app):
    db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', None)
    if db_uri is not None:
        uri = URL(db_uri)
        if uri.scheme == 'postgresql':
            wait_for_tcp(uri.netloc.hostname, _POSTGRES_TCP_PORT)

    broker_uri = app.config.get('CELERY_BROKER_URL')
    if broker_uri is not None:
        url = URL(broker_uri)
        if url.scheme == 'amqp':
            wait_for_tcp(uri.netloc.hostname, _RABBITMQ_TCP_PORT)
