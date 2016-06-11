import os

import emport

_SUBSYSTEM_BY_NAME = {}

class SubsystemMeta(type):

    def __new__(mcs, classname, bases, classdict):
        returned = type.__new__(mcs, classname, bases, classdict)
        if 'NAME' in classdict:
            _SUBSYSTEM_BY_NAME[classdict['NAME']] = returned
        return returned


class SubsystemBase(metaclass=SubsystemMeta):

    SUBSYSTEM_BY_NAME = _SUBSYSTEM_BY_NAME

    def __init__(self, manager):
        super(SubsystemBase, self).__init__()
        self.manager = manager
        self.project = self.manager.project
        self.modules = []

    def add_module(self, path, config):
        self.modules.append((path, config))

    def activate(self):
        for index, (path, config) in enumerate(self.modules):
            self.modules[index] = LoadedModule(path, config)

    def configure_app(self, flask_app):
        raise NotImplementedError() # pragma: no cover


class LoadedModule(object):

    def __init__(self, path, config):
        super(LoadedModule, self).__init__()
        self.path = path
        self.config = config

    def load_python_symbol_by_name(self, symbol):
        filename, symbol = symbol.rsplit(':', 1)
        assert not os.path.isabs(filename)
        filename = os.path.join(self.path, filename)
        if not os.path.isfile(filename) and not filename.endswith('.py'):
            filename += '.py'
        if not os.path.isfile(filename):
            raise RuntimeError('File does not exist: {!r}'.format(filename))
        module = emport.import_file(filename)
        return getattr(module, symbol)
