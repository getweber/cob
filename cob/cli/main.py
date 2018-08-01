#!/usr/bin/env python
import os
import pkg_resources
import sys

import logbook
import click

from cob.app import build_app
from cob.project import get_project
from cob.exceptions import CobExecutionError
from cob.bootstrapping import ensure_project_bootstrapped

@click.group()
@click.option("-v", "--verbose", count=True)
@click.option("-q", "--quiet", count=True)
def main(verbose, quiet):
    logbook.NullHandler().push_application()
    logbook.StreamHandler(sys.stderr, level=logbook.WARNING -
                          verbose + quiet, bubble=False).push_application()

@main.command()
def version():
    print(pkg_resources.get_distribution('cob').version)


@main.add_command
@click.command()
def bootstrap():
    try:
        ensure_project_bootstrapped()
    except RuntimeError as e:
        raise CobExecutionError(str(e))


@main.add_command
@click.command(context_settings={
    'ignore_unknown_options': True
})
@click.option('--migrate', is_flag=True, default=False)
@click.argument('pytest_args', nargs=-1, type=click.UNPROCESSED)
def test(pytest_args, migrate):
    ensure_project_bootstrapped()
    python_executable = os.path.abspath('.cob/env/bin/python')
    if migrate:
        with build_app().app_context():
            get_project().setup_db()
    os.execv(python_executable, [python_executable, '-m', 'pytest'] + list(pytest_args))


@main.add_command
@click.command()
def shell():
    ensure_project_bootstrapped()
    app = build_app()

    sys.path[:] = [p for p in sys.path if p not in ('', '.')]


    with app.app_context():
        ns = {'app': app, '__package__': '_cob'}
        try:
            from IPython import embed
        except ImportError:
            import code
            code.interact(local=ns)
        else:
            embed(user_ns=ns)



def _add_all_subcommands():
    for name in [
            'celery',
            'db',
            'develop',
            'docker',
            'generate',
            'info',
            'testserver',
            'list',
            'migrate',
    ]:
        mod = __import__(f'cob.cli.{name}_cli', fromlist=[''])
        cmd = getattr(mod, name)
        main.add_command(cmd)

_add_all_subcommands()


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
