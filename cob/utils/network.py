import time
import socket

from contextlib import closing
import logbook

_logger = logbook.Logger(__name__)

def wait_for_tcp(hostname, port, timeout_seconds=600):
    end_time = time.time() + timeout_seconds

    with closing(socket.socket()) as sock:
        while True:
            try:
                _logger.debug('Trying to connect to {!r}:{}...', hostname, port)
                sock.connect((hostname, port)) # pylint: disable=no-member
            except socket.error as e:
                _logger.debug('Could not connect ({})', e)
                if time.time() > end_time:
                    raise IOError('Could not connect to {}:{}'.format(hostname, port))
                time.sleep(1)
            else:
                return
