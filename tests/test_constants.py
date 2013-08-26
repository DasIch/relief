# coding: utf-8
"""
    tests.test_constants
    ~~~~~~~~~~~~~~~~~~~~

    :copyright: 2013 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
from relief import Unspecified, NotUnserializable


class TestUnspecified(object):
    def test_bool(self):
        assert not Unspecified

    def test_repr(self):
        assert repr(Unspecified) == 'Unspecified'


class TestNotUnserializable(object):
    def test_bool(self):
        assert not NotUnserializable

    def test_repr(self):
        assert repr(NotUnserializable) == 'NotUnserializable'
