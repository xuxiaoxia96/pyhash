"""
性能基准测试 - 多数据类型对比
"""

import time
import statistics
import json
from src.pyhash import my_hash, Hasher
from hashlib import md5


def original_my_hash(obj) -> bytes:
    """原始递归实现（用于性能对比）"""
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


def create_test_cases():
    """创建多种测试用例"""
    test_cases = {}

    # 1. 小字符串
    test_cases["small_string"] = "hello world"

    # 2. 大字符串 (100KB)
    test_cases["large_string"] = "x" * 100000

    # 3. 整数
    test_cases["integer"] = 123456789

    # 4. 浮点数
    test_cases["float"] = 3.141592653589793

    # 5. None
    test_cases["none"] = None

    # 6. 简单列表
    test_cases["simple_list"] = [1, "hello", 3.14, None, True, False]

    # 7. 嵌套列表
    test_cases["nested_list"] = [
        [1, 2, 3],
        ["a", "b", "c"],
        [{"x": 1}, {"y": 2}],
        [None, True, False]
    ]

    # 8. 简单字典
    test_cases["simple_dict"] = {
        "name": "John",
        "age": 30,
        "city": "New York",
        "active": True
    }

    # 9. 嵌套字典
    test_cases["nested_dict"] = {
        "users": [
            {
                "id": i,
                "name": f"User_{i}",
                "email": f"user_{i}@example.com",
                "preferences": {
                    "theme": "dark" if i % 2 == 0 else "light",
                    "notifications": i % 3 == 0,
                    "language": ["en", "es", "fr"][i % 3]
                }
            }
            for i in range(50)  # 减小规模以避免测试时间过长
        ],
        "metadata": {
            "version": "1.0.0",
            "timestamp": 1234567890,
            "flags": [True, False, None] * 5
        }
    }

    # 10. 混合复杂结构
    test_cases["mixed_complex"] = {
        "string_types": {
            "small": "hello",
            "medium": "a" * 1000,
            "large": "b" * 10000
        },
        "numeric_types": {
            "integers": list(range(100)),
            "floats": [i * 0.1 for i in range(50)],
            "mixed": [1, 2.5, 3, 4.7]
        },
        "boolean_none": [True, False, None] * 10,
        "deeply_nested": {
            "level1": {
                "level2": {
                    "level3": {
                        "level4": {
                            "value": "deep_value"
                        }
                    }
                }
            }
        }
    }

    return test_cases


def benchmark_function(func, test_data, iterations=100):
    """基准测试函数"""
    times = []

    # 预热（避免第一次调用的开销影响结果）
    for _ in range(10):
        func(test_data)

    # 正式测试
    for _ in range(iterations):
        start_time = time.perf_counter()
        func(test_data)
        end_time = time.perf_counter()
        times.append((end_time - start_time) * 1000)  # 转换为毫秒

    return {
        "min": min(times),
        "max": max(times),
        "mean": statistics.mean(times),
        "median": statistics.median(times),
        "stdev": statistics.stdev(times) if len(times) > 1 else 0,
        "total": sum(times)
    }


def format_time(ms):
    """格式化时间显示"""
    if ms < 0.001:
        return f"{ms * 1000:.3f} μs"
    elif ms < 1:
        return f"{ms * 1000:.1f} μs"
    else:
        return f"{ms:.3f} ms"


def format_size(obj):
    """估算对象大小"""
    try:
        size = len(str(obj).encode('utf-8'))
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        else:
            return f"{size / (1024 * 1024):.1f} MB"
    except:
        return "N/A"


