import logbook

from .base import SubsystemBase
from ..ctx import context

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


_logger = logbook.Logger(__name__)


class ModelsSubsystem(SubsystemBase):

    NAME = 'models'

    def activate(self, app):
        context.db = SQLAlchemy(app)
        Migrate(app, context.db).init_app(app)
        super(ModelsSubsystem, self).activate(app)

    def configure_grain(self, grain, app): # pylint: disable=unused-argument
        _logger.trace('Found models: {m.path}', grain)
        grain.load()
