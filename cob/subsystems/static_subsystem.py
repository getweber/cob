import os

import logbook

from flask.helpers import send_from_directory

from .base import SubsystemBase

_logger = logbook.Logger(__name__)



class StaticSubsystem(SubsystemBase):

    NAME = 'static'

    def configure_module(self, module, app):
        cfg = module.config
        root = os.path.join(module.path, cfg['root'])
        mountpoint = cfg['mountpoint']
        view_func = self._get_static_view(root)
        view_name = 'static_view_{}'.format(os.path.basename(module.path))
        _logger.trace('registering static handler on {} for {}', mountpoint, root)
        app.route('{}/<path:path>'.format(mountpoint), endpoint=view_name)(
            view_func
        )

    def _get_static_view(self, root):

        def view_func(path):
            return send_from_directory(root, path)

        return view_func
