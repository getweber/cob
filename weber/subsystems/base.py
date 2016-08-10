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
        module = self.load_python_module_by_name(filename)
        return getattr(module, symbol)

    def load_python_module_by_name(self, rel_filename):
        assert not os.path.isabs(rel_filename)
        rel_filename = os.path.join(self.path, rel_filename)
        if not os.path.isfile(rel_filename) and not rel_filename.endswith('.py'):
            rel_filename += '.py'
        if not os.path.isfile(rel_filename):
            raise RuntimeError('File does not exist: {!r}'.format(rel_filename))
        module = emport.import_file(rel_filename)
        return module
