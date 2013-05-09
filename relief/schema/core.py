# coding: utf-8
"""
    relief.schema.core
    ~~~~~~~~~~~~~~~~~~~

    :copyright: 2013 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
from functools import wraps

from relief.utils import class_cloner
from relief.constants import Unspecified, NotUnserializable

import six


def specifiying(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        result = method(self, *args, **kwargs)
        self.state = None
        return result
    return wrapper


class Element(object):
    default = Unspecified
    default_factory = Unspecified
    validators = []

    @class_cloner
    def using(cls, **kwargs):
        for key, value in six.iteritems(kwargs):
            if not hasattr(cls, key):
                raise TypeError("unexpected keyword argument %r" % key)
            setattr(cls, key, value)
        return cls

    @classmethod
    def validated_by(cls, validators):
        return cls.using(validators=cls.validators + validators)

    @classmethod
    def from_raw_value(cls, raw_value):
        self = cls()
        self.raw_value = raw_value
        return self

    def __init__(self, value=Unspecified):
        self.value = value

        self.is_valid = None
        self.raw_value = Unspecified
        self.errors = []

    @property
    def value(self):
        if self._value is not Unspecified:
            return self._value
        if self.default is not Unspecified:
            return self.default
        if self.default_factory is not Unspecified:
            return self.default_factory()
        return Unspecified

    def set_value(self, value, propagate=True):
        self._value = value
        if propagate:
            self.set_raw_value(self.serialize(value), propagate=False)

    @value.setter
    def value(self, new_value):
        self.set_value(new_value)

    @value.deleter
    def value(self):
        self._value = self._raw_value = Unspecified

    @property
    def raw_value(self):
        if self._raw_value is not Unspecified:
            return self._raw_value
        return Unspecified

    def set_raw_value(self, raw_value, propagate=True):
        self._raw_value = raw_value
        if propagate:
            self.set_value(
                raw_value if raw_value is Unspecified else self.unserialize(raw_value),
                propagate=False
            )

    @raw_value.setter
    def raw_value(self, new_raw_value):
        self.set_raw_value(new_raw_value)

    @raw_value.deleter
    def raw_value(self):
        self._raw_value = self._value = Unspecified

    @property
    def state(self):
        missing = object()
        if getattr(self, "_state", missing) is not missing:
            return self._state
        if self.value is Unspecified or self.value is NotUnserializable:
            return self.value

    @state.setter
    def state(self, new_state):
        self._state = new_state

    @state.deleter
    def state(self):
        if hasattr(self, "_state"):
            del self._state

    @classmethod
    def serialize(cls, value):
        return value

    @classmethod
    def unserialize(cls, raw_value):
        return raw_value

    def validate(self, context=None):
        if context is None:
            context = {}
        if self.validators:
            self.is_valid = all(
                validator(self, context) for validator in self.validators
            )
        else:
            self.is_valid = self.state is None
        return self.is_valid

    def traverse(self, prefix=None):
        yield prefix, self


class Container(Element):
    member_schema = None

    @class_cloner
    def of(cls, schema):
        cls.member_schema = schema
        return cls

    def __init__(self, value=Unspecified):
        super(Container, self).__init__(value)
        if self.member_schema is None:
            raise TypeError("member_schema is unknown")
