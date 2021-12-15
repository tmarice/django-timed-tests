from time import time
from unittest import TextTestResult, TextTestRunner
from django.test.runner import DiscoverRunner


class TimedTextTestResult(TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._starts = {}
        self.durations = {}

    def startTest(self, test):
        self._starts[test] = time()

    def addSuccess(self, test):
        self.durations[test] = time() - self._starts[test]


class TimedTextTestRunner(TextTestRunner):
    resultclass = TimedTextTestResult


class TimedTestRunner(DiscoverRunner):
    test_runner = TimedTextTestRunner
