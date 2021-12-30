import multiprocessing
import os
import sys
from io import StringIO
from time import perf_counter
from unittest.mock import patch

from django.core import management
from django.test import TestCase, override_settings

from django_timed_tests.runner import NUM_SLOWEST_TESTS, TimedTestRunner

EXAMPLE_TEST_SUITE_PATH = "tests.example_tests"
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

    def _test_short_formatting(self, stream):
        text = stream.getvalue()
        table_start = text.find("OK")
        table = text[table_start + 3 :].strip()  # Need to account for lenght of 'OK\n'
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

    def _test_full_formatting(self, stream):
        text = stream.getvalue()
        tables_start = text.find("OK")
        tables_text = text[tables_start + 3 :]  # Need to account for lenght of 'OK\n'
        tables = tables_text.split("\n\n")

        for i, table in enumerate(tables):
            table = table.strip()
            rows = table.split("\n")[2:]  # Skip header and horizontal line

            if i == 0:  # module table
                self.assertEqual(len(rows), 2)
            elif i == 1:  # class table
                self.assertEqual(len(rows), 3)
            elif i == 2:  # method table
                self.assertEqual(len(rows), 12)

    def _test_run(self, parallel=1, full_report=False, debug_sql=False):
        start = perf_counter()

        django_test_runner = TimedTestRunner(parallel=parallel, debug_sql=debug_sql)
        suite = django_test_runner.build_suite([EXAMPLE_TEST_SUITE_PATH])
        runner_kwargs = django_test_runner.get_test_runner_kwargs()
        output_stream = StringIO()
        runner_kwargs["stream"] = output_stream
        runner_kwargs["full_report"] = full_report
        test_runner = django_test_runner.test_runner(**runner_kwargs)

        result = test_runner.run(suite)

        duration = perf_counter() - start
        self.assertAlmostEqual(duration, TOTAL_TEST_DURATION / parallel, places=0)

        for test, duration in result.durations.items():
            expected_duration = int(test._testMethodName.split("_")[-1])
            self.assertAlmostEqual(expected_duration, duration, places=1)

        if full_report:
            self._test_full_formatting(output_stream)
        else:
            self._test_short_formatting(output_stream)
        # print(output_stream.getvalue())

    def test_sequential_short_output(self):
        self._test_run()

    def test_parallel_short_output(self):
        self._test_run(parallel=3)

    def test_sequential_full_output(self):
        self._test_run(full_report=True)

    def test_parallel_full_output(self):
        self._test_run(parallel=3, full_report=True)

    def test_debug_sql(self):
        self._test_run(debug_sql=True)

    @patch("django.core.management.commands.test.Command.handle", return_value="")
    @override_settings(TEST_RUNNER="django_timed_tests.TimedTestRunner")
    def test_command_invocation_short_report(self, mock_handle):
        management.call_command("test", EXAMPLE_TEST_SUITE_PATH)

        args, kwargs = mock_handle.call_args

        self.assertFalse(kwargs["full_report"])

    @patch("django.core.management.commands.test.Command.handle", return_value="")
    @override_settings(TEST_RUNNER="django_timed_tests.TimedTestRunner")
    def test_command_invocation_full_report(self, mock_handle):
        management.call_command("test", EXAMPLE_TEST_SUITE_PATH, "--full-report")

        args, kwargs = mock_handle.call_args

        self.assertTrue(kwargs["full_report"])

    def test_failed_test_not_measured(self):
        """Duration of failed tests shouldn't be recoreded."""
        pass
