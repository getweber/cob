from click import ClickException


class CobException(Exception):
    pass


class CobExecutionError(CobException, ClickException):
    exit_code = -1


class NotInProject(CobExecutionError):
    pass


class CobConflict(CobExecutionError):
    pass


class BadMountpoint(CobConflict):
    pass


class MountpointConflict(CobConflict):
    pass
