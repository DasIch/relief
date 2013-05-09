# coding: utf-8
"""
    relief.tests.test_validation
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2013 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
from relief.validation import (
    Present, Converted, IsTrue, IsFalse, ShorterThan, LongerThan,
    LengthWithinRange, ContainedIn, LessThan, GreaterThan, WithinRange
)
from relief.schema.scalars import Unicode, Integer


def test_present():
    Validated = Unicode.using(validators=[Present()])
    unicode = Validated(u"foobar")
    assert unicode.validate()
    assert not unicode.errors

    unicode = Validated()
    assert not unicode.validate()
    assert unicode.errors == [u"May not be blank."]


def test_converted():
    Validated = Integer.using(validators=[Converted()])
    integer = Integer.from_raw_value(1)
    assert integer.validate()
    assert not integer.errors

    integer = Validated.from_raw_value("foobar")
    assert not integer.validate()
    assert integer.errors == [u"Not a valid value."]


def test_is_true():
    Validated = Unicode.using(validators=[IsTrue()])
    unicode = Validated(u"foobar")
    assert unicode.validate()
    assert not unicode.errors

    unicode = Validated(u"")
    assert not unicode.validate()
    assert unicode.errors == [u"Must be true."]


def test_is_false():
    Validated = Unicode.using(validators=[IsFalse()])
    unicode = Validated(u"")
    assert unicode.validate()
    assert not unicode.errors

    unicode = Validated(u"foobar")
    assert not unicode.validate()
    assert unicode.errors == [u"Must be false."]


def test_shorter_than():
    Validated = Unicode.using(validators=[ShorterThan(3)])
    unicode = Validated(u"ab")
    assert unicode.validate()
    assert not unicode.errors

    unicode = Validated(u"abc")
    assert not unicode.validate()
    assert unicode.errors == [u"Must be shorter than 3."]


def test_longer_than():
    Validated = Unicode.using(validators=[LongerThan(3)])
    unicode = Validated(u"abcd")
    assert unicode.validate()
    assert not unicode.errors

    unicode = Validated(u"abc")
    assert not unicode.validate()
    assert unicode.errors == [u"Must be longer than 3."]


def test_length_within_range():
    Validated = Unicode.using(validators=[LengthWithinRange(3, 6)])
    unicode = Validated(u"abcd")
    assert unicode.validate()
    assert not unicode.errors

    for value in [u"abc", u"abcdef"]:
        unicode = Validated(value)
        assert not unicode.validate()
        assert unicode.errors == [u"Must be longer than 3 and shorter than 6."]


def test_contained_in():
    Validated = Unicode.using(validators=[ContainedIn([u"foo", u"bar"])])
    for value in [u"foo", u"bar"]:
        unicode = Validated(value)
        assert unicode.validate()
        assert not unicode.errors

    unicode = Validated(u"baz")
    assert not unicode.validate()
    assert unicode.errors == [u"Not a valid value."]


def test_less_than():
    Validated = Integer.using(validators=[LessThan(3)])
    integer = Validated(2)
    assert integer.validate()
    assert not integer.errors

    integer = Validated(4)
    assert not integer.validate()
    assert integer.errors == [u"Must be less than 3."]


def test_greater_than():
    Validated = Integer.using(validators=[GreaterThan(3)])
    integer = Validated(4)
    assert integer.validate()
    assert not integer.errors

    integer = Validated(2)
    assert not integer.validate()
    assert integer.errors == [u"Must be greater than 3."]


def test_within_range():
    Validated = Integer.using(validators=[WithinRange(3, 6)])
    integer = Validated(4)
    assert integer.validate()
    assert not integer.errors

    for value in [2, 7]:
        integer = Validated(4)
        assert integer.validate()
        assert not integer.errors
