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

    def _set_value_from_native(self, value):
        super(Mapping, self).clear()
        if value is not Unspecified:
            if hasattr(self, "_raw_value"):
                del self._raw_value
            for key in value:
                super(Mapping, self).__setitem__(key, _Value(
                    self.member_schema[0](key),
                    self.member_schema[1](value[key])
                ))

    def _set_value_from_raw(self, value):
        super(Mapping, self).clear()
        if value is not Unspecified:
            if hasattr(self, "_raw_value"):
                del self._raw_value
            for key in value:
                super(Mapping, self).__setitem__(key, _Value(
                    self.member_schema[0](key),
                    self.member_schema[1](value[key])
                ))

    def unserialize(self, raw_value):
        raw_value = super(Mapping, self).unserialize(raw_value)
        if raw_value is NotUnserializable:
            return raw_value
        try:
            return self.native_type(raw_value)
        except (TypeError, ValueError):
            return NotUnserializable

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
       >>> element.set_from_raw({u"foo": 1})

    :class:`Dict` is a subclass of :class:`dict`, so all non-mutating
    operations you can perform on a :class:`dict` you can also perform on a
    :class:`Dict`. Any operation that return objects stored within the
    dictionary will return the element not the value.
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
       >>> element.set_from_raw([("foo", 1), ("bar", u"spam")])
       >>> element.value
       OrderedDict([('foo', 1), ('bar', u'spam')])

    It is quite common to have very specific validation requirements for values
    in forms. In order to conveniently handle this case, you can add methods
    with names like `validate_{key}` where `key` is the key under which the
    value is reachable::

        class Something(Form):
            foo = Integer

            def validate_foo(self, element, context):
                # Perform validation on `foo` value.
                ...

    .. versionadded:: 0.2
       Added the ability to validate values with `validate_{key}` methods.
    """
    native_type = dict

    @class_cloner
    def of(cls, schema):
        cls.member_schema = _compat.OrderedDict(schema)
        return cls

    def __new__(cls, *args, **kwargs):
        self = super(Form, cls).__new__(cls)
        for attribute_name in dir(self):
            if not attribute_name.startswith('validate_'):
                continue
            attribute = getattr(self, attribute_name)
            member_name = attribute_name[len('validate_'):]
            member = self.member_schema[member_name]
            self.member_schema[member_name] = member.validated_by([attribute])

        self._elements = _compat.OrderedDict()
        for name, element_cls in iteritems(self.member_schema):
            self._elements[name] = element = element_cls()
            setattr(self, name, element)

        return self

    def _set_default_value(self):
        if self.default is not Unspecified:
            self.set_from_native(self.default)
        elif self.default_factory is not Unspecified:
            self.set_from_native(self.default_factory())
        else:
            self._state = None
            for key, value in iteritems(self):
                value._set_default_value()

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

    def _set_value_from_native(self, value):
        if value is Unspecified:
            for element in itervalues(self):
                element.set_from_native(value)
        else:
            for key, value in iteritems(value):
                self[key].set_from_native(value)

    def _set_value_from_raw(self, value):
        if value is Unspecified:
            for element in itervalues(self):
                element.set_from_raw(value)
        else:
            for key, value in iteritems(value):
                self[key].set_from_raw(value)

    def unserialize(self, raw_value):
        raw_value = super(Form, self).unserialize(raw_value)
        if raw_value is NotUnserializable:
            return raw_value
        if not isinstance(raw_value, dict):
            try:
                raw_value = dict(raw_value)
            except (TypeError, ValueError):
                return NotUnserializable
        if set(raw_value) != set(self.member_schema):
            return NotUnserializable
        return raw_value

    def validate(self, context=None):
        if context is None:
            context = {}
        self.is_valid = True
        for element in itervalues(self):
            self.is_valid &= element.validate(context=context)
        self.is_valid &= super(Form, self).validate(context=context)
        return self.is_valid
