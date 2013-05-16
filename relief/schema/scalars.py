# coding: utf-8
"""
    relief.schema.scalars
    ~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2013 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
import sys

from relief import NotUnserializable, Element

import six


class Boolean(Element):
    """
    Represents a :func:`bool`.

    Accepts ``u"True"``, ``u"False"``, ``b"True"``, and ``b"False"`` as raw
    values.
    """
    native_type = bool

    @classmethod
    def unserialize(cls, raw_value):
        raw_value = super(Boolean, cls).unserialize(raw_value)
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
    @classmethod
    def unserialize(cls, raw_value):
        raw_value = super(Number, cls).unserialize(raw_value)
        if raw_value is NotUnserializable:
            return raw_value
        if isinstance(raw_value, cls.native_type):
            return raw_value
        elif isinstance(raw_value, bytes):
            raw_value = raw_value.decode(sys.getdefaultencoding())
        try:
            return cls.native_type(raw_value)
        except (ValueError, TypeError):
            return NotUnserializable


class Integer(Number):
    """
    Represents an :func:`int`.

    Accepts :func:`unicode` and :func:`bytes` representation in base 10 as raw
    value.
    """
    native_type = int


class Float(Number):
    """
    Represents a :func:`float`.

    Accepts :func:`unicode` and :func:`bytes` representation as raw value.
    """
    native_type = float


class Complex(Number):
    """
    Represents a :func:`complex`.

    Accepts :func:`unicode` and :func:`bytes` representation as raw value.
    """
    native_type = complex


class Unicode(Element):
    """
    Represents a :func:`unicode` string.
    """
    native_type = six.text_type

    #: The encoding used to decode raw values, can be set with :meth:`using`
    #: and defaults to the default encoding, which is usually ASCII or UTF-8
    #: depending on whether you use 2.x or 3.x.
    encoding = None

    @classmethod
    def unserialize(cls, raw_value):
        raw_value = super(Unicode, cls).unserialize(raw_value)
        if raw_value is NotUnserializable:
            return raw_value
        if isinstance(raw_value, six.text_type):
            return raw_value
        elif isinstance(raw_value, six.binary_type):
            if cls.encoding is None:
                encoding = sys.getdefaultencoding()
            else:
                encoding  = cls.encoding
            try:
                return raw_value.decode(encoding)
            except UnicodeDecodeError:
                return NotUnserializable
        return six.text_type(raw_value)


class Bytes(Element):
    """
    Represents a :func:`bytes` string.
    """
    native_type = bytes

    @classmethod
    def unserialize(cls, raw_value):
        raw_value = super(Bytes, cls).unserialize(raw_value)
        if raw_value is NotUnserializable:
            return raw_value
        if isinstance(raw_value, bytes):
            return raw_value
        elif isinstance(raw_value, six.text_type):
            try:
                return raw_value.encode(sys.getdefaultencoding())
            except UnicodeEncodeError:
                return NotUnserializable
        try:
            return bytes(raw_value)
        except TypeError:
            return NotUnserializable
