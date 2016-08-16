import logbook

from .base import SubsystemBase
from .. import this

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


_logger = logbook.Logger(__name__)


class ModelsSubsystem(SubsystemBase):

    NAME = 'models'

    def configure_app(self, app):  # pylint: disable=unused-argument
        this.db = SQLAlchemy(app)
        Migrate(app, this.db).init_app(app)

        for m in self.modules:
            _logger.trace('Found models: {m.path}', m)
            models = m.load_python_module_by_name('models.py')  # pylint: disable=unused-variable
