# coding: utf-8
"""
    relief.schema.scalars
    ~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2013 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
import sys

from relief.constants import Unspecified, NotUnserializable
from relief.schema.core import Element

import six


class Boolean(Element):
    @classmethod
    def unserialize(cls, raw_value):
        if isinstance(raw_value, bool):
            return raw_value
        if isinstance(raw_value, (bytes, six.text_type)):
            if isinstance(raw_value, bytes):
                try:
                    raw_value = raw_value.decode(sys.getdefaultencoding())
                except UnicodeDecodeError:
                    return NotUnserializable
            if raw_value == u"True":
                return True
            elif raw_value == u"False":
                return False
        return NotUnserializable


class Number(Element):
    number_cls = None

    @classmethod
    def unserialize(cls, raw_value):
        if isinstance(raw_value, complex):
            return raw_value
        elif isinstance(raw_value, bytes):
            raw_value = raw_value.decode(sys.getdefaultencoding())
        try:
            return cls.number_cls(raw_value)
        except (ValueError, TypeError):
            return NotUnserializable


class Integer(Number):
    number_cls = int


class Float(Number):
    number_cls = float


class Complex(Number):
    number_cls = complex


class Unicode(Element):
    encoding = sys.getdefaultencoding()

    @classmethod
    def unserialize(cls, raw_value):
        if isinstance(raw_value, six.text_type):
            return raw_value
        try:
            return raw_value.decode(cls.encoding)
        except UnicodeDecodeError:
            return NotUnserializable


class Bytes(Element):
    @classmethod
    def unserialize(cls, raw_value):
        if isinstance(raw_value, bytes):
            return raw_value
        try:
            if isinstance(raw_value, six.text_type):
                return raw_value.encode(sys.getdefaultencoding())
            return bytes(raw_value)
        except UnicodeEncodeError:
            return NotUnserializable
