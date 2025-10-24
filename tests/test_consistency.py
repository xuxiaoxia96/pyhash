"""
一致性测试 - 确保与原始实现一致
"""

from src.pyhash import my_hash
from hashlib import md5


def original_my_hash(obj) -> bytes:
    """原始递归实现（用于对比）"""
    if isinstance(obj, str):
        return md5(b"\x02" + obj.encode()).digest()
    elif isinstance(obj, (int, float)):
        return md5(b"\x01" + str(obj).encode()).digest()
    elif obj is None:
        return md5(b"\x00").digest()
    elif isinstance(obj, list):
        return md5(b"list" + b",".join(original_my_hash(item) for item in obj)).digest()
    elif isinstance(obj, dict):
        sorted_items = sorted(obj.items(), key=lambda x: str(x[0]))
        return md5(
            b"dict" + b",".join(original_my_hash(k) + original_my_hash(v) for k, v in sorted_items)
        ).digest()
    else:
        raise TypeError(f"Unsupported type: {type(obj)}")


class TestConsistencyWithOriginal:
    """与原始实现的一致性测试"""

    def test_basic_types_consistency(self):
        """基本类型一致性"""
        test_cases = [
            "test",
            123,
            3.14,
            None,
        ]

        for case in test_cases:
            original = original_my_hash(case)
            optimized = my_hash(case)
            assert original == optimized, f"Failed for: {case}"

    def test_list_consistency(self):
        """列表一致性"""
        test_cases = [
            [],
            [1, 2, 3],
        ]

        for case in test_cases:
            original = original_my_hash(case)
            optimized = my_hash(case)
            assert original == optimized, f"Failed for: {case}"

    def test_dict_consistency(self):
        """字典一致性"""
        test_cases = [
            {},
            {"a": 1},
            {"a": 1, "b": 2},
            {"z": 1, "a": 2},  # 测试排序
            {"nested": {"a": 1}, "list": [1, 2, 3]}
        ]

        for case in test_cases:
            original = original_my_hash(case)
            optimized = my_hash(case)
            assert original == optimized, f"Failed for: {case}"

    def test_complex_structure_consistency(self):
        """复杂结构一致性"""
        complex_obj = {
            "users": [
                {"name": "Alice", "age": 30, "tags": ["admin", "user"]},
                {"name": "Bob", "age": 25, "tags": ["user"]}
            ],
            "settings": {
                "theme": "dark",
                "notifications": True
            },
            "version": 1.0
        }

        original = original_my_hash(complex_obj)
        optimized = my_hash(complex_obj)

        assert original == optimized
        print(f"Complex structure hash: {original.hex()}")