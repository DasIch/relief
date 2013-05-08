# coding: utf-8
"""
    relief.tests.test_utils
    ~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2013 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
import inspect

from relief.utils import class_cloner, unimethod, inheritable_property

import py.test


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
        assert unbound.im_class is type
        assert unbound.im_self is self.Foo
        assert inspect.isfunction(unbound.im_func)

    def test_wraps_bound_correctly(self):
        instance = self.Foo()
        bound = instance.method
        assert bound.__name__ == "method"
        assert bound.__module__ == "relief.tests.test_utils"
        assert bound.__doc__ == "Documentation"
        assert bound.im_class is type
        assert bound.im_self is self.Foo
        assert inspect.isfunction(bound.im_func)

    def test_called_with_clone(self):
        assert self.Foo.method() is not self.Foo


class TestUniMethod(object):
    class Foo(object):
        @unimethod
        def method(cls, instance):
            """Documentation"""
            return cls, instance

    @py.test.mark.parametrize("wrapped", [Foo.method, Foo().method])
    def test_wrapping(self, wrapped):
        assert wrapped.__name__ == "method"
        assert wrapped.__module__ == "relief.tests.test_utils"
        assert wrapped.__doc__ == "Documentation"
        assert inspect.isfunction(wrapped.im_func)

    def test_unbound_wrapping(self):
        unbound = self.Foo.method
        assert unbound.im_class is type
        assert unbound.im_self is self.Foo

    def test_bound_wrapping(self):
        instance = self.Foo()
        bound = instance.method
        assert bound.im_class is self.Foo
        assert bound.im_self is instance

    def test_classmethod_behaviour(self):
        assert self.Foo.method() == (self.Foo, None)

    def test_instance_behaviour(self):
        instance = self.Foo()
        assert instance.method() == (self.Foo, instance)


class TestInheritableProperty(object):
    accessed = []

    class Foo(object):
        @property
        def spam(self):
            TestInheritableProperty.accessed.append("get")

        @spam.setter
        def spam(self, new_spam):
            TestInheritableProperty.accessed.append("set")

        @spam.deleter
        def spam(self):
            TestInheritableProperty.accessed.append("del")

    class BarGet(Foo):
        @inheritable_property
        def spam(self):
            pass

    class BarSet(Foo):
        @inheritable_property.setter
        def spam(self, new_spam):
            pass

    class BarDel(Foo):
        @inheritable_property.deleter
        def spam(self):
            pass

    @py.test.mark.parametrize(("cls", "accessed"), [
        (Foo, ["get", "set", "del"]),
        (BarGet, ["set", "del"]),
        (BarSet, ["get", "del"]),
        (BarDel, ["get", "set"])
    ])
    def test_access_methods(self, cls, accessed):
        instance = cls()
        instance.spam
        instance.spam = 1
        del instance.spam
        assert self.accessed == accessed
        del self.accessed[:]
