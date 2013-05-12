# coding: utf-8
"""
    relief.schema.mappings
    ~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2013 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
import sys

from relief._compat import add_native_itermethods
from relief.utils import class_cloner, inheritable_property
from relief.constants import Unspecified, NotUnserializable
from relief.schema.core import Container, specifiying

import six


class _Value(object):
    def __init__(self, key, value):
        self.key = key
        self.value = value


@add_native_itermethods
class Mapping(Container):
    @class_cloner
    def of(cls, key_schema, value_schema):
        cls.member_schema = (key_schema, value_schema)
        return cls

    def __getitem__(self, key):
        return super(Mapping, self).__getitem__(key).value

    def get(self, key, default=None):
        try:
            return self.__getitem__(key)
        except KeyError:
            return self.member_schema[1](default)

    def __iter__(self):
        for key in super(Mapping, self).__iter__():
            yield super(Mapping, self).__getitem__(key).key

    def keys(self):
        return iter(self)

    def values(self):
        return (self[key.value] for key in self)

    def items(self):
        return ((key, self[key.value]) for key in self)

    def validate(self, context=None):
        if context is None:
            context = {}
        self.is_valid = True
        for key, value in six.iteritems(self):
            self.is_valid &= key.validate(context)
            self.is_valid &= value.validate(context)
        self.is_valid &= super(Mapping, self).validate(context)
        return self.is_valid

    def traverse(self, prefix=None):
        for i, (key, value) in enumerate(six.iteritems(self)):
            if prefix is None:
                current_prefix = [i]
            else:
                current_prefix = prefix + [i]
            for child in key.traverse(current_prefix + [0]):
                yield child
            for child in value.traverse(current_prefix + [1]):
                yield child


class MutableMapping(Mapping):
    @specifiying
    def __setitem__(self, key, value):
        super(Mapping, self).__setitem__(key, _Value(
            self.member_schema[0](key),
            self.member_schema[1](value)
        ))

    @specifiying
    def setdefault(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            self[key] = default
            return self[key]

    @specifiying
    def popitem(self):
        v = super(MutableMapping, self).popitem()[1]
        return v.key, v.value

    @specifiying
    def pop(self, key, *args):
        if len(args) > 1:
            raise TypeError(
                "pop expected at most 2 arguments, got %d" % (len(args) + 1)
            )
        try:
            value = super(MutableMapping, self).pop(key).value
        except KeyError:
            if args:
                value = self.member_schema[1](args[0])
            else:
                raise
        return value

    @specifiying
    def update(self, *args, **kwargs):
        if len(args) > 1:
            raise TypeError(
                "update expected at most 1 argument, got %d" % len(args)
            )
        mappings = []
        if args:
            if hasattr(args[0], "keys"):
                mappings.append((key, args[0][key]) for key in args[0])
            else:
                mappings.append(args[0])
        mappings.append(six.iteritems(kwargs))
        for mapping in mappings:
            for key, value in mapping:
                self[key] = value


class Dict(MutableMapping, dict):
    def __init__(self, *args, **kwargs):
        super(MutableMapping, self).__init__()
        self.state = Unspecified
        if args or kwargs:
            self.update(*args, **kwargs)

    @inheritable_property
    def value(self):
        if self.state is not None:
            return self.state
        return {key.value: v.value for key, v in six.iteritems(self)}

    def set_value(self, new_value, propagate=True):
        if new_value is Unspecified:
            del self.value
        elif new_value is NotUnserializable:
            self.state = NotUnserializable
        else:
            self.state = None
            self.clear()
            self.update(new_value)
        if propagate:
            self.set_raw_value(self.serialize(new_value), propagate=False)

    @value.deleter
    def value(self):
        self.clear()
        self._raw_value = Unspecified
        self.state = Unspecified

    def has_key(self, key):
        return key in self

    @classmethod
    def serialize(cls, values):
        if values is Unspecified:
            return values
        return dict(
            (cls.member_schema[0].serialize(key), cls.member_schema[1].serialize(value))
            for key, value in values.iteritems()
        )

    @classmethod
    def unserialize(cls, raw_value):
        if not isinstance(raw_value, dict):
            try:
                raw_values = dict(raw_value)
            except TypeError:
                return NotUnserializable
        result = {}
        for key, value in six.iteritems(raw_value):
            serialized_key = cls.member_schema[0].unserialize(key)
            if serialized_key is NotUnserializable:
                return NotUnserializable
            serialized_value = cls.member_schema[1].unserialize(value)
            if serialized_value is NotUnserializable:
                return NotUnserializable
            result[serialized_key] = serialized_value
        return result
