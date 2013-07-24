# coding: utf-8
import os
import sys
from setuptools import setup

from relief import __version__


PACKAGE_PATH = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), "relief"
)


if sys.version_info[:2] < (2, 7):
    install_requires = ['ordereddict>=1.1', 'Counter>=1.0.0']
else:
    install_requires = []


setup(
    name="Relief",
    version=__version__,
    author="Daniel Neuhäuser",
    author_email="ich@danielneuhaeuser.de",
    license="BSD",
    description="datastructure validation",
    packages=['relief', 'relief.schema'],
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
