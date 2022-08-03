# django-timed-tests
> What gets measured gets improved.

`django-timed-tests` produce the timing breakdown for your tests.

## Requirements
Python 3.6 through 3.10 supported.

Django 2.0 through 4.1 supported.

**`django-timed-tests` only works if you're using Django's testing framework.**

## Installation
Install using `pip`:
```
python -m pip install django-timed-tests
```

## Usage
Edit your `settings.py`:
```
INSTALLED_APPS = [
    ...
    django_timed_tests,
    ...
]

TEST_RUNNER = "django_timed_tests.TimedTestRunner"
```

`django-timed-tests` support the use of `--parallel`, `--debug-sql`, and `--pdb` flags.

### Regular report
The regular report shows **10** slowest **passing** tests that were run, ordered by descending duration.

The next time you run your tests using `manage.py test`, you'll see something like:

```
.............
----------------------------------------------------------------------
Ran 12 tests in 18.036s

OK
| Test                                       |   Duration (s) |
|--------------------------------------------|----------------|
| tests.examples.DummyTestCase1.test_dummy_3 |    3.0048      |
| tests.examples.DummyTestCase3.test_dummy_3 |    3.0041      |
| tests.examples.DummyTestCase2.test_dummy_3 |    3.00086     |
| tests.examples.DummyTestCase3.test_dummy_2 |    2.0052      |
| tests.examples.DummyTestCase1.test_dummy_2 |    2.00372     |
| tests.examples.DummyTestCase2.test_dummy_2 |    2.00194     |
| tests.examples.DummyTestCase3.test_dummy_1 |    1.0043      |
| tests.examples.DummyTestCase1.test_dummy_1 |    1.00235     |
| tests.examples.DummyTestCase2.test_dummy_1 |    1.00044     |
| tests.examples.DummyTestCase3.test_dummy_0 |    0.000109295 |
```

### Full report
Full report shows **all** passing tests, with a breakdown per module, test class, and test method.

When you run `manage.py test --full-report`, you'll see something like:
```
..............
----------------------------------------------------------------------
Ran 12 tests in 6.157s

OK
| Module         |   Duration (s) |
|----------------|----------------|
| tests.examples |        18.0088 |

| Class                         |   Duration (s) |
|-------------------------------|----------------|
| tests.examples.DummyTestCase1 |        6.00306 |
| tests.examples.DummyTestCase2 |        6.00299 |
| tests.examples.DummyTestCase3 |        6.00273 |

| Test                                       |   Duration (s) |
|--------------------------------------------|----------------|
| tests.examples.DummyTestCase2.test_dummy_3 |    3.00136     |
| tests.examples.DummyTestCase3.test_dummy_3 |    3.00136     |
| tests.examples.DummyTestCase1.test_dummy_3 |    3.00126     |
| tests.examples.DummyTestCase3.test_dummy_2 |    2.00039     |
| tests.examples.DummyTestCase1.test_dummy_2 |    2.00031     |
| tests.examples.DummyTestCase2.test_dummy_2 |    2.00026     |
| tests.examples.DummyTestCase1.test_dummy_1 |    1.00128     |
| tests.examples.DummyTestCase2.test_dummy_1 |    1.00112     |
| tests.examples.DummyTestCase3.test_dummy_1 |    1.0008      |
| tests.examples.DummyTestCase2.test_dummy_0 |    0.000246959 |
| tests.examples.DummyTestCase1.test_dummy_0 |    0.00022184  |
| tests.examples.DummyTestCase3.test_dummy_0 |    0.000178818 |
```

### Combining with your own test runner
`TimedTestRunner` tries to be minimally invasive, and integrating it into your custom test runner shouldn't be too complex.

If your custom runner just inherits from `DiscoverRunner`, without redefining `DiscoverRunner.test_runner`,  `DiscoverRunner.parallel_test_runner` and `DiscoverRunner.get_resultclass`, you should be fine with just inheriting `TimedTestRunner` and calling `super()` at the beginning of your overriden methods:

```
class MyOwnTestRunner(TimedTestRunner):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Do something else

    ...
```

If your test runner also uses custom `TestRunner` or `TestResult` classes, best course of action would be to inspect the `django_timed_tests.runner` module to see which classes should be inherited and which attributes and method should be overridden.
