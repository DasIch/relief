# coding: utf-8
"""
    relief.utils
    ~~~~~~~~~~~~

    :copyright: 2013 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
import sys
from functools import partial


class class_cloner(object):
    """
    Like :class:`classmethod` but calls the method with a clone of the class.
    """
    def __init__(self, function):
        self.function = function

        self.__name__ = function.__name__
        self.__module__ = function.__module__
        self.__doc__ = function.__doc__

    def __get__(self, instance, cls):
        attributes = {
            "__doc__": getattr(cls, "__doc__", None),
            # module name in the scope of the caller
            "__module__": sys._getframe(1).f_globals["__name__"]
        }
        clone = type(cls.__name__, (cls, ), attributes)
        return MethodWrapper(cls, self.function, (clone, ))


class MethodWrapper(object):
    def __init__(self, im_self, function, args=None, kwargs=None):
        self.im_self = im_self
        self.im_func = function
        self._method = partial(
            self.im_func,
            *(() if args is None else args),
            **({} if kwargs is None else kwargs)
        )

    @property
    def __name__(self):
        return self.im_func.__name__

    @property
    def __module__(self):
        return self.im_func.__module__

    @property
    def __doc__(self):
        return self.im_func.__doc__

    @property
    def im_class(self):
        return self.im_self.__class__

    def __call__(self, *args, **kwargs):
        return self._method(*args, **kwargs)


def as_singleton(cls):
    return cls()
