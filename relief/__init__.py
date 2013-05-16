# coding: utf-8
"""
    relief
    ~~~~~~

    :copyright: 2013 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
from relief.constants import Unspecified, NotUnserializable
from relief.schema.core import Element
from relief.schema.scalars import (
    Boolean, Integer, Float, Complex, Unicode, Bytes
)
from relief.schema.mappings import Dict, OrderedDict, Form
from relief.schema.sequences import Tuple, List


__version__ = "0.0.0-dev"
__version_info__ = (0, 0, 0)


__all__ = [
    "Unspecified", "NotUnserializable", "Element", "Boolean", "Integer",
    "Float", "Complex", "Unicode", "Bytes", "Form", "Dict", "OrderedDict",
    "Tuple", "List"
]
