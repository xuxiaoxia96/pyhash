"""
序列化器基类和工具

提供可重用的序列化策略，用于自定义类型的哈希生成。

序列化器负责将对象转换为字节序列，然后由哈希函数处理。
"""

from abc import ABC, abstractmethod
from typing import Any, Type
import json
import struct


class HashSerializer(ABC):
    """
    哈希序列化器抽象基类

    子类需要实现 serialize() 方法，将对象转换为 bytes。

    使用示例：
        class PointSerializer(HashSerializer):
            def serialize(self, obj) -> bytes:
                return f"Point({obj.x},{obj.y})".encode()

        serializer = PointSerializer()
        hash_bytes = serializer.serialize(my_point)
    """

    @abstractmethod
    def serialize(self, obj: Any) -> bytes:
        """
        将对象序列化为字节

        Args:
            obj: 要序列化的对象

        Returns:
            字节序列

        Raises:
            应该抛出明确的异常说明序列化失败原因
        """
        pass

    def __call__(self, obj: Any) -> bytes:
        """允许序列化器作为函数使用"""
        return self.serialize(obj)


class JSONSerializer(HashSerializer):
    """
    基于JSON的序列化器

    将对象转换为JSON字符串，然后编码为字节。

    参数：
        key_func: 将对象转换为可JSON序列化字典的函数（可选）
        sort_keys: 是否排序字典键（默认True，确保一致性）
        default: JSON编码器的default函数
    """

    def __init__(self, key_func=None, sort_keys=True, default=str):
        self.key_func = key_func
        self.sort_keys = sort_keys
        self.default = default

    def serialize(self, obj: Any) -> bytes:
        # 转换为字典
        if self.key_func:
            obj_dict = self.key_func(obj)
        elif hasattr(obj, '__dict__'):
            obj_dict = obj.__dict__
        else:
            raise TypeError(f"Cannot serialize {type(obj).__name__} to JSON")

        # JSON序列化
        json_str = json.dumps(
            obj_dict,
            sort_keys=self.sort_keys,
            default=self.default
        )
        return json_str.encode("utf-8")


class AttrSerializer(HashSerializer):
    """
    基于属性的序列化器

    提取对象的指定属性，序列化为字节。

    参数：
        *attr_names: 要序列化的属性名
        class_name: 类名前缀（可选）
    """

    def __init__(self, *attr_names, class_name=None):
        self.attr_names = attr_names
        self.class_name = class_name

    def serialize(self, obj: Any) -> bytes:
        # 提取属性值
        values = []
        for attr_name in self.attr_names:
            if not hasattr(obj, attr_name):
                raise AttributeError(
                    f"{type(obj).__name__} has no attribute '{attr_name}'"
                )
            values.append(getattr(obj, attr_name))

        # 序列化
        class_prefix = self.class_name or type(obj).__name__
        values_str = json.dumps(values, default=str)
        return f"{class_prefix}({values_str})".encode("utf-8")


class StructSerializer(HashSerializer):
    """
    基于struct的序列化器

    使用Python的struct模块将对象序列化为紧凑的二进制格式。
    适用于固定格式的数据结构。

    参数：
        format_string: struct格式字符串（如 ">iff" 表示big-endian, int, float, float）
        extractor: 从对象提取值的函数，返回元组

    示例：
        # 序列化一个包含(int, float, float)的Point3D
        serializer = StructSerializer(
            ">iff",
            lambda obj: (obj.id, obj.x, obj.y)
        )
    """

    def __init__(self, format_string: str, extractor):
        self.format_string = format_string
        self.extractor = extractor

    def serialize(self, obj: Any) -> bytes:
        values = self.extractor(obj)
        return struct.pack(self.format_string, *values)


class ChainSerializer(HashSerializer):
    """
    链式序列化器

    组合多个序列化器，按顺序应用。

    示例：
        serializer = ChainSerializer(
            lambda obj: obj.to_dict(),  # 第一步：转为字典
            JSONSerializer()             # 第二步：JSON序列化
        )
    """

    def __init__(self, *serializers):
        self.serializers = serializers

    def serialize(self, obj: Any) -> bytes:
        result = obj
        for serializer in self.serializers:
            if callable(serializer):
                result = serializer(result)
            else:
                raise TypeError(f"Serializer must be callable, got {type(serializer)}")

        if not isinstance(result, bytes):
            raise TypeError(
                f"Chain must end with bytes, got {type(result).__name__}"
            )
        return result


# ============================================================================
# 预定义的常用序列化器
# ============================================================================

def make_json_serializer(key_func=None):
    """
    工厂函数：创建JSON序列化器

    Args:
        key_func: 对象到字典的转换函数

    Returns:
        JSONSerializer实例
    """
    return JSONSerializer(key_func=key_func)


def make_attr_serializer(*attr_names):
    """
    工厂函数：创建属性序列化器

    Args:
        *attr_names: 属性名

    Returns:
        AttrSerializer实例
    """
    return AttrSerializer(*attr_names)


def make_method_serializer(method_name: str):
    """
    工厂函数：创建基于方法的序列化器

    Args:
        method_name: 方法名（应返回bytes）

    Returns:
        序列化器函数
    """
    class MethodSerializer(HashSerializer):
        def serialize(self, obj: Any) -> bytes:
            method = getattr(obj, method_name, None)
            if method is None:
                raise AttributeError(
                    f"{type(obj).__name__} has no method '{method_name}'"
                )
            result = method()
            if not isinstance(result, bytes):
                raise TypeError(
                    f"{method_name} must return bytes, got {type(result).__name__}"
                )
            return result

    return MethodSerializer()
