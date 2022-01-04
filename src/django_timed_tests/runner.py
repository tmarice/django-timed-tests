import time
from collections import defaultdict
from operator import itemgetter
from unittest import TextTestResult, TextTestRunner

from tabulate import tabulate

import django
from django.test.runner import (
    DebugSQLTextTestResult,
    DiscoverRunner,
    ParallelTestSuite,
    RemoteTestResult,
    RemoteTestRunner,
)

try:
    from django.test.runner import PDBDebugResult
except ImportError:

    class PDBDebugResult:
        pass


class TimedRemoteTestResult(RemoteTestResult):
    def startTest(self, test):
        self.testsRun += 1
        self.events.append(("startTest", self.test_index, time.perf_counter()))

    def addSuccess(self, test):
        self.events.append(("addSuccess", self.test_index, time.perf_counter()))


class TimedRemoteTestRunner(RemoteTestRunner):
    resultclass = TimedRemoteTestResult


class TimedParallelTestSuite(ParallelTestSuite):
    runner_class = TimedRemoteTestRunner


class TimedTextTestResult(TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._starts = {}
        self.durations = {}

    def startTest(self, test, start_time=None):
        if start_time is None:
            start_time = time.perf_counter()

        self._starts[test] = start_time

        return super().startTest(test)

    def addSuccess(self, test, end_time=None):
        if end_time is None:
            end_time = time.perf_counter()

        self.durations[test] = end_time - self._starts[test]

        return super().addSuccess(test)


class TimedDebugSQLTextTestResult(DebugSQLTextTestResult, TimedTextTestResult):
    pass


class TimedPDBDebugResult(PDBDebugResult, TimedTextTestResult):
    pass


class TimedTextTestRunner(TextTestRunner):
    resultclass = TimedTextTestResult

    def __init__(self, full_report=False, **kwargs):
        super().__init__(**kwargs)

        self._full_report = full_report

    def run(self, test):
        result = super().run(test)

        report = generate_report(durations=result.durations, full_report=self._full_report)

        self.stream.write(report)
        self.stream.write("\n")
        self.stream.flush()

        return result


class TimedTestRunner(DiscoverRunner):
    test_runner = TimedTextTestRunner
    parallel_test_suite = TimedParallelTestSuite

    def __init__(self, full_report=False, **kwargs):
        super().__init__(**kwargs)

        self._full_report = full_report

    @classmethod
    def add_arguments(cls, parser):
        super().add_arguments(parser)
        parser.add_argument(
            "--full-report",
            action="store_true",
            dest="full_report",
            help="Generate a module, class and method duration breakdown",
        )

    def get_resultclass(self):
        if self.debug_sql:
            return TimedDebugSQLTextTestResult
        elif django.VERSION[0] >= 3 and self.pdb:
            return TimedPDBDebugResult

    def get_test_runner_kwargs(self):
        kwargs = super().get_test_runner_kwargs()
        kwargs["full_report"] = self._full_report

        return kwargs


NUM_SLOWEST_TESTS = 10


def generate_report(durations, limit=NUM_SLOWEST_TESTS, full_report=False):
    reports = []
    method_report_data, class_report_data, module_report_data = _get_breakdown(durations)
    if limit is not None and not full_report:
        method_report_data = method_report_data[:NUM_SLOWEST_TESTS]

    if full_report:
        reports.append(
            tabulate(module_report_data, headers=["Module", "Duration (s)"], tablefmt="github", floatfmt=".5f")
        )
        reports.append(
            tabulate(class_report_data, headers=["Class", "Duration (s)"], tablefmt="github", floatfmt=".5f")
        )

    reports.append(tabulate(method_report_data, headers=["Test", "Duration (s)"], tablefmt="github", floatfmt=".5f"))

    report = "\n\n".join(reports)
    return report


def _get_breakdown(durations):
    method_report_data = {}
    class_report_data = defaultdict(int)
    module_report_data = defaultdict(int)

    for test, duration in durations.items():
        module_name = test.__class__.__module__
        class_name = test.__class__.__name__
        method_name = test._testMethodName

        method_report_data[f"{module_name}.{class_name}.{method_name}"] = duration
        class_report_data[f"{module_name}.{class_name}"] += duration
        module_report_data[module_name] += duration

    return [
        sorted(report_data.items(), key=itemgetter(1), reverse=True)
        for report_data in (method_report_data, class_report_data, module_report_data)
    ]
