# coding: utf-8
"""
    relief.tests.test_validation
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2013 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
from relief.validation import (
    Present, Converted, IsTrue, IsFalse, ShorterThan, LongerThan,
    LengthWithinRange, ContainedIn, LessThan, GreaterThan, WithinRange,
    ItemsEqual, AttributesEqual, ProbablyAnEmailAddress
)
from relief.schema.scalars import Unicode, Integer
from relief.schema.mappings import Dict, Form


def test_present():
    Validated = Unicode.validated_by([Present()])
    unicode = Validated(u"foobar")
    assert unicode.validate()
    assert not unicode.errors

    unicode = Validated()
    assert not unicode.validate()
    assert unicode.errors == [u"May not be blank."]


def test_converted():
    Validated = Integer.validated_by([Converted()])
    integer = Integer(1)
    assert integer.validate()
    assert not integer.errors

    integer = Validated("foobar")
    assert not integer.validate()
    assert integer.errors == [u"Not a valid value."]

    integer = Validated()
    assert not integer.validate()
    assert integer.errors == [u"Not a valid value."]


def test_is_true():
    Validated = Unicode.validated_by([IsTrue()])
    unicode = Validated(u"foobar")
    assert unicode.validate()
    assert not unicode.errors

    unicode = Validated(u"")
    assert not unicode.validate()
    assert unicode.errors == [u"Must be true."]

    unicode = Validated()
    assert not unicode.validate()
    assert unicode.errors == [u"Must be true."]

    integer = Integer.validated_by([IsTrue()])("foobar")
    assert not integer.validate()
    assert integer.errors == [u"Must be true."]


def test_is_false():
    Validated = Unicode.validated_by([IsFalse()])
    unicode = Validated(u"")
    assert unicode.validate()
    assert not unicode.errors

    unicode = Validated(u"foobar")
    assert not unicode.validate()
    assert unicode.errors == [u"Must be false."]

    unicode = Validated()
    assert not unicode.validate()
    assert unicode.errors == [u"Must be false."]

    integer = Integer.validated_by([IsFalse()])("foobar")
    assert not integer.validate()
    assert integer.errors == [u"Must be false."]


def test_shorter_than():
    Validated = Unicode.validated_by([ShorterThan(3)])
    unicode = Validated(u"ab")
    assert unicode.validate()
    assert not unicode.errors

    unicode = Validated(u"abc")
    assert not unicode.validate()
    assert unicode.errors == [u"Must be shorter than 3."]

    unicode = Validated()
    assert not unicode.validate()
    assert unicode.errors == [u"Must be shorter than 3."]


def test_longer_than():
    Validated = Unicode.validated_by([LongerThan(3)])
    unicode = Validated(u"abcd")
    assert unicode.validate()
    assert not unicode.errors

    unicode = Validated(u"abc")
    assert not unicode.validate()
    assert unicode.errors == [u"Must be longer than 3."]

    unicode = Validated()
    assert not unicode.validate()
    assert unicode.errors == [u"Must be longer than 3."]


def test_length_within_range():
    Validated = Unicode.validated_by([LengthWithinRange(3, 6)])
    unicode = Validated(u"abcd")
    assert unicode.validate()
    assert not unicode.errors

    for value in [u"abc", u"abcdef"]:
        unicode = Validated(value)
        assert not unicode.validate()
        assert unicode.errors == [u"Must be longer than 3 and shorter than 6."]

    unicode = Validated()
    assert not unicode.validate()
    assert unicode.errors == [u"Must be longer than 3 and shorter than 6."]


def test_contained_in():
    Validated = Unicode.validated_by([ContainedIn([u"foo", u"bar"])])
    for value in [u"foo", u"bar"]:
        unicode = Validated(value)
        assert unicode.validate()
        assert not unicode.errors

    unicode = Validated(u"baz")
    assert not unicode.validate()
    assert unicode.errors == [u"Not a valid value."]

    unicode = Validated()
    assert not unicode.validate()
    assert unicode.errors == [u"Not a valid value."]


def test_less_than():
    Validated = Integer.validated_by([LessThan(3)])
    integer = Validated(2)
    assert integer.validate()
    assert not integer.errors

    integer = Validated(4)
    assert not integer.validate()
    assert integer.errors == [u"Must be less than 3."]

    integer = Validated()
    assert not integer.validate()
    assert integer.errors == [u"Must be less than 3."]

    integer = Validated("foo")
    assert not integer.validate()
    assert integer.errors == [u"Must be less than 3."]


def test_greater_than():
    Validated = Integer.validated_by([GreaterThan(3)])
    integer = Validated(4)
    assert integer.validate()
    assert not integer.errors

    integer = Validated(2)
    assert not integer.validate()
    assert integer.errors == [u"Must be greater than 3."]

    integer = Validated()
    assert not integer.validate()
    assert integer.errors == [u"Must be greater than 3."]

    integer = Validated("foo")
    assert not integer.validate()
    assert integer.errors == [u"Must be greater than 3."]


def test_within_range():
    Validated = Integer.validated_by([WithinRange(3, 6)])
    integer = Validated(4)
    assert integer.validate()
    assert not integer.errors

    for value in [2, 7]:
        integer = Validated(value)
        assert not integer.validate()
        assert integer.errors == [u"Must be greater than 3 and shorter than 6."]

    integer = Validated()
    assert not integer.validate()
    assert integer.errors == [u"Must be greater than 3 and shorter than 6."]

    integer = Validated("foo")
    assert not integer.validate()
    assert integer.errors == [u"Must be greater than 3 and shorter than 6."]


def test_items_equal():
    Validated = Dict.of(Unicode, Unicode).validated_by(
        [ItemsEqual((u"Spam", u"spam"), (u"Eggs", u"eggs"))]
    )
    dict = Validated({u"spam": u"foo", u"eggs": u"foo"})
    assert dict.validate()
    assert not dict.errors

    dict = Validated({u"spam": u"foo", u"eggs": u"bar"})
    assert not dict.validate()
    assert dict.errors == [u"Spam and Eggs must be equal."]

    dict = Validated()
    assert not dict.validate()
    assert dict.errors == [u"Spam and Eggs must be equal."]

    dict = Validated("foo")
    assert not dict.validate()
    assert dict.errors == [u"Spam and Eggs must be equal."]


def test_attributes_equal():
    Validated = Form.of({"spam": Unicode, "eggs": Unicode}).validated_by(
        [AttributesEqual((u"Spam", "spam"), (u"Eggs", "eggs"))]
    )
    form = Validated({"spam": u"foo", "eggs": u"foo"})
    assert form.validate()
    assert not form.errors

    form = Validated({"spam": u"foo", "eggs": u"bar"})
    assert not form.validate()
    assert form.errors == [u"Spam and Eggs must be equal."]

    form = Validated()
    assert not form.validate()
    assert form.errors == [u"Spam and Eggs must be equal."]

    form = Validated("foo")
    assert not form.validate()
    assert form.errors == [u"Spam and Eggs must be equal."]


def test_probably_an_email_address():
    Validated = Unicode.validated_by([ProbablyAnEmailAddress()])
    email = Validated(u"test@example.com")
    assert email.validate()
    assert not email.errors

    invalid_addresses = [
        u"foobar",  # @ missing
        u"foo@bar", # tld missing
    ]
    for invalid_address in invalid_addresses:
        email = Validated(invalid_address)
        assert not email.validate()
        assert email.errors == [u"Must be a valid e-mail address."]

    email = Validated()
    assert not email.validate()
    assert email.errors == [u"Must be a valid e-mail address."]
