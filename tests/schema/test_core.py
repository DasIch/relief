# coding: utf-8
"""
    tests.schema.test_core
    ~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2013 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
import pytest

from relief import Unspecified, Element

from tests.schema.conftest import ElementTest


class TestElement(ElementTest):
    @pytest.fixture
    def element_cls(self):
        return Element

    @pytest.fixture
    def possible_value(self):
        return object()

    def test_using(self):
        with pytest.raises(AttributeError):
            Element.does_not_exist

        with pytest.raises(TypeError):
            Element.using(does_not_exist=True)

    def test_set_from_raw(self):
        element = Element()
        assert element.value is Unspecified
        assert element.raw_value is Unspecified
        element.set_from_raw(1)
        assert element.value == 1
        assert element.raw_value == 1

    def test_set_from_native(self):
        element = Element()
        assert element.value is Unspecified
        assert element.raw_value is Unspecified
        element.set_from_raw(1)
        assert element.value == 1
        assert element.raw_value == 1
