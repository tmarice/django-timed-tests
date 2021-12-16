from time import sleep
from django.test import TestCase

class DummyTestCase(TestCase):
    def test_dummy_1(self):
        self.assertTrue(True)
        sleep(1)

    def test_dummy_2(self):
        self.assertTrue(True)
        sleep(2)

    def test_dummy_3(self):
        self.assertTrue(True)
        sleep(3)
