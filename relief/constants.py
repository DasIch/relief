# coding: utf-8
"""
    relief.constants
    ~~~~~~~~~~~~~~~~

    :copyright: 2013 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
from relief.utils import as_singleton
from relief._compat import implements_bool


@as_singleton
@implements_bool
class Unspecified(object):
    """
    A constant that describes unspecified values.
    """
    def __bool__(self):
        return False

    def __str__(self):
        return u''

    def __repr__(self):
        return self.__class__.__name__


@as_singleton
@implements_bool
class NotUnserializable(object):
    """
    A constant that describes values that could not be unserialized.
    """
    def __bool__(self):
        return False

    def __str__(self):
        return u''

    def __repr__(self):
        return self.__class__.__name__
