import os
import logbook

from .base import SubsystemBase
from ..ctx import context

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


_logger = logbook.Logger(__name__)


class ModelsSubsystem(SubsystemBase):

    NAME = 'models'

    def activate(self, flask_app):

        env_override = os.environ.get('COB_DATABASE_URI')
        if env_override:
            flask_app.config['SQLALCHEMY_DATABASE_URI'] = env_override
        else:
            flask_app.config.setdefault('SQLALCHEMY_DATABASE_URI', f'sqlite:///{os.path.join(self.project.root, ".cob", "db.sqlite")}')

        context.db = SQLAlchemy(flask_app)
        Migrate(flask_app, context.db).init_app(flask_app)
        super(ModelsSubsystem, self).activate(flask_app)

    def has_migrations(self):
        return os.path.isdir(os.path.join(self.project.root, 'migrations'))


    def configure_grain(self, grain, flask_app): # pylint: disable=unused-argument
        _logger.trace('Found models: {.path}', grain)
        grain.load()

    def iter_locations(self):
        return None
