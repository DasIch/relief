# coding: utf-8
"""
    relief.tests.schema.test_special
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2013 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
from relief import Form, Unicode, Integer
from relief.constants import NotUnserializable
from relief.schema.core import Element
from relief.tests.conftest import python2_only


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

    def test_setitem(self):
        class Foo(Form):
            spam = Integer

        foo = Foo()
        foo["spam"] = "1"
        assert foo["spam"].value == 1

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

    def test_set_non_mapping(self):
        class Foo(Form):
            spam = Unicode

        foo = Foo(1)
        assert foo.raw_value == 1
        assert foo.value is NotUnserializable

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

    def test_traverse(self):
        class Foo(Form):
            spam = Unicode
            eggs = Unicode
        foo = Foo({"spam": u"one", "eggs": u"two"})
        assert [
            (prefix, child.value) for prefix, child in foo.traverse()
        ] == [(["spam"], u"one"), (["eggs"], u"two")]
        assert [
            (prefix, child.value) for prefix, child in foo.traverse(prefix=["foo"])
        ] == [(["foo", "spam"], u"one"), (["foo", "eggs"], u"two")]
