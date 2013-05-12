# coding: utf-8
"""
    relief._compat
    ~~~~~~~~~~~~~~

    :copyright: 2013 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
import sys
import inspect
from functools import wraps

import six


def add_native_itermethods(cls):
    def set_method(cls, name):
        iter_method = getattr(cls, name)
        if not six.PY3:
            setattr(cls, "iter" + name, iter_method)
            setattr(cls, "view" + name, iter_method)
            setattr(cls, name, lambda self: list(iter_method(self)))
    for name in ["keys", "values", "items"]:
        set_method(cls, name)
    return cls


class Prepareable(type):
    if not six.PY3:
        def __new__(cls, name, bases, attributes):
            try:
                constructor = attributes["__new__"]
            except KeyError:
                return super(Prepareable, cls).__new__(cls, name, bases, attributes)

            def preparing_constructor(cls, name, bases, attributes):
                try:
                    cls.__prepare__
                except AttributeError:
                    return constructor(cls, name, bases, attributes)
                namespace = cls.__prepare__.im_func(name, bases)
                defining_frame = sys._getframe(1)
                for constant in reversed(defining_frame.f_code.co_consts):
                    if inspect.iscode(constant) and constant.co_name == name:
                        def get_index(attribute_name, _names=constant.co_names):
                            try:
                                return _names.index(attribute_name)
                            except ValueError:
                                return 0
                        break
                by_appearance = sorted(
                    attributes.items(), key=lambda item: get_index(item[0])
                )
                for key, value in by_appearance:
                    namespace[key] = value
                return constructor(cls, name, bases, namespace)
            attributes["__new__"] = wraps(constructor)(preparing_constructor)
            return super(Prepareable, cls).__new__(cls, name, bases, attributes)
