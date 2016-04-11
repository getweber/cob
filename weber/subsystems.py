import os

import emport


class Subsystem(object):

    def __init__(self, path, config):
        super(Subsystem, self).__init__()
        self.path = path
        self.type = config['type']
        self.config = config

    @classmethod
    def from_config(cls, path, config):
        if config['type'] == 'blueprint':
            cls = BlueprintSubsystem
        else:
            raise TypeError(
                'Unrecognized blueprint type: {}'.format(config['type']))
        return cls(path, config)


class BlueprintSubsystem(Subsystem):

    def iter_blueprints(self):
        mountpoint = self.config['mountpoint']
        blueprint_name = self.config['blueprint']
        module_name, symbol = blueprint_name.rsplit(':', 1)
        filename = os.path.join(self.path, module_name)
        if not filename.endswith('.py'):
            filename += '.py'
        mod = emport.import_file(filename)
        yield mountpoint, getattr(mod, symbol)
