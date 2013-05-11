# coding: utf-8
"""
    relief.tests.schema.conftest
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2013 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
from relief.validation import Present, Converted

import py.test


python2_only = py.test.mark.skipif("sys.version_info >= (3, 0)")


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