# coding: utf-8
"""
    tests.conftest
    ~~~~~~~~~~~~~~

    :copyright: 2013 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
import pytest


python2_only = pytest.mark.skipif("sys.version_info >= (3, 0)")
