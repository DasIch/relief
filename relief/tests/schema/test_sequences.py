# coding: utf-8
"""
    relief.tests.schema.test_sequences
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2013 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
from collections import Counter

from relief import Tuple, List, Integer, Unspecified, NotUnserializable
from relief.tests.schema.conftest import ElementTest

import six
import py.test


class SequenceTest(ElementTest):
    def test_getitem(self, element_cls, possible_value):
        element = element_cls(possible_value)
        for i, value in enumerate(possible_value):
            assert isinstance(element[i], Integer)
            assert element[i].value == value

        with py.test.raises(IndexError):
            element[i + 1]

        assert len(element[:]) == len(possible_value)
        for child, value in zip(element[:], possible_value):
            assert isinstance(child, Integer)
            assert child.value == value

    def test_contains(self, element_cls, possible_value):
        element = element_cls(possible_value)
        for value in possible_value:
            assert value in element
        assert 3 not in element

    def test_index(self, element_cls, possible_value):
        element = element_cls(possible_value)
        seen = set()
        for i, value in enumerate(possible_value):
            if value in seen:
                continue
            assert element.index(value) == i
            seen.add(value)

        with py.test.raises(ValueError):
            element.index(3)

    def test_count(self, element_cls, possible_value):
        element = element_cls(possible_value)
        for value, count in six.iteritems(Counter(possible_value)):
            assert element.count(value) == count
        assert element.count(3) == 0

    def test_validate_empty(self, element_cls):
        element = element_cls()
        assert not element.validate()
        assert not element.is_valid

    def test_validate_value(self, element_cls, possible_value):
        element = element_cls(possible_value)
        assert element.value == possible_value
        assert element.raw_value == possible_value
        assert element.validate()
        assert element.is_valid

    def test_validate_raw_value(self, element_cls, possible_value, possible_raw_value):
        element = element_cls(possible_raw_value)
        assert element.raw_value == possible_raw_value
        assert element.value == possible_value
        for child, value, raw_value in zip(element, possible_value, possible_raw_value):
            assert child.value == value
            assert child.raw_value == raw_value
        assert element.validate()
        assert element.is_valid

    def test_validate_invalid_raw_value(self, element_cls, invalid_raw_values):
        element = element_cls(invalid_raw_values)
        assert element.raw_value == invalid_raw_values
        assert element.value is NotUnserializable
        assert not element.validate()
        assert not element.is_valid

    def test_validate_is_recursive(self, element_cls, possible_value):
        is_recursive = [False]
        def validate(element, context):
            is_recursive[0] = True
            return True
        element = element_cls.validated_by([validate])(possible_value)
        assert element.validate()
        assert element.is_valid
        assert is_recursive[0]

    def test_traverse(self, element_cls, possible_value):
        element = element_cls(possible_value)
        assert [
            (prefix, child.value) for prefix, child in element.traverse()
        ] == [([i], value) for i, value in enumerate(possible_value)]
        assert [
            (prefix, child.value)
            for prefix, child in element.traverse(prefix=["foo"])
        ] == [(["foo", i], value) for i, value in enumerate(possible_value)]


class TestTuple(SequenceTest):
    @py.test.fixture
    def element_cls(self):
        return Tuple.of(Integer, Integer, Integer)

    @py.test.fixture
    def possible_value(self):
        return (1, 1, 2)

    @py.test.fixture
    def possible_raw_value(self):
        return ("1", 1, "2")

    @py.test.fixture(params=[(1, "1", "foobar"), 1])
    def invalid_raw_values(self, request):
        return request.param

    def test_validate_without_members(self):
        element = Tuple.of()()
        assert element.value is Unspecified
        assert not element.validate()

        element = Tuple.of()(())
        assert element.value == ()
        assert element.validate()

    def test_traverse_nested(self):
        element_cls = Tuple.of(Tuple.of(Integer, Integer), Integer)
        element = element_cls(((1, 2), (3)))
        assert [
            (prefix, child.value) for prefix, child in element.traverse()
        ] == [
            ([0, 0], 1),
            ([0, 1], 2),
            ([1], 3)
        ]


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
    def possible_value(self):
        return [1, 1, 2]

    @py.test.fixture
    def possible_raw_value(self):
        return ["1", 1, "2"]

    @py.test.fixture(params=[("1", 1, "foobar"), 1])
    def invalid_raw_values(self, request):
        if isinstance(request.param, tuple):
            return list(request.param)
        return request.param

    def test_traverse_nested(self):
        element_cls = List.of(List.of(Integer))
        element = element_cls([[1, 2], [3, 4]])
        assert [
            (prefix, child.value) for prefix, child in element.traverse()
        ] == [
            ([0, 0], 1),
            ([0, 1], 2),
            ([1, 0], 3),
            ([1, 1], 4)
        ]
