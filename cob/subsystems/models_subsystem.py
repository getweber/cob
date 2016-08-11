import logbook

from .base import SubsystemBase

_logger = logbook.Logger(__name__)

class ModelsSubsystem(SubsystemBase):

    NAME = 'models'

    def configure_app(self, app): # pylint: disable=unused-argument
        for m in self.modules:
            self.project.db.begin_declarations()
            _logger.trace('Found models: {m.path}', m)
            models = m.load_python_module_by_name('models.py') # pylint: disable=unused-variable
