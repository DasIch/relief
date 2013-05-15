Tutorial
========

Data in relief is modeled using *schemas*. There are several different kinds
you can use. One of them is :class:`relief.Integer`. :class:`~relief.Integer`
represents an :func:`int`, in order to use it you create an instance, instances
of schemas are referred to as *elements*:

.. doctest::

    >>> from relief import Integer

    >>> element = Integer()

After creating an element it's `value` is `Unspecified`:

.. doctest::

    >>> element.value
    Unspecified

Furthermore the element does not know whether it is valid because it was not
validated and so `is_valid` is `None`::

    >>> element.is_valid
    None

To change that we can set a value and validate it:

.. doctest::

    >>> element.set(1)
    >>> element.validate()
    True
    >>> element.is_valid
    True
    >>> element.value
    1

This was not very interesting, we know that ``1`` is an integer and that it is
a valid value. So what happens if we set the element to something that is not an
integer?

.. doctest::

    >>> element.set('1')
    >>> element.validate()
    True
    >>> element.value
    1

Wait, what? ``"1"`` is not an integer so this shouldn't happen should it? What
happens here is that the *raw value* ``"1"`` is assumed to be serialized and Relief
attempts to unserialize it. In the case of an integer, this basically amounts to
trying if ``int(raw_value)`` works, this `raw_value` remains accessible as an
attribute of `element`:

.. doctest::

    >>> element.raw_value
    '1'

Now we have seen what happens when we work with values that are described by
our schema but what happens if we set our :class:`~relief.Integer` element to
something that cannot be unserialized?

.. doctest::

    >>> element.set('Hello, World!')
    >>> element.validate()
    False
    >>> element.value
    NotUnserializable
    >>> element.raw_value
    'Hello, World!'

So what happens is pretty much what one would assume beforehand, validation
fails and the raw value cannot be unserialized. Raw values that cannot be
unserialized are represented with the `NotUnserializable` constant.

Now that we have learned about :class:`relief.Integer` what about other
schemas? Turns out they all work pretty much the same take a look at the
:mod:`relief` module for an overview.
