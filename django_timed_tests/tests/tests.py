from django.test import TestCase
from io import StringIO
from django_timed_tests.runner import TimedTestRunner
from django.test.runner import DiscoverRunner

class DummyTestCase(TestCase):
    def test_dummy(self):
        # test_runner = TimedTestRunner()
        django_test_runner = DiscoverRunner()
        suite = django_test_runner.build_suite(["examples"])
        runner_kwargs = django_test_runner.get_test_runner_kwargs()
        output_stream = StringIO()
        runner_kwargs['stream'] = output_stream
        test_runner = django_test_runner.test_runner(**runner_kwargs)
        result = test_runner.run(suite)
