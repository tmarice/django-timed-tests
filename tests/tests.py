import multiprocessing
import os
import sys
from io import StringIO
from time import time

from django.test import TestCase

from django_timed_tests.runner import NUM_SLOWEST_TESTS, TimedTestRunner

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

    def _test_formatting(self, stream):
        text = stream.getvalue()
        table_start = text.find("OK")
        table = text[table_start + 3 :]  # Need to account for lenght of 'OK\n'
        rows = table.split("\n")[2:]  # Skip header and horizontal line

        last_duration = float("inf")
        for row in rows:
            clean_row = row[1:-1]  # Skip leading and trailing pipes
            test_name, duration = [r.strip() for r in clean_row.split("|")]  # Split by middle pipe
            duration = int(float(duration))

            expected_duration = int(test_name.rsplit("_", 1)[-1])  # test_method_X lasts X seconds
            self.assertAlmostEqual(expected_duration, duration, places=1)
            self.assertLessEqual(duration, last_duration)
            last_duration = duration

        self.assertEqual(len(rows), NUM_SLOWEST_TESTS)

    def _test_run(self, parallel=1, full_report=False):
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

        self._test_formatting(output_stream)

    def test_sequential(self):
        self._test_run()

    def test_parallel(self):
        self._test_run(parallel=3)
