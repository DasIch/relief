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


class unimethod(object):
    def __init__(self, function):
        self.function = function

        self.__name__ = function.__name__
        self.__module__ = function.__module__
        self.__doc__ = function.__doc__

    def __get__(self, instance, cls):
        return MethodWrapper(
            cls if instance is None else instance,
            self.function,
            (cls, instance)
        )


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


class inheritable_property(property):
    @unimethod
    def getter(cls, self, func):
        if self is None:
            return cls(fget=func)
        return super(inheritable_property, self).getter(func)

    @unimethod
    def setter(cls, self, func):
        if self is None:
            return cls(fset=func)
        return super(inheritable_property, self).setter(func)

    @unimethod
    def deleter(cls, self, func):
        if self is None:
            return cls(fdel=func)
        return super(inheritable_property, self).deleter(func)

    @property
    def __name__(self):
        if self.fget is not None:
            return self.fget.__name__
        if self.fset is not None:
            return self.fset.__name__
        if self.fdel is not None:
            return self.fdel.__name__
        assert False, "either one of fget, fset or fdel must be not None"

    def __get__(self, instance, cls):
        if instance is None:
            return self
        if self.fget is None:
            for superclass in cls.mro():
                if hasattr(superclass, self.__name__):
                    attribute = getattr(superclass, self.__name__)
                    if hasattr(attribute, "__get__"):
                        if attribute is self:
                            continue
                        return attribute.__get__(instance, cls)
                    return attribute
            raise AttributeError("unreadable attribute")
        return self.fget(instance)

    def __set__(self, instance, value):
        if self.fset is None:
            for superclass in instance.__class__.mro():
                if hasattr(superclass, self.__name__):
                    attribute = getattr(superclass, self.__name__)
                    if hasattr(attribute, "__set__"):
                        if attribute is self:
                            continue
                        return attribute.__set__(instance, value)
                    return attribute
            raise AttributeError("can't set attribute")
        return self.fset(instance, value)

    def __delete__(self, instance):
        if self.fdel is None:
            for superclass in instance.__class__.mro():
                if hasattr(superclass, self.__name__):
                    attribute = getattr(superclass, self.__name__)
                    if hasattr(attribute, "__delete__"):
                        if attribute is self:
                            continue
                        return attribute.__delete__(instance)
                    return attribute
            raise AttributeError("can't delete attribute")
        return self.fdel(instance)


def as_singleton(cls):
    return cls()
