import sys
import copy


def route(*args, **kwargs):
    def callable(func):
        calling_module_globals = sys._getframe(1).f_globals # pylint: disable=protected-access
        routes = calling_module_globals.setdefault('__cob_routes__', [])
        routes.append(DeferredRoute(args, kwargs, func))
        return func
    return callable


class DeferredRoute(object):

    def __init__(self, args, kwargs, func):
        super(DeferredRoute, self).__init__()
        self.args = copy.deepcopy(args)
        self.kwargs = copy.deepcopy(kwargs)
        self.func = func

    def register(self, parent):
        parent.route(*self.args, **self.kwargs)(self.func)
