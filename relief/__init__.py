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


__version__ = "0.2.0"
__version_info__ = (0, 2, 0)


__all__ = [
    # constants
    "Unspecified", "NotUnserializable",
    # core
    "Element",
    # scalars
    "Boolean", "Integer", "Float", "Complex", "Unicode", "Bytes",
    # mappings
    "Dict", "OrderedDict", "Form",
    # sequences
    "Tuple", "List"
]
