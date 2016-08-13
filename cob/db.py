from flask_sqlalchemy import SQLAlchemy

from . import this


class Database(object):

    def __init__(self, project):
        super(Database, self).__init__()
        self.project = project

    def begin_declarations(self):
        self._sa = SQLAlchemy()
        this.db = self._sa
