from flask_sqlalchemy import SQLAlchemy

from . import current


class Database(object):

    def __init__(self, project):
        super(Database, self).__init__()
        self.project = project

    def begin_declarations(self):
        self._sa = SQLAlchemy()
        current.db = self._sa
