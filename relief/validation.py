# coding: utf-8
"""
    relief.validation
    ~~~~~~~~~~~~~~~~~

    :copyright: 2013 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
from relief.constants import Unspecified, NotUnserializable


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
    accepts_unspecified = True

    def validate(self, element, state):
        if element.value is Unspecified:
            self.note_error(element, u"May not be blank.")
            return False
        return True


class Converted(Validator):
    accepts_not_unserializable = True

    def validate(self, element, state):
        if element.value is NotUnserializable:
            self.note_error(element, u"Not a valid value.")
            return False
        return True


class IsTrue(Validator):
    def validate(self, element, context):
        if not bool(element.value):
            self.note_error(element, u"Must be true.")
            return False
        return True


class IsFalse(Validator):
    def validate(self, element, context):
        if bool(element.value):
            self.note_error(element, u"Must be false.")
            return False
        return True


class ShorterThan(Validator):
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
    def __init__(self, options):
        self.options = options

    def validate(self, element, context):
        if element.value not in self.options:
            self.note_error(element, u"Not a valid value.")
            return False
        return True


class LessThan(Validator):
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
