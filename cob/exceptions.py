from click import ClickException

class CobException(Exception):
    pass

class CobExecutionError(CobException, ClickException):

    exit_code = -1

class NotInProject(CobExecutionError):

    pass
