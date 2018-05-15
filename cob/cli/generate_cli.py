import os
import subprocess
from contextlib import contextmanager

import click
import jinja2
import logbook

import gossip

_logger = logbook.Logger(__name__)

_SKELETONS_ROOT = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', '_skeletons'))

_ctx = {}


class UnknownSkeleton(Exception):
    pass


@click.group()
def generate():
    pass

def _get_grain_types():
    return sorted(filename.split('-', 1)[1]
                  for filename in os.listdir(_SKELETONS_ROOT)
                  if filename.startswith('grain-'))

@generate.command()
@click.option('-m', '--mountpoint', default="/")
@click.option('grain_type', '-t', '--type', default='views', type=click.Choice(_get_grain_types()))
@click.argument('name')
def grain(grain_type, name, mountpoint):
    _generate(f'grain-{grain_type}', name, {
        'name': name,
        'mountpoint': mountpoint,
    })
    gossip.trigger_with_tags('cob.after_generate.grain', tags=[grain_type], kwargs={'name': name})

@gossip.register('cob.after_generate.grain', tags=['frontend-ember'])
def after_generate_grain_frontend_ember(*, name):
    status, _ = subprocess.getstatusoutput('which ember')
    if status != 0:
        click.echo('You do not seem to have ember-cli installed. Skipping ember app creation...')
    else:
        click.echo('Generating new Ember project')
        subprocess.check_call('ember init', cwd=name, shell=True)
        subprocess.check_call('npm install', cwd=name, shell=True)


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
    _generate('grain-models', name, {
        'name': name,
    })


def _generate(skeleton_name, dest_path, ctx):
    try:
        s = load_skeleton(skeleton_name)
    except UnknownSkeleton:
        raise click.ClickException(f'Unknown skeleton: {skeleton_name}')
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
        raise UnknownSkeleton()

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
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(self._path)),
                                 keep_trailing_newline=True)
        template = env.get_template(os.path.basename(self._path))
        normalized_path = os.path.relpath(dest_path) if not os.path.isabs(dest_path) else dest_path
        click.echo(f'Generating {normalized_path}')
        if os.path.exists(dest_path):
            raise click.ClickException(f"{normalized_path} already exists")
        with open(normalized_path, 'w') as f:
            f.write(template.render(**_ctx))
