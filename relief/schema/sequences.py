# coding: utf-8
"""
    relief.schema.sequences
    ~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2013 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
from itertools import repeat

from relief.utils import class_cloner
from relief.constants import Unspecified, NotUnserializable
from relief.schema.core import Container


class Sequence(Container):
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

    @classmethod
    def unserialize(cls, raw_values, shallow=False):
        try:
            if len(raw_values) != len(cls.member_schema):
                return NotUnserializable
        except TypeError:
            # raw_values is not a sequence
            return NotUnserializable
        if shallow:
            return tuple(raw_values)
        return tuple(
            schema.unserialize(raw_value)
            for schema, raw_value in zip(cls.member_schema, raw_values)
        )

    @property
    def value(self):
        if not isinstance(self.raw_value, tuple):
            if self.raw_value in [Unspecified, NotUnserializable]:
                return self.raw_value
            return NotUnserializable
        elif len(self.raw_value) != len(self):
            return NotUnserializable
        result = []
        for element in self:
            if element.value is NotUnserializable:
                return NotUnserializable
            result.append(element.value)
        return tuple(result)

    def set(self, raw_value):
        self.raw_value = raw_value
        if raw_value is Unspecified:
            for element in self:
                element.set(raw_value)
        else:
            unserialized = self.unserialize(raw_value, shallow=True)
            if unserialized is not NotUnserializable:
                for element, raw_part in zip(self, unserialized):
                    element.set(raw_part)


class MutableSequence(Sequence):
    def __setitem__(self, key, value):
        if isinstance(key, slice):
            value = map(self.member_schema, value)
        super(MutableSequence, self).__setitem__(key, value)

    def __setslice__(self, start, stop, values):
        self.__setitem__(slice(start, stop), values)

    def append(self, value):
        super(MutableSequence, self).append(self.member_schema(value))

    def extend(self, value):
        super(MutableSequence, self).extend(map(self.member_schema, value))

    def insert(self, index, value):
        self[index:index] = [value]

    def pop(self, index=None):
        if index is None:
            index = len(self) - 1
        value = self[index]
        del self[index]
        return value

    def remove(self, value):
        del self[self.index(value)]


class List(MutableSequence, list):
    @classmethod
    def unserialize(cls, raw_values, shallow=False):
        if not isinstance(raw_values, list):
            try:
                raw_values = list(raw_values)
            except TypeError:
                return NotUnserializable
        if shallow:
            return raw_values
        return map(cls.member_schema.unserialize, raw_values)

    @property
    def value(self):
        if not isinstance(self.raw_value, list):
            if self.raw_value in [Unspecified, NotUnserializable]:
                return self.raw_value
            return NotUnserializable
        result = []
        for element in self:
            if element.value is NotUnserializable:
                return NotUnserializable
            result.append(element.value)
        return result

    def set(self, raw_value):
        self.raw_value = raw_value
        if raw_value is Unspecified:
            for element in self:
                element.set(raw_value)
        else:
            unserialized = self.unserialize(raw_value, shallow=True)
            if unserialized is NotUnserializable:
                del self[:]
            else:
                self.extend(unserialized)
