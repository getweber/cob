import logbook

from .base import SubsystemBase
from .. import this

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


_logger = logbook.Logger(__name__)


class ModelsSubsystem(SubsystemBase):

    NAME = 'models'

    def activate(self, app):
        this.db = SQLAlchemy(app)
        Migrate(app, this.db).init_app(app)
        super(ModelsSubsystem, self).activate(app)

    def configure_module(self, module, app):
        _logger.trace('Found models: {m.path}', module)
        models = module.load_python_module_by_name('models.py')  # pylint: disable=unused-variable
