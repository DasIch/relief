# coding: utf-8
"""
    relief.schema.special
    ~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2013 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
from collections import OrderedDict

from relief._compat import add_native_itermethods, Prepareable
from relief.constants import Unspecified, NotUnserializable
from relief.schema.core import Element
from relief.schema.scalars import Unicode

import six


class FormMeta(six.with_metaclass(Prepareable, type)):
    def __new__(cls, cls_name, bases, attributes):
        member_schema = attributes["member_schema"] = OrderedDict()
        for base in reversed(bases):
            member_schema.update(getattr(base, "member_schema", {}))
        for name, attribute in six.iteritems(attributes):
            if isinstance(attribute, type) and issubclass(attribute, Element):
                member_schema[name] = attribute
        return super(FormMeta, cls).__new__(cls, cls_name, bases, attributes)

    def __prepare__(name, bases, **kwargs):
        return OrderedDict()


@add_native_itermethods
class Form(six.with_metaclass(FormMeta, Element)):
    def __new__(cls, *args, **kwargs):
        self = super(Form, cls).__new__(cls)
        self._elements = OrderedDict(
            (name, element())
            for name, element in six.iteritems(self.member_schema)
        )
        return self

    def __getitem__(self, key):
        return self._elements[key]

    def __setitem__(self, key, value):
        if key not in self:
            raise KeyError(key)
        self._elements[key].value = value

    def __contains__(self, key):
        return key in self._elements

    def __len__(self):
        return len(self._elements)

    def __iter__(self):
        return iter(self._elements)

    def keys(self):
        return six.iterkeys(self._elements)

    def values(self):
        return six.itervalues(self._elements)

    def items(self):
        return six.iteritems(self._elements)

    @property
    def value(self):
        if set(self.raw_value) != set(self):
            return NotUnserializable
        result = OrderedDict()
        for key, element in six.iteritems(self):
            if element.value is Unspecified:
                return NotUnserializable
            result[key] = element.value
        return result

    @property
    def raw_value(self):
        if not hasattr(self, "_raw_value"):
            self._raw_value = OrderedDict()
        for key, element in six.iteritems(self):
            if element.raw_value is Unspecified:
                if key in self._raw_value:
                    del self._raw_value[key]
            else:
                self._raw_value[key] = element.raw_value
        return self._raw_value

    def set(self, raw_value):
        if raw_value is Unspecified:
            for element in six.itervalues(self):
                element.set(raw_value)
        else:
            if set(raw_value) != set(self):
                self._raw_value = raw_value
            for key, element in six.iteritems(self):
                try:
                    raw_value_ = raw_value[key]
                except KeyError:
                    pass
                else:
                    element.set(raw_value_)

    def validate(self, context=None):
        if context is None:
            context = {}
        self.is_valid = True
        for element in six.itervalues(self):
            self.is_valid &= element.validate(context=context)
        self.is_valid &= super(Form, self).validate(context=context)
        return self.is_valid

    def traverse(self, prefix=None):
        if prefix is None:
            prefix = []
        for key, element in six.iteritems(self):
            yield prefix + [key], element
