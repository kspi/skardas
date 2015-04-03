#!/usr/bin/env python3
from setuptools import setup
import sys
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


def readme():
    with open("README.rst", "r") as f:
        return f.read()


setup(
    name="skardas",
    version="0.1",
    description="Measure frequency response with a sweep.",
    long_description=readme(),
    author="Kiprianas Spiridonovas",
    author_email="k.spiridonovas@gmail.com",
    url="https://github.com/kspi/skardas",
    license="GPL3",
    packages=['skardas'],
    scripts=["bin/skardas"],
    
    install_requires=[
        "python-usbtmc",
        "pyusb",
        "matplotlib",
        "blist",
    ],

    tests_require=[
        "pytest",
    ],
    cmdclass={'test': PyTest},
)
