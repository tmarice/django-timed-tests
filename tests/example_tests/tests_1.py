import time

from django.test import TestCase


class DummyTestCase2(TestCase):
    def test_dummy_0(self):
        self.assertTrue(True)

    def test_dummy_1(self):
        self.assertTrue(True)
        time.sleep(1)

    def test_dummy_2(self):
        self.assertTrue(True)
        time.sleep(2)

    def test_dummy_3(self):
        self.assertTrue(True)
        time.sleep(3)


class DummyTestCase3(TestCase):
    def test_dummy_0(self):
        self.assertTrue(True)

    def test_dummy_1(self):
        self.assertTrue(True)
        time.sleep(1)

    def test_dummy_2(self):
        self.assertTrue(True)
        time.sleep(2)

    def test_dummy_3(self):
        self.assertTrue(True)
        time.sleep(3)
