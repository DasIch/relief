# coding: utf-8
"""
    tests.schema.test_scalars
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2013 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
import sys

from relief import (
    Boolean, Integer, Float, Complex, Unicode, Bytes, Unspecified, 
    NotUnserializable
)

from tests.schema.conftest import ElementTest

import py.test


class ScalarTest(ElementTest):
    def test_value(self, element_cls, possible_value):
        element = element_cls()
        assert element.value is Unspecified
        element.set_from_raw(possible_value)
        assert element.value == possible_value
        assert element.raw_value == possible_value
        element.set_from_raw(Unspecified)
        assert element.value is Unspecified
        assert element.raw_value is Unspecified

    def test_validate_empty(self, element_cls):
        element = element_cls()
        assert element.is_valid is None
        assert element.validate() == False
        assert element.is_valid == False

    def test_validate_value(self, element_cls, possible_value):
        element = element_cls(possible_value)
        assert element.is_valid is None
        assert element.validate()
        assert element.is_valid

    def test_validate_invalid(self, element_cls, invalid_value):
        element = element_cls(invalid_value)
        assert element.is_valid is None
        assert not element.validate()
        assert not element.is_valid

    def test_set_strict(self, element_cls, possible_value):
        element = element_cls.using(strict=True)(possible_value)
        assert element.raw_value == possible_value
        assert element.value == possible_value

    def test_set_strict_raw_value(self, element_cls, possible_raw_value):
        element = element_cls.using(strict=True)(possible_raw_value)
        assert element.raw_value == possible_raw_value
        assert element.value is NotUnserializable

    def test_set_from_raw_native(self, element_cls, possible_value):
        element = element_cls()
        element.set_from_raw(possible_value)
        assert element.raw_value == possible_value
        assert element.value == possible_value


class TestBoolean(ScalarTest):
    @py.test.fixture
    def element_cls(self):
        return Boolean

    @py.test.fixture(params=[True, False])
    def possible_value(self, request):
        return request.param

    @py.test.fixture(params=[u"True", u"False"])
    def possible_raw_value(self, request):
        return request.param

    @py.test.fixture
    def invalid_value(self):
        return "asd"

    @py.test.mark.parametrize(("raw_value", "value"), [
        (u"True", True),
        (u"False", False),
        (u"foo", NotUnserializable)
    ])
    def test_value_unicode(self, raw_value, value):
        boolean = Boolean(raw_value)
        assert boolean.raw_value is raw_value
        assert boolean.value is value

    @py.test.mark.parametrize(("raw_value", "value"), [
        (b"True", True),
        (b"False", False),
        (b"foo", NotUnserializable)
    ])
    def test_value_bytes(self, raw_value, value):
        boolean = Boolean(raw_value)
        assert boolean.raw_value is raw_value
        assert boolean.value is value


class TestInteger(ScalarTest):
    @py.test.fixture
    def element_cls(self):
        return Integer

    @py.test.fixture
    def possible_value(self):
        return 1

    @py.test.fixture
    def possible_raw_value(self):
        return "1"

    @py.test.fixture
    def invalid_value(self):
        return "asd"

    @py.test.mark.parametrize(("raw_value", "value"), [
        (u"1", 1),
        (u"foo", NotUnserializable)
    ])
    def test_value_unicode(self, raw_value, value):
        integer = Integer(raw_value)
        assert integer.raw_value == raw_value
        assert integer.value == value

    @py.test.mark.parametrize(("raw_value", "value"), [
        (b"1", 1),
        (b"foo", NotUnserializable)
    ])
    def test_value_bytes(self, raw_value, value):
        integer = Integer(raw_value)
        assert integer.raw_value == raw_value
        assert integer.value == value


class TestFloat(ScalarTest):
    @py.test.fixture
    def element_cls(self):
        return Float

    @py.test.fixture
    def possible_value(self):
        return 1.0

    @py.test.fixture
    def possible_raw_value(self):
        return "1.0"

    @py.test.fixture
    def invalid_value(self):
        return "asd"

    @py.test.mark.parametrize(("raw_value", "value"), [
        (u"1.0", 1.0),
        (u"foo", NotUnserializable)
    ])
    def test_value_unicode(self, raw_value, value):
        float = Float(raw_value)
        assert float.raw_value == raw_value
        assert float.value == value

    @py.test.mark.parametrize(("raw_value", "value"), [
        (b"1.0", 1.0),
        (b"foo", NotUnserializable)
    ])
    def test_value_bytes(self, raw_value, value):
        float = Float(raw_value)
        assert float.raw_value == raw_value
        assert float.value == value


class TestComplex(ScalarTest):
    @py.test.fixture
    def element_cls(self):
        return Complex

    @py.test.fixture
    def possible_value(self):
        return 1j

    @py.test.fixture
    def possible_raw_value(self):
        return "1j"

    @py.test.fixture
    def invalid_value(self):
        return "asd"

    @py.test.mark.parametrize(("raw_value", "value"), [
        (u"1j", 1j),
        (u"foo", NotUnserializable)
    ])
    def test_value_unicode(self, raw_value, value):
        complex = Complex(raw_value)
        assert complex.raw_value == raw_value
        assert complex.value == value

    @py.test.mark.parametrize(("raw_value", "value"), [
        (b"1j", 1j),
        (b"foo", NotUnserializable)
    ])
    def test_value_bytes(self, raw_value, value):
        complex = Complex(raw_value)
        assert complex.raw_value == raw_value
        assert complex.value == value


class TestUnicode(ScalarTest):
    @py.test.fixture
    def element_cls(self):
        return Unicode

    @py.test.fixture
    def possible_value(self):
        return u"foobar"

    @py.test.fixture
    def possible_raw_value(self):
        return b"foobar"

    @py.test.fixture
    def invalid_value(self):
        # is missing \xc4 after the first character
        return b"\xc3\xc3\xb6\xc3\xbc"

    @py.test.mark.parametrize(("raw_value", "value"), [
        (b"hello", u"hello"),
        # is missing \xc4 after the first character
        (b"\xc3\xc3\xb6\xc3\xbc", NotUnserializable)
    ])
    def test_value_bytes(self, raw_value, value):
        unicode = Unicode(raw_value)
        assert unicode.raw_value == raw_value
        assert unicode.value == value

    def test_value_non_string(self):
        unicode = Unicode(1)
        assert unicode.raw_value == 1
        assert unicode.value == u"1"


class TestBytes(ScalarTest):
    @py.test.fixture
    def element_cls(self):
        return Bytes

    @py.test.fixture
    def possible_value(self):
        return b"foobar"

    @py.test.fixture
    def possible_raw_value(self):
        return u"foobar"

    @py.test.fixture
    def invalid_value(self):
        if sys.version_info >= (3, 0):
            py.test.skip('sys.version_info >= (3, 0)')
        return u"äöü"

    @py.test.mark.parametrize(("raw_value", "value"), [
        (u"hello", b"hello"),
        (u"hëllö", u"hëllö".encode("utf-8") if sys.version_info >= (3, 0) else NotUnserializable)
    ])
    def test_value_bytes(self, raw_value, value):
        bytes = Bytes(raw_value)
        assert bytes.raw_value == raw_value
        assert bytes.value == value

    if sys.version_info >= (3, 0):
        def test_value_non_string(self):
            bytes = Bytes(1)
            assert bytes.raw_value == 1
            assert bytes.value == b"\x00"
    else:
        def test_value_non_string(self):
            bytes = Bytes(1)
            assert bytes.raw_value == 1
            assert bytes.value == b"1"
