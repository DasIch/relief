# coding: utf-8
"""
    tests.test_utils
    ~~~~~~~~~~~~~~~~

    :copyright: 2013 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
import sys
import inspect

import pytest

from relief.utils import class_cloner, InheritingDictDescriptor



class TestClassCloner(object):
    class Foo(object):
        @class_cloner
        def method(cls):
            """Documentation"""
            return cls

    def test_wraps_unbound_correctly(self):
        unbound = self.Foo.method

        assert unbound.__name__ == "method"
        assert unbound.__module__ == "tests.test_utils"
        assert unbound.__doc__ == "Documentation"
        if sys.version_info < (3, 0):
            assert issubclass(unbound.im_self, self.Foo)
            assert inspect.isfunction(unbound.im_func)

    def test_wraps_bound_correctly(self):
        instance = self.Foo()
        bound = instance.method
        assert bound.__name__ == "method"
        assert bound.__module__ == "tests.test_utils"
        assert bound.__doc__ == "Documentation"
        if sys.version_info < (3, 0):
            assert issubclass(bound.im_self, self.Foo)
            assert inspect.isfunction(bound.im_func)

    def test_called_with_clone(self):
        assert self.Foo.method() is not self.Foo


class TestInheritingDictDescriptor(object):
    def test_class_attribute_access(self):
        class Foo(object):
            properties = InheritingDictDescriptor('properties', foo=1)

        assert Foo.properties['foo'] == 1
        assert Foo.properties == {'foo': 1}
        assert list(Foo.properties) == ['foo']
        assert len(Foo.properties) == 1
        with pytest.raises(KeyError):
            Foo.properties['bar']

    def test_class_attribute_modification(self):
        class Foo(object):
            properties = InheritingDictDescriptor('properties', foo=1)

        Foo.properties['foo'] = 2
        assert Foo.properties['foo'] == 2
        assert Foo.properties == {'foo': 2}

        del Foo.properties['foo']
        with pytest.raises(KeyError):
            Foo.properties['foo']
        assert Foo.properties == {}
        assert list(Foo.properties) == []
        assert len(Foo.properties) == 0

    def test_class_attribute_deletion(self):
        class Foo(object):
            properties = InheritingDictDescriptor('properties', foo=1)

        del Foo.properties['foo']
        with pytest.raises(KeyError):
            Foo.properties['foo']
        assert Foo.properties == {}
        assert list(Foo.properties) == []
        assert len(Foo.properties) == 0

    def test_class_attribute_repr(self):
        class Foo(object):
            properties = InheritingDictDescriptor('properties', foo=1)

        assert repr(Foo.properties) == "{'foo': 1}"

    def test_subclass_attribute_access(self):
        class Foo(object):
            properties = InheritingDictDescriptor('properties', foo=1)

        class Bar(Foo):
            pass

        assert Bar.properties['foo'] == 1
        assert Bar.properties == {'foo': 1}
        with pytest.raises(KeyError):
            Bar.properties['bar']

    def test_subclass_attribute_modification(self):
        class Foo(object):
            properties = InheritingDictDescriptor('properties', foo=1)

        class Bar(Foo):
            pass

        Bar.properties['foo'] = 2
        assert Bar.properties['foo'] == 2
        assert Bar.properties == {'foo': 2}
        assert Foo.properties['foo'] == 1
        assert Foo.properties == {'foo': 1}

        del Bar.properties['foo']
        with pytest.raises(KeyError):
            Bar.properties['foo']
        assert Bar.properties == {}
        assert list(Bar.properties) == []
        assert len(Bar.properties) == 0
        assert Foo.properties['foo'] == 1
        assert Foo.properties == {'foo': 1}

    def test_subclass_attribute_deletion(self):
        class Foo(object):
            properties = InheritingDictDescriptor('properties', foo=1)

        class Bar(Foo):
            pass

        del Bar.properties['foo']
        with pytest.raises(KeyError):
            Bar.properties['foo']
        assert Bar.properties == {}
        assert list(Bar.properties) == []
        assert len(Bar.properties) == 0
        assert Foo.properties['foo'] == 1
        assert Foo.properties == {'foo': 1}

    def test_instance_attribute_access(self):
        class Foo(object):
            properties = InheritingDictDescriptor('properties', foo=1)

        foo = Foo()
        assert foo.properties['foo'] == 1
        assert foo.properties == {'foo': 1}

        with pytest.raises(KeyError):
            foo.properties['bar']

    def test_instance_attribute_modification(self):
        class Foo(object):
            properties = InheritingDictDescriptor('properties', foo=1)

        foo = Foo()
        foo.properties['foo'] = 2
        assert foo.properties['foo'] == 2
        assert foo.properties == {'foo': 2}
        assert Foo.properties['foo'] == 1
        assert Foo.properties == {'foo': 1}

        del foo.properties['foo']
        with pytest.raises(KeyError):
            foo.properties['foo']
        assert foo.properties == {}
        assert list(foo.properties) == []
        assert len(foo.properties) == 0
        assert Foo.properties['foo'] == 1
        assert Foo.properties == {'foo': 1}

    def test_instance_attribute_deletion(self):
        class Foo(object):
            properties = InheritingDictDescriptor('properties', foo=1)

        foo = Foo()
        del foo.properties['foo']
        with pytest.raises(KeyError):
            foo.properties['foo']
        assert foo.properties == {}
        assert list(foo.properties) == []
        assert len(foo.properties) == 0
        assert Foo.properties['foo'] == 1
        assert Foo.properties == {'foo': 1}

    def test_instance_attribute_repr(self):
        class Foo(object):
            properties = InheritingDictDescriptor('properties', foo=1)

        foo = Foo()
        assert repr(foo.properties) == "{'foo': 1}"
