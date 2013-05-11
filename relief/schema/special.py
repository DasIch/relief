# coding: utf-8
"""
	relief.schema.special
	~~~~~~~~~~~~~~~~~~~~~

	:copyright: 2013 by Daniel Neuhäuser
	:license: BSD, see LICENSE.rst for details
"""
import sys
import inspect
from collections import OrderedDict

from relief.utils import inheritable_property
from relief.constants import Unspecified, NotUnserializable
from relief.schema.core import Element
from relief.schema.scalars import Unicode

import six


class FormMeta(type):
	def __new__(cls, cls_name, bases, cls_attributes):
		member_schema = cls_attributes["member_schema"] = OrderedDict()
		for base in reversed(bases):
			member_schema.update(getattr(base, "member_schema", {}))

		if isinstance(cls_attributes, OrderedDict):
			# Python 3.x __prepare__ works.
			member_schema_is_ordered = True
			member_schema.update(cls._get_elements(cls_attributes))
		else:
			# This ensures that `member_schema` is ordered by the order in
			# which the members are defined in the source code, if you are
			# using a Python 2.x. You are not expected to understand how this
			# works.
			def get_index(name):
				# Should provide random order.
				return 0
			member_schema_is_ordered = False
			try:
				# CPython implementation detail that not every implementation
				# has to support. CPython and PyPy should both support it
				# though.
				sys._getframe
			except AttributeError:
				pass
			else:
				defining_frame = sys._getframe(1)
				# class bodies are stored stored as code objects, with the name
				# of their class as `co_name`, in the constants (`co_consts`)
				# in the code object of the frame (`f_code`) in which the class
				# is defined.
				for constant in reversed(defining_frame.f_code.co_consts):
					if inspect.iscode(constant) and constant.co_name == cls_name:
						def get_index(name, _names=constant.co_names):
							return _names.index(name)
						member_schema_is_ordered = True
						break
			schemas = []
			for name, element in cls._get_elements(cls_attributes):
				schemas.append((get_index(name), name, element))
			member_schema.update(
				(name, element) for _, name, element in sorted(schemas)
			)
		# This should be useful for debugging in case someone is wondering why
		# the ordering is off.
		cls_attributes["_member_schema_is_ordered"] = member_schema_is_ordered
		return super(FormMeta, cls).__new__(
			cls, cls_name, bases, cls_attributes
		)

	def __prepare__(name, bases, **kwargs):
		return OrderedDict()

	@staticmethod
	def _get_elements(attributes):
		for name, attribute in six.iteritems(attributes):
			if isinstance(attribute, type) and issubclass(attribute, Element):
				yield name, attribute


class Form(six.with_metaclass(FormMeta, Element)):
	def __new__(cls, *args, **kwargs):
		self = super(Form, cls).__new__(cls)
		self._elements = OrderedDict(
			(name, element()) for name, element in six.iteritems(self.member_schema)
		)
		return self

	@inheritable_property
	def state(self):
		missing = object()
		if getattr(self, "_state", missing) is not missing:
			return self._state
		elif len(self) != len(self.raw_value):
			return NotUnserializable

	@inheritable_property
	def value(self):
		if self.state is not None:
			return self.state
		result = OrderedDict()
		for key, element in self.iteritems():
			if element.value is NotUnserializable:
				return NotUnserializable
			result[key] = element.value
		return result

	def set_value(self, new_value, propagate=True):
		if new_value is Unspecified:
			del self.value
		elif new_value is NotUnserializable:
			del self.state
		else:
			self.state = None
			if len(new_value) != len(self) or any(key not in self for key in new_value):
				raise TypeError()
			for key, value in six.iteritems(new_value):
				self[key].set_value(value, propagate=propagate)

	@value.deleter
	def value(self):
		for element in six.itervalues(self):
			del element.value
		self.state = Unspecified

	@inheritable_property
	def raw_value(self):
		if getattr(self, "_raw_value", None) is not None:
			result = self._raw_value
			for key, element in self.iteritems():
				if key not in result or result[key] != element.raw_value:
					result[key] = element.raw_value
			return result
		return OrderedDict(
			(key, element.raw_value) for key, element in self.iteritems()
		)

	def set_raw_value(self, raw_values, propagate=True):
		assert False
		if raw_values is Unspecified:
			del self.raw_value
		else:
			if len(raw_values) != len(self):
				self._raw_value = raw_values
			for key, element in self.iteritems():
				if key in raw_values:
					element.set_raw_value(raw_values[key], propagate=propagate)

	@raw_value.deleter
	def raw_value(self):
		if hasattr(self, "_raw_value"):
			del self._raw_value
		for element in six.itervalues(self):
			del element.raw_value

	def __getitem__(self, key):
		return self._elements[key]

	def __setitem__(self, key, value):
		if key not in self:
			raise KeyError(key)
		self._elements[key].value = value

	def __contains__(self, key):
		return key in self._elements

	def __len__(self):
		return len(self._elements)

	def __iter__(self):
		return iter(self._elements)

	if sys.version_info < (3, 0):
		def iterkeys(self):
			return self._elements.iterkeys()

		def itervalues(self):
			return self._elements.itervalues()

		def iteritems(self):
			return self._elements.iteritems()

	def keys(self):
		return self._elements.keys()

	def values(self):
		return self._elements.values()

	def items(self):
		return self._elements.items()

	def validate(self, context=None):
		if context is None:
			context = {}
		self.is_valid = True
		for element in six.itervalues(self):
			self.is_valid &= element.validate(context=context)
		self.is_valid &= super(Form, self).validate(context=context)
		return self.is_valid

	def traverse(self, prefix=None):
		if prefix is None:
			prefix = []
		for key, element in six.iteritems(self):
			yield prefix + [key], element