# coding: utf-8
"""
    relief.tests.schema.test_core
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2013 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
from relief.constants import Unspecified
from relief.schema.core import Element
from relief.tests.schema.conftest import ElementTest

import py.test


class TestElement(ElementTest):
    @py.test.fixture
    def element_cls(self):
        return Element

    @py.test.fixture
    def possible_value(self):
        return object()

    def test_using(self):
        assert Element.default is Unspecified
        NewElement = Element.using(default=1)
        assert NewElement is not Element
        assert NewElement.default == 1
        assert Element.default is Unspecified

        with py.test.raises(AttributeError):
            Element.does_not_exist

        with py.test.raises(TypeError):
            Element.using(does_not_exist=True)

    def test_value(self):
        element = Element()
        assert element.value is Unspecified
        element.value = 1
        assert element.value == 1
        assert element.raw_value == 1

    def test_raw_value(self):
        element = Element()
        assert element.raw_value is Unspecified
        element.raw_value = 1
        assert element.raw_value == 1
        assert element.value == 1

    def test_state(self):
        element = Element()
        assert element.state is Unspecified
        element.value = 1
        assert element.state is None
