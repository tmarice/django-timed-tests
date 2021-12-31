build:
	python -m build

test_pypi_upload:
	python -m twine upload --repository testpypi dist/*

upload:
	python -m twine upload dist/*

clean:
	rm -rf __pycache__
	rm -rf dist
	rm -rf src/django_timed_tests.egg-info
	rm -rf src/django_timed_tests/__pycache__
	python -m coverage erase

test:
	python -m runtests

coverage:
	pip install -e .
	python -m coverage erase
	python -m coverage run runtests.py
	python -m coverage combine
	python -m coverage report -m
