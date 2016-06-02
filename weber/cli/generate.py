import os
from contextlib import contextmanager

import click
import jinja2
import logbook

from .exceptions import UsageError

_logger = logbook.Logger(__name__)

_SKELETONS_ROOT = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', '_skeletons'))

_ctx = {}

@click.group()
def generate():
    pass

@generate.command()
@click.argument('path')
@click.argument('project_name', required=False)
def project(path, project_name=None):
    if project_name is None:
        project_name = os.path.basename(path)
    _generate('project', path, {
        'project_name': project_name
    })

@generate.command()
@click.argument('name')
@click.argument('mountpoint')
def blueprint(name, mountpoint):
    _generate('blueprint', name, {
        'name': name,
        'mountpoint': mountpoint,
    })



def _generate(skeleton_name, dest_path, ctx):
    s = load_skeleton(skeleton_name)
    with template_context(ctx):
        s.generate(dest_path)

@contextmanager
def template_context(ctx):
    _ctx.update(ctx)
    try:
        yield
    finally:
        _ctx.clear()


def load_skeleton(skeleton_name):
    skeleton_path = os.path.join(_SKELETONS_ROOT, skeleton_name)
    if not os.path.exists(skeleton_path):
        raise UsageError('No such skeleton: {!r}'.format(skeleton_name))

    if os.path.isdir(skeleton_path):
        return SkeletonDir(skeleton_path)

    return SkeletonFile(skeleton_path)


class Skeleton(object):

    def generate(self, dest_path):
        raise NotImplementedError()  # pragma: no cover


class SkeletonDir(Skeleton):

    def __init__(self, path):
        super(SkeletonDir, self).__init__()
        self._path = path

    def generate(self, dest_path):
        if not os.path.isdir(dest_path):
            os.mkdir(dest_path)
        for filename in os.listdir(self._path):
            skeleton = load_skeleton(os.path.join(self._path, filename))
            skeleton.generate(os.path.join(dest_path, filename))


class SkeletonFile(Skeleton):

    def __init__(self, path):
        super(SkeletonFile, self).__init__()
        self._path = path

    def generate(self, dest_path):
        with open(self._path, 'r') as template:
            template = jinja2.Template(template.read())
        with open(dest_path, 'w') as f:
            f.write(template.render(**_ctx))
