import logging
from functools import wraps

from optimize_later.utils import NoArgDecoratorMeta, with_metaclass

try:
    import threading
except ImportError:
    import dummy_threading as threading

log = logging.getLogger(__name__.rpartition('.')[0] or __name__)

_global_callbacks = []
_local = threading.local()


def get_callbacks():
    try:
        return _local.callbacks
    except AttributeError:
        return _global_callbacks


def register_callback(callback):
    get_callbacks().append(callback)
    return callback


def deregister_callback(callback):
    get_callbacks().remove(callback)


def global_callback(report):
    for callback in get_callbacks():
        try:
            callback(report)
        except Exception:
            log.exception('Failed to invoke global callback: %r', callback)


class optimize_context(with_metaclass(NoArgDecoratorMeta)):
    def __init__(self, callbacks=None, reset=False):
        self.callbacks = callbacks or []
        self.reset = reset

    def __enter__(self):
        try:
            self.old_context = _local.callbacks
        except AttributeError:
            self.old_context = None

        if self.reset:
            base_context = []
        elif self.old_context is None:
            base_context = _global_callbacks
        else:
            base_context = self.old_context
        _local.callbacks = base_context + self.callbacks

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.old_context is None:
            del _local.callbacks
        else:
            _local.callbacks = self.old_context

    def __call__(self, function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            with optimize_context(self.callbacks, reset=self.reset):
                return function(*args, **kwargs)
        return wrapper
