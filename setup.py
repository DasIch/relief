# coding: utf-8
import os
import sys
from setuptools import setup


PACKAGE_PATH = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), "relief"
)


if sys.version_info[:2] < (2, 7):
    install_requires = ['ordereddict>=1.1', 'Counter>=1.0.0']
else:
    install_requires = []


def get_version():
    path = os.path.join(PACKAGE_PATH, "__init__.py")
    with open(path) as f:
        for line in f:
            if line.startswith("__version__"):
                return line.split("=")[1].replace('"', '').strip()
        else:
            raise ValueError("__version__ not found in %s" % path)


setup(
    name="Relief",
    version=get_version(),
    author="Daniel Neuhäuser",
    author_email="ich@danielneuhaeuser.de",
    license="BSD",
    description="datastructure validation",
    packages=['relief', 'relief.schema', 'relief.utils'],
    install_requires=install_requires,
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Software Development :: Libraries"
    ]
)
