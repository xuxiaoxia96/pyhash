"""
Hash Optimizer - 跨进程一致性哈希函数库

这个库提供了一个优化的哈希函数，解决了Python内置hash函数的以下问题：
1. 跨进程一致性 - 同一对象在不同进程中产生相同的哈希值
2. 容器支持 - 支持 dict、list、set 等容器类型
3. 高性能 - 通过LRU缓存和栈迭代优化性能
4. 可扩展 - 支持自定义类型的哈希计算

主要特性：
- ✓ 性能优化：LRU缓存、栈迭代、高效序列化
- ✓ 递归限制解决：不受Python递归深度限制
- ✓ 类型扩展：灵活的类型注册机制

快速开始：
    >>> from hash_optimizer import my_hash
    >>> my_hash("hello")  # 字符串
    b'\\x5d\\x41\\x40...'
    >>> my_hash([1, 2, 3])  # 列表
    b'\\x4e\\xd9\\x40...'
    >>> my_hash({'a': 1})  # 字典
    b'\\x8f\\x14\\x47...'

自定义类型：
    >>> from hash_optimizer import register_type
    >>>
    >>> class Point:
    ...     def __init__(self, x, y):
    ...         self.x, self.y = x, y
    ...     def __hash_bytes__(self):
    ...         return f"Point({self.x},{self.y})".encode()
    >>>
    >>> my_hash(Point(1, 2))
    b'\\x9a\\x8b\\xc3...'

版本: 1.0.0
作者: XuShaoshen
许可: MIT
"""

__version__ = "1.0.0"
__all__ = [
    # 核心函数
    "my_hash",
    "Hasher",
    # 类型注册
    "register_type",
    "TypeRegistry",
    "HashableProtocol",
    # 扩展
    "extensions",
]
__author__ = "XuShaoshen"

from .core.hasher import Hasher, my_hash
from .core.registry import TypeRegistry, HashableProtocol, register_type
from . import extensions