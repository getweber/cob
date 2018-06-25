import sys
import click


class CobException(Exception):
    pass


class CobExecutionError(CobException, click.ClickException):
    exit_code = -1

    def show(self, file=None):
        if file is not None:
            file = sys.stderr
        click.echo(click.style(f'Error: {self.format_message()}', fg='red'), file=file)


class NotInProject(CobExecutionError):
    pass


class CobConflict(CobExecutionError):
    pass


class BadMountpoint(CobConflict):
    pass


class MountpointConflict(CobConflict):
    pass


class MissingDependency(CobExecutionError):
    pass


class UnknownSubsystem(CobExecutionError):
    pass


class TestsFailed(CobExecutionError):
    pass
