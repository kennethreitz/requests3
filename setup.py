#!/usr/bin/env python
# Learn more: https://github.com/kennethreitz/setup.py
import os
import sys

from codecs import open

from setuptools import setup, Command
from setuptools.command.test import test as TestCommand

here = os.path.abspath(os.path.dirname(__file__))


class Format(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        os.system("black requests3")


class PyTest(Command):
    user_options = [("pytest-args=", "a", "Arguments to pass into py.test")]

    def initialize_options(self):
        pass

    def finalize_options(self):
        # Command.finalize_options(self)
        pass

    def run(self):
        import pytest

        errno = pytest.main(["-n", "auto"])
        # errno = pytest.main([])

        sys.exit(errno)


class MyPyTest(Command):
    user_options = [("pytest-args=", "a", "Arguments to pass into py.test")]

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run_tests(self):
        import pytest

        errno = pytest.main(["-n", "auto", "--mypy", "tests"])
        sys.exit(errno)


# 'setup.py publish' shortcut.
if sys.argv[-1] == "publish":
    os.system("python setup.py sdist bdist_wheel")
    os.system("twine upload dist/*")
    sys.exit()
packages = ["requests3"]
requires = ["chardet>=3.0.2,<3.1.0", "idna>=2.5,<2.9", "certifi>=2017.4.17"]
test_requirements = [
    "pytest-httpbin==0.0.7",
    "pytest-cov",
    "pytest-mock",
    "pytest-xdist",
    "PySocks>=1.5.6, !=1.5.7",
    "pytest>=2.8.0",
]

about = {}
with open(os.path.join(here, "requests3", "__version__.py"), "r", "utf-8") as f:
    exec(f.read(), about)

with open("README.md", "r", "utf-8") as f:
    readme = f.read()
with open("HISTORY.md", "r", "utf-8") as f:
    history = f.read()
setup(
    name=about["__title__"],
    version=about["__version__"],
    description=about["__description__"],
    long_description=readme,
    long_description_content_type="text/markdown",
    author=about["__author__"],
    author_email=about["__author_email__"],
    url=about["__url__"],
    packages=packages,
    package_data={"": ["LICENSE", "NOTICE"], "requests": ["*.pem"]},
    package_dir={"requests3": "requests3"},
    include_package_data=True,
    python_requires=">=3.6",
    install_requires=requires,
    license=about["__license__"],
    zip_safe=False,
    classifiers=[
        # "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
    cmdclass={"test": PyTest, "mypy": MyPyTest, "format": Format},
    tests_require=test_requirements,
    extras_require={
        "security": ["pyOpenSSL >= 0.14", "cryptography>=1.3.4", "idna>=2.0.0"],
        "socks": ["PySocks>=1.5.6, !=1.5.7"],
        'socks:sys_platform == "win32" and python_version == "2.7"': ["win_inet_pton"],
    },
)
