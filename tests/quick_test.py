from src.pyhash import my_hash

# 基本类型测试
print("测试基本类型...")
assert my_hash(None) == my_hash(None)
assert my_hash("hello") == my_hash("hello")
assert my_hash(42) == my_hash(42)
assert my_hash(3.14) == my_hash(3.14)
assert my_hash(True) == my_hash(True)
print("✓ 基本类型测试通过")

# 容器测试
print("\n测试容器...")
assert my_hash([1, 2, 3]) == my_hash([1, 2, 3])
assert my_hash({"a": 1, "b": 2}) == my_hash({"a": 1, "b": 2})
assert my_hash({1, 2, 3}) == my_hash({1, 2, 3})
assert my_hash((1, 2, 3)) == my_hash((1, 2, 3))
print("✓ 容器测试通过")

# 空容器测试
print("\n测试空容器...")
assert my_hash([]) == my_hash([])
assert my_hash({}) == my_hash({})
assert my_hash(set()) == my_hash(set())
assert my_hash(()) == my_hash(())
print("✓ 空容器测试通过")

# 嵌套结构测试
print("\n测试嵌套结构...")
nested = {"a": [1, 2, {"b": 3}], "c": [4, 5]}
assert my_hash(nested) == my_hash(nested)
print("✓ 嵌套结构测试通过")

# 顺序一致性测试
print("\n测试列表排序一致性...")
list1 = [3, 1, 2]
list2 = [2, 3, 1]
list3 = [1, 2, 3]
h1 = my_hash(list1)
h2 = my_hash(list2)
h3 = my_hash(list3)
assert h1 == h2 == h3, "列表应该按内容排序后计算哈希"
print("✓ 列表排序一致性测试通过")

# 字典键顺序一致性
print("\n测试字典键顺序一致性...")
dict1 = {"a": 1, "b": 2}
dict2 = {"b": 2, "a": 1}
assert my_hash(dict1) == my_hash(dict2)
print("✓ 字典键顺序测试通过")

# 深度嵌套测试
print("\n测试深度嵌套...")
current = {"value": 0}
root = current
for i in range(100):
    current["next"] = {"value": i+1}
    current = current["next"]
h = my_hash(root)
assert len(h) == 16  # MD5 哈希值应该是 16 字节
print("✓ 深度嵌套测试通过")

print("\n" + "=" * 50)
print("所有测试通过！ ✓")
print("=" * 50)
