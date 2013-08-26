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
try:
    from collections import Counter
except ImportError: # < 2.7
    from counter import Counter
try:
    from collections import OrderedDict
except ImportError: # < 2.7
    from ordereddict import OrderedDict


PY2 = sys.version_info[0] == 2


if PY2:
    def itervalues(d):
        return d.itervalues()

    def iteritems(d):
        return d.iteritems()

    text_type = unicode

    class Prepareable(type):
        def __new__(cls, name, bases, attributes):
            try:
                constructor = attributes["__new__"]
            except KeyError:
                return super(Prepareable, cls).__new__(
                    cls, name, bases, attributes
                )

            def preparing_constructor(cls, name, bases, attributes):
                try:
                    cls.__prepare__
                except AttributeError:
                    return constructor(cls, name, bases, attributes)
                namespace = cls.__prepare__.im_func(name, bases)
                defining_frame = sys._getframe(1)
                for constant in reversed(defining_frame.f_code.co_consts):
                    if inspect.iscode(constant) and constant.co_name == name:
                        def get_index(name, _index=constant.co_names.index):
                            try:
                                return _index(name)
                            except ValueError:
                                return 0
                        assert get_index # silence pyflakes
                        break
                else:
                    # If a subclass is created dynamically we won't find a code
                    # object and there is no attribute order to recover.
                    def get_index(attribute_name):
                        return 0
                by_appearance = sorted(
                    attributes.items(), key=lambda item: get_index(item[0])
                )
                for key, value in by_appearance:
                    namespace[key] = value
                return constructor(cls, name, bases, namespace)
            attributes["__new__"] = wraps(constructor)(preparing_constructor)
            return super(Prepareable, cls).__new__(
                cls, name, bases, attributes
            )
else:
    def itervalues(d):
        return iter(d.values())

    def iteritems(d):
        return iter(d.items())

    text_type = str

    Prepareable = type


def add_native_itermethods(cls):
    def set_method(cls, name):
        iter_method = getattr(cls, name)
        if PY2:
            setattr(cls, "iter" + name, iter_method)
            setattr(cls, "view" + name, iter_method)
            setattr(cls, name, lambda self: list(iter_method(self)))
    for name in ["keys", "values", "items"]:
        set_method(cls, name)
    return cls


def with_metaclass(meta, *bases):
    return meta("NewBase", bases, {})


def implements_bool(cls):
    if PY2:
        cls.__nonzero__ = cls.__bool__
    return cls


__all__ = [
    'Counter', 'OrderedDict', 'itervalues', 'iteritems', 'text_type',
    'Prepareable', 'add_native_itermethods', 'with_metaclass',
    'implements_bool'
]
