# coding: utf-8
"""
    relief.schema.scalars
    ~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2013 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
import sys

from relief import Unspecified, NotUnserializable, Element
from relief._compat import text_type


class Boolean(Element):
    """
    Represents a :func:`bool`.

    Unlike other elements this does not call :func:`bool` on an object to
    unserialize a raw value, instead if the raw value is one of ``u"True"`` or
    ``b"True"`` it will unserialize to `True` and if the raw value is one of
    ``u"False"`` or ``b"False"`` it will unserialize to `False`.
    """
    native_type = bool

    def unserialize(self, raw_value):
        raw_value = super(Boolean, self).unserialize(raw_value)
        if isinstance(raw_value, bool) or raw_value is Unspecified:
            return raw_value
        elif raw_value in [u"True", b"True"]:
            return True
        elif raw_value in [u"False", b"False"]:
            return False
        return NotUnserializable


class Number(Element):
    def unserialize(self, raw_value):
        raw_value = super(Number, self).unserialize(raw_value)
        if raw_value is Unspecified or raw_value is NotUnserializable:
            return raw_value
        if isinstance(raw_value, self.native_type):
            return raw_value
        elif isinstance(raw_value, bytes):
            raw_value = raw_value.decode(sys.getdefaultencoding())
        try:
            return self.native_type(raw_value)
        except (ValueError, TypeError):
            return NotUnserializable


class Integer(Number):
    """
    Represents an :func:`int`.

    Unserializes unicode and byte strings that represent integers in base 10 as
    raw values:

    .. doctest::

       >>> from relief import Integer
       >>> element = Integer()
       >>> element.set_from_raw(u"1")
       >>> element.value
       1
       >>> element.set_from_raw(b"1")
       >>> element.value
       1
    """
    native_type = int


class Float(Number):
    """
    Represents a :func:`float`.

    Unserializes unicode and byte strings like :class:`Integer`.
    """
    native_type = float


class Complex(Number):
    """
    Represents a :func:`complex`.

    Unserializes unicode and byte strings like :class:`Integer`.
    """
    native_type = complex


class Unicode(Element):
    """
    Represents a :func:`unicode` string.

    Accepts any byte string that is encoded using the default encoding or which
    ever encoding has been set as :attr:`encoding`::

        >>> from relief import Unicode
        >>> element = Unicode()
        >>> element.set_from_raw(u"Hello, World!")
        >>> element.value
        u"Hello, World!"
        >>> element.set_from_raw(b"Hello, World!")
        >>> element.value
        u"Hello, World!"
    """
    native_type = text_type

    #: The encoding used to decode raw values, can be set with :meth:`using`
    #: and defaults to the default encoding, which is usually ASCII or UTF-8
    #: depending on whether you use 2.x or 3.x.
    encoding = None

    def unserialize(self, raw_value):
        raw_value = super(Unicode, self).unserialize(raw_value)
        if raw_value is Unspecified or raw_value is NotUnserializable:
            return raw_value
        if isinstance(raw_value, text_type):
            return raw_value
        elif isinstance(raw_value, bytes):
            if self.encoding is None:
                encoding = sys.getdefaultencoding()
            else:
                encoding  = self.encoding
            try:
                return raw_value.decode(encoding)
            except UnicodeDecodeError:
                return NotUnserializable
        return text_type(raw_value)


class Bytes(Element):
    """
    Represents a :func:`bytes` string.

    Accepts any unicode string that can be decoded using the default encoding::

        >>> from relief import Bytes
        >>> element = Bytes()
        >>> element.set_from_raw(b"Hello, World!")
        >>> element.value
        b"Hello, World!"
        >>> element.set_from_raw(u"Hello, World!")
        >>> element.value
        b"Hello, World!"
    """
    native_type = bytes

    def unserialize(self, raw_value):
        raw_value = super(Bytes, self).unserialize(raw_value)
        if raw_value is Unspecified or raw_value is NotUnserializable:
            return raw_value
        if isinstance(raw_value, bytes):
            return raw_value
        elif isinstance(raw_value, text_type):
            try:
                return raw_value.encode(sys.getdefaultencoding())
            except UnicodeEncodeError:
                return NotUnserializable
        try:
            return bytes(raw_value)
        except TypeError:
            return NotUnserializable
