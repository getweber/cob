import os
import socket
import subprocess
import sys
import time
from contextlib import contextmanager

import jinja2

from urlobject import URLObject


@contextmanager
def server_context(project):
    with end_killing(run_weber(project, ['bootstrap'])):
        pass
    with end_killing(run_weber(project, ['testserver'])) as p:
        wait_for_server(process=p)
        yield URLObject('http://127.0.0.1:5000')


def run_weber(proj_fixture, argv):
    return subprocess.Popen(
        [sys.executable, '-m', 'weber.cli.main', *argv],
        cwd=proj_fixture.path,
        )

@contextmanager
def end_killing(p):
    try:
        yield p
    finally:
        if p.returncode is not None:
            p.kill()
            p.wait()


def wait_for_server(port=5000, timeout_seconds=5, process=None):
    end_time = time.time() + timeout_seconds
    while time.time() < end_time:
        s = socket.socket()
        try:
            s.connect(('127.0.0.1', port))
        except socket.error:
            if process is not None and process.poll() is not None:
                raise RuntimeError('Process exited!')
            time.sleep(0.1)
            continue
        else:
            break
    else:
        raise RuntimeError('Could not connect')

def write_template(fileobj, name, args):
    with open(os.path.join(os.path.dirname(__file__), '_templates', name)) as f:
        template = jinja2.Template(f.read())
    fileobj.write(template.render(**args))
