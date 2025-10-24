"""
类型注册测试
"""

import pytest
from src.pyhash import TypeRegistry, register_type, my_hash


class TestTypeRegistry:
    """类型注册表测试"""

    def test_basic_registration(self):
        """测试基本类型注册"""
        registry = TypeRegistry()

        class CustomType:
            def __init__(self, value):
                self.value = value

        def handler(obj):
            return f"Custom:{obj.value}".encode()

        registry.register(CustomType, handler)

        obj = CustomType(42)
        assert registry.get_handler(obj) == handler

    def test_protocol_implementation(self):
        """测试协议实现"""

        class Point:
            def __init__(self, x, y):
                self.x = x
                self.y = y

            def __hash_bytes__(self):
                return f"Point({self.x},{self.y})".encode()

        registry = TypeRegistry()
        point = Point(10, 20)

        handler = registry.get_handler(point)
        assert handler is not None
        assert handler(point) == b"Point(10,20)"

    def test_subclass_handling(self):
        """测试子类处理"""
        registry = TypeRegistry()

        class BaseClass:
            pass

        class DerivedClass(BaseClass):
            pass

        def handler(obj):
            return b"base"

        registry.register(BaseClass, handler)

        derived_obj = DerivedClass()
        assert registry.get_handler(derived_obj) == handler


class TestRegisterTypeDecorator:
    """注册装饰器测试"""

    def test_decorator_registration(self):
        """测试装饰器注册"""

        class MyClass:
            def __init__(self, data):
                self.data = data

        @register_type(MyClass)
        def hash_myclass(obj):
            return obj.data.encode()

        obj = MyClass("hello")
        result = my_hash(obj)
        assert len(result) == 16  # 应该是有效的MD5哈希