Tutorial
========

Relief allows you to easily model data structures using schemas. A very simple
schema is :class:`relief.Integer`, which represents a single
integer.


Basics
------

You can create an instance of :class:`~relief.Integer` to
validate objects, to find out whether they match your schema.

.. doctest::

   >>> from relief import Integer
   >>> element = Integer()
   >>> element.set(1)
   >>> element.validate()
   True


Conversion
----------

Quite often you deal with data that quite but not exactly matches a schema,
especially when dealing with user input. A lot of the time this data can be
converted to something that does match your schema, such as the string ``"1"``
to the integer ``1``. Relief will do that for your by default:

.. doctest::

   >>> element.set('1')
   >>> element.validate()
   True

In order to work with the converted data you can get it using the
:attr:`~relief.Element.value` attribute, the raw value you passed to the schema
is available as :attr:`~relief.Element.raw_value`.

.. doctest::

   >>> element.value
   1
   >>> element.raw_value
   '1'

Sometimes you don't want any conversion to happen though, in these cases you
want a schema that behaves differently. Conversion behaviour is controlled with
the :attr:`~relief.Element.strict` class attribute, we could change that by
creating subclass of :class:`~relief.Integer`, this however would add quite a
bit of syntax overhead for something so frequently needed. This problem is
solved by the :meth:`~relief.Element.using` class method.

.. doctest::

   >>> StrictInteger = Integer.using(strict=True)
   >>> element = StrictInteger()
   >>> element.set("1")
   >>> element.validate()
   False

:meth:`~relief.Element.using` provides a convenient way to create subclasses
purely for the purpose of changing class attributes. Subclassing schemas to
change their behaviour in some way is a common pattern within Relief you need
to make yourself familiar with.


Validation
----------

Before we start modelling more complex data structures, let's take a look at
another important feature: validation.

Validation is performed by using validators, these are callables that take a
schema instance and a context (which we ignore for now), and return either
`True` or `False` to signal whether the element was validated successfully or
not.

.. doctest::

   >>> from relief import Unspecified, NotUnserializable
   >>> def is_greater_than_3(element, context):
   ...     if element.value is Unspecified:
   ...         return False
   ...     elif element.value is NotUnserializable:
   ...         return False
   ...     return element.value > 3

As you can see a validator has to handle three cases, if
:meth:`~relief.Element.validate` is called before a value has been set the
value is :data:`relief.Unspecified`, if a value has been set but it couldn't be
converted it's :data:`relief.NotUnserializable` and if it's neither of these
it's a value that ignoring validatation would be considered valid.

In order to use such a validator you create a new schema that includes the
validator using :meth:`~relief.Element.validated_by`, similar to how we created
a new schema with :meth:`~relief.Element.using`.

.. doctest::

   >>> element = Integer.validated_by([is_greater_than_3])()
   >>> element.set(4)
   >>> element.validate()
   True
   >>> element.set(3)
   >>> element.validate()
   False


Containers
----------

When modelling data structures most of the time you work with containers,
meaning data structures that contain other data structures to form information.
Corresponding with that such data structures are modelled in Relief with
schemas, that contain other schemas.

.. doctest::

   >>> from relief import List
   >>> ListOfIntegers = List.of(Integer)
   >>> element = ListOfIntegers()
   >>> element.set([1, 2, 3])
   >>> element.validate()
   True

Schemas that contain other schemas are *containers* -- like
:class:`relief.List` which is used in the above example -- have an
:meth:`~relief.Container.of` class method. :meth:`~relief.Container.of` works
similar to :meth:`~relief.Element.using` or
:meth:`~relief.Element.validated_by` in that it returns a modified schema,
unlike these, which *can be called* to perform modifications,
:meth:`~relief.Container.of` *must be called* to create a usable schema.

:class:`~relief.List` just as any other container is abstract and attempting to
use it without defining what it contains, will raise an exception.

.. doctest::

   >>> List()
   Traceback (most recent call last):
   ...
   TypeError: member_schema is unknown


To learn more about which schemas are available, take a look at the
:mod:`relief` module.
