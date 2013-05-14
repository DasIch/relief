# coding: utf-8
"""
    relief.schema.mappings
    ~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2013 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
import collections

from relief import Unspecified, NotUnserializable
from relief._compat import add_native_itermethods, Prepareable
from relief.utils import class_cloner
from relief.schema.core import Container, Element

import six


class _Value(object):
    __slots__ = ["key", "value"]

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
    """
    Represents a :func:`dict`.

    In order to use :class:`Dict`, you need to define the element type for keys
    and values using :meth:`of`, which will return a new :class:`Dict` class::

        Dict.of(Unicode, Integer)

    would be a :class:`Dict` whose keys are :class:`~relief.Unicode` strings
    and whose values are :class:`~relief.Integer`.

    Anything that can be coerced to a dictionary will be accepted as a raw
    value.
    """
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

    @value.setter
    def value(self, new_value):
        if new_value is not Unspecified:
            raise AttributeError("can't set attribute")

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


class OrderedDict(MutableMapping, collections.OrderedDict):
    """
    Represents a :class:`collections.OrderedDict`.

    See :class:`Dict` for more information.
    """
    @classmethod
    def unserialize(cls, raw_value):
        try:
            return collections.OrderedDict(raw_value)
        except TypeError:
            return NotUnserializable

    def __init__(self, value=Unspecified):
        collections.OrderedDict.__init__(self)
        MutableMapping.__init__(self, value=value)

    @property
    def value(self):
        if not isinstance(self.raw_value, dict):
            if self.raw_value is Unspecified:
                return Unspecified
            return NotUnserializable
        result = collections.OrderedDict()
        for key, value in six.iteritems(self):
            if key.value is NotUnserializable or value.value is NotUnserializable:
                return NotUnserializable
            result[key.value] = value.value
        return result

    @value.setter
    def value(self, new_value):
        if new_value is not Unspecified:
            raise AttributeError("can't set attribute")

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

    def __reversed__(self):
        for key in super(OrderedDict, self).__reversed__():
            yield super(collections.OrderedDict, self).__getitem__(key).key

    def popitem(self, last=True):
        if not self:
            raise KeyError("dictionary is empty")
        key = next(reversed(self) if last else iter(self))
        value = self.pop(key.value)
        return key, value

    __missing = object()
    def pop(self, key, default=__missing):
        if key in self:
            value = self[key]
            del self[key]
            return value
        if default is self.__missing:
            raise KeyError(key)
        return self.member_schema[1](default)


class FormMeta(six.with_metaclass(Prepareable, type)):
    def __new__(cls, cls_name, bases, attributes):
        member_schema = attributes["member_schema"] = collections.OrderedDict()
        for base in reversed(bases):
            member_schema.update(getattr(base, "member_schema", {}) or {})
        for name, attribute in six.iteritems(attributes):
            if isinstance(attribute, type) and issubclass(attribute, Element):
                member_schema[name] = attribute
        return super(FormMeta, cls).__new__(cls, cls_name, bases, attributes)

    def __prepare__(name, bases, **kwargs):
        return collections.OrderedDict()


@add_native_itermethods
class Form(six.with_metaclass(FormMeta, Container)):
    @class_cloner
    def of(cls, schema):
        cls.member_schema = collections.OrderedDict(schema)
        return cls

    @classmethod
    def unserialize(cls, raw_value):
        if not isinstance(raw_value, dict):
            try:
                raw_value = dict(raw_value)
            except TypeError:
                return NotUnserializable
        if set(raw_value) != set(cls.member_schema):
            return NotUnserializable
        return raw_value

    def __new__(cls, *args, **kwargs):
        self = super(Form, cls).__new__(cls)
        self._elements = collections.OrderedDict(
            (name, element())
            for name, element in six.iteritems(self.member_schema)
        )
        return self

    def __getitem__(self, key):
        return self._elements[key]

    def __setitem__(self, key, value):
        if key not in self:
            raise KeyError(key)
        self._elements[key].set(value)

    def __contains__(self, key):
        return key in self._elements

    def __len__(self):
        return len(self._elements)

    def __iter__(self):
        return iter(self._elements)

    def keys(self):
        return six.iterkeys(self._elements)

    def values(self):
        return six.itervalues(self._elements)

    def items(self):
        return six.iteritems(self._elements)

    @property
    def value(self):
        if not isinstance(self.raw_value, dict):
            if self.raw_value is Unspecified:
                return Unspecified
            return NotUnserializable
        if set(self.raw_value) != set(self):
            return NotUnserializable
        result = collections.OrderedDict()
        for key, element in six.iteritems(self):
            if element.value is Unspecified:
                return NotUnserializable
            result[key] = element.value
        return result

    @value.setter
    def value(self, new_value):
        if new_value is not Unspecified:
            raise AttributeError("can't set attribute")

    def set(self, raw_value):
        self.raw_value = raw_value
        if raw_value is Unspecified:
            for element in six.itervalues(self):
                element.set(raw_value)
        else:
            unserialized = self.unserialize(raw_value)
            if unserialized is not NotUnserializable:
                for key, value in six.iteritems(unserialized):
                    self[key].set(value)

    def validate(self, context=None):
        if context is None:
            context = {}
        self.is_valid = True
        for element in six.itervalues(self):
            self.is_valid &= element.validate(context=context)
        self.is_valid &= super(Form, self).validate(context=context)
        return self.is_valid

    def traverse(self, prefix=None):
        if prefix is None:
            prefix = []
        for key, element in six.iteritems(self):
            yield prefix + [key], element
