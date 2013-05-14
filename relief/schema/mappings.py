# coding: utf-8
"""
    relief.schema.mappings
    ~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2013 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
from relief import Unspecified, NotUnserializable
from relief._compat import add_native_itermethods
from relief.utils import class_cloner
from relief.schema.core import Container

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
    def __setitem__(self, key, value):
        super(Mapping, self).__setitem__(key, _Value(
            self.member_schema[0](key),
            self.member_schema[1](value)
        ))

    def setdefault(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            self[key] = default
            return self[key]

    def popitem(self):
        v = super(MutableMapping, self).popitem()[1]
        return v.key, v.value

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
    @classmethod
    def unserialize(cls, raw_value):
        try:
            return dict(raw_value)
        except TypeError:
            return NotUnserializable

    @property
    def value(self):
        if not isinstance(self.raw_value, dict):
            if self.raw_value is Unspecified:
                return Unspecified
            return NotUnserializable
        result = {}
        for key, value in six.iteritems(self):
            if key.value is NotUnserializable or value.value is NotUnserializable:
                return NotUnserializable
            result[key.value] = value.value
        return result

    def set(self, raw_value):
        self.raw_value = raw_value
        self.clear()
        if raw_value is not Unspecified:
            unserialized = self.unserialize(raw_value)
            if unserialized is not NotUnserializable:
                if hasattr(self, "_raw_value"):
                    del self._raw_value
                self.update(unserialized)

    def has_key(self, key):
        return key in self
