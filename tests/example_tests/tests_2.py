from time import sleep

from django.test import TestCase


class DummyTestCase1(TestCase):
    def test_dummy_0(self):
        self.assertTrue(True)

    def test_dummy_1(self):
        self.assertTrue(True)
        sleep(1)

    def test_dummy_2(self):
        self.assertTrue(True)
        sleep(2)

    def test_dummy_3(self):
        self.assertTrue(True)
        sleep(3)
