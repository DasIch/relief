# coding: utf-8
"""
    tests.schema.conftest
    ~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2013 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
from relief.validation import Present, Converted


class ElementTest(object):
    def test_validate_with_context(self, element_cls, possible_value):
        def is_empty_dict(element, context):
            assert context == {}
            return True
        element = element_cls.validated_by([is_empty_dict])(possible_value)
        assert element.validate()
        assert element.is_valid

        def contains_foo(element, context):
            assert context["foo"] == 1
            return True
        element = element_cls.validated_by([contains_foo])(possible_value)
        assert element.validate(context={"foo": 1})
        assert element.is_valid

    def test_validate_fails_with_validator(self, element_cls, possible_value):
        element = element_cls.validated_by([lambda e, c: False])(possible_value)
        assert not element.validate()
        assert not element.is_valid

    def test_errors(self, element_cls):
        # just check that we have an errors attribute we can do list-like stuff
        # with
        element = element_cls()
        element.errors.append(u"something")
        assert element.errors == [u"something"]

    def test_validated_by(self, element_cls, possible_value):
        element = element_cls.validated_by([Present()]).validated_by([Converted()])()
        assert not element.validate()
        assert element.errors == [u"May not be blank."]

    def test_default(self, element_cls, possible_value):
        element = element_cls.using(default=possible_value)()
        assert element.raw_value == possible_value
        assert element.value == possible_value

    def test_default_factory(self, element_cls, possible_value):
        element = element_cls.using(default_factory=lambda e: possible_value)()
        assert element.raw_value == possible_value
        assert element.value == possible_value

    def test_set_from_native_invalidates_is_valid(self, element_cls, possible_value):
        element = element_cls()
        element.set_from_native(possible_value)
        assert element.validate()
        assert element.is_valid
        element.set_from_native(possible_value)
        assert element.is_valid is None

    def test_set_from_raw_invalidates_is_valid(self, element_cls, possible_value):
        element = element_cls()
        element.set_from_raw(possible_value)
        assert element.validate()
        assert element.is_valid
        element.set_from_raw(possible_value)
        assert element.is_valid is None

    def test_with_properties(self, element_cls):
        a = element_cls.with_properties(foo=1)
        assert a.properties == {'foo': 1}
        b = a.with_properties(bar=2)
        assert b.properties == {'foo': 1, 'bar': 2}

    def test_set_from_native_custom_serialize(self, element_cls, possible_value):
        class FooElement(element_cls):
            def serialize(self, value):
                return 'foo'

        element = FooElement()
        element.set_from_native(possible_value)
        assert element.value == possible_value
        assert element.raw_value == 'foo'
