"""
核心模块

包含哈希函数的核心实现和类型注册机制
"""

from .hasher import Hasher, my_hash
from .registry import TypeRegistry, HashableProtocol, register_type

__all__ = [
    "Hasher",
    "my_hash",
    "TypeRegistry",
    "HashableProtocol",
    "register_type",
]
