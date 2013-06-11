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
    Validator that fails with :attr:`message` if the value is unspecified.
    """
    accepts_unspecified = True

    #: Message that is stored in :attr:`Element.errors`.
    message = u"May not be blank."

    def validate(self, element, state):
        if element.value is Unspecified:
            self.note_error(element, self.message)
            return False
        return True


class Converted(Validator):
    """
    Validator that fails with :attr:`message` if the value is not
    unserializable.
    """
    accepts_not_unserializable = True

    #: Message that is stored in :attr:`Element.errors`.
    message = u"Not a valid value."

    def validate(self, element, state):
        if element.value is NotUnserializable:
            self.note_error(element, self.message)
            return False
        return True


class IsTrue(Validator):
    """
    Validator that fails with :attr:`message` if the value is false-ish.
    """
    #: Message that is stored in :attr:`Element.errors`.
    message = u"Must be true."

    def validate(self, element, context):
        if not bool(element.value):
            self.note_error(element, self.message)
            return False
        return True


class IsFalse(Validator):
    """
    Validator that fails with :attr:`message` if the value is true-ish.
    """
    #: Message that is stored in :attr:`Element.errors`.
    message = u"Must be false."

    def validate(self, element, context):
        if bool(element.value):
            self.note_error(element, self.message)
            return False
        return True


class ShorterThan(Validator):
    """
    Validator that fails with :attr:`message` if the length of the value is
    equal to or longer than the given `upperbound`.
    """
    #: Message that is stored in :attr:`Element.errors`. ``{upperbound}`` in
    #: the message is substituted with the given `upperbound`.
    message = u"Must be shorter than {upperbound}."

    def __init__(self, upperbound):
        self.upperbound = upperbound

    def validate(self, element, context):
        if len(element.value) >= self.upperbound:
            self.note_error(
                element,
                self.message,
                substitutions={"upperbound": self.upperbound}
            )
            return False
        return True


class LongerThan(Validator):
    """
    Validator that fails with :attr:`message` if the length of the value is
    equal to or shorter than the given `lowerbound`.
    """
    #: Message that is stored in :attr:`Element.errors`. ``{lowerbound}`` in
    #: the message is substituted with the given `lowerbound`.
    message = u"Must be longer than {lowerbound}."

    def __init__(self, lowerbound):
        self.lowerbound = lowerbound

    def validate(self, element, context):
        if len(element.value) <= self.lowerbound:
            self.note_error(
                element,
                self.message,
                substitutions={"lowerbound": self.lowerbound}
            )
            return False
        return True


class LengthWithinRange(Validator):
    """
    Validator that fails with :attr:`message` if the length of the value is
    less than or equal to `start` or greater than or equal to `end`.
    """
    #: Message that is stored in :attr:`Element.errors`. ``{start}`` and
    #: ``{end}`` is substituted with the given `start` and `end`.
    message = u"Must be longer than {start} and shorter than {end}."

    def __init__(self, start, end):
        self.start = start
        self.end = end

    def validate(self, element, context):
        if self.start < len(element.value) < self.end:
            return True
        self.note_error(
            element,
            self.message,
            substitutions={"start": self.start, "end": self.end}
        )
        return False


class ContainedIn(Validator):
    """
    A validator that fails with ``"Not a valid value."`` if the value is not
    contained in `options`.
    """
    #: Message that is stored in :attr:`Element.errors`.
    message = u"Not a valid value."

    def __init__(self, options):
        self.options = options

    def validate(self, element, context):
        if element.value not in self.options:
            self.note_error(element, u"Not a valid value.")
            return False
        return True


class LessThan(Validator):
    """
    Validator that fails with :attr:`message` if the value is greater than or
    equal to `upperbound`.
    """
    #: Message that is stored in :attr:`Element.errors`. ``{upperbound}`` is
    #: substituted with the given `upperbound`.
    message = u"Must be less than {upperbound}."

    def __init__(self, upperbound):
        self.upperbound = upperbound

    def validate(self, element, context):
        if element.value >= self.upperbound:
            self.note_error(
                element,
                self.message,
                substitutions={"upperbound": self.upperbound}
            )
            return False
        return True


class GreaterThan(Validator):
    """
    Validator that fails with :attr:`message` if the value is less than or
    equal to `lowerbound`.
    """
    #: Message that is stored in the :attr:`Element.errors`. ``{lowerbound}``
    #: is substituted with the given `lowerbound`.
    message = u"Must be greater than {lowerbound}."

    def __init__(self, lowerbound):
        self.lowerbound = lowerbound

    def validate(self, element, context):
        if element.value <= self.lowerbound:
            self.note_error(
                element,
                self.message,
                substitutions={"lowerbound": self.lowerbound}
            )
            return False
        return True


class WithinRange(Validator):
    """
    Validator that fails with :attr:`message` if the value is less than or
    equal to `start` or greater than or equal to `end.`
    """
    #: Message that is stored in :attr:`Element.errors`. ``{start}`` and
    #: ``{end}`` are substituted with the given `start` and `end`.
    message = u"Must be greater than {start} and shorter than {end}."

    def __init__(self, start, end):
        self.start = start
        self.end = end

    def validate(self, element, context):
        if self.start < element.value < self.end:
            return True
        self.note_error(
            element,
            self.message,
            substitutions={"start": self.start, "end": self.end}
        )
        return False


class ItemsEqual(Validator):
    """
    Validator that fails with :attr:`message` if two items in the value are
    unequal.

    The items are defined with the tuples `a` and `b` each of which consist of
    two elements ``(label, key)``. The `key` is used to determine the item to
    compare and the `label` is used for substitution in the message.
    """
    #: Message that is stored in :attr:`Element.errors`. ``{a}`` and ``{b}``
    #: are substituted with the labels in the given `a` and `b`.
    message = u"{a} and {b} must be equal."

    def __init__(self, a, b):
        self.a = a
        self.b = b

    def validate(self, element, context):
        if element[self.a[1]].value == element[self.b[1]].value:
            return True
        self.note_error(
            element,
            self.message,
            substitutions={"a": self.a[0], "b": self.b[0]}
        )
        return False


class AttributesEqual(Validator):
    """
    Validator that fails with :attr:`message` if two attributes of the value
    are unequal.

    Similar to :class:`ItemsEqual` the attributes are defined with the tuples
    `a` and `b` each of which consists of two element in the form ``(label,
    attribute_name)``. `attribute_name` is used to determine the attributes to
    compare and the `label` is used for substitution in the message.
    """
    #: Message that is stored in :attr:`Element.errors`. ``{a}`` and ``{b}``
    #: are substituted with the labels in the given `a` and `b`.
    message = u"{a} and {b} must be equal."

    def __init__(self, a, b):
        self.a = a
        self.b = b

    def validate(self, element, context):
        if getattr(element, self.a[1]).value == getattr(element, self.b[1]).value:
            return True
        self.note_error(
            element,
            self.message,
            substitutions={"a": self.a[0], "b": self.b[0]}
        )
        return False


class ProbablyAnEmailAddress(Validator):
    """
    A validator that fails with :attr:`message`, if the value of the validated
    e-mail is not a valid e-mail address.

    While this validator works on valid e-mail addresses it is not expected to
    pick up all bad e-mail addresses. The reason for this is that parsing
    e-mail addresses is very complicated, costly, probably would wrongly
    recognize some valid e-mail addresses as invalid and cannot determine if
    someone is reachable with this address.

    If you want to truly validate e-mail addresses you need to send an e-mail
    and wait for a response.
    """
    #: Message that is stored in the :attr:`Element.errors`.
    message = u"Must be a valid e-mail address."

    def validate(self, element, context):
        if u"@" in element.value:
            host = element.value.split(u"@", 1)[1]
            if u"." in host:
                parts = host.split(u".")
                if len(parts) >= 2:
                    return True
        self.note_error(
            element,
            self.message
        )
        return False
