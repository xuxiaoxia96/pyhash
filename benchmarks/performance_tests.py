"""
扩展性能测试
"""

import time
import sys
from src.pyhash import my_hash, Hasher


class PerformanceTests:
    """性能测试套件"""

    @staticmethod
    def test_small_objects():
        """测试小对象性能"""
        print("小对象性能测试:")
        small_objects = [
            "hello",
            42,
            3.14159,
            None,
            [1, 2, 3],
            {"a": 1, "b": 2},
            {1, 2, 3}
        ]

        iterations = 10000
        start_time = time.perf_counter()

        for obj in small_objects * (iterations // len(small_objects)):
            my_hash(obj)

        end_time = time.perf_counter()
        total_time = (end_time - start_time) * 1000
        ops_per_second = iterations / (end_time - start_time)

        print(f"  总时间: {total_time:.2f} ms")
        print(f"  操作/秒: {ops_per_second:.0f}")
        print(f"  平均时间: {total_time / iterations:.4f} ms")
        print()

        return ops_per_second

    @staticmethod
    def test_large_structure():
        """测试大结构性能"""
        print("大结构性能测试:")

        # 创建大型嵌套结构
        large_structure = {}
        for i in range(1000):
            large_structure[f"key_{i}"] = {
                "id": i,
                "data": list(range(100)),
                "nested": {
                    f"nested_{j}": j * 2 for j in range(10)
                }
            }

        iterations = 100
        start_time = time.perf_counter()

        for _ in range(iterations):
            my_hash(large_structure)

        end_time = time.perf_counter()
        total_time = (end_time - start_time) * 1000

        print(f"  结构大小: {sys.getsizeof(large_structure)} 字节")
        print(f"  总时间: {total_time:.2f} ms")
        print(f"  平均时间: {total_time / iterations:.2f} ms")
        print(f"  操作/秒: {iterations / (end_time - start_time):.2f}")
        print()

        return total_time / iterations

    @staticmethod
    def test_deep_nesting():
        """测试深度嵌套性能"""
        print("深度嵌套性能测试:")

        # 创建深度嵌套结构
        current = {}
        root = current
        for i in range(500):
            current["next"] = {}
            current = current["next"]

        iterations = 1000
        start_time = time.perf_counter()

        for _ in range(iterations):
            my_hash(root)

        end_time = time.perf_counter()
        total_time = (end_time - start_time) * 1000

        print(f"  嵌套深度: 500")
        print(f"  总时间: {total_time:.2f} ms")
        print(f"  平均时间: {total_time / iterations:.4f} ms")
        print(f"  操作/秒: {iterations / (end_time - start_time):.0f}")
        print()

        return total_time / iterations

    @staticmethod
    def test_cache_effectiveness():
        """测试缓存效果"""
        print("缓存效果测试:")

        hasher_no_cache = Hasher(cache_size=0)
        hasher_with_cache = Hasher(cache_size=10000)

        test_strings = ["test_" + str(i) for i in range(1000)]

        # 无缓存测试
        start_time = time.perf_counter()
        for s in test_strings:
            hasher_no_cache.my_hash(s)
        no_cache_time = (time.perf_counter() - start_time) * 1000

        # 有缓存测试
        start_time = time.perf_counter()
        for s in test_strings:
            hasher_with_cache.my_hash(s)
        cache_time = (time.perf_counter() - start_time) * 1000

        improvement = no_cache_time / cache_time

        print(f"  无缓存时间: {no_cache_time:.2f} ms")
        print(f"  有缓存时间: {cache_time:.2f} ms")
        print(f"  缓存效果: {improvement:.2f}x")
        print()

        return improvement


def run_all_performance_tests():
    """运行所有性能测试"""
    print("扩展性能测试套件")
    print("=" * 50)

    results = {"small_objects": PerformanceTests.test_small_objects(),
               "large_structure": PerformanceTests.test_large_structure(),
               "deep_nesting": PerformanceTests.test_deep_nesting(),
               "cache_effectiveness": PerformanceTests.test_cache_effectiveness()}

    print("性能测试完成!")
    return results


if __name__ == "__main__":
    run_all_performance_tests()