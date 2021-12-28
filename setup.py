from pathlib import Path

from setuptools import find_packages, setup

NAME = "django-timed-tests"
DESCRIPTION = "Get timing breakdown of your Django test suite"
VERSION = "0.1.0"
URL = "https://github.com/tmarice/django-timed-tests"
AUTHOR = "Tomislav Maricevic"
AUTHOR_EMAIL = "django_timed_tests@sorting.me"

HERE = Path(__file__).parent
README_TEXT = (HERE / "README.md").read_text()

PYTHON_REQUIRES = ">=3.6"
INSTALL_REQUIRES = ["Django>=2.0", "tabulate"]

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=README_TEXT,
    long_description_content_type="text/markdown",
    url=URL,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    include_package_data=True,
    python_requires=PYTHON_REQUIRES,
    install_requires=INSTALL_REQUIRES,
)
