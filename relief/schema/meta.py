# coding: utf-8
"""
    relief.schema.meta
    ~~~~~~~~~~~~~~~~~~

    :copyright: 2013 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
from relief.utils import class_cloner
from relief.constants import Unspecified
from relief.schema.core import BaseElement


class Maybe(BaseElement):
    """
    A meta element that represents an element that is optional. The value of
    this element will be `None` unless the contained element's value is not
    `Unspecified`.

    >>> from relief import Unicode
    >>> Maybe.of(Unicode)().value
    None
    >>> Maybe.of(Unicode)(u'foobar').value
    u'foobar

    .. versionadded:: 2.1.0
    """
    member_schema = None

    @class_cloner
    def of(cls, schema):
        cls.member_schema = schema
        return cls

    def __init__(self, value=Unspecified):
        self.member = self.member_schema()
        super(Maybe, self).__init__(value)
        if self.member_schema is None:
            raise TypeError('member_schema is unknown')

    @property
    def value(self):
        return None if self.member.value is Unspecified else self.member.value

    @value.setter
    def value(self, new_value):
        if new_value is not Unspecified:
            raise AttributeError("can't set attribute")

    def serialize(self, value):
        if value is None:
            return Unspecified
        return self.member.serialize(value)

    def unserialize(self, raw_value):
        value = self.member.unserialize(raw_value)
        return None if value is Unspecified else value

    def set_from_raw(self, raw_value):
        self.raw_value = raw_value
        value = self.unserialize(raw_value)
        if value is None:
            self.member.set_from_raw(Unspecified)
        else:
            self.member.set_from_raw(raw_value)
        self.is_valid = None

    def set_from_native(self, value):
        self.member.set_from_native(value)
        self.raw_value = self.member.raw_value
        self.is_valid = None

    def validate(self, context=None):
        if context is None:
            context = {}
        self.is_valid = self.member.validate() or self.value is None
        return self.is_valid
