import os
from contextlib import contextmanager

import click
import jinja2
import logbook


_logger = logbook.Logger(__name__)

_SKELETONS_ROOT = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', '_skeletons'))

_ctx = {}

@click.group()
def generate():
    pass

@generate.command()
@click.option('-m', '--mountpoint', default=None)
@click.option('-t', '--type', default='views')
@click.argument('name')
def grain(type, name, mountpoint):
    if mountpoint is None:
        mountpoint = '/{}'.format(name)

    if type not in {'views', 'blueprint', 'templates', 'models', 'static'}:
        raise click.ClickException('Unknown grain type: {}'.format(type))

    _generate('grain-{}'.format(type), name, {
        'name': name,
        'mountpoint': mountpoint,
    })


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
@click.argument('mountpoint', default='/static')
def static_dir(name, mountpoint):
    _generate('static_dir', name, {
        'name': name,
        'mountpoint': mountpoint,
    })
    os.mkdir(os.path.join(name, 'root'))

@generate.command()
@click.argument('name', default='models')
def models(name):
    _generate('models', name, {
        'name': name,
    })


def _generate(skeleton_name, dest_path, ctx):
    s = load_skeleton(skeleton_name)
    if s.is_single_file() and not dest_path.endswith('.py'):
        dest_path += '.py'
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
        raise click.ClickException('No such skeleton: {!r}'.format(skeleton_name))

    if os.path.isdir(skeleton_path):
        return SkeletonDir(skeleton_path)

    return SkeletonFile(skeleton_path)


class Skeleton(object):

    def generate(self, dest_path):
        raise NotImplementedError()  # pragma: no cover

    def is_single_file(self):
        return isinstance(self, SkeletonFile)

class SkeletonDir(Skeleton):

    def __init__(self, path):
        super(SkeletonDir, self).__init__()
        self._path = path

    def generate(self, dest_path):
        if not os.path.isdir(dest_path):
            os.mkdir(dest_path)
        for filename in os.listdir(self._path):
            if filename == '.cob.git.keep':
                continue
            skeleton = load_skeleton(os.path.join(self._path, filename))
            skeleton.generate(os.path.join(dest_path, filename))


class SkeletonFile(Skeleton):

    def __init__(self, path):
        super(SkeletonFile, self).__init__()
        self._path = path

    def generate(self, dest_path):
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(self._path)))
        template = env.get_template(os.path.basename(self._path))
        click.echo('Generating {}'.format(os.path.relpath(dest_path)))
        with open(dest_path, 'w') as f:
            f.write(template.render(**_ctx))
