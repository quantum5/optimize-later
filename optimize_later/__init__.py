from optimize_later.config import register_callback, deregister_callback, optimize_context
from optimize_later.core import optimize_later

__all__ = ['register_callback', 'deregister_callback', 'optimize_context', 'optimize_later']

# Make this usable as a Django application.
default_app_config = 'optimize_later.apps.OptimizeLaterConfig'
