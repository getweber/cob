from click import ClickException

class CobException(Exception):
    pass

class NotInProject(CobException, ClickException):

    exit_code = -1
