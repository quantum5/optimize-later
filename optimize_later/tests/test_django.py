import imp
import sys
import uuid

from optimize_later.core import optimize_later, OptimizeReport

try:
    from django.conf import settings
except ImportError:
    use_django = False
else:
    use_django = settings.configured

if use_django:
    from django.test import TestCase
    from optimize_later import apps


    class DjangoCallbackTest(TestCase):
        def make_module_path(self, function):
            name = 'id_%s' % (uuid.uuid4().hex,)
            module = imp.new_module(name)
            module.function = function
            sys.modules[name] = module
            return '%s.function' % (name,)

        def test_no_callbacks(self):
            apps.initialize_django_callbacks()
            self.assertEqual(apps.django_callbacks, [])

        def test_callbacks(self):
            reports = []
            with self.settings(OPTIMIZE_LATER_CALLBACKS=[
                self.make_module_path(reports.append),
            ]):
                apps.initialize_django_callbacks()
                with optimize_later('test'):
                    pass
            self.assertEqual(len(reports), 1)
            self.assertIsInstance(reports[0], OptimizeReport)
