import re
import os
import socket
import subprocess
import sys
import tempfile
import time
from contextlib import contextmanager

import logbook
from jinja2 import Environment as TemplateEnvironment, FileSystemLoader

from urlobject import URLObject
from cob.cli.generate import blueprint as _generate_blueprint
from cob.cli.generate import project as _generate_project
from cob.cli.generate import static_dir as _generate_static_dir
from cob.cli.generate import models as _generate_models

from .utils import chdir_context

_logger = logbook.Logger(__name__)

_DEFAULT_PORT = 6789


template_env = TemplateEnvironment(loader=FileSystemLoader(
    os.path.join(os.path.abspath(os.path.dirname(__file__)), '_templates')))


class Project(object):

    def __init__(self, projdir, projname):
        super(Project, self).__init__()
        self._parent_dir = projdir
        self.path = projdir.join(projname)
        self._name = projname

    def generate_project(self):
        assert not self.path.exists()
        with chdir_context(self._parent_dir):
            _generate_project.callback(self._name)

    def generate_blueprint(self, name):
        with chdir_context(self.path):
            _generate_blueprint.callback(
                name=name, mountpoint='/{}'.format(name))
        return TemplateContainer(self, self.path.join(name).join('blueprint.py'))

    def generate_models(self, name, **kwargs):
        with chdir_context(self.path):
            _generate_models.callback(name=name, **kwargs)
        return TemplateContainer(self, self.path.join(name).join('models.py'))

    def generate_static_dir(self, name, **kw):
        with chdir_context(self.path):
            _generate_static_dir.callback(
                name=name, **kw)

    def append_template(self, relpath, template_name, template_vars):
        template = template_env.get_template(template_name + '.j2')
        with relpath.open("a") as f:
            f.write("\n")
            f.write(template.render(template_vars))



    @contextmanager
    def server_context(self):


        tempdir = tempfile.mkdtemp()
        logfile_name = os.path.join(tempdir, 'testserver.log')
        _logger.debug('Server log is going to {}...', logfile_name)

        with open(logfile_name, 'a') as logfile:

            self._run_cob(['bootstrap'], logfile).wait()
            with self._end_killing(self._run_cob(['testserver', '-p', '0'], logfile)) as p:
                port = self._parse_port(logfile)
                self._wait_for_server(process=p, port=port)
                yield URLObject('http://127.0.0.1:{}'.format(port))

    def _run_cob(self, argv, logfile):
        _logger.debug('Running cob on {}...', self.path)
        return subprocess.Popen(
            ' '.join([sys.executable, '-m', 'cob.cli.main', '-vvvvv', *argv]),
            cwd=str(self.path),
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
                    match = re.search(r'Running on http://127\.0\.0\.1:(\d+)', line)
                    if match:
                        return int(match.group(1))
            time.sleep(0.1)

    def _wait_for_server(self, port, timeout_seconds=5, process=None):
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


class TemplateContainer(object):

    def __init__(self, proj, path):
        super(TemplateContainer, self).__init__()
        self._proj = proj
        self._path = path

    def append_template(self, *args, **kwargs):
        return self._proj.append_template(self._path, *args, **kwargs)
