#!/usr/bin/env python
import os
import pkg_resources
import sys

import logbook
import click

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
@click.argument('pytest_args', nargs=-1, type=click.UNPROCESSED)
def test(pytest_args):
    ensure_project_bootstrapped()
    python_executable = os.path.abspath('.cob/env/bin/python')
    os.execv(python_executable, [python_executable, '-m', 'pytest'] + list(pytest_args))


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
