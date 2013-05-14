# coding: utf-8
"""
    relief.schema.core
    ~~~~~~~~~~~~~~~~~~~

    :copyright: 2013 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
from relief import Unspecified, NotUnserializable
from relief.utils import class_cloner

import six


class Element(object):
    validators = []

    @class_cloner
    def using(cls, **kwargs):
        for key, value in six.iteritems(kwargs):
            if not hasattr(cls, key):
                raise TypeError("unexpected keyword argument %r" % key)
            setattr(cls, key, value)
        return cls

    @classmethod
    def validated_by(cls, validators):
        return cls.using(validators=cls.validators + validators)

    @classmethod
    def unserialize(cls, raw_value):
        return raw_value

    def __init__(self, value=Unspecified):
        self.is_valid = None
        self.errors = []

        self.set(value)

    def set(self, raw_value):
        self.raw_value = raw_value
        if raw_value is Unspecified:
            self.value = raw_value
        else:
            self.value = self.unserialize(raw_value)

    def validate(self, context=None):
        if context is None:
            context = {}
        if self.validators:
            self.is_valid = all(
                validator(self, context) for validator in self.validators
            )
        else:
            self.is_valid = self.value not in [Unspecified, NotUnserializable]
        return self.is_valid

    def traverse(self, prefix=None):
        yield prefix, self


class Container(Element):
    member_schema = None

    @class_cloner
    def of(cls, schema):
        cls.member_schema = schema
        return cls

    def __init__(self, value=Unspecified):
        super(Container, self).__init__(value)
        if self.member_schema is None:
            raise TypeError("member_schema is unknown")
