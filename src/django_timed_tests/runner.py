from collections import defaultdict
from operator import itemgetter
from time import time
from unittest import TextTestResult, TextTestRunner

from tabulate import tabulate

from django.test.runner import DiscoverRunner, ParallelTestSuite, RemoteTestResult, RemoteTestRunner


class TimedRemoteTestResult(RemoteTestResult):
    def startTest(self, test):
        self.testsRun += 1
        self.events.append(("startTest", self.test_index, time()))

    def addSuccess(self, test):
        self.events.append(("addSuccess", self.test_index, time()))


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
            start_time = time()

        self._starts[test] = start_time

        return super().startTest(test)

    def addSuccess(self, test, end_time=None):
        if end_time is None:
            end_time = time()

        self.durations[test] = end_time - self._starts[test]

        return super().addSuccess(test)


class TimedTextTestRunner(TextTestRunner):
    resultclass = TimedTextTestResult

    def run(self, test):
        result = super().run(test)

        report = generate_report(durations=result.durations)

        self.stream.write(report)
        self.stream.flush()

        return result


class TimedTestRunner(DiscoverRunner):
    test_runner = TimedTextTestRunner
    parallel_test_suite = TimedParallelTestSuite


NUM_SLOWEST_TESTS = 10


def generate_report(durations, limit=NUM_SLOWEST_TESTS, full_report=False):
    reports = []
    method_report_data, class_report_data, module_report_data = _get_breakdown(durations)
    if limit is not None and not full_report:
        method_report_data = method_report_data[:NUM_SLOWEST_TESTS]

    if full_report:
        reports.append(tabulate(module_report_data, headers=["Module", "Duration (s)"], tablefmt="github"))
        reports.append(tabulate(class_report_data, headers=["Class", "Duration (s)"], tablefmt="github"))

    reports.append(tabulate(method_report_data, headers=["Test", "Duration (s)"], tablefmt="github"))

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
        sorted(report_data.items(), key=itemgetter(1))
        for report_data in (method_report_data, class_report_data, module_report_data)
    ]
