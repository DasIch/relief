# coding: utf-8
"""
    relief.tests.schema.test_core
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2013 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
from relief import Unspecified
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
        with py.test.raises(AttributeError):
            Element.does_not_exist

        with py.test.raises(TypeError):
            Element.using(does_not_exist=True)

    def test_set(self):
        element = Element()
        assert element.value is Unspecified
        assert element.raw_value is Unspecified
        element.set(1)
        assert element.value == 1
        assert element.raw_value == 1
