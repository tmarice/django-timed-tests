build:
	python -m build

test_pypi_upload:
	python -m twine upload --repository testpypi dist/*

upload:
	python -m twine upload dist/*

clean:
	rm -rf __pycache__
	rm -rf dist