def run_benchmarks():
    """运行基准测试"""
    print("性能基准测试 - 多数据类型对比")
    print("=" * 80)

    test_cases = create_test_cases()

    # 根据数据类型复杂度调整迭代次数
    iteration_config = {
        "small_string": 10000,
        "large_string": 100,
        "integer": 10000,
        "float": 10000,
        "none": 10000,
        "simple_list": 5000,
        "nested_list": 1000,
        "simple_dict": 5000,
        "nested_dict": 100,
        "mixed_complex": 50
    }

    results = {}

    for case_name, test_data in test_cases.items():
        print(f"\n测试用例: {case_name}")
        print(f"数据大小: {format_size(test_data)}")
        print("-" * 50)

        iterations = iteration_config.get(case_name, 100)

        # 测试原始实现
        print("原始递归实现:")
        try:
            original_stats = benchmark_function(original_my_hash, test_data, iterations)
            for key, value in original_stats.items():
                if key == "total":
                    print(f"  {key}: {format_time(value)}")
                else:
                    print(f"  {key}: {format_time(value)}")
        except Exception as e:
            print(f"  ERROR: {e}")
            original_stats = None

        print()

        # 测试优化实现
        print("优化栈迭代实现:")
        try:
            optimized_stats = benchmark_function(my_hash, test_data, iterations)
            for key, value in optimized_stats.items():
                if key == "total":
                    print(f"  {key}: {format_time(value)}")
                else:
                    print(f"  {key}: {format_time(value)}")
        except Exception as e:
            print(f"  ERROR: {e}")
            optimized_stats = None

        # 性能对比
        if original_stats and optimized_stats:
            speedup = original_stats["mean"] / optimized_stats["mean"]
            print(f"\n性能提升: {speedup:.2f}x")
            if speedup > 1:
                print(f"✓ 优化实现更快 ({speedup:.2f}x)")
            else:
                print(f"⚠ 原始实现更快 ({1/speedup:.2f}x)")

        results[case_name] = {
            "original": original_stats,
            "optimized": optimized_stats
        }

    # 汇总报告
    print("\n" + "=" * 80)
    print("性能测试汇总报告")
    print("=" * 80)

    successful_cases = []
    speedups = []

    for case_name, result in results.items():
        if result["original"] and result["optimized"]:
            speedup = result["original"]["mean"] / result["optimized"]["mean"]
            speedups.append(speedup)
            successful_cases.append((case_name, speedup))

    if successful_cases:
        print("\n各用例性能提升:")
        for case_name, speedup in successful_cases:
            status = "✓" if speedup > 1 else "⚠"
            print(f"  {status} {case_name:20} {speedup:6.2f}x")

        avg_speedup = statistics.mean(speedups)
        print(f"\n平均性能提升: {avg_speedup:.2f}x")

        if avg_speedup > 1:
            print("🎉 优化实现在大多数情况下表现更好！")
        else:
            print("🤔 优化实现需要进一步改进")

    return results


def memory_usage_test():
    """内存使用测试（针对深度嵌套结构）"""
    print("\n" + "=" * 80)
    print("深度嵌套结构测试")
    print("=" * 80)

    # 创建深度嵌套结构
    def create_deep_dict(depth):
        if depth == 0:
            return "base_value"
        return {"level": depth, "next": create_deep_dict(depth - 1)}

    def create_deep_list(depth):
        if depth == 0:
            return "base_value"
        return [depth, create_deep_list(depth - 1)]

    test_depths = [100, 500, 1000, 2000]

    for depth in test_depths:
        print(f"\n测试深度: {depth}")

        # 测试深度字典
        try:
            deep_dict = create_deep_dict(depth)
            start_time = time.perf_counter()
            result_orig = original_my_hash(deep_dict)
            time_orig = (time.perf_counter() - start_time) * 1000

            start_time = time.perf_counter()
            result_opt = my_hash(deep_dict)
            time_opt = (time.perf_counter() - start_time) * 1000

            print(f"深度字典 - 原始: {format_time(time_orig)}, 优化: {format_time(time_opt)}")
            print(f"结果一致: {result_orig == result_opt}")

        except Exception as e:
            print(f"深度字典 - 错误: {e}")

        # 测试深度列表
        try:
            deep_list = create_deep_list(depth)
            start_time = time.perf_counter()
            result_orig = original_my_hash(deep_list)
            time_orig = (time.perf_counter() - start_time) * 1000

            start_time = time.perf_counter()
            result_opt = my_hash(deep_list)
            time_opt = (time.perf_counter() - start_time) * 1000

            print(f"深度列表 - 原始: {format_time(time_orig)}, 优化: {format_time(time_opt)}")
            print(f"结果一致: {result_orig == result_opt}")

        except Exception as e:
            print(f"深度列表 - 错误: {e}")


if __name__ == "__main__":
    results = run_benchmarks()
    memory_usage_test()