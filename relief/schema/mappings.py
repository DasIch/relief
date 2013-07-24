# coding: utf-8
"""
    relief.schema.mappings
    ~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2013 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
import collections

from relief import Unspecified, NotUnserializable, Element, _compat
from relief.utils import class_cloner
from relief.schema.core import Container
from relief._compat import (
    add_native_itermethods, Prepareable, itervalues, iteritems, with_metaclass
)


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
        except (TypeError, ValueError):
            return NotUnserializable

    @property
    def value(self):
        if self._state is not None:
            return self._state
        result = self.native_type()
        for key, value in iteritems(self):
            if key.value is NotUnserializable or value.value is NotUnserializable:
                return NotUnserializable
            result[key.value] = value.value
        return result

    @value.setter
    def value(self, new_value):
        if new_value is not Unspecified:
            raise AttributeError("can't set attribute")

    def _set_value(self, value):
        super(Mapping, self).clear()
        if value is not Unspecified:
            if hasattr(self, "_raw_value"):
                del self._raw_value
            for key in value:
                super(Mapping, self).__setitem__(key, _Value(
                    self.member_schema[0](key),
                    self.member_schema[1](value[key])
                ))

    def __getitem__(self, key):
        return super(Mapping, self).__getitem__(key).value

    def __setitem__(self, key, value):
        raise TypeError(
            "%r object does not support item assignment" % self.__class__.__name__
        )

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
        for key, value in iteritems(self):
            self.is_valid &= key.validate(context)
            self.is_valid &= value.validate(context)
        self.is_valid &= super(Mapping, self).validate(context)
        return self.is_valid

    def traverse(self, prefix=None):
        for i, (key, value) in enumerate(iteritems(self)):
            if prefix is None:
                current_prefix = [i]
            else:
                current_prefix = prefix + [i]
            for child in key.traverse(current_prefix + [0]):
                yield child
            for child in value.traverse(current_prefix + [1]):
                yield child

    def __getattribute__(self, name):
        mutating_methods = set([
            'setdefault', 'popitem', 'pop', 'update', 'clear'
        ])
        if name in mutating_methods:
            raise AttributeError(name)
        return super(Mapping, self).__getattribute__(name)


class Dict(Mapping, dict):
    """
    Represents a :class:`dict`.

    :class:`Dict` maps homogenous keys to homogeneous values, in order to use
    it you have to derive a :class:`Dict` schema using :meth:`of` specifying
    the schemas used for keys and values:

    .. doctest::

       >>> from relief import Dict, Unicode, Integer
       >>> UnicodeIntegerDict = Dict.of(Unicode, Integer)

    The derived schema will behave like other container schemas, anything you
    can pass to :class:`dict` as positional argument can be used as a raw
    value.

    .. doctest::

       >>> element = UnicodeIntegerDict()
       >>> element.set({u"foo": 1})

    :class:`Dict` is a subclass of :class:`dict`, so all operations you can
    perform on a :class:`dict` you can also perform on a :class:`Dict`. Any
    operation that return objects stored within the dictionary will return the
    element not the value.
    """
    native_type = dict


class OrderedDict(Mapping, _compat.OrderedDict):
    """
    Represents a :class:`collections.OrderedDict`.

    See :class:`Dict` for more information.
    """
    native_type = _compat.OrderedDict

    def __init__(self, value=Unspecified):
        # The non-stdlib OrderedDict implementation we use for < 2.7 does weird
        # things in __init__ causing issues, so we don't call it. We do have to
        # call __init__ when we use the stdlib implementation because not
        # calling that does cause issues as well.
        if hasattr(collections, 'OrderedDict'):
            _compat.OrderedDict.__init__(self)
        Mapping.__init__(self, value=value)

    def __reversed__(self):
        for key in super(OrderedDict, self).__reversed__():
            yield super(_compat.OrderedDict, self).__getitem__(key).key


class FormMeta(collections.Mapping.__class__, with_metaclass(Prepareable, type)):
    def __new__(cls, cls_name, bases, attributes):
        member_schema = attributes["member_schema"] = _compat.OrderedDict()
        for base in reversed(bases):
            member_schema.update(getattr(base, "member_schema", {}) or {})
        for name, attribute in iteritems(attributes):
            if isinstance(attribute, type) and issubclass(attribute, Element):
                member_schema[name] = attribute
        return super(FormMeta, cls).__new__(cls, cls_name, bases, attributes)

    def __prepare__(name, bases, **kwargs):
        return _compat.OrderedDict()


@add_native_itermethods
class Form(with_metaclass(FormMeta, collections.Mapping, Container)):
    """
    Represents a :class:`dict` that maps a fixed set of keys to heterogeneous
    values.

    In order to use :class:`Form` you need to derive a :class:`Form` schema
    that knows what kind of keys it contains and what schemas corresponding to
    those keys are:

    .. doctest::

       >>> from relief import Form, Integer, Unicode
       >>> Something = Form.of({
       ...     "foo": Integer,
       ...     "bar": Unicode
       ... })

    `Something` is such a derived schema, defined to have to keys `foo` and
    `bar` with an integer and a unicode string as values.

    Instead of passing a :class:`dict` to :meth:`of` you can also use an
    :class:`collections.OrderedDict` this way you can enforce an order that
    will be respected during iteration over the form. It will have no effect on
    what is considered a valid value.

    Instead of using :meth:`of` to derive schemas :class:`Form` you can also
    subclass :class:`Form` and define the contents declaratively:

    .. doctest::

       >>> class Something(Form):
       ...     foo = Integer
       ...     bar = Unicode

    This is almost equivalent to the example using :meth:`of` above, the
    difference being that the order will be remembered, the same way as it
    would have been, if :class:`collections.OrderedDict` would have been used
    in the :meth:`of` example.

    Anything that can be passed as a positional argument to :class:`dict` can
    be used as a raw value::

       >>> element = Something()
       >>> element.set([("foo", 1), ("bar", u"spam")])
       >>> element.value
       OrderedDict([('foo', 1), ('bar', u'spam')])

    Unlike :class:`Dict` :class:`Form` is a subclass of
    :class:`collections.Mapping` but not of :class:`dict`. While you can set
    values using ``form[key] = value`` syntax, any operation that would remove
    keys defined by the schema or add keys not defined in the schema will fail
    with exceptions (excluding the use of :meth:`set`).
    """
    native_type = dict

    @class_cloner
    def of(cls, schema):
        cls.member_schema = _compat.OrderedDict(schema)
        return cls

    @classmethod
    def unserialize(cls, raw_value):
        raw_value = super(Form, cls).unserialize(raw_value)
        if raw_value is NotUnserializable:
            return raw_value
        if not isinstance(raw_value, dict):
            try:
                raw_value = dict(raw_value)
            except (TypeError, ValueError):
                return NotUnserializable
        if set(raw_value) != set(cls.member_schema):
            return NotUnserializable
        return raw_value

    def __new__(cls, *args, **kwargs):
        self = super(Form, cls).__new__(cls)
        self._elements = _compat.OrderedDict()
        for name, element_cls in iteritems(self.member_schema):
            self._elements[name] = element = element_cls()
            setattr(self, name, element)
        return self

    def __getitem__(self, key):
        return self._elements[key]

    def __len__(self):
        return len(self._elements)

    def __iter__(self):
        return iter(self._elements)

    @property
    def value(self):
        if self._state is not None:
            return self._state
        result = _compat.OrderedDict()
        for key, element in iteritems(self):
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
            for element in itervalues(self):
                element.set(value)
        else:
            for key, value in iteritems(value):
                self[key].set(value)

    def validate(self, context=None):
        if context is None:
            context = {}
        self.is_valid = True
        for element in itervalues(self):
            self.is_valid &= element.validate(context=context)
        self.is_valid &= super(Form, self).validate(context=context)
        return self.is_valid

    def traverse(self, prefix=None):
        if prefix is None:
            prefix = []
        for key, element in iteritems(self):
            yield prefix + [key], element
