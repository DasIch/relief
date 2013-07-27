# coding: utf-8
"""
    relief.utils.idd
    ~~~~~~~~~~~~~~~~

    :copyright: 2013 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
from weakref import WeakKeyDictionary
from collections import MutableMapping as MutableMappingBase

from relief._compat import iteritems


DELETED = object()


class InheritingDictDescriptor(object):
    def __init__(self, name, **values):
        self.name = name
        self.values = values
        self.cls_values_mapping = WeakKeyDictionary()

    def __get__(self, instance, cls):
        class_lookup = ClassLookup(self.name, cls, self)
        if instance is None:
            return class_lookup
        return InstanceLookup(
            instance.__dict__.setdefault(self.name, {}),
            class_lookup
        )

    def __set__(self, instance, value):
        instance.__dict__[self.name] = value


class MutableMapping(MutableMappingBase):
    def __len__(self):
        return sum(1 for _ in self)

    def __repr__(self):
        return '{%s}' % ', '.join(
            '%r: %r' % (key, value) for key, value in iteritems(self)
        )


class ClassLookup(MutableMapping):
    def __init__(self, attribute_name, base_cls, descriptor):
        self._attribute_name = attribute_name
        self._base_cls = base_cls
        self._descriptor = descriptor

    @property
    def _base_values(self):
        try:
            return self._descriptor.cls_values_mapping[self._base_cls]
        except KeyError:
            pass
        return self._descriptor.cls_values_mapping.setdefault(self._base_cls, {})

    def _all_values(self):
        for cls in self._base_cls.mro():
            attribute = cls.__dict__.get(self._attribute_name)
            if cls not in self._descriptor.cls_values_mapping:
                if attribute is None:
                    continue
                self._descriptor.cls_values_mapping.setdefault(cls, attribute.values)
            yield self._descriptor.cls_values_mapping[cls]

    def __getitem__(self, key):
        for values in self._all_values():
            try:
                value = values[key]
            except KeyError:
                continue
            if value is DELETED:
                raise KeyError(key)
            return value
        raise KeyError(key)

    def __setitem__(self, key, value):
        self._base_values[key] = value

    def __delitem__(self, key):
        self[key]
        self._base_values[key] = DELETED

    def __iter__(self):
        seen = set()
        for values in self._all_values():
            for key, value in iteritems(values):
                if key not in seen:
                    if value is not DELETED:
                        yield key
                    seen.add(key)


class InstanceLookup(MutableMapping):
    def __init__(self, instance_values, class_lookup):
        self._instance_values = instance_values
        self._class_lookup = class_lookup

    def __getitem__(self, key):
        try:
            value = self._instance_values[key]
        except KeyError:
            value = self._class_lookup[key]
        if value is DELETED:
            raise KeyError(key)
        return value

    def __setitem__(self, key, value):
        self._instance_values[key] = value

    def __delitem__(self, key):
        self[key]
        self._instance_values[key] = DELETED

    def __iter__(self):
        seen = set()
        for key, value in iteritems(self._instance_values):
            if value is not DELETED:
                yield key
            seen.add(key)
        for key, value in iteritems(self._class_lookup):
            if key not in seen:
                yield key
