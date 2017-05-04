#!/usr/bin/env python
import os
import sys

import logbook
import click


from cob.bootstrapping import ensure_project_bootstrapped

@click.group()
@click.option("-v", "--verbose", count=True)
@click.option("-q", "--quiet", count=True)
def main(verbose, quiet):
    logbook.NullHandler().push_application()
    logbook.StreamHandler(sys.stderr, level=logbook.WARNING -
                          verbose + quiet, bubble=False).push_application()


@main.add_command
@click.command()
def bootstrap():
    ensure_project_bootstrapped()


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
            'testserver',
            'list',
            'migrate',
    ]:
        mod = __import__('cob.cli.{}'.format(name), fromlist=[''])
        cmd = getattr(mod, name)
        main.add_command(cmd)

_add_all_subcommands()


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
