# coding: utf-8
"""
    relief.schema.scalars
    ~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2013 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
import sys

from relief import NotUnserializable
from relief.schema.core import Element

import six


class Boolean(Element):
    """
    Represents a :func:`bool`.

    Accepts ``u"True"``, ``u"False"``, ``b"True"``, and ``b"False"`` as raw
    values.
    """
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
    """
    Represents an :func:`int`.

    Accepts :func:`unicode` and :func:`bytes` representation in base 10 as raw
    value.
    """
    number_cls = int


class Float(Number):
    """
    Represents a :func:`float`.

    Accepts :func:`unicode` and :func:`bytes` representation as raw value.
    """
    number_cls = float


class Complex(Number):
    """
    Represents a :func:`complex`.

    Accepts :func:`unicode` and :func:`bytes` representation as raw value.
    """
    number_cls = complex


class Unicode(Element):
    """
    Represents a :func:`unicode` string.

    Accepts :func:`bytes` encoded using :attr:`encoding`.
    """
    #: The encoding used to decode raw values, can be set with :meth:`using`
    #: and defaults to the default encoding, which is usually ASCII or UTF-8
    #: depending on whether you use 2.x or 3.x.
    encoding = None

    @classmethod
    def unserialize(cls, raw_value):
        if isinstance(raw_value, six.text_type):
            return raw_value
        try:
            if cls.encoding is None:
                encoding = sys.getdefaultencoding()
            else:
                encoding  = cls.encoding
            return raw_value.decode(encoding)
        except UnicodeDecodeError:
            return NotUnserializable


class Bytes(Element):
    """
    Represents a :func:`bytes` string.

    Accepts :func:`unicode` if it can be coerced to bytes.
    """
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
