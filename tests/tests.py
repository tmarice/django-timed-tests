import multiprocessing
import os
import sys
from io import StringIO
from time import time

from django.test import TestCase

from django_timed_tests.runner import TimedTestRunner

EXAMPLE_TEST_SUITE_PATH = "tests.examples"
TOTAL_TEST_DURATION = 18


class TimedTestRunnerTestCase(TestCase):
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

    def _test_run(self, parallel=1):
        start = time()
        django_test_runner = TimedTestRunner(parallel=parallel)
        suite = django_test_runner.build_suite([EXAMPLE_TEST_SUITE_PATH])
        runner_kwargs = django_test_runner.get_test_runner_kwargs()
        output_stream = StringIO()
        runner_kwargs["stream"] = output_stream
        test_runner = django_test_runner.test_runner(**runner_kwargs)

        result = test_runner.run(suite)

        duration = time() - start
        self.assertAlmostEqual(duration, TOTAL_TEST_DURATION / parallel, places=0)

        for test, duration in result.durations.items():
            expected_duration = int(test._testMethodName.split("_")[-1])
            self.assertAlmostEqual(expected_duration, duration, places=1)

    def test_sequential(self):
        self._test_run()

    def test_parallel(self):
        self._test_run(parallel=3)
