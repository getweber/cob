import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import time
from contextlib import contextmanager

import logbook
from jinja2 import Environment as TemplateEnvironment
from jinja2 import FileSystemLoader

import requests
from urlobject import URLObject

_logger = logbook.Logger(__name__)

_DEFAULT_PORT = 6789

_PROJS_ROOT = os.path.join(os.path.dirname(__file__), '_projects')


template_env = TemplateEnvironment(loader=FileSystemLoader(
    os.path.join(os.path.abspath(os.path.dirname(__file__)), '_templates')))


class Project(object):

    def __init__(self, name):
        super(Project, self).__init__()
        self._name = name
        self.tempdir = tempfile.mkdtemp()
        self.projdir = os.path.join(self.tempdir, 'proj')
        shutil.copytree(os.path.join(_PROJS_ROOT, self._name), self.projdir)
        self.logfile_name = os.path.join(self.tempdir, 'testserver.log')

    def cmd(self, cmd):
        return subprocess.check_call(cmd, shell=True, cwd=self.projdir)

    def on(self, path):
        return ProjectPath(self, path)

    @contextmanager
    def server_context(self):

        _logger.debug('Server log is going to {}...', self.logfile_name)

        with open(self.logfile_name, 'a') as logfile:

            self._run_cob(['bootstrap'], logfile).wait()
            with self._end_killing(self._run_cob(['testserver', '-p', '0'], logfile)) as p:
                port = self._parse_port(logfile)
                self._wait_for_server(process=p, port=port)
                yield URLObject('http://127.0.0.1:{}'.format(port))

    def _run_cob(self, argv, logfile):
        return subprocess.Popen(
            ' '.join([sys.executable, '-m', 'cob.cli.main', '-vvvvv', *argv]),
            cwd=self.projdir,
            shell=True,
            stdout=logfile,
            stderr=subprocess.STDOUT,
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

    def _parse_port(self, logfile, timeout_seconds=5):
        end_time = time.time() + timeout_seconds
        while time.time() < end_time:
            with open(logfile.name, 'r') as f:
                for line in f:
                    match = re.search(
                        r'Running on http://127\.0\.0\.1:(\d+)', line)
                    if match:
                        return int(match.group(1))
            time.sleep(0.1)
        with open(logfile.name, 'r') as f:
            error_msg = 'Could not parse port. It is very likely that cob has failed or encountered an exception.\nOutput was:\n {})'.format(f.read())
            raise RuntimeError(error_msg)

    def _wait_for_server(self, port, timeout_seconds=2, process=None):
        end_time = time.time() + timeout_seconds
        while time.time() < end_time:
            s = socket.socket()
            try:
                s.connect(('127.0.0.1', port))
            except socket.error:
                if process is not None and process.poll() is not None:
                    raise RuntimeError('Process exited!')
                time.sleep(0.05)
                continue
            else:
                break
        else:
            raise RuntimeError('Could not connect')

class ProjectPath(object):

    def __init__(self, project, path):
        super(ProjectPath, self).__init__()
        self.project = project
        self.path = path

    def returns(self, code_or_string):
        resp = self._request()
        if isinstance(code_or_string, int):
            assert resp.status_code == code_or_string
        else:
            assert resp.text == code_or_string
        return True

    def returns_json(self, value):
        assert self._request().json() == value
        return True

    def _request(self):
        with self.project.server_context() as url:
            return requests.get(url.add_path(self.path))
