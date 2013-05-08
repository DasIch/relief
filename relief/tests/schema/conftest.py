# coding: utf-8
"""
    relief.tests.schema.conftest
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2013 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""


class ElementTest(object):
    def test_validate_with_context(self, element_cls, possible_value):
        def is_empty_dict(element, context):
            assert context == {}
            return True
        element = element_cls.using(validators=[is_empty_dict])(possible_value)
        assert element.validate()
        assert element.is_valid

        def contains_foo(element, context):
            assert context["foo"] == 1
            return True
        element = element_cls.using(validators=[contains_foo])(possible_value)
        assert element.validate(context={"foo": 1})
        assert element.is_valid

    def test_validate_fails_with_validator(self, element_cls, possible_value):
        element = element_cls.using(validators=[lambda e, c: False])(possible_value)
        assert not element.validate()
        assert not element.is_valid
