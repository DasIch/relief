# coding: utf-8
"""
    relief.schema.sequences
    ~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2013 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
from relief import Unspecified, NotUnserializable
from relief.utils import class_cloner
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
    def unserialize(cls, raw_value):
        try:
            raw_value = tuple(raw_value)
        except TypeError:
            return NotUnserializable
        if len(raw_value) != len(cls.member_schema):
            return NotUnserializable
        return raw_value

    @property
    def value(self):
        if not isinstance(self.raw_value, tuple):
            if self.raw_value is Unspecified:
                return Unspecified
            return NotUnserializable
        elif len(self.raw_value) != len(self):
            return NotUnserializable
        result = []
        for element in self:
            if element.value is NotUnserializable:
                return NotUnserializable
            result.append(element.value)
        return tuple(result)

    @value.setter
    def value(self, new_value):
        if new_value is not Unspecified:
            raise ValueError("can't set attribute")

    def set(self, raw_value):
        self.raw_value = raw_value
        if raw_value is Unspecified:
            for element in self:
                element.set(raw_value)
        else:
            unserialized = self.unserialize(raw_value)
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
    def unserialize(cls, raw_values):
        try:
            return list(raw_values)
        except TypeError:
            return NotUnserializable

    @property
    def value(self):
        if not isinstance(self.raw_value, list):
            if self.raw_value is Unspecified:
                return self.raw_value
            return NotUnserializable
        result = []
        for element in self:
            if element.value is NotUnserializable:
                return NotUnserializable
            result.append(element.value)
        return result

    @value.setter
    def value(self, new_value):
        if new_value is not Unspecified:
            raise AttributeError("can't set attribute")

    def set(self, raw_value):
        self.raw_value = raw_value
        if raw_value is Unspecified:
            for element in self:
                element.set(raw_value)
        else:
            unserialized = self.unserialize(raw_value)
            if unserialized is NotUnserializable:
                del self[:]
            else:
                self.extend(unserialized)
