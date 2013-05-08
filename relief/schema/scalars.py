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


class Scalar(Element):
    def __init__(self, value=Unspecified):
        super(Scalar, self).__init__()
        self.value = value


class Boolean(Scalar):
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


class Integer(Scalar):
    @classmethod
    def unserialize(cls, raw_value):
        if isinstance(raw_value, int):
            return raw_value
        try:
            return int(raw_value)
        except (ValueError, TypeError):
            return NotUnserializable


class Float(Scalar):
    @classmethod
    def unserialize(cls, raw_value):
        if isinstance(raw_value, float):
            return raw_value
        try:
            return float(raw_value)
        except (ValueError, TypeError):
            return NotUnserializable


class Complex(Scalar):
    @classmethod
    def unserialize(cls, raw_value):
        if isinstance(raw_value, complex):
            return raw_value
        elif isinstance(raw_value, bytes):
            raw_value = raw_value.decode(sys.getdefaultencoding())
        try:
            return complex(raw_value)
        except (ValueError, TypeError):
            return NotUnserializable


class Unicode(Scalar):
    encoding = sys.getdefaultencoding()

    @classmethod
    def unserialize(cls, raw_value):
        if isinstance(raw_value, six.text_type):
            return raw_value
        try:
            return raw_value.decode(cls.encoding)
        except UnicodeDecodeError:
            return NotUnserializable


class Bytes(Scalar):
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
