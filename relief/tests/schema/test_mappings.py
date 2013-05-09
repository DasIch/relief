# coding: utf-8
"""
    relief.tests.schema.test_mappings
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2013 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
from relief.constants import Unspecified, NotUnserializable
from relief.schema.scalars import Unicode, Integer
from relief.schema.mappings import Dict
from relief.tests.schema.conftest import ElementTest

import py.test


class MappingTest(ElementTest):
    def test_getitem(self, element_cls):
        element = element_cls({u"foo": 1})
        assert element[u"foo"].value == 1

    def test_get(self, element_cls):
        element = element_cls({u"foo": 1})
        assert element.get(u"foo").value == 1
        assert element.get(u"bar").value is None

    def test_iter(self, element_cls):
        keys = list(element_cls({u"foo": 1}))
        assert len(keys) == 1
        assert keys[0].value == u"foo"

    def test_iterkeys(self, element_cls):
        keys = list(element_cls({u"foo": 1}).iterkeys())
        assert len(keys) == 1
        assert keys[0].value == u"foo"

    def test_keys(self, element_cls):
        keys = element_cls({u"foo": 1}).keys()
        assert len(keys) == 1
        assert keys[0].value == u"foo"

    def test_itervalues(self, element_cls):
        values = list(element_cls({u"foo": 1}).itervalues())
        assert len(values) == 1
        assert values[0].value == 1

    def test_values(self, element_cls):
        values = element_cls({u"foo": 1}).values()
        assert len(values) == 1
        assert values[0].value == 1

    def test_iteritems(self, element_cls):
        items = list(element_cls({u"foo": 1}).iteritems())
        assert len(items) == 1
        assert items[0][0].value == u"foo"
        assert items[0][1].value == 1

    def test_items(self, element_cls):
        items = element_cls({u"foo": 1}).items()
        assert len(items) == 1
        assert items[0][0].value == u"foo"
        assert items[0][1].value == 1

    def test_validate_empty(self, element_cls):
        element = element_cls()
        assert element.is_valid is None
        assert not element.validate()
        assert not element.is_valid

    def test_validate_is_recursive(self):
        validators = []
        def key_validator(element, state):
            validators.append("key")
            return True
        def value_validator(element, state):
            validators.append("value")
            return True
        element = Dict.of(
            Integer.using(validators=[key_validator]),
            Integer.using(validators=[value_validator])
        )({1: 1})
        assert element.validate()
        assert element.is_valid
        assert validators == ["key", "value"]

    def test_traverse(self, element_cls):
        mapping = {u"foo": 1, u"bar": 2}
        element = element_cls(mapping)
        assert [
            (prefix, child.value) for prefix, child in element.traverse()
        ] == [
            ([0, 0], u"foo"),
            ([0, 1], 1),
            ([1, 0], u"bar"),
            ([1, 1], 2)
        ]
        assert [
            (prefix, child.value)
            for prefix, child in element.traverse(prefix=["foo"])
        ] == [
            (["foo", 0, 0], u"foo"),
            (["foo", 0, 1], 1),
            (["foo", 1, 0], u"bar"),
            (["foo", 1, 1], 2)
        ]


class MutableMappingTest(MappingTest):
    def test_setitem(self, element_cls):
        element = element_cls()
        element[u"foo"] = 1
        assert element[u"foo"].value == 1

    def test_setdefault(self, element_cls):
        element = element_cls()
        assert element.setdefault(u"foo", 1).value == 1
        assert element[u"foo"].value == 1
        assert element.setdefault(u"foo", 2).value == 1
        assert element[u"foo"].value == 1

    def test_popitem(self, element_cls):
        key, value = element_cls({u"foo": 1}).popitem()
        assert key.value == u"foo"
        assert value.value == 1

    def test_pop(self, element_cls):
        element = element_cls({u"foo": 1})
        assert element.pop(u"foo").value == 1
        with py.test.raises(KeyError):
            element.pop(u"foo")
        assert element.pop(u"foo", 2).value == 2

    def test_update(self, element_cls):
        element = element_cls()
        element.update([(u"foo", 1)])
        assert element[u"foo"].value == 1

        element = element_cls()
        element.update({u"foo": 1})
        assert element[u"foo"].value == 1

        element = element_cls()
        element.update(foo=1)
        assert element[u"foo"].value == 1


class TestDict(MutableMappingTest):
    @py.test.fixture
    def element_cls(self):
        return Dict.of(Unicode, Integer)

    @py.test.fixture
    def possible_value(self):
        return {u"foo": 1}

    def test_has_key(self, element_cls):
        assert element_cls({u"foo": 1}).has_key(u"foo")
        assert not element_cls({u"foo": 1}).has_key(u"bar")

    def test_validate_value_empty(self, element_cls):
        element = element_cls({})
        assert element.is_valid is None
        assert element.validate()
        assert element.is_valid

    def test_validate_value(self, element_cls):
        element = element_cls({u"foo": 1})
        assert element.is_valid is None
        assert element.validate()
        assert element.is_valid

    def test_validate_raw_value_empty(self, element_cls):
        element = element_cls.from_raw_value({})
        assert element.raw_value == {}
        assert element.value == {}
        assert element.is_valid is None
        assert element.validate()
        assert element.is_valid

    def test_validate_raw_value(self, element_cls):
        element = element_cls.from_raw_value({"foo": "1"})
        assert element.raw_value == {"foo": "1"}
        assert element.value == {u"foo": 1}
        assert element.is_valid is None
        assert element.validate()
        assert element.is_valid

    def test_validate_invalid_raw_value(self, element_cls):
        element = element_cls.from_raw_value({"foo": "foo"})
        assert element.raw_value == {"foo": "foo"}
        assert element.value is NotUnserializable
        assert element.is_valid is None
        assert not element.validate()
        assert not element.is_valid
