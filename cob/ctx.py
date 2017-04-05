class ProjectContext(object):

    __slots__ = ['db']

    def __init__(self):
        super(ProjectContext, self).__init__()
        self.db = None


class _ContextStack(object):

    def __init__(self):
        super(_ContextStack, self).__init__()
        self._stack = [ProjectContext()]

    def __getattr__(self, attr):
        if not self._stack:
            raise AttributeError(attr)
        return getattr(self._stack[-1], attr)

    def __dir__(self):
        if self._stack:
            return dir(self._stack[-1])
        return []

    def __setattr__(self, attr, value):
        if attr.startswith("_"):
            return super(_ContextStack, self).__setattr__(attr, value)
        setattr(self._stack[-1], attr, value)

    def push(self, ctx):
        self._stack.append(ctx)
        return ctx

    def pop(self):
        assert len(self._stack) != 0  # pylint: disable=len-as-condition
        if len(self._stack) == 1:
            raise RuntimeError("No more contexts to pop")
        return self._stack.pop(-1)

context = _ContextStack()

class ContextAttributeProxy(object):

    def __init__(self, name):
        super(ContextAttributeProxy, self).__init__()
        self._proxy__name = name

    @property
    def _obj(self):
        return getattr(context, self._proxy__name)

    def __getattr__(self, attr):
        return getattr(self._obj, attr)

    def __setattr__(self, attr, value):
        if attr == "_proxy__name":
            return super(ContextAttributeProxy, self).__setattr__(attr, value)
        setattr(self._obj, attr, value)

    def __eq__(self, other):
        return self._obj == other

    def __ne__(self, other):
        return self._obj != other

    def __call__(self, *args, **kwargs):
        return self._obj(*args, **kwargs)  # pylint: disable=not-callable

    def __repr__(self):
        return repr(self._obj)

    def __dir__(self):
        return dir(self._obj)

    __members__ = __dir__

    def __str__(self):
        return str(self._obj)


db = ContextAttributeProxy("db")
