# coding: utf-8
"""
    relief.schema.core
    ~~~~~~~~~~~~~~~~~~~

    :copyright: 2013 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
from relief import Unspecified, NotUnserializable
from relief.utils import class_cloner, InheritingDictDescriptor
from relief._compat import iteritems


class Element(object):
    """
    Base class for elements. An element allows you to describe Python objects.

    This class specifically defines a basic interface for elements and provides
    some generally useful methods.
    """
    #: When `True` :meth:`unserialize` should not attempt to unserialize raw
    #: values that are instances of :attr:`native_type` and return
    #: :data:`~relief.NotUnserializable` instead.
    strict = False

    #: The "native" type represented by this element.
    native_type = None.__class__

    validators = []

    #: The default value that should be used for this element. This value will
    #: be used if not initial value is given.
    default = Unspecified

    #: A callable that is called with the element, which should be used to
    #: produce the default value that is used if no initial value is given.
    #: :attr:`default` takes precedence.
    default_factory = Unspecified

    #: A dictionary whose contents are inherited by subclasses, which should be
    #: used for application-specific information associated with an element.
    properties = InheritingDictDescriptor('properties')

    @class_cloner
    def using(cls, **kwargs):
        """
        Returns a clone of the class whose attributes have been overwritten
        with the given keyword arguments.
        """
        for key, value in iteritems(kwargs):
            if not hasattr(cls, key):
                raise TypeError("unexpected keyword argument %r" % key)
            setattr(cls, key, value)
        return cls

    @classmethod
    def validated_by(cls, validators):
        """
        Returns a clone of the class that is *also* validated by the given
        iterable of `validators`.
        """
        return cls.using(validators=cls.validators + validators)

    @classmethod
    def with_properties(cls, **properties):
        """
        Returns a clone of the class whose :attr:`properties` contain the given
        `properties` in addition to the ones inherited from this one.
        """
        return cls.using(
            properties=InheritingDictDescriptor('properties', **properties)
        )

    def __init__(self, value=Unspecified):
        #: Defines the validation state of the element, may be one of the
        #: following values:
        #:
        #: `None`
        #:     The element has not been validated, yet.
        #:
        #: `True`
        #:     The element is valid.
        #:
        #: `False`
        #:     The element is not valid.
        self.is_valid = None

        #: A list that is supposed to be populated with unicode strings by a
        #: validator as an explanation of why the element is invalid.
        self.errors = []

        #: The unserialized concrete value this element represents. May also be
        #: :data:`~relief.Unspecified` if the value has not been set or
        #: :data:`~relief.NotUnserializable` if :meth:`unserialize` was unable
        #: to unserialize the value.
        self.value = Unspecified

        #: The concrete value this element represents. May also be
        #: :data:`~relief.Unspecified` if the value has not been set. This may
        #: be helpful to look at if :attr:`value` is
        #: :data:`~relief.NotUnserializable`.
        self.raw_value = Unspecified

        if value is Unspecified:
            if self.default is not Unspecified:
                value = self.default
            elif self.default_factory is not Unspecified:
                value = self.default_factory()
        self.set(value)

    def set(self, raw_value):
        """
        Sets :attr:`raw_value` with the given `raw_value` and sets
        :attr:`value` to the unserialized form of `raw_value` if applicable.
        """
        self.raw_value = raw_value
        if raw_value is Unspecified:
            self.value = raw_value
        else:
            self.value = self.unserialize(raw_value)
        self.is_valid = None

    def unserialize(self, raw_value):
        """
        Tries to unserialize the given `raw_value` and returns an object whose
        type matches the type described by the element.
        """
        if self.strict and not isinstance(raw_value, self.native_type):
            return NotUnserializable
        return raw_value

    def validate(self, context=None):
        """
        Returns `True` when the element is valid and `False` otherwise, and
        sets :attr:`is_valid` to the returned value.

        If any validators have been defined for this element, each validator is
        called with the element and the given `context` (which defaults to
        `None`). If any validator returns `False`, the element will be
        considered invalid.

        If no validators have been defined, the element will be considered
        invalid if :attr:`value` is :data:`~relief.Unspecified` or
        :data:`~relief.NotUnserializable`.
        """
        if context is None:
            context = {}
        if self.validators:
            self.is_valid = all(
                validator(self, context) for validator in self.validators
            )
        else:
            self.is_valid = self.value not in [Unspecified, NotUnserializable]
        return self.is_valid


class Container(Element):
    member_schema = None

    @class_cloner
    def of(cls, schema):
        cls.member_schema = schema
        return cls

    def __init__(self, value=Unspecified):
        self._state = Unspecified
        super(Container, self).__init__(value)
        if self.member_schema is None:
            raise TypeError("member_schema is unknown")

    def set(self, raw_value):
        self.raw_value = raw_value
        self._state = None
        if raw_value is Unspecified:
            self._state = Unspecified
            self._set_value(raw_value)
        else:
            unserialized = self.unserialize(raw_value)
            if unserialized is NotUnserializable:
                self._state = NotUnserializable
            else:
                self._set_value(unserialized)
        self.is_valid = None
