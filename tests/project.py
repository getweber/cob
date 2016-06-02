import os
import socket
import subprocess
import sys
import time
from contextlib import contextmanager

import logbook
from jinja2 import Environment as TemplateEnvironment, FileSystemLoader

from urlobject import URLObject
from weber.cli.generate import blueprint as _generate_blueprint
from weber.cli.generate import project as _generate_project

from .utils import chdir_context

_logger = logbook.Logger(__name__)


template_env = TemplateEnvironment(loader=FileSystemLoader(
    os.path.join(os.path.abspath(os.path.dirname(__file__)), '_templates')))


class Project(object):

    def __init__(self, projdir, projname):
        super(Project, self).__init__()
        self._parent_dir = projdir
        self._path = projdir.join(projname)
        self._name = projname

    def generate_project(self):
        assert not self._path.exists()
        with chdir_context(self._parent_dir):
            _generate_project.callback(self._name)

    def generate_blueprint(self, name):
        with chdir_context(self._path):
            _generate_blueprint.callback(
                name=name, mountpoint='/{}'.format(name))

    def append_template(self, relpath, template_name, template_vars):
        template = template_env.get_template(template_name + '.j2')
        with self._path.join(relpath).open("a") as f:
            f.write("\n")
            f.write(template.render(template_vars))



    @contextmanager
    def server_context(self):
        self._run_weber(['bootstrap']).wait()
        with self._end_killing(self._run_weber(['testserver'])) as p:
            self._wait_for_server(process=p)
            yield URLObject('http://127.0.0.1:5000')

    def _run_weber(self, argv):
        _logger.debug('Running weber on {}...', self._path)
        return subprocess.Popen(
            ' '.join([sys.executable, '-m', 'weber.cli.main', '-vvvvv', *argv]),
            cwd=str(self._path),
            shell=True,
        )

    @contextmanager
    def _end_killing(self, p):
        try:
            yield p
        finally:
            _logger.debug('Killing server')
            if p.poll() is None:
                p.terminate()
            p.wait()

    def _wait_for_server(self, port=5000, timeout_seconds=5, process=None):
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