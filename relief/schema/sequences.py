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
        """
        Recursively traverses over the elements over the list. Adds the index
        of each element to the prefix:

        >>> from relief import Integer
        >>> Sequence.of(Integer)([1, 2, 3]).traverse()
        ([0], 1)
        ([1], 2)
        ([2], 3)
        """
        for i, element in enumerate(self):
            if prefix is None:
                current_prefix = [i]
            else:
                current_prefix = prefix + [i]
            for child in element.traverse(current_prefix):
                yield child


class Tuple(Sequence, tuple):
    """
    Represents a :func:`tuple`.

    In order to use :class:`Tuple`, you need to define the elements it contains
    using :meth:`of`, which will return a new :class:`Tuple` class::

        Tuple.of(Integer, Unicode)

    would be a :class:`Tuple` of length 2, with an :class:`~relief.Integer` at
    index 0, and a :class:`~relief.Unicode` string at index 1.

        Tuple.of()

    would be a :class:`Tuple` of length 0.

    Any kind of iterable will be accepted as raw value.
    """

    @class_cloner
    def of(cls, *schemas):
        """
        Returns a new :class:`Tuple` class whose contents are defined by the
        given schemas.
        """
        cls.member_schema = schemas
        return cls

    def __new__(cls, *args, **kwargs):
        if cls.member_schema is None:
            raise TypeError(
                "You need to create a %s type with .of()" % cls.__name__
            )
        return super(Tuple, cls).__new__(
            cls,
            (schema() for schema in cls.member_schema)
        )

    def __init__(self, value=Unspecified):
        self._state = Unspecified
        super(Tuple, self).__init__(value=value)

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
        if self._state is not None:
            return self._state
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
        self._state = None
        if raw_value is Unspecified:
            self._state = Unspecified
            for element in self:
                element.set(raw_value)
        else:
            unserialized = self.unserialize(raw_value)
            if unserialized is NotUnserializable:
                self._state = NotUnserializable
            else:
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
    """
    Represents a :func:`list`.

    In order to use :class:`List`, you need to define the schema the list is
    supposed to contain with :meth:`of`::

        List.of(Integer)

    would be a :class:`List` containing integers. Unlike :class:`Tuple` the
    length is not part of the element definition and lists are homogeneous.

    Any kind of iterable will be accepted as raw value.
    """
    @classmethod
    def unserialize(cls, raw_values):
        try:
            return list(raw_values)
        except TypeError:
            return NotUnserializable

    def __init__(self, value=Unspecified):
        self._state = Unspecified
        super(List, self).__init__(value=value)

    @property
    def value(self):
        if self._state is not None:
            return self._state
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
        self._state = None
        if raw_value is Unspecified:
            self._state = Unspecified
            for element in self:
                element.set(raw_value)
        else:
            unserialized = self.unserialize(raw_value)
            if unserialized is NotUnserializable:
                self._state = NotUnserializable
                del self[:]
            else:
                self.extend(unserialized)
