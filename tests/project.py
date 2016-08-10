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
from weber.cli.generate import static_dir as _generate_static_dir
from weber.cli.generate import models as _generate_models

from .utils import chdir_context

_logger = logbook.Logger(__name__)


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
        self._run_weber(['bootstrap']).wait()
        with self._end_killing(self._run_weber(['testserver'])) as p:
            self._wait_for_server(process=p)
            yield URLObject('http://127.0.0.1:5000')

    def _run_weber(self, argv):
        _logger.debug('Running weber on {}...', self.path)
        return subprocess.Popen(
            ' '.join([sys.executable, '-m', 'weber.cli.main', '-vvvvv', *argv]),
            cwd=str(self.path),
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


class TemplateContainer(object):

    def __init__(self, proj, path):
        super(TemplateContainer, self).__init__()
        self._proj = proj
        self._path = path

    def append_template(self, *args, **kwargs):
        return self._proj.append_template(self._path, *args, **kwargs)
