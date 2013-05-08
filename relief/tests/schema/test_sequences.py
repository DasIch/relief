# coding: utf-8
"""
    relief.tests.schema.test_sequences
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2013 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
from collections import Counter

from relief.constants import Unspecified, NotUnserializable
from relief.schema.scalars import Integer
from relief.schema.sequences import Tuple, List

import six
import py.test


class SequenceTest(object):
    def test_getitem(self, element_cls, values):
        element = element_cls(values)
        for i, value in enumerate(values):
            assert isinstance(element[i], Integer)
            assert element[i].value == value

        with py.test.raises(IndexError):
            element[i + 1]

        assert len(element[:]) == len(values)
        for child, value in zip(element[:], values):
            assert isinstance(child, Integer)
            assert child.value == value

    def test_contains(self, element_cls, values):
        element = element_cls(values)
        for value in values:
            assert value in element
        assert 3 not in element

    def test_index(self, element_cls, values):
        element = element_cls(values)
        seen = set()
        for i, value in enumerate(values):
            if value in seen:
                continue
            assert element.index(value) == i
            seen.add(value)

        with py.test.raises(ValueError):
            element.index(3)

    def test_count(self, element_cls, values):
        element = element_cls(values)
        for value, count in six.iteritems(Counter(values)):
            assert element.count(value) == count
        assert element.count(3) == 0

    def test_validate_empty(self, element_cls):
        element = element_cls()
        assert not element.validate()
        assert not element.is_valid

    def test_validate_value(self, element_cls, values):
        element = element_cls(values)
        assert element.value == values
        assert element.raw_value == values
        assert element.validate()
        assert element.is_valid

    def test_validate_raw_value(self, element_cls, values, raw_values):
        element = element_cls.from_raw_value(raw_values)
        assert element.raw_value == raw_values
        assert element.value == values
        for child, value, raw_value in zip(element, values, raw_values):
            assert child.value == value
            assert child.raw_value == raw_value
        assert element.validate()
        assert element.is_valid

    def test_validate_invalid_raw_value(self, element_cls, invalid_raw_values):
        element = element_cls.from_raw_value(invalid_raw_values)
        assert element.raw_value == invalid_raw_values
        assert element.value is NotUnserializable
        assert not element.validate()
        assert not element.is_valid


class TestTuple(SequenceTest):
    @py.test.fixture
    def element_cls(self):
        return Tuple.of(Integer, Integer, Integer)

    @py.test.fixture
    def values(self):
        return (1, 1, 2)

    @py.test.fixture
    def raw_values(self):
        return ("1", 1, "2")

    @py.test.fixture
    def invalid_raw_values(self):
        return (1, "1", "foobar")

    def test_validate_without_members(self):
        element = Tuple.of()()
        assert element.value is Unspecified
        assert not element.validate()

        element = Tuple.of()(())
        assert element.value == ()
        assert element.validate()

    def test_raw_value_longer(self, element_cls):
        element = element_cls.from_raw_value((1, 2, 3, 4))
        assert element.raw_value == (1, 2, 3, 4)
        assert element.value is NotUnserializable

        # Tuples always have a fixed length and a fixed amount of elements.
        # However we allow raw_value to be longer than that size. This means
        # that the Tuple has to store a longer raw_value somewhere else and has
        # to update it somehow, if the raw_value of a child that fits within
        # the fixed length of the Tuple is changed.
        element[0].set_raw_value(5)
        assert element.raw_value == (5, 2, 3, 4)
        assert element.value is NotUnserializable

    def test_raw_value_shorter(self, element_cls):
        element = element_cls.from_raw_value((1, 2))
        assert element.raw_value == (1, 2)
        assert element.value is NotUnserializable

        element[0].set_raw_value(3)
        assert element.raw_value == (3, 2)
        assert element.value is NotUnserializable

        element[2].set_raw_value(4)
        assert element.raw_value == (3, 2, 4)
        assert element.value == (3, 2, 4)


class MutableSequenceTest(SequenceTest):
    def test_setitem(self, element_cls):
        element = element_cls([0])
        element[0] = 1
        assert element[0] == 1

    def test_setslice(self, element_cls):
        element = element_cls([1, 2, 3, 4, 5])
        element[:5] = [6, 7, 8, 9, 10]
        assert [e.value for e in element] == [6, 7, 8, 9, 10]

    def test_delitem(self, element_cls):
        element = element_cls([1])
        del element[0]
        with py.test.raises(IndexError):
            del element[0]

    def test_delslice(self, element_cls):
        element = element_cls([1, 2])
        del element[:]
        assert not element

    def test_append(self, element_cls):
        element = element_cls()
        element.append(1)
        assert element[0].value == 1

    def test_extend(self, element_cls):
        element = element_cls()
        element.extend([1, 2, 3])
        assert [e.value for e in element] == [1, 2, 3]

    def test_insert(self, element_cls):
        element = element_cls()
        for value in [1, 2, 3]:
            element.insert(0, value)
        assert [e.value for e in element] == [3, 2, 1]

    def test_pop(self, element_cls):
        element = element_cls([1, 2, 3])
        assert element.pop().value == 3
        assert element.pop(0).value == 1
        with py.test.raises(IndexError):
            element.pop(1)

    def test_remove(self, element_cls):
        element = element_cls([1])
        element.remove(1)
        with py.test.raises(ValueError):
            element.remove(1)


class TestList(MutableSequenceTest):
    @py.test.fixture
    def element_cls(self):
        return List.of(Integer)

    @py.test.fixture
    def values(self):
        return [1, 1, 2]

    @py.test.fixture
    def raw_values(self):
        return ["1", 1, "2"]

    @py.test.fixture
    def invalid_raw_values(self):
        return ["1", 1, "foobar"]
