# For Django applications.
import logging

from django.apps import AppConfig
from django.conf import settings
from django.utils.module_loading import import_string

from optimize_later import config

log = logging.getLogger(__name__.rpartition('.')[0] or __name__)

django_callbacks = []


class OptimizeLaterConfig(AppConfig):
    name = 'optimize_later'
    verbose_name = 'Optimize Later'

    def ready(self):
        initialize_django_callbacks()


def django_callback(result):
    for callback in django_callbacks:
        try:
            callback(result)
        except Exception:
            log.exception('Failed to invoke Django callback: %r', callback)


def initialize_django_callbacks():
    global django_callbacks
    django_callbacks = []
    for callback in getattr(settings, 'OPTIMIZE_LATER_CALLBACKS', None) or []:
        django_callbacks.append(import_string(callback))

config.register_callback(django_callback)
