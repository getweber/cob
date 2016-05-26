#!/usr/bin/env python
import sys

import logbook
import click

from ..bootstrapping import ensure_project_bootstrapped


@click.group()
@click.option("-v", "--verbose", count=True)
@click.option("-q", "--quiet", count=True)
def main(verbose, quiet):
    logbook.NullHandler().push_application()
    logbook.StreamHandler(sys.stderr, level=logbook.WARNING-verbose+quiet, bubble=False).push_application()
    ensure_project_bootstrapped()

@main.add_command
@click.command()
def bootstrap():
    pass


def _add_all_subcommands():
    for name in [
            'testserver',
    ]:
        mod = __import__('weber.cli.{}'.format(name), fromlist=[''])
        cmd = getattr(mod, name)
        main.add_command(cmd)

_add_all_subcommands()



if __name__ == "__main__":
    main() # pylint: disable=no-value-for-parameter