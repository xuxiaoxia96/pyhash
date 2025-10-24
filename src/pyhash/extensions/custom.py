"""
自定义类型工具

提供便捷的装饰器和工具函数，帮助快速为自定义类型添加哈希支持。

主要工具：
1. auto_hash_by_attrs: 基于指定属性自动生成哈希
2. auto_hash_by_dict: 基于对象的 __dict__ 生成哈希
3. auto_hash_by_json: 基于JSON序列化生成哈希

这些工具简化了自定义类型的哈希实现，无需手动编写 __hash_bytes__ 方法。
"""

import json
from typing import Tuple, Any, Callable
from functools import wraps
from ..core.registry import register_type


def auto_hash_by_attrs(*attr_names: str):
    """
    装饰器：基于指定属性自动生成哈希

    这个装饰器会自动为类添加 __hash_bytes__ 方法，
    该方法基于指定的属性生成哈希值。

    Args:
        *attr_names: 要包含在哈希中的属性名

    Returns:
        装饰器函数

    示例：
        @auto_hash_by_attrs('x', 'y')
        class Point:
            def __init__(self, x, y):
                self.x = x
                self.y = y

        # Point 自动支持哈希
        from hash_optimizer import my_hash
        p = Point(10, 20)
        hash_val = my_hash(p)

    注意：
        - 属性值本身必须是可哈希的（支持的基本类型或已注册类型）
        - 属性顺序会影响哈希值
        - 缺失的属性会被视为 None
    """
    def decorator(cls):
        # 保存原始类名
        class_name = cls.__name__

        # 定义 __hash_bytes__ 方法
        def __hash_bytes__(self) -> bytes:
            # 收集所有指定属性的值
            values = []
            for attr_name in attr_names:
                value = getattr(self, attr_name, None)
                values.append(value)

            # 序列化为字符串
            # 使用JSON确保一致性（需要值是JSON可序列化的）
            try:
                values_str = json.dumps(values, sort_keys=True, default=str)
            except (TypeError, ValueError):
                # 如果JSON序列化失败，使用repr
                values_str = repr(values)

            return f"{class_name}({values_str})".encode("utf-8")

        # 将方法添加到类
        cls.__hash_bytes__ = __hash_bytes__
        return cls

    return decorator


def auto_hash_by_dict(exclude_attrs: Tuple[str, ...] = ()):
    """
    装饰器：基于对象的 __dict__ 生成哈希

    这个装饰器会使用对象的所有实例属性生成哈希。

    Args:
        exclude_attrs: 要排除的属性名元组

    Returns:
        装饰器函数

    示例：
        @auto_hash_by_dict(exclude_attrs=('_cache',))
        class Person:
            def __init__(self, name, age):
                self.name = name
                self.age = age
                self._cache = {}  # 内部缓存，不参与哈希

        from hash_optimizer import my_hash
        p = Person("Alice", 30)
        hash_val = my_hash(p)

    注意：
        - 所有实例属性都会参与哈希（除了excluded）
        - 属性按名称排序，确保顺序一致
        - 私有属性（_开头）建议排除
    """
    def decorator(cls):
        class_name = cls.__name__

        def __hash_bytes__(self) -> bytes:
            # 获取所有实例属性
            obj_dict = {k: v for k, v in self.__dict__.items()
                       if k not in exclude_attrs}

            # 按键排序
            sorted_items = sorted(obj_dict.items())

            # 序列化
            try:
                content = json.dumps(sorted_items, sort_keys=True, default=str)
            except (TypeError, ValueError):
                content = repr(sorted_items)

            return f"{class_name}({content})".encode("utf-8")

        cls.__hash_bytes__ = __hash_bytes__
        return cls

    return decorator


def auto_hash_by_json(key_func: Callable[[Any], dict] = None):
    """
    装饰器：基于JSON序列化生成哈希

    这个装饰器允许自定义如何将对象转换为可序列化的字典。

    Args:
        key_func: 将对象转换为字典的函数（可选）
                 如果不提供，会尝试使用 obj.__dict__

    Returns:
        装饰器函数

    示例：
        @auto_hash_by_json(lambda obj: {'name': obj.name, 'age': obj.age})
        class Person:
            def __init__(self, name, age):
                self.name = name
                self.age = age

        # 或使用默认的 __dict__
        @auto_hash_by_json()
        class Point:
            def __init__(self, x, y):
                self.x = x
                self.y = y

        from hash_optimizer import my_hash
        person = Person("Alice", 30)
        hash_val = my_hash(person)
    """
    def decorator(cls):
        class_name = cls.__name__

        def __hash_bytes__(self) -> bytes:
            # 获取对象的字典表示
            if key_func is not None:
                obj_dict = key_func(self)
            else:
                obj_dict = self.__dict__

            # JSON序列化（确保键排序）
            try:
                json_str = json.dumps(obj_dict, sort_keys=True, default=str)
            except (TypeError, ValueError) as e:
                raise TypeError(
                    f"Failed to serialize {class_name} to JSON: {e}. "
                    f"Consider providing a custom key_func."
                ) from e

            return f"{class_name}({json_str})".encode("utf-8")

        cls.__hash_bytes__ = __hash_bytes__
        return cls

    return decorator


def make_hash_by_method(method_name: str):
    """
    装饰器工厂：基于对象的特定方法生成哈希

    Args:
        method_name: 方法名，该方法应返回 bytes

    Returns:
        装饰器函数

    示例：
        @make_hash_by_method('to_bytes')
        class MyClass:
            def to_bytes(self) -> bytes:
                return b"my_data"

        from hash_optimizer import my_hash
        obj = MyClass()
        hash_val = my_hash(obj)
    """
    def decorator(cls):
        def __hash_bytes__(self) -> bytes:
            method = getattr(self, method_name, None)
            if method is None:
                raise AttributeError(
                    f"{cls.__name__} must have a {method_name} method"
                )
            if not callable(method):
                raise TypeError(
                    f"{cls.__name__}.{method_name} must be callable"
                )

            result = method()
            if not isinstance(result, bytes):
                raise TypeError(
                    f"{cls.__name__}.{method_name} must return bytes, "
                    f"got {type(result).__name__}"
                )
            return result

        cls.__hash_bytes__ = __hash_bytes__
        return cls

    return decorator


def register_simple_class(cls, *attr_names):
    """
    便捷函数：为简单类注册哈希（不使用装饰器）

    适用于无法修改类定义的情况。

    Args:
        cls: 要注册的类
        *attr_names: 要包含在哈希中的属性名

    示例：
        class Point:
            def __init__(self, x, y):
                self.x = x
                self.y = y

        # 注册Point类的哈希
        from hash_optimizer.extensions import register_simple_class
        register_simple_class(Point, 'x', 'y')

        from hash_optimizer import my_hash
        p = Point(10, 20)
        hash_val = my_hash(p)
    """
    class_name = cls.__name__

    @register_type(cls)
    def hash_handler(obj) -> bytes:
        values = [getattr(obj, attr, None) for attr in attr_names]
        try:
            values_str = json.dumps(values, sort_keys=True, default=str)
        except (TypeError, ValueError):
            values_str = repr(values)
        return f"{class_name}({values_str})".encode("utf-8")

    return hash_handler
