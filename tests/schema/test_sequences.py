# coding: utf-8
"""
    tests.schema.test_sequences
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2013 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
from relief import Tuple, List, Integer, Unspecified, NotUnserializable
from relief._compat import iteritems, Counter

from tests.schema.conftest import ElementTest

import pytest


class SequenceTest(ElementTest):
    def test_getitem(self, element_cls, possible_value):
        element = element_cls(possible_value)
        for i, value in enumerate(possible_value):
            assert isinstance(element[i], Integer)
            assert element[i].value == value

        with pytest.raises(IndexError):
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

        with pytest.raises(ValueError):
            element.index(3)

    def test_count(self, element_cls, possible_value):
        element = element_cls(possible_value)
        for value, count in iteritems(Counter(possible_value)):
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


class TestTuple(SequenceTest):
    @pytest.fixture
    def element_cls(self):
        return Tuple.of(Integer, Integer, Integer)

    @pytest.fixture
    def possible_value(self):
        return (1, 1, 2)

    @pytest.fixture
    def possible_raw_value(self):
        return ("1", 1, "2")

    @pytest.fixture(params=[(1, "1", "foobar"), 1])
    def invalid_raw_values(self, request):
        return request.param

    def test_set_list(self):
        element = self.element_cls()([1, 2, 3])
        assert element.raw_value == [1, 2, 3]
        assert element.value == (1, 2, 3)

    def test_set_strict(self):
        element = self.element_cls().using(strict=True)((1, 2, 3))
        assert element.raw_value == (1, 2, 3)
        assert element.value == (1, 2, 3)

    def test_set_strict_raw(self):
        element = self.element_cls().using(strict=True)([1, 2, 3])
        assert element.raw_value == [1, 2, 3]
        assert element.value is NotUnserializable

    def test_validate_without_members(self):
        element = Tuple.of()()
        assert element.value is Unspecified
        assert not element.validate()

        element = Tuple.of()(())
        assert element.value == ()
        assert element.validate()


class TestList(SequenceTest):
    @pytest.fixture
    def element_cls(self):
        return List.of(Integer)

    @pytest.fixture
    def possible_value(self):
        return [1, 1, 2]

    @pytest.fixture
    def possible_raw_value(self):
        return ["1", 1, "2"]

    @pytest.fixture(params=[("1", 1, "foobar"), 1])
    def invalid_raw_values(self, request):
        if isinstance(request.param, tuple):
            return list(request.param)
        return request.param

    def test_set_tuple(self):
        element = self.element_cls()((1, 2, 3))
        assert element.raw_value == (1, 2, 3)
        assert element.value == [1, 2, 3]

    def test_set_strict(self, element_cls):
        element = element_cls.using(strict=True)([1, 2, 3])
        assert element.raw_value == [1, 2, 3]
        assert element.value == [1, 2, 3]

    def test_set_strict_raw(self, element_cls):
        element = element_cls.using(strict=True)((1, 2, 3))
        assert element.raw_value == (1, 2, 3)
        assert element.value is NotUnserializable

    def test_setitem(self):
        element = List.of(Integer)()
        with pytest.raises(TypeError):
            element[0] = 1

    def test_setslice(self):
        element = List.of(Integer)()
        with pytest.raises(TypeError):
            element[0:1] = [1, 2]

    def test_delitem(self):
        element = List.of(Integer)([1])
        with pytest.raises(TypeError):
            del element[0]

    def test_delslice(self):
        element = List.of(Integer)([1, 2])
        with pytest.raises(TypeError):
            del element[0:1]

    @pytest.mark.parametrize('method', [
        'append', 'extend', 'insert', 'pop', 'remove'
    ])
    def test_does_not_have_mutating_list_methods(self, method):
        element = List.of(Integer)()
        assert not hasattr(element, method)
        with pytest.raises(AttributeError):
            getattr(element, method)
