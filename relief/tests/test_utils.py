# coding: utf-8
"""
    relief.tests.test_utils
    ~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2013 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
import sys
import inspect

from relief.utils import class_cloner


class TestClassCloner(object):
    class Foo(object):
        @class_cloner
        def method(cls):
            """Documentation"""
            return cls

    def test_wraps_unbound_correctly(self):
        unbound = self.Foo.method

        assert unbound.__name__ == "method"
        assert unbound.__module__ == "relief.tests.test_utils"
        assert unbound.__doc__ == "Documentation"
        if sys.version_info < (3, 0):
            assert issubclass(unbound.im_self, self.Foo)
            assert inspect.isfunction(unbound.im_func)

    def test_wraps_bound_correctly(self):
        instance = self.Foo()
        bound = instance.method
        assert bound.__name__ == "method"
        assert bound.__module__ == "relief.tests.test_utils"
        assert bound.__doc__ == "Documentation"
        if sys.version_info < (3, 0):
            assert issubclass(bound.im_self, self.Foo)
            assert inspect.isfunction(bound.im_func)

    def test_called_with_clone(self):
        assert self.Foo.method() is not self.Foo
