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
        self.grains = []

    def add_grain(self, path, config):
        self.grains.append(LoadedGrain(self, path, config))

    def activate(self, flask_app):
        pass

    def configure_app(self, flask_app):
        for grain in self.grains:
            self.configure_grain(grain, flask_app)

    def configure_grain(self, grain, flask_app):
        raise NotImplementedError() # pragma: no cover

    def configure_tmux_window(self, windows):
        pass


class LoadedGrain(object):

    def __init__(self, subsystem, path, config):
        super(LoadedGrain, self).__init__()
        self.subsystem = subsystem
        self.path = path
        self.config = config

    def load(self):
        if os.path.isfile(self.path):
            return emport.import_file(self.path)
        main = self.config.get('main', 'main')
        if not main.endswith('.py'):
            main += '.py'
        print("Importing %s" % os.path.join(self.path, main))
        return emport.import_file(os.path.join(self.path, main))

    def load_python_symbol_by_name(self, symbol):
        filename, symbol = symbol.rsplit(':', 1)
        grain = self.load_python_module_by_name(filename)
        return getattr(grain, symbol)

    def load_python_module_by_name(self, rel_filename):
        assert not os.path.isabs(rel_filename)
        rel_filename = os.path.join(self.path, rel_filename)
        if not os.path.isfile(rel_filename) and not rel_filename.endswith('.py'):
            rel_filename += '.py'
        if not os.path.isfile(rel_filename):
            raise RuntimeError('File does not exist: {!r}'.format(rel_filename))
        module = emport.import_file(rel_filename)
        return module

    def __repr__(self):
        return self.path
