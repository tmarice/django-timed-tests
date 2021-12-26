import multiprocessing
import os
import sys
from io import StringIO

from django.test import TestCase

from django_timed_tests.runner import TimedTestRunner


class DummyTestCase(TestCase):
    def test_dummy(self):
        django_test_runner = TimedTestRunner()
        suite = django_test_runner.build_suite(["examples"])
        runner_kwargs = django_test_runner.get_test_runner_kwargs()
        output_stream = StringIO()
        runner_kwargs["stream"] = output_stream
        test_runner = django_test_runner.test_runner(**runner_kwargs)
        result = test_runner.run(suite)

        for test, duration in result.durations.items():
            expected_duration = int(test._testMethodName.split("_")[-1])
            self.assertAlmostEqual(expected_duration, duration, places=1)


class DummyParallelTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        if sys.platform == "darwin" and os.environ.get("OBJC_DISABLE_INITIALIZE_FORK_SAFETY", "") != "YES":
            print(
                (
                    "Set OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES in your"
                    + " environment to work around use of forking in Django's"
                    + " test runner."
                ),
                file=sys.stderr,
            )
            sys.exit(1)

        multiprocessing.set_start_method("fork")

    def test_dummy_parallel(self):
        django_test_runner = TimedTestRunner(parallel=3)
        suite = django_test_runner.build_suite(["examples"])
        runner_kwargs = django_test_runner.get_test_runner_kwargs()
        output_stream = StringIO()
        runner_kwargs["stream"] = output_stream
        test_runner = django_test_runner.test_runner(**runner_kwargs)
        result = test_runner.run(suite)

        for test, duration in result.durations.items():
            expected_duration = int(test._testMethodName.split("_")[-1])
            self.assertAlmostEqual(expected_duration, duration, places=1)
