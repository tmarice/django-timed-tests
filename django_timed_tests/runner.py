from time import time
from unittest import TextTestResult, TextTestRunner
from django.test.runner import DiscoverRunner, RemoteTestResult, RemoteTestRunner, ParallelTestSuite


class TimedRemoteTestResult(RemoteTestResult):
    def startTest(self, test):
        self.testsRun += 1
        self.events.append(('startTest', self.test_index, time()))

    def addSuccess(self, test):
        self.events.append(('addSuccess', self.test_index, time()))


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


class TimedTestRunner(DiscoverRunner):
    test_runner = TimedTextTestRunner
    parallel_test_suite = TimedParallelTestSuite
