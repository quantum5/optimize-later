# optimize-later [![Build Status](https://img.shields.io/travis/quantum5/optimize-later.svg)](https://travis-ci.org/quantum5/optimize-later) [![Coverage](https://img.shields.io/codecov/c/gh/quantum5/optimize-later.svg)](https://codecov.io/gh/quantum5/optimize-later) [![PyPI](https://img.shields.io/pypi/v/optimize-later.svg)](https://pypi.org/project/optimize-later/) [![PyPI - Format](https://img.shields.io/pypi/format/optimize-later.svg)](https://pypi.org/project/optimize-later/) [![PyPI - Django Version](https://img.shields.io/pypi/djversions/optimize-later.svg)](#django)

> Premature optimization is the root of all evil (or at least most of it) in programming.
>
> -- <cite>Donald Knuth</cite>

Wouldn't it be nice to have something to tell you when optimization is really necessary?

Enter `optimize-later`.

Instead of trying to guess what code ought to be optimized, `optimize-later` times potentially
slow blocks of code for you, and calls a user-specified function when it exceeds the specified
time limit. This way, you only have to optimize code when speed becomes a problem, saving you
from both the evils of premature optimization, and the evils of slow code. 

## Usage

```python
from optimize_later import optimize_later, register_callback

### Basic usage.
with optimize_later('test_block', 0.2):
    # potentially slow block of code...
    time.sleep(1)

@register_callback
def my_report_function(report):
    # Short one line description.
    print(report.short())

    # Long description with breakdown based on blocks.
    print(report.long())
    
    # Details available in:
    #   - report.name: block name
    #   - report.limit: time limit
    #   - report.delta: time consumed
    #   - report.blocks: breakdown by blocks
    #   - report.start, report.end: start and end time with an unspecified timer:
    #     useful for building a relative timeline with blocks.

### More advanced uses.
# Automatic block names from file and source line (slightly slow).
with optimize_later(0.2):
    # potentially slow block of code...
    time.sleep(1)

# Always warn. Good for exceptional cases that you suspect should not happen.
with optimize_later():
    # potentially slow block of code...
    time.sleep(1)

# Also available as a decorator.
@optimize_later('bad-function', 0.2)
def function_name():
    # potentially slow function...
    time.sleep(1)

# Will use module:function as block name, if you do not specify a name.
# There is no performance penalty this way, as the function name can be easily detected.
@optimize_later(0.2)
def function_name():
    # potentially slow function...
    time.sleep(1)

### Blocks.
with optimize_later() as o:
    with o.block('block 1'):
        # When the time limit of whole block is exceeded, your report will contain
        # a detailed breakdown by sub-blocks executed. This allows you to pinpoint
        # which exact block is the culprit.
        time.sleep(1)
    
    # optimize-later will automatically generate a block name for you from file and
    # line number, with a slightly performance penalty.
    with o.block() as b:
        # You can also nest blocks.
        with b.block():
            pass

### Callbacks deregistration and contexts.
from optimize_later import deregister_callback, optimize_context

deregister_callback(my_report_function)

with optimize_context():
    # Register a callback here.
    register_callback(my_report_function)
# Callback is not available here.

@optimize_context
def function():
    # This callback will be available for the duration of this function.
    register_callback(my_report_function)

# Remove global callbacks for this block.
with optimize_context(renew=True):
    pass
# or...
@optimize_context(renew=True)
def function():
    pass
    
# Shortcut registration syntax.
with optimize_context(my_report_function):
    pass

@optimize_context(my_report_function, renew=True)
def function():
    pass
```

A sample short report:

```Block 'tests.py@152' took 0.011565s (+0.011565s over limit)```

A sample long report:

```
Block 'tests.py@152' took 0.011565s (+0.011565s over limit), children:
  - Block 'tests.py@153' took 0.006662s, children:
      - Block 'tests.py@154' took 0.000002s
      - Block 'tests.py@156' took 0.000002s
  - Block 'tests.py@159' took 0.000001s
```

## Installation

Install the module with:

```
$ pip install optimize-later
```

Or if you want the latest bleeding edge version:

```
$ pip install -e git://github.com/quantum5/optimize-later.git
```

That's it!

### Django

If you are using Django, you might want to configure `optimize-later` in `settings.py` instead of
adding callbacks directly.

You have to add `'optimize_later'` to `INSTALLED_APPS`.

Then, the list of callbacks as dot-separated import paths can be specified in `'OPTIMIZE_LATER_CALLBACKS'`
in `settings.py`. For example:

```python
OPTIMIZE_LATER_CALLBACKS = [
    'myapp.optimize.report',
    'otherapp.optimize.report',
]
```
