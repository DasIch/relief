# coding: utf-8
"""
    relief.constants
    ~~~~~~~~~~~~~~~~

    :copyright: 2013 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
from relief.utils import as_singleton


@as_singleton
class Unspecified(object):
    """
    A constant that described unspecified values.
    """
    def __repr__(self):
        return self.__class__.__name__


@as_singleton
class NotUnserializable(object):
    """
    A constant that describes values that could not be unserialized.
    """
    def __repr__(self):
        return self.__class__.__name__
