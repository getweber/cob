import logbook

from .base import SubsystemBase
from ..ctx import context

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


_logger = logbook.Logger(__name__)


class ModelsSubsystem(SubsystemBase):

    NAME = 'models'

    def activate(self, flask_app):
        context.db = SQLAlchemy(flask_app)
        Migrate(flask_app, context.db).init_app(flask_app)
        super(ModelsSubsystem, self).activate(flask_app)

    def configure_grain(self, grain, flask_app): # pylint: disable=unused-argument
        _logger.trace('Found models: {m.path}', grain)
        grain.load()
