# coding: utf-8
"""
    tests.schema.test_mappings
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2013 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
from relief import (
    Dict, OrderedDict, Unicode, Integer, NotUnserializable, Form, Element,
    _compat
)

from tests.conftest import python2_only
from tests.schema.conftest import ElementTest

import py.test


class MappingTest(ElementTest):
    def test_getitem(self, element_cls):
        element = element_cls({u"foo": 1})
        assert element[u"foo"].value == 1

    def test_get(self, element_cls):
        element = element_cls({u"foo": 1})
        assert element.get(u"foo").value == 1
        assert element.get(u"bar").value is NotUnserializable
        assert element.get(u"bar").raw_value is None

    def test_iter(self, element_cls):
        keys = list(element_cls({u"foo": 1}))
        assert len(keys) == 1
        assert keys[0].value == u"foo"

    @python2_only
    def test_iterkeys(self, element_cls):
        keys = list(element_cls({u"foo": 1}).iterkeys())
        assert len(keys) == 1
        assert keys[0].value == u"foo"

    @python2_only
    def test_viewkeys(self, element_cls):
        keys = list(element_cls({u"foo": 1}).viewkeys())
        assert len(keys) == 1
        assert keys[0].value == u"foo"

    def test_keys(self, element_cls):
        keys = list(element_cls({u"foo": 1}).keys())
        assert len(keys) == 1
        assert keys[0].value == u"foo"

    @python2_only
    def test_itervalues(self, element_cls):
        values = list(element_cls({u"foo": 1}).itervalues())
        assert len(values) == 1
        assert values[0].value == 1

    @python2_only
    def test_viewvalues(self, element_cls):
        values = list(element_cls({u"foo": 1}).viewvalues())
        assert len(values) == 1
        assert values[0].value == 1

    def test_values(self, element_cls):
        values = list(element_cls({u"foo": 1}).values())
        assert len(values) == 1
        assert values[0].value == 1

    @python2_only
    def test_iteritems(self, element_cls):
        items = list(element_cls({u"foo": 1}).iteritems())
        assert len(items) == 1
        assert items[0][0].value == u"foo"
        assert items[0][1].value == 1

    @python2_only
    def test_viewitems(self, element_cls):
        items = list(element_cls({u"foo": 1}).viewitems())
        assert len(items) == 1
        assert items[0][0].value == u"foo"
        assert items[0][1].value == 1

    def test_items(self, element_cls):
        items = list(element_cls({u"foo": 1}).items())
        assert len(items) == 1
        assert items[0][0].value == u"foo"
        assert items[0][1].value == 1

    def test_set_list_of_tuples(self, element_cls):
        element = element_cls([(u"foo", 1)])
        assert element.raw_value == [(u"foo", 1)]
        assert element.value == {u"foo": 1}

    def test_set_non_mapping(self, element_cls):
        element = element_cls(1)
        assert element.raw_value == 1
        assert element.value is NotUnserializable

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
            Integer.validated_by([key_validator]),
            Integer.validated_by([value_validator])
        )({1: 1})
        assert element.validate()
        assert element.is_valid
        assert validators == ["key", "value"]

    def test_validate_value_empty(self, element_cls):
        element = element_cls({})
        assert element.is_valid is None
        assert element.validate()
        assert element.is_valid

    def test_validate_value(self, element_cls):
        element = element_cls({"foo": "1"})
        assert element.raw_value == {"foo": "1"}
        assert element.value == {u"foo": 1}
        assert element.is_valid is None
        assert element.validate()
        assert element.is_valid

    def test_validate_invalid_value(self, element_cls):
        element = element_cls({"foo": "foo"})
        assert element.raw_value == {"foo": "foo"}
        assert element.value is NotUnserializable
        assert element.is_valid is None
        assert not element.validate()
        assert not element.is_valid


class MutableMappingTest(MappingTest):
    def test_setitem(self, element_cls):
        element = element_cls()
        with py.test.raises(TypeError):
            element[u"foo"] = 1

    @py.test.mark.parametrize('method', [
        'setdefault', 'popitem', 'pop', 'update', 'clear'
    ])
    def test_mutating_method_missing(self, element_cls, method):
        element = element_cls()
        assert not hasattr(element, method)
        with py.test.raises(AttributeError):
            getattr(element, method)


class TestDict(MutableMappingTest):
    @py.test.fixture
    def element_cls(self):
        return Dict.of(Unicode, Integer)

    @py.test.fixture
    def possible_value(self):
        return {u"foo": 1}

    @python2_only
    def test_has_key(self, element_cls):
        assert element_cls({u"foo": 1}).has_key(u"foo")
        assert not element_cls({u"foo": 1}).has_key(u"bar")

    def test_set_strict(self, element_cls):
        element = element_cls.using(strict=True)({u"foo": 1})
        assert element.raw_value == {u"foo": 1}
        assert element.value == {u"foo": 1}

    def test_set_strict_raw(self, element_cls):
        element = element_cls.using(strict=True)([(u"foo", 1)])
        assert element.raw_value == [(u"foo", 1)]
        assert element.value is NotUnserializable

    def test_retains_ordering(self, element_cls):
        value = [
            (u"foo", 1),
            (u"bar", 2),
            (u"baz", 3)
        ]
        assert element_cls(value).value == _compat.OrderedDict(value)


class TestOrderedDict(MutableMappingTest):
    @py.test.fixture
    def element_cls(self):
        return OrderedDict.of(Unicode, Integer)

    @py.test.fixture
    def possible_value(self):
        return _compat.OrderedDict([(u"foo", 1)])

    @python2_only
    def test_has_key(self, element_cls):
        assert element_cls({u"foo": 1}).has_key(u"foo")
        assert not element_cls({u"foo": 1}).has_key(u"bar")

    def test_set_strict(self, element_cls):
        value = _compat.OrderedDict({u"foo": 1})
        element = element_cls.using(strict=True)(value)
        assert element.raw_value == value
        assert element.value == value

    def test_set_strict_raw(self, element_cls):
        element = element_cls.using(strict=True)({u"foo": 1})
        assert element.raw_value == {u"foo": 1}
        assert element.value is NotUnserializable


class TestForm(object):
    def test_member_schema_ordering(self):
        class Foo(Form):
            spam = Element
            eggs = Element
        assert list(Foo.member_schema.keys()) == ["spam", "eggs"]

    def test_member_schema_inheritance(self):
        class Foo(Form):
            spam = Element

        class Bar(Foo):
            eggs = Element

        assert list(Bar.member_schema.keys()) == ["spam", "eggs"]

    def test_getitem(self):
        class Foo(Form):
            spam = Unicode

        foo = Foo({"spam": u"one"})
        assert foo["spam"].value == u"one"

    def test_contains(self):
        class Foo(Form):
            spam = Unicode

        foo = Foo()
        assert "spam" in foo
        assert "eggs" not in foo

    def test_len(self):
        class Foo(Form):
            spam = Unicode

        assert len(Foo()) == 1

    def test_iter(self):
        class Foo(Form):
            spam = Unicode
            eggs = Unicode

        assert list(Foo()) == ["spam", "eggs"]

    @python2_only
    def test_iterkeys(self):
        class Foo(Form):
            spam = Unicode
            eggs = Unicode

        assert list(Foo().iterkeys()) == ["spam", "eggs"]

    def test_keys(self):
        class Foo(Form):
            spam = Unicode
            eggs = Unicode

        assert list(Foo().keys()) == ["spam", "eggs"]

    @python2_only
    def test_itervalues(self):
        class Foo(Form):
            spam = Unicode
            eggs = Unicode

        foo = Foo({"spam": u"one", "eggs": u"two"})
        assert [element.value for element in foo.itervalues()] == [u"one", u"two"]

    def test_values(self):
        class Foo(Form):
            spam = Unicode
            eggs = Unicode

        foo = Foo({"spam": u"one", "eggs": u"two"})
        assert [element.value for element in foo.values()] == [u"one", u"two"]

    @python2_only
    def test_iteritems(self):
        class Foo(Form):
            spam = Unicode
            eggs = Unicode

        foo = Foo({"spam": u"one", "eggs": u"two"})
        assert [(key, element.value) for key, element in foo.iteritems()] == [
            ("spam", u"one"),
            ("eggs", u"two")
        ]

    def test_items(self):
        class Foo(Form):
            spam = Unicode
            eggs = Unicode

        foo = Foo({"spam": u"one", "eggs": u"two"})
        assert [(key, element.value) for key, element in foo.items()] == [
            ("spam", u"one"),
            ("eggs", u"two")
        ]

    def test_set(self):
        class Foo(Form):
            spam = Integer

        foo = Foo({"spam": "1"})
        assert foo.raw_value == {"spam": "1"}
        assert foo.value == {"spam": 1}
        assert foo["spam"].raw_value == "1"
        assert foo["spam"].value == 1

    def test_set_list_of_tuples(self):
        form = Form.of({"spam": Integer})([("spam", 1)])
        assert form.raw_value == [("spam", 1)]
        assert form.value == {"spam": 1}

    def test_set_non_mapping(self):
        class Foo(Form):
            spam = Unicode

        foo = Foo(1)
        assert foo.raw_value == 1
        assert foo.value is NotUnserializable

    def test_set_strict(self):
        value = {"spam": 1}
        form = Form.of({"spam": Integer}).using(strict=True)(value)
        assert form.raw_value == value
        assert form.value == value

    def test_set_strict_raw(self):
        value = [("spam", 1)]
        form = Form.of({"spam": Integer}).using(strict=True)(value)
        assert form.raw_value == value
        assert form.value is NotUnserializable

    def test_validate_empty(self):
        class Foo(Form):
            spam = Unicode

        foo = Foo()
        assert foo.is_valid is None
        assert not foo.validate()
        assert not foo.is_valid

    def test_validate_is_recursive(self):
        validators = []
        def spam_validator(element, state):
            validators.append("spam")
            return True
        class Foo(Form):
            spam = Unicode.validated_by([spam_validator])
        foo = Foo({"spam": u"one"})
        assert foo.validate()
        assert foo.is_valid
        assert validators == ["spam"]

    def test_validate_methods(self):
        class Foo(Form):
            spam = Unicode

            def validate_spam(self, element, context):
                return element.value == u'spam'

        foo = Foo({'spam': u'spam'})
        assert foo.validate()
        assert foo.is_valid

        foo = Foo({'spam': u'eggs'})
        assert not foo.validate()
        assert not foo.is_valid

    def test_of(self):
        form = Form.of({"spam": Unicode})({"spam": "foo"})
        assert form.value == {"spam": u"foo"}
        assert form.raw_value == {"spam": "foo"}

    def test_attribute_access(self):
        class Foo(Form):
            spam = Unicode
            eggs = Unicode

        form = Foo({"spam": u"foo", "eggs": u"bar"})
        assert form.spam.value == u"foo"
        assert form.eggs.value == u"bar"
