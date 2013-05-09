# coding: utf-8
"""
    relief.schema.sequences
    ~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2013 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
from itertools import repeat

from relief.utils import class_cloner, inheritable_property
from relief.constants import Unspecified, NotUnserializable
from relief.schema.core import Container, specifiying


class Sequence(Container):
    def __init__(self, value=Unspecified):
        super(Sequence, self).__init__()
        if value is not Unspecified:
            self.value = value
        else:
            self.state = Unspecified

    def __contains__(self, value):
        return any(element.value == value for element in self)

    def index(self, value, start=None, stop=None):
        for i, element in enumerate(self[start:stop], start or 0):
            if element.value == value:
                return i
        raise ValueError("%r not in %s" % (value, self.__class__.__name__))

    def count(self, value):
        return sum(element.value == value for element in self)

    def validate(self, context=None):
        if context is None:
            context = {}
        self.is_valid = True
        for element in self:
            self.is_valid &= element.validate(context)
        self.is_valid &= super(Sequence, self).validate(context)
        return self.is_valid

    def traverse(self, prefix=None):
        for i, element in enumerate(self):
            if prefix is None:
                yield i, element
            else:
                yield prefix + [i], element


class Tuple(Sequence, tuple):
    @class_cloner
    def of(cls, *schemas):
        cls.member_schema = schemas
        return cls

    def __new__(cls, *args, **kwargs):
        if cls.member_schema is None:
            raise TypeError("member_schema is None")
        return super(Tuple, cls).__new__(
            cls,
            (schema() for schema in cls.member_schema)
        )

    @inheritable_property
    def state(self):
        missing = object()
        if getattr(self, "_state", missing) is not missing:
            return self._state
        elif len(self) != len(self.raw_value):
            return NotUnserializable

    @inheritable_property
    def value(self):
        if self.state is not None:
            return self.state
        result = []
        for element in self:
            if element.value is NotUnserializable:
                return NotUnserializable
            result.append(element.value)
        return tuple(result)

    def set_value(self, new_values, propagate=True):
        if new_values is Unspecified:
            del self.value
        elif new_values is NotUnserializable:
            del self.state
        else:
            self.state = None
            if len(new_values) != len(self):
                raise TypeError("requires iterable of length %d" % len(self))
            for element, new_value in zip(self, new_values):
                element.set_value(new_value, propagate=propagate)
        if propagate:
            self.set_raw_value(self.serialize(new_values), propagate=False)

    @value.deleter
    def value(self):
        for element in self:
            del element.value
        self.state = Unspecified

    @inheritable_property
    def raw_value(self):
        if getattr(self, "_raw_value", None) is not None:
            result = list(self._raw_value)
            for i, element in enumerate(self):
                if i >= len(result):
                    if element.raw_value is not Unspecified:
                        result.append(element.raw_value)
                elif result[i] != element.raw_value:
                    result[i] = element.raw_value
            return tuple(result)
        return tuple(element.raw_value for element in self)

    def set_raw_value(self, raw_values, propagate=True):
        if raw_values is Unspecified:
            del self.raw_value
        else:
            if len(raw_values) != len(self):
                self._raw_value = raw_values
            for element, raw_value in zip(self, raw_values):
                element.set_raw_value(raw_value, propagate=propagate)
        if propagate:
            self.set_value(
                raw_values if raw_values is Unspecified else self.unserialize(raw_values),
                propagate=False
            )

    @raw_value.deleter
    def raw_value(self):
        if hasattr(self, "_raw_value"):
            del self._raw_value
        for element in self:
            del element.raw_value

    @classmethod
    def unserialize(cls, raw_values):
        if len(raw_values) != len(cls.member_schema):
            return NotUnserializable
        return tuple(
            schema.unserialize(raw_value)
            for schema, raw_value in zip(cls.member_schema, raw_values)
        )

    @classmethod
    def serialize(cls, values):
        if values is Unspecified:
            return values
        return tuple(
            schema.serialize(value)
            for schema, value in zip(cls.member_schema, values)
        )


class MutableSequence(Sequence):
    @specifiying
    def __setitem__(self, key, value):
        if isinstance(key, slice):
            value = map(self.member_schema, value)
        super(MutableSequence, self).__setitem__(key, value)

    def __setslice__(self, start, stop, values):
        self.__setitem__(slice(start, stop), values)

    @specifiying
    def append(self, value):
        super(MutableSequence, self).append(self.member_schema(value))

    @specifiying
    def extend(self, value):
        super(MutableSequence, self).extend(map(self.member_schema, value))

    @specifiying
    def insert(self, index, value):
        self[index:index] = [value]

    @specifiying
    def pop(self, index=None):
        if index is None:
            index = len(self) - 1
        value = self[index]
        del self[index]
        return value

    @specifiying
    def remove(self, value):
        del self[self.index(value)]


class List(MutableSequence, list):
    @inheritable_property
    def value(self):
        if self.state is not None:
            return self.state
        result = []
        for element in self:
            if element.value is NotUnserializable:
                return NotUnserializable
            result.append(element.value)
        return result

    @specifiying
    def set_value(self, new_values, propagate=True):
        assert propagate
        if new_values is not Unspecified:
            del self[:]
            self.extend(new_values)

    @value.deleter
    def value(self):
        del self[:]
        self.state = Unspecified

    @inheritable_property
    def raw_value(self):
        return [element.raw_value for element in self]

    def set_raw_value(self, raw_values, propagate=True):
        assert propagate
        del self.raw_value
        if raw_values is not Unspecified:
            self.state = None
            for raw_value in raw_values:
                list.append(self, self.member_schema.from_raw_value(raw_value))

    @raw_value.deleter
    def raw_value(self):
        del self[:]
        self.state = Unspecified

    @classmethod
    def serialize(cls, values):
        if values is Unspecified:
            return values
        return map(cls.member_schema.serialize, values)

    @classmethod
    def unserialize(cls, raw_values):
        if not isinstance(raw_values, list):
            try:
                raw_values = list(raw_values)
            except TypeError:
                return Unspecified
        return map(cls.member_schema.unserialize, raw_values)
