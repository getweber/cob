import time

import socket
from contextlib import closing


def wait_for_tcp(hostname, port, timeout_seconds):
    end_time = time.time() + timeout_seconds
    with closing(socket.socket()) as sock:
        while True:
            try:
                sock.connect((hostname, port)) # pylint: disable=no-member
            except socket.error:
                if time.time() > end_time:
                    raise IOError('Could not connect to {}:{}'.format(hostname, port))
                time.sleep(1)
            else:
                return
