#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys

from setuptools import setup, Command

__PATH__ = os.path.abspath(os.path.dirname(__file__))


def read_readme():
    with open("README.md") as f:
        return f.read()


def read_version():
    # importing dcustat causes an ImportError :-)
    __PATH__ = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(__PATH__, "dcustat/__init__.py")) as f:
        version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                                  f.read(), re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find __version__ string")


__version__ = read_version()
print(f"version: {__version__}")


# brought from https://github.com/kennethreitz/setup.py
class DeployCommand(Command):
    description = "Build and deploy the package to PyPI."
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    @staticmethod
    def status(s):
        print(s)

    def run(self):

        assert "dev" not in __version__, (
            "Only non-devel versions are allowed. "
            "__version__ == {}".format(__version__))

        with os.popen("git status --short") as fp:
            git_status = fp.read().strip()
            if git_status:
                print("Error: git repository is not clean.\n")
                os.system("git status --short")
                sys.exit(1)

        try:
            from shutil import rmtree
            self.status("Removing previous builds ...")
            rmtree(os.path.join(__PATH__, "dist"))
        except OSError:
            pass

        self.status("Building Source and Wheel (universal) distribution ...")
        os.system("{0} setup.py sdist".format(sys.executable))

        self.status("Uploading the package to PyPI via Twine ...")
        ret = os.system("twine upload dist/*")
        if ret != 0:
            sys.exit(ret)

        self.status("Creating git tags ...")
        os.system("git tag v{0}".format(__version__))
        os.system("git tag --list")
        sys.exit()


setup_requires = []

install_requires = [
    "six>=1.7",
    "blessed>=1.17.1",  # GH-126
]

setup(
    name="dcustat",
    version=__version__,
    license="MIT",
    description="An utility to monitor Hygon DCU status and usage",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/wmc1992/dcustat",
    author="wmc1992",
    author_email="m18810541081@163.com",
    keywords="dcu monitoring dcustat",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Topic :: System :: Monitoring",
    ],
    packages=["dcustat"],
    install_requires=install_requires,
    setup_requires=setup_requires,
    entry_points={
        "console_scripts": ["dcustat=dcustat:main"],
    },
    cmdclass={
        "deploy": DeployCommand,
    },
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.8",
)
