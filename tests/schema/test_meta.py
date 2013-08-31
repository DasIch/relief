# coding: utf-8
"""
    tests.schema.test_mappings
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2013 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
from relief import Maybe, Unicode, Unspecified

from tests.schema.conftest import BaseElementTest

import py.test


class TestMaybe(BaseElementTest):
    @py.test.fixture
    def element_cls(self):
        return Maybe.of(Unicode)

    @py.test.fixture
    def possible_value(self):
        return u'foo'

    def test_set_from_raw(self, element_cls):
        element = element_cls()
        element.set_from_raw(u'foo')
        assert element.value == u'foo'
        assert element.raw_value == u'foo'

        element = element_cls()
        element.set_from_raw(Unspecified)
        assert element.value is None
        assert element.raw_value is Unspecified

    def test_set_from_native(self, element_cls):
        element = element_cls()
        element.set_from_native(u'foo')
        assert element.value == u'foo'
        assert element.raw_value == u'foo'

        element = element_cls()
        element.set_from_native(None)
        assert element.value is None
        assert element.raw_value is None

    def test_validate(self, element_cls):
        element = element_cls()
        element.set_from_raw(u'foo')
        assert element.validate()
        assert element.is_valid

        element = element_cls()
        element.set_from_raw(Unspecified)
        assert element.validate()
        assert element.is_valid

        Validated = Maybe.of(
            Unicode.validated_by(
                [lambda element, context: element.value == u'foo']
            )
        )
        element = Validated()
        assert element.validate()
        assert element.value is None
        assert element.raw_value is Unspecified

        element = Validated()
        element.set_from_raw(u'foo')
        assert element.validate()
        assert element.value == u'foo'
        assert element.raw_value == u'foo'

        element = Validated()
        element.set_from_raw(u'bar')
        assert not element.validate()
        assert element.value == u'bar'
        assert element.raw_value == u'bar'
