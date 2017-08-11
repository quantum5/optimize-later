import time
from unittest import TestCase

from optimize_later import config
from optimize_later.core import optimize_later, OptimizeReport, OptimizeBlock, optimize_context


class OptimizeLaterTest(TestCase):
    def setUp(self):
        self.optimize_context = optimize_context([])
        self.optimize_context.__enter__()

    def tearDown(self):
        self.optimize_context.__exit__(None, None, None)

    def assertReport(self, report, name=None, blocks=0):
        self.assertIsInstance(report, OptimizeReport)
        self.assertIsInstance(report.start, float)
        self.assertIsInstance(report.end, float)
        self.assertIsInstance(report.delta, float)
        self.assertIsInstance(report.blocks, list)

        self.assertLessEqual(report.start, report.end)
        self.assertGreaterEqual(report.delta, 0)

        if name:
            self.assertEqual(report.name, name)

        self.assertEqual(len(report.blocks), blocks)

        cumtime = 0
        for block in report.blocks:
            self.assertBlock(block)
            self.assertGreaterEqual(block.start, report.start)
            self.assertLessEqual(block.end, report.end)
            cumtime += block.delta
        self.assertLessEqual(cumtime, report.delta)

    def assertBlock(self, block):
        self.assertIsInstance(block, OptimizeBlock)
        self.assertIsInstance(block.start, float)
        self.assertIsInstance(block.end, float)
        self.assertIsInstance(block.delta, float)

        self.assertLessEqual(block.start, block.end)
        self.assertGreaterEqual(block.delta, 0)

        cumtime = 0
        for subblock in block.blocks:
            self.assertBlock(subblock)
            cumtime += subblock.delta
        self.assertLessEqual(cumtime, block.delta)

    def test_default_name(self):
        self.assertIn('.py@', optimize_later().name)

    def get_report(self, *args, **kwargs):
        reports = []
        function = kwargs.pop('function', lambda: None)
        with optimize_later(*args, callback=reports.append, **kwargs):
            function()
        self.assertIn(len(reports), (0, 1))
        return reports[0] if reports else None

    def test_simple(self):
        self.assertReport(self.get_report())

    def test_simple_fast(self):
        self.assertIs(self.get_report(float('inf')), None)

    def test_name(self):
        self.assertReport(self.get_report('magic_name'),
                          name='magic_name')

    def test_name_fast(self):
        self.assertIs(self.get_report('name', float('inf')), None)

    def test_100_ms(self):
        self.assertReport(self.get_report(function=lambda: time.sleep(0.1)))

    def test_blocks(self):
        reports = []
        with optimize_later(callback=reports.append) as o:
            with o.block('a'):
                pass
            with o.block('b'):
                pass
        self.assertEqual(len(reports), 1)
        self.assertReport(reports[0], blocks=2)
        for block, name in zip(reports[0].blocks, 'ab'):
            self.assertEqual(block.name, name)

    def test_block_naming(self):
        with optimize_later() as o:
            with o.block() as b:
                self.assertIn('.py@', b.name)

    def test_nested_block(self):
        reports = []
        with optimize_later(callback=reports.append) as o:
            with o.block() as b:
                with b.block():
                    pass
                with b.block():
                    pass

            with o.block():
                pass

        self.assertEqual(len(reports), 1)
        self.assertReport(reports[0], blocks=2)
        report = reports[0].long()
        print report
        self.assertIn('      - Block ', report)
        self.assertIn('  - Block', report)
        self.assertEqual(report.count(', children:'), 2)

    def test_decorator(self):
        reports = []
        config.register_callback(reports.append)

        @optimize_later
        def function():
            pass
        self.assertEqual(function.__name__, 'function')
        self.assertEqual(function.__module__, __name__)

        for i in xrange(10):
            function()
        self.assertEqual(len(reports), 10)
        for report in reports:
            self.assertReport(report)

    def test_optimize_context(self):
        config.register_callback(1)
        with optimize_context():
            self.assertEqual(config.callbacks, [1])
            config.register_callback(2)
            self.assertEqual(config.callbacks, [1, 2])

            with optimize_context([]):
                self.assertEqual(config.callbacks, [])
                config.register_callback(3)
                self.assertEqual(config.callbacks, [3])

            config.register_callback(4)
            self.assertEqual(config.callbacks, [1, 2, 4])
        self.assertEqual(config.callbacks, [1])
