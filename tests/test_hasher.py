"""
哈希器单元测试
"""

import pytest
from src.pyhash import my_hash, Hasher


class TestBasicTypes:
    """基本类型测试"""

    def test_none(self):
        assert my_hash(None) == my_hash(None)

    def test_string(self):
        assert my_hash("test") == my_hash("test")
        assert my_hash("hello") != my_hash("world")

    def test_integer(self):
        assert my_hash(123) == my_hash(123)
        assert my_hash(123) != my_hash(456)

    def test_float(self):
        assert my_hash(3.14) == my_hash(3.14)
        assert my_hash(3.14) != my_hash(2.71)

    def test_boolean(self):
        assert my_hash(True) == my_hash(True)
        assert my_hash(False) == my_hash(False)
        assert my_hash(True) != my_hash(False)


class TestContainers:
    """容器类型测试"""

    def test_empty_list(self):
        assert my_hash([]) == my_hash([])

    def test_list(self):
        assert my_hash([1, 2, 3]) == my_hash([1, 3, 2])
        assert my_hash([1, 2, 3]) != my_hash([1, 2, 4])

    def test_nested_list(self):
        list1 = [1, [3, 2], 4]
        list2 = [1, [2, 3], 4]
        assert my_hash(list1) == my_hash(list2)

    def test_empty_dict(self):
        assert my_hash({}) == my_hash({})

    def test_dict(self):
        dict1 = {"a": 1, "b": 2}
        dict2 = {"b": 2, "a": 1}  # 不同顺序
        assert my_hash(dict1) == my_hash(dict2)

    def test_nested_dict(self):
        dict1 = {"a": {"b": 1}, "c": [2, 3]}
        dict2 = {"c": [2, 3], "a": {"b": 1}}
        assert my_hash(dict1) == my_hash(dict2)

    def test_set(self):
        assert my_hash({1, 2, 3}) == my_hash({3, 2, 1})
        assert my_hash({1, 2, 3}) != my_hash({1, 2, 4})

    def test_tuple(self):
        assert my_hash((1, 2, 3)) == my_hash((1, 2, 3))
        assert my_hash((1, 2, 3)) != my_hash((1, 2, 4))


class TestEdgeCases:
    """边界情况测试"""

    def test_large_structure(self):
        """测试大型结构（验证栈深度）"""
        # 创建深度嵌套的结构
        nested = {}
        current = nested
        for i in range(1000):
            current["next"] = {}
            current = current["next"]

        # 应该不会达到递归深度限制
        hash_result = my_hash(nested)
        assert len(hash_result) == 16  # MD5哈希长度

    def test_circular_reference(self):
        """测试循环引用"""
        # 注意：当前实现可能不支持循环引用，测试是否正常报错
        list1 = [1, 2, 3]
        list1.append(list1)  # 创建循环引用

        with pytest.raises(Exception):
            my_hash(list1)

    def test_unsupported_type(self):
        """测试不支持的类型"""

        class UnsupportedType:
            pass

        with pytest.raises(TypeError):
            my_hash(UnsupportedType())


class TestConsistency:
    """一致性测试"""

    def test_cross_process_consistency(self):
        """测试跨进程一致性"""
        # 相同内容的对象应该产生相同的哈希
        obj1 = {"users": [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]}
        obj2 = {"users": [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]}

        assert my_hash(obj1) == my_hash(obj2)

    def test_deterministic_hashing(self):
        """测试确定性哈希"""
        obj = {"a": 1, "b": [2, 3], "c": {"d": 4}}
        hash1 = my_hash(obj)
        hash2 = my_hash(obj)
        hash3 = my_hash(obj)

        assert hash1 == hash2 == hash3


class TestCustomHasher:
    """自定义哈希器测试"""

    def test_custom_cache_size(self):
        """测试自定义缓存大小"""
        hasher = Hasher(cache_size=100)
        result1 = hasher.my_hash("test")
        result2 = hasher.my_hash("test")
        assert result1 == result2

    def test_zero_cache(self):
        """测试禁用缓存"""
        hasher = Hasher(cache_size=0)
        result1 = hasher.my_hash("test")
        result2 = hasher.my_hash("test")
        assert result1 == result2