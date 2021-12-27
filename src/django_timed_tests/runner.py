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


def generate_report(durations):
    report_data = sorted(
        [
            (
                f"{test.__class__.__module__}.{test.__class__.__name__}.{test._testMethodName}",
                duration,
            )
            for test, duration in durations.items()
        ],
        key=itemgetter(1),
        reverse=True,
    )[:NUM_SLOWEST_TESTS]

    table = tabulate(report_data, headers=["Test", "Duration (s)"], tablefmt="github")
    return table
