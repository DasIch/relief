# coding: utf-8
"""
    relief.schema.mappings
    ~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2013 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
import collections

from relief import Unspecified, NotUnserializable, Element
from relief._compat import add_native_itermethods, Prepareable
from relief.utils import class_cloner
from relief.schema.core import Container

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

    @classmethod
    def unserialize(cls, raw_value):
        raw_value = super(Mapping, cls).unserialize(raw_value)
        if raw_value is NotUnserializable:
            return raw_value
        try:
            return cls.native_type(raw_value)
        except TypeError:
            return NotUnserializable

    @property
    def value(self):
        if self._state is not None:
            return self._state
        result = self.native_type()
        for key, value in six.iteritems(self):
            if key.value is NotUnserializable or value.value is NotUnserializable:
                return NotUnserializable
            result[key.value] = value.value
        return result

    @value.setter
    def value(self, new_value):
        if new_value is not Unspecified:
            raise AttributeError("can't set attribute")

    def _set_value(self, value):
        self.clear()
        if value is not Unspecified:
            if hasattr(self, "_raw_value"):
                del self._raw_value
            self.update(value)

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

    :class:`Dict` maps homogenous keys to homogeneous values, in order to use
    it you have to derive a :class:`Dict` schema using :meth:`of` specifying
    the schemas used for keys and values:

    .. doctest::

       >>> from relief import Dict, Unicode, Integer
       >>> UnicodeIntegerDict = Dict.of(Unicode, Integer)

    The derived schema will behave like other container schemas, anything you
    can pass to :func:`dict` as positional argument can be used as a raw value.

    .. doctest::

       >>> element = UnicodeIntegerDict()
       >>> element.set({u"foo": 1})

    :class:`Dict` is a subclass of :func:`dict`, so all operations you can
    perform on a :func:`dict` you can also perform on a :class:`Dict`. Any
    operation that return objects stored within the dictionary will return the
    element not the value.
    """
    native_type = dict


class OrderedDict(MutableMapping, collections.OrderedDict):
    """
    Represents a :class:`collections.OrderedDict`.

    See :class:`Dict` for more information.
    """
    native_type = collections.OrderedDict

    def __init__(self, value=Unspecified):
        collections.OrderedDict.__init__(self)
        MutableMapping.__init__(self, value=value)

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


class FormMeta(collections.Mapping.__class__, six.with_metaclass(Prepareable, type)):
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
class Form(collections.Mapping, six.with_metaclass(FormMeta, Container)):
    """
    Represents a :func:`dict` that maps a fixed set of keys to heterogeneous
    values.

    In order to use :class:`Form`, you need to define the keys and the schema
    to which they map using :meth:`of`, which will return a new :class:`Form`
    class::

        Form.of({
            "foo": Integer,
            "bar": Unicode
        })

    You can also use a list of tuples or a :class:`~collections.OrderedDict` if
    you care about the order of the items.

    Alternatively you can also use the equivalent declarative syntax::

        class MyForm(Form):
            foo = Integer
            bar = Unicode

    The order of the elements will be preserved.

    Anything that can be coerced to a dictionary will be accepted as a raw
    value.
    """
    native_type = dict

    @class_cloner
    def of(cls, schema):
        cls.member_schema = collections.OrderedDict(schema)
        return cls

    @classmethod
    def unserialize(cls, raw_value):
        raw_value = super(Form, cls).unserialize(raw_value)
        if raw_value is NotUnserializable:
            return raw_value
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

    def __len__(self):
        return len(self._elements)

    def __iter__(self):
        return iter(self._elements)

    @property
    def value(self):
        if self._state is not None:
            return self._state
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

    def _set_value(self, value):
        if value is Unspecified:
            for element in six.itervalues(self):
                element.set(value)
        else:
            for key, value in six.iteritems(value):
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
