Changelog
=========

Version 2.1.0
-------------

- Split :class:`Element` up into :class:`BaseElement`, :class:`NativeMixin`,
  :class:`ValidatedByMixin` and :class:`DefaultMixin`.
- Add :class:`Maybe`.
- Add :class:`relief.validation.MatchesRegex`.
- Add :class:`relief.validation.IsURL`.

Version 2.0.0
-------------

- Pass :data:`Unspecified` to :meth:`Element.serialize` and
  :meth:`Element.serialize`, when setting values.
- Don't ignore defaults of members in :class:`Form`.

Version 1.0.0
-------------

- Turn :meth:`Element.unserialize` into an instance method.
- Rename :meth:`Element.set` to `Element.set_from_raw`.
- Add :meth:`Element.serialize` and :meth:`Element.set_from_native`.
- Make :data:`Unspecified` and :data:`NotUnserializable` false-ish.
- Make ``unicode(Unspecified)`` and ``unicode(NotUnserializable)`` return an
  empty string.
- Make ``bytes(Unspecified)`` and ``bytes(NotUnserializable)`` return an
  empty string.

Version 0.2.0
-------------

- Values in :class:`~relief.Form` structures can now be validated by
  subclassing :class:`~relief.Form` and adding `validate_{key}` methods.

Version 0.1.1
-------------

- Removed mention of being able to mutate :class:`relief.Dict` and
  :class:`relief.Form`.

Version 0.1.0
-------------

Initial release.
