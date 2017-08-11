import inspect
import logging
import os
import time
from copy import copy
from functools import wraps
from numbers import Number
from types import FunctionType

from optimize_later import config

log = logging.getLogger(__name__.rpartition('.')[0] or __name__)
timer = [time.time, time.clock][os.name == 'nt']


def global_callback(report):
    for callback in config.callbacks:
        try:
            callback(report)
        except Exception:
            log.exception('Failed to invoke global callback: %r', callback)


def _generate_default_name():
    for entry in inspect.stack():
        file, line = entry[1:3]
        if file != __file__:
            break
    else:
        return '-'
    return '%s@%d' % (os.path.basename(file), line)


class OptimizeBlock(object):
    def __init__(self, name):
        self.name = name
        self.start = None
        self.end = None
        self.delta = None
        self.blocks = []

    def block(self, name=None):
        block = OptimizeBlock(name or _generate_default_name())
        self.blocks.append(block)
        return block

    def __enter__(self):
        assert self.start is None, 'Do not reuse blocks.'
        self.start = timer()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end = timer()
        self.delta = self.end - self.start

    def short(self, precision=3):
        return 'Block %r took %.*fs' % (self.name, precision, self.delta)

    def long(self, precision=6):
        lines = ['  - %s%s' % (self.short(precision), ', children:' if self.blocks else '')]
        for block in self.blocks:
            lines.append('    ' + block.long().replace('\n', '\n    '))
        return '\n'.join(lines)

    def __str__(self):
        return 'Block %r took %.6fs' % (self.name, self.delta)

    def __repr__(self):
        return 'optimize_block(%r, delta=%.6f, blocks=%r)' % (self.name, self.delta, self.blocks)


class OptimizeReport(object):
    def __init__(self, name, limit, start, end, delta, blocks):
        self.name = name
        self.limit = limit
        self.start = start
        self.end = end
        self.delta = delta
        self.blocks = blocks

    def short(self, precision=3):
        return 'Block %r took %.*fs (+%.*fs over limit)' % (
            self.name,
            precision, self.delta,
            precision, self.delta - self.limit,
        )

    def long(self, precision=6):
        lines = [self.short(precision)]
        if self.blocks:
            lines[-1] += ', children:'
            for block in self.blocks:
                lines.append(block.long())
        return '\n'.join(lines)

    def __str__(self):
        return self.short()


class NoArgDecoratorMeta(type):
    def __call__(cls, *args, **kwargs):
        if len(args) == 1 and isinstance(args[0], FunctionType):
            return cls()(args[0])
        return super(NoArgDecoratorMeta, cls).__call__(*args, **kwargs)


class optimize_later(object):
    __metaclass__ = NoArgDecoratorMeta

    def __init__(self, name=None, limit=None, callback=None):
        if limit is None and isinstance(name, Number):
            name, limit = None, name
        self._default_name = not name
        self.name = name or _generate_default_name()
        self.limit = limit or 0
        self.callback = callback
        self.start = None
        self.end = None
        self.delta = None

        # This is going to get shallow copied, so we shouldn't use [].
        self.blocks = None

    def block(self, name=None):
        assert self.start is not None, 'Blocks are meant to be used inside with.'
        if self.blocks is None:
            self.blocks = []
        block = OptimizeBlock(name or _generate_default_name())
        self.blocks.append(block)
        return block

    def __enter__(self):
        assert self.start is None, 'Do not reuse optimize_later objects.'
        self.start = timer()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end = timer()
        self.delta = self.end - self.start
        if self.delta >= self.limit:
            self._report()

    def _report(self):
        report = OptimizeReport(self.name, self.limit, self.start, self.end, self.delta, self.blocks or [])
        if self.callback:
            try:
                self.callback(report)
            except Exception:
                log.exception('Failed to invoke user-specified callback: %r', self.callback)
        else:
            global_callback(report)

    def __call__(self, function):
        self.name = '%s:%s' % (function.__module__, function.__name__)

        @wraps(function)
        def wrapped(*args, **kwargs):
            with copy(self):
                return function(*args, **kwargs)
        return wrapped


class optimize_context(object):
    __metaclass__ = NoArgDecoratorMeta

    def __init__(self, callbacks=None):
        self.callbacks = callbacks

    def __enter__(self):
        self.old_context = config.callbacks[:]
        if self.callbacks is None:
            config.callbacks[:] = self.old_context
        else:
            config.callbacks[:] = self.callbacks

    def __exit__(self, exc_type, exc_val, exc_tb):
        config.callbacks[:] = self.old_context

    def __call__(self, function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            with optimize_context(self.callbacks):
                return function(*args, **kwargs)
        return wrapper
