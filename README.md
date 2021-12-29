# django-timed-tests
> What gets measured gets improved.

`django-timed-tests` produce the timing breakdown for your tests.

## Requirements
Python 3.6 through 3.10 supported.

Django 2.0 through 4.0 supported.

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

`django-timed-tests` support the use of `--parallel` and `--debug-sql` flags.

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
