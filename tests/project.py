import json
import os
from pathlib import Path
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

from . import conftest


_logger = logbook.Logger(__name__)

_DEFAULT_PORT = 6789

PROJECTS_ROOT = os.path.join(os.path.dirname(__file__), '..', '_test_projects')


template_env = TemplateEnvironment(loader=FileSystemLoader(
    os.path.join(os.path.abspath(os.path.dirname(__file__)), '_templates')))


_built_dockers = set()
_projs_root = tempfile.mkdtemp()


class Project(object):

    def __init__(self, name):
        super(Project, self).__init__()
        self._name = name
        self.projdir = os.path.join(_projs_root, self._name)
        if not os.path.isdir(self.projdir):
            shutil.copytree(os.path.join(
                PROJECTS_ROOT, self._name), self.projdir)

    def cmd(self, cmd, **kwargs):
        assert not cmd.startswith(
            'cob '), "You must run cob from this project's path"
        return subprocess.check_call(cmd, shell=True, cwd=self.projdir, **kwargs)

    def cob_develop_cmd(self, cmd, **kwargs):
        root = Path(sys.executable).parent
        return self.cmd(f'{root / "cob"} {cmd}', env={'COB_DEVELOP': '1'}, **kwargs)

    def on(self, path):
        return ProjectPath(self, path)

    def _build(self):
        if self._name in _built_dockers or conftest.config.getoption('--prebuilt'):
            _logger.debug('Docker image for {._name} already built', self)
        else:
            _logger.debug('Building docker image for {._name}...', self)
            res = self._run_cob(['docker', 'build']).wait()
            assert res == 0, 'cob docker build failed!'
            _built_dockers.add(self._name)

    @contextmanager
    def server_context(self):

        port = 8888

        self._build()
        try:
            with self._end_killing(self._run_cob(['docker', 'run', '--http-port', str(port)])) as p:
                self._wait_for_server(process=p, port=port)
                try:
                    yield RunningProject(self, port)
                except Exception:
                    self._run_cob(['docker', 'logs']).wait()
                    raise
        finally:
            self._run_cob(['docker stop']).wait()

    def _run_cob(self, argv, *, logfile=None):
        return subprocess.Popen(
            ' '.join([sys.executable, '-m', 'cob.cli.main', '-vvvvv', *argv]),
            cwd=self.projdir,
            shell=True,
            stdout=logfile,
            stderr=subprocess.STDOUT,
            env={**os.environ, **{'COB_DEVELOP': 'true'}},
        )

    @contextmanager
    def _end_killing(self, p):
        try:
            yield p
        finally:
            _logger.debug('Killing server')
            if p.poll() is None:
                try:
                    p.terminate()
                except PermissionError:
                    subprocess.check_call(f'sudo -p "Enter password to kill docker-compose process: " kill -9 {p.pid}', shell=True)
            p.wait()

    def _wait_for_server(self, port, timeout_seconds=60, process=None):
        end_time = time.time() + timeout_seconds
        while time.time() < end_time:
            try:
                resp = requests.get(f'http://127.0.0.1:{port}')
            except (socket.error, requests.ConnectionError) as e:
                if process is not None and process.poll() is not None:
                    raise RuntimeError('Process exited!')
                _logger.debug(
                    'Could not connect to server on port {} ({})', port, e)
                time.sleep(1)
                continue
            else:
                break
        else:
            _logger.error('Giving up on connection attempt to http://127.0.0.1:{}', port)
            raise RuntimeError('Could not connect')


class ProjectPath(object):

    def __init__(self, project, path):
        super(ProjectPath, self).__init__()
        self.project = project
        self.path = path

    def returns(self, code_or_string):
        resp = self._request(assert_success=False)
        if isinstance(code_or_string, int):
            assert resp.status_code == code_or_string
        else:
            assert resp.text == code_or_string
        return True

    def returns_json(self, value):
        assert self._request().json() == value
        return True

    def _request(self, **kwargs):
        with self.project.server_context() as app:
            return app.get(self.path, **kwargs)


class RunningProject(object):

    def __init__(self, project, port):
        super().__init__()
        self.project = project
        self.port = port

    def get(self, *args, **kwargs):
        return self.request('get', *args, **kwargs)

    def post(self, *args, **kwargs):
        return self.request('post', *args, **kwargs)

    def post_json(self, *args, **kwargs):
        data = json.dumps(kwargs.pop('data'))
        headers = kwargs.pop('headers', {})
        headers['Content-type'] = 'application/json'
        return self.post(*args, **kwargs, data=data, headers=headers)


    def request(self, method, path, *args, **kwargs):

        assert_success = kwargs.pop('assert_success', True)

        returned = requests.request(method, f'http://127.0.0.1:{self.port}/{path}', *args, **kwargs)
        if assert_success:
            assert returned.ok

        return returned
