"""
类型注册机制
"""

from typing import Any, Dict, Callable, Optional, Protocol


class HashableProtocol(Protocol):
    """支持自定义类型实现此协议"""
    def __hash_bytes__(self) -> bytes:
        """返回对象的字节表示用于哈希计算"""
        ...


class TypeRegistry:
    """类型注册表 - 支持自定义类型的哈希计算"""

    def __init__(self):
        self._handlers: Dict[type, Callable[[Any], bytes]] = {}

    def register(self, type_: type, handler: Callable[[Any], bytes]):
        """注册类型的哈希处理函数

        Args:
            type_: 要注册的类型
            handler: 处理函数，接收对象返回bytes用于哈希
        """
        self._handlers[type_] = handler

    def get_handler(self, obj: Any) -> Optional[Callable[[Any], bytes]]:
        """获取对象类型的处理函数"""
        # 1. 检查是否实现了 __hash_bytes__ 协议
        if hasattr(obj, '__hash_bytes__') and callable(getattr(obj, '__hash_bytes__')):
            return lambda o: o.__hash_bytes__()

        # 2. 检查类型注册表
        obj_type = type(obj)
        if obj_type in self._handlers:
            return self._handlers[obj_type]

        # 3. 检查是否是注册类型的子类
        for registered_type, handler in self._handlers.items():
            if isinstance(obj, registered_type):
                return handler

        return None


# 全局类型注册表
_type_registry = TypeRegistry()


def register_type(type_: type):
    """装饰器：注册自定义类型的哈希函数

    使用示例：
        @register_type(MyClass)
        def hash_myclass(obj: MyClass) -> bytes:
            return obj.to_bytes()
    """
    def decorator(handler: Callable[[Any], bytes]):
        _type_registry.register(type_, handler)
        return handler
    return decorator