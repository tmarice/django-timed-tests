import multiprocessing
import os
import sys
from io import StringIO
from unittest.mock import patch

import django
from django.core import management
from django.test import TestCase, override_settings

from django_timed_tests.runner import NUM_SLOWEST_TESTS, TimedTestRunner

EXAMPLE_TEST_SUITE_PATH = "tests.example_tests"


class FakeTime:
    def __init__(self):
        self._time = 0

    def perf_counter(self):
        return self._time

    def sleep(self, t):
        self._time += t


def extract_tables(stream):
    return_tables = []
    text = stream.getvalue()
    tables_start = text.find("OK")
    tables_text = text[tables_start + 3 :]  # Need to account for lenght of 'OK\n'
    tables = tables_text.split("\n\n")

    for table in tables:
        table = table.strip()
        rows = table.split("\n")[2:]  # Skip header and horizontal line
        return_tables.append(rows)

    return return_tables


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

    def _test_table(self, rows):
        """Every name_X method/class/module should last X seconds, rows should be ordered by descending duration."""
        last_duration = float("inf")
        for row in rows:
            clean_row = row[1:-1]  # Skip leading and trailing pipes
            test_name, duration = [r.strip() for r in clean_row.split("|")]  # Split by middle pipe
            duration = int(float(duration))

            expected_duration = int(test_name.rsplit("_", 1)[-1])
            self.assertEqual(expected_duration, duration)
            self.assertLessEqual(duration, last_duration)
            last_duration = duration

    def _test_short_formatting(self, stream):
        tables = extract_tables(stream)

        self.assertEqual(len(tables), 1)

        rows = tables[0]
        self._test_table(rows=rows)

        self.assertEqual(len(rows), NUM_SLOWEST_TESTS)

    def _test_full_formatting(self, stream):
        tables = extract_tables(stream)

        for i, rows in enumerate(tables):
            if i == 0:  # module table
                self.assertEqual(len(rows), 2)
            elif i == 1:  # class table
                self.assertEqual(len(rows), 3)
            elif i == 2:  # method table
                self.assertEqual(len(rows), 15)

            self._test_table(rows)

    def _test_run(self, parallel=1, full_report=False, debug_sql=False, pdb=False):
        fake_time = FakeTime()
        output_stream = StringIO()

        django_test_runner = TimedTestRunner(parallel=parallel, debug_sql=debug_sql, pdb=pdb)
        suite = django_test_runner.build_suite([EXAMPLE_TEST_SUITE_PATH])
        runner_kwargs = django_test_runner.get_test_runner_kwargs()
        runner_kwargs.update(stream=output_stream, full_report=full_report)
        test_runner = django_test_runner.test_runner(**runner_kwargs)

        with patch("django_timed_tests.runner.time", new=fake_time), patch(
            "tests.example_tests.tests_6.time", new=fake_time
        ), patch("tests.example_tests.tests_25.time", new=fake_time):
            result = test_runner.run(suite)

        for test, duration in result.durations.items():
            expected_duration = int(test._testMethodName.split("_")[-1])
            self.assertEqual(expected_duration, duration)

        if full_report:
            self._test_full_formatting(output_stream)
        else:
            self._test_short_formatting(output_stream)

        return result

    def test_sequential_short_output(self):
        self._test_run()

    def test_parallel_short_output(self):
        self._test_run(parallel=3)

    def test_sequential_full_output(self):
        self._test_run(full_report=True)

    def test_parallel_full_output(self):
        self._test_run(parallel=3, full_report=True)

    def test_debug_sql(self):
        debug_sql_result = self._test_run(debug_sql=True)

        self.assertIsNotNone(debug_sql_result.debug_sql_stream)

    def test_pdb(self):
        if django.VERSION[0] < 3:
            return

        pdb_result = self._test_run(pdb=True)

        with patch("django.test.runner.pdb") as mock_pdb:
            pdb_result.debug(error=(None, None, None))

            self.assertEqual(mock_pdb.post_mortem.call_count, 1)

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
