# coding: utf-8
"""
    relief._compat
    ~~~~~~~~~~~~~~

    :copyright: 2013 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
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
