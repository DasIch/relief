# coding: utf-8
"""
    relief.validation
    ~~~~~~~~~~~~~~~~~

    :copyright: 2013 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
from relief import Unspecified, NotUnserializable


class Validator(object):
    accepts_unspecified = False
    accepts_not_unserializable = False

    def validate(self, element, context):
        return False

    def note_error(self, element, error, substitutions=None):
        if substitutions is None:
            substitutions = {}
        element.errors.append(error.format(**substitutions))

    def __call__(self, element, context):
        if element.value is Unspecified and not self.accepts_unspecified:
            return False
        elif element.value is NotUnserializable and not self.accepts_not_unserializable:
            return False
        return self.validate(element, context)


class Present(Validator):
    """
    A validator that fails with ``"May not be blank."`` if the value is
    unspecified.
    """
    accepts_unspecified = True

    def validate(self, element, state):
        if element.value is Unspecified:
            self.note_error(element, u"May not be blank.")
            return False
        return True


class Converted(Validator):
    """
    A validator that fails with ``"Not a valid value."`` if the value is not
    unserializable.
    """
    accepts_not_unserializable = True

    def validate(self, element, state):
        if element.value is NotUnserializable:
            self.note_error(element, u"Not a valid value.")
            return False
        return True


class IsTrue(Validator):
    """
    A validator that fails with ``"Must be true."`` if the value is false-ish.
    """
    def validate(self, element, context):
        if not bool(element.value):
            self.note_error(element, u"Must be true.")
            return False
        return True


class IsFalse(Validator):
    """
    A validator that fails with ``"Must be false."`` if the value is true-ish.
    """
    def validate(self, element, context):
        if bool(element.value):
            self.note_error(element, u"Must be false.")
            return False
        return True


class ShorterThan(Validator):
    """
    A validator that fails with ``"Must be shorter than {upperbound}."`` if the
    length of the value is equal to or exceeds the given `upperbound`.
    """
    def __init__(self, upperbound):
        self.upperbound = upperbound

    def validate(self, element, context):
        if len(element.value) >= self.upperbound:
            self.note_error(
                element,
                u"Must be shorter than {upperbound}.",
                substitutions={"upperbound": self.upperbound}
            )
            return False
        return True


class LongerThan(Validator):
    """
    A validator that fails with ``"Must be longer than {lowerbound}."`` if the
    length of the value is equal to or exceeds the given `lowerbound`.
    """
    def __init__(self, lowerbound):
        self.lowerbound = lowerbound

    def validate(self, element, context):
        if len(element.value) <= self.lowerbound:
            self.note_error(
                element,
                u"Must be longer than {lowerbound}.",
                substitutions={"lowerbound": self.lowerbound}
            )
            return False
        return True


class LengthWithinRange(Validator):
    """
    A validator that fails with ``"Must be longer than {start} and shorter than
    {end}."`` if the length of the value is less than or equal to `start` or
    greater than or equal to `end`.
    """
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def validate(self, element, context):
        if self.start < len(element.value) < self.end:
            return True
        self.note_error(
            element,
            u"Must be longer than {start} and shorter than {end}.",
            substitutions={"start": self.start, "end": self.end}
        )
        return False


class ContainedIn(Validator):
    """
    A validator that fails with ``"Not a valid value."`` if the value is not
    contained in `options`.
    """
    def __init__(self, options):
        self.options = options

    def validate(self, element, context):
        if element.value not in self.options:
            self.note_error(element, u"Not a valid value.")
            return False
        return True


class LessThan(Validator):
    """
    A validator that fails with ``"Must be less than {upperbound}."`` if the
    value is greater than or equal to `upperbound`.
    """
    def __init__(self, upperbound):
        self.upperbound = upperbound

    def validate(self, element, context):
        if element.value >= self.upperbound:
            self.note_error(
                element,
                u"Must be less than {upperbound}.",
                substitutions={"upperbound": self.upperbound}
            )
            return False
        return True


class GreaterThan(Validator):
    """
    A validator that fails with ``"Must be greater than {lowerbound}."`` if the
    value is less than or equal to `lowerbound`.
    """
    def __init__(self, lowerbound):
        self.lowerbound = lowerbound

    def validate(self, element, context):
        if element.value <= self.lowerbound:
            self.note_error(
                element,
                u"Must be greater than {lowerbound}.",
                substitutions={"lowerbound": self.lowerbound}
            )
            return False
        return True


class WithinRange(Validator):
    """
    A validator that fails with ``"Must be greater than {start} and shorter
    than {end}."`` if the value is less than or equal to `start` or greater
    than or equal to `end`.
    """
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def validate(self, element, context):
        if self.start < element.value < self.end:
            return True
        self.note_error(
            element,
            u"Must be greater than {start} and shorter than {end}.",
            substitutions={"start": self.start, "end": self.end}
        )
        return False


class ItemsEqual(Validator):
    """
    A validator that fails with ``"{a} and {b} must be equal."``

    `a` and `b` should be tuples in the form ``(label, key)``. In the message
    `a` and `b` is substituted with the `label` but the `key` is used to
    determine the items to compare.
    """
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def validate(self, element, context):
        if element[self.a[1]].value == element[self.b[1]].value:
            return True
        self.note_error(
            element,
            u"{a} and {b} must be equal.",
            substitutions={"a": self.a[0], "b": self.b[0]}
        )
        return False


class AttributesEqual(Validator):
    """
    A validator that fails with ``"{a} and {b} must be equal."``

    `a` and `b` should be tuples in the form ``(label, attribute_name)``. In
    the message `a` and `b` is substituted with the `label` but the
    `attribute_name` is used to determine the attributes to compare.
    """
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def validate(self, element, context):
        if getattr(element, self.a[1]).value == getattr(element, self.b[1]).value:
            return True
        self.note_error(
            element,
            u"{a} and {b} must be equal.",
            substitutions={"a": self.a[0], "b": self.b[0]}
        )
        return False


class ProbablyAnEmailAddress(Validator):
    """
    A validator that fails with ``"Must be a valid e-mail address."``, if the
    value of the validated e-mail is not a valid e-mail address.

    While this validator works on valid e-mail addresses it is not expected to
    pick up all bad e-mail addresses. The reason for this is that parsing
    e-mail addresses is very complicated, costly, probably would wrongly
    recognize some valid e-mail addresses as invalid and cannot determine if
    someone is reachable with this address.

    If you want to truly validate e-mail addresses you need to send an e-mail
    and wait for a response.
    """
    def validate(self, element, context):
        if u"@" in element.value:
            host = element.value.split(u"@", 1)[1]
            if u"." in host:
                parts = host.split(u".")
                if len(parts) >= 2:
                    return True
        self.note_error(
            element,
            u"Must be a valid e-mail address."
        )
        return False
