import inspect
import logging
import os
from copy import copy
from functools import wraps
from numbers import Number
from time import perf_counter

from optimize_later.config import global_callback
from optimize_later.utils import NoArgDecoratorMeta, with_metaclass
from optimize_later import utils

log = logging.getLogger(__name__.rpartition('.')[0] or __name__)


def _generate_default_name():
    for entry in inspect.stack():
        file, line = entry[1:3]
        if file not in (__file__, utils.__file__):
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
        self.start = perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end = perf_counter()
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


class optimize_later(with_metaclass(NoArgDecoratorMeta)):
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
        self.start = perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end = perf_counter()
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
        if self._default_name:
            self.name = '%s:%s' % (function.__module__, function.__name__)

        @wraps(function)
        def wrapped(*args, **kwargs):
            with copy(self):
                return function(*args, **kwargs)
        return wrapped
