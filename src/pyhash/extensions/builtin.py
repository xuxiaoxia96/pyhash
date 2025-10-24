"""
内置类型扩展

为Python常用的内置类型提供哈希支持，包括：
- datetime, date, time, timedelta
- Decimal
- Path (pathlib)
- UUID
- Enum
- dataclass

这些类型虽然不是基本类型，但非常常用，因此提供开箱即用的支持。
"""

import sys
from typing import Any
from ..core.registry import register_type


def enable_datetime_support() -> None:
    """
    启用 datetime 模块类型的哈希支持

    支持的类型：
    - datetime.datetime
    - datetime.date
    - datetime.time
    - datetime.timedelta

    注意：使用 ISO 格式字符串确保跨进程一致性
    """
    try:
        from datetime import datetime, date, time, timedelta

        @register_type(datetime)
        def hash_datetime(dt: datetime) -> bytes:
            # 使用ISO格式字符串，确保时区信息也被包含
            return dt.isoformat().encode("utf-8")

        @register_type(date)
        def hash_date(d: date) -> bytes:
            return d.isoformat().encode("utf-8")

        @register_type(time)
        def hash_time(t: time) -> bytes:
            return t.isoformat().encode("utf-8")

        @register_type(timedelta)
        def hash_timedelta(td: timedelta) -> bytes:
            # 转换为总秒数
            return f"timedelta({td.total_seconds()})".encode("utf-8")

    except ImportError:
        pass  # datetime 是标准库，不应该失败


def enable_decimal_support() -> None:
    """
    启用 Decimal 类型的哈希支持

    注意：使用字符串表示确保精度
    """
    try:
        from decimal import Decimal

        @register_type(Decimal)
        def hash_decimal(d: Decimal) -> bytes:
            # 使用字符串表示保持精度
            return f"Decimal({str(d)})".encode("utf-8")

    except ImportError:
        pass


def enable_path_support() -> None:
    """
    启用 pathlib.Path 类型的哈希支持

    注意：使用 POSIX 格式路径确保跨平台一致性
    """
    try:
        from pathlib import Path, PurePath

        @register_type(PurePath)  # Path 继承自 PurePath
        def hash_path(p: PurePath) -> bytes:
            # 使用 as_posix() 确保跨平台一致性
            return f"Path({p.as_posix()})".encode("utf-8")

    except ImportError:
        pass


def enable_uuid_support() -> None:
    """
    启用 UUID 类型的哈希支持
    """
    try:
        from uuid import UUID

        @register_type(UUID)
        def hash_uuid(u: UUID) -> bytes:
            # 使用标准字符串格式
            return f"UUID({str(u)})".encode("utf-8")

    except ImportError:
        pass


def enable_enum_support() -> None:
    """
    启用 Enum 类型的哈希支持

    注意：使用类名和值确保唯一性
    """
    try:
        from enum import Enum

        @register_type(Enum)
        def hash_enum(e: Enum) -> bytes:
            # 包含类名和值
            class_name = type(e).__name__
            return f"Enum({class_name}.{e.name})".encode("utf-8")

    except ImportError:
        pass


def enable_dataclass_support() -> None:
    """
    启用 dataclass 的通用哈希支持

    注意：dataclass 本身不是类型，这里提供了一个辅助函数
    实际使用时需要为具体的 dataclass 类注册
    """
    try:
        from dataclasses import is_dataclass, fields
        import json

        def make_dataclass_handler(cls):
            """为dataclass生成哈希处理函数"""
            @register_type(cls)
            def hash_dataclass(obj) -> bytes:
                if not is_dataclass(obj):
                    raise TypeError(f"{obj} is not a dataclass instance")

                # 提取所有字段的值
                field_dict = {f.name: getattr(obj, f.name) for f in fields(obj)}
                # 使用JSON序列化（需要字段值是可序列化的）
                class_name = type(obj).__name__
                content = json.dumps(field_dict, sort_keys=True, default=str)
                return f"dataclass({class_name},{content})".encode("utf-8")

            return hash_dataclass

        # 注意：这个函数不会自动注册所有dataclass，
        # 需要用户显式调用 make_dataclass_handler(MyDataClass)

    except ImportError:
        pass


def enable_numpy_support() -> None:
    """
    启用 NumPy 数组的哈希支持（可选）

    注意：需要安装 numpy
    """
    try:
        import numpy as np

        @register_type(np.ndarray)
        def hash_ndarray(arr: np.ndarray) -> bytes:
            # 使用 tobytes() 获取数组的二进制表示
            # 包含 shape 和 dtype 信息确保完整性
            shape_str = str(arr.shape)
            dtype_str = str(arr.dtype)
            data_bytes = arr.tobytes()
            return f"ndarray({shape_str},{dtype_str})".encode("utf-8") + data_bytes

    except ImportError:
        pass  # NumPy 不是标准库，允许失败


def enable_all_extensions() -> None:
    """
    启用所有内置类型扩展

    这会注册所有常用类型的哈希处理函数。
    如果某些库未安装，会自动跳过。

    推荐在应用启动时调用此函数。

    示例：
        from hash_optimizer.extensions import enable_all_extensions
        enable_all_extensions()

        # 现在可以直接哈希这些类型
        from hash_optimizer import my_hash
        from datetime import datetime

        hash_val = my_hash(datetime.now())
    """
    enable_datetime_support()
    enable_decimal_support()
    enable_path_support()
    enable_uuid_support()
    enable_enum_support()
    # enable_numpy_support()  # 可选，仅在需要时启用


# 自动启用标准库扩展（可选）
# 如果希望导入时自动启用，取消下面的注释：
# enable_all_extensions()
