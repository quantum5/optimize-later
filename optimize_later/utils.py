from types import FunctionType


class NoArgDecoratorMeta(type):
    def __call__(cls, *args, **kwargs):
        if len(args) == 1 and isinstance(args[0], FunctionType):
            return cls()(args[0])
        return super(NoArgDecoratorMeta, cls).__call__(*args, **kwargs)


# Borrowed from the six library.
def with_metaclass(meta, *bases):
    """Create a base class with a metaclass."""

    # This requires a bit of explanation: the basic idea is to make a dummy
    # metaclass for one level of class instantiation that replaces itself with
    # the actual metaclass.
    class metaclass(meta):
        def __new__(cls, name, this_bases, d):
            return meta(name, bases, d)

    return type.__new__(metaclass, 'temporary_class', (), {})
