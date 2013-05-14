# coding: utf-8
from setuptools import setup

from relief import __version__


setup(
    name="Relief",
    version=__version__,
    author="Daniel Neuhäuser",
    author_email="ich@danielneuhaeuser.de",
    license="BSD",
    description="datastructure validation",
    install_requires=["six"],
    packages=["relief", "relief.schema", "relief.tests", "relief.tests.schema"],
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Software Development :: Libraries"
    ]
)
