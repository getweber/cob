def get_module_by_type(typename):
    mods = get_all_modules_by_type(typename)
    if not mods:
        raise RuntimeError('No modules found with type {}'.format(typename))
    if len(mods) > 1:
        raise RuntimeError(
            'Too many modules found with type {}'.format(typename))
    return mods[0]


def get_all_modules_by_type(typename):
    _scan_modules()
    return [mod for mod in _modules if mod.typename == typename]

_modules = None


def _scan_modules():
    global _modules  # pylint: disable=global-statement
    if _modules is not None:
        return

    _modules = []
