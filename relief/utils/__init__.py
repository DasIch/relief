# coding: utf-8
"""
    relief.utils
    ~~~~~~~~~~~~

    :copyright: 2013 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
import sys


class class_cloner(classmethod):
    """
    Like :class:`classmethod` but calls the method with a clone of the class.
    """
    def __get__(self, instance, cls):
        attributes = {
            "__doc__": getattr(cls, "__doc__", None),
            # module name in the scope of the caller
            "__module__": sys._getframe(1).f_globals.get("__name__", "__main__")
        }
        clone = cls.__class__(cls.__name__, (cls, ), attributes)
        return super(class_cloner, self).__get__(instance, clone)


def as_singleton(cls):
    return cls()
