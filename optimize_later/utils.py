from types import FunctionType


class NoArgDecoratorMeta(type):
    def __call__(cls, *args, **kwargs):
        if len(args) == 1 and isinstance(args[0], FunctionType):
            return cls()(args[0])
        return super(NoArgDecoratorMeta, cls).__call__(*args, **kwargs)