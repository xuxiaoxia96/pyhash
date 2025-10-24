"""
自定义类型使用示例
"""

from src.pyhash import register_type, my_hash
from datetime import datetime, date
from decimal import Decimal
import uuid


# 注册 datetime 类型
@register_type(datetime)
def hash_datetime(obj):
    return obj.isoformat().encode()


# 注册 date 类型
@register_type(date)
def hash_date(obj):
    return obj.isoformat().encode()


# 注册 Decimal 类型
@register_type(Decimal)
def hash_decimal(obj):
    return str(obj).encode()


# 注册 UUID 类型
@register_type(uuid.UUID)
def hash_uuid(obj):
    return obj.bytes


# 自定义类实现协议
class Product:
    def __init__(self, id, name, price, created_at):
        self.id = id
        self.name = name
        self.price = price
        self.created_at = created_at

    def __hash_bytes__(self):
        return f"Product({self.id},{self.name},{self.price},{self.created_at.isoformat()})".encode()


def demonstrate_custom_types():
    """演示自定义类型使用"""
    print("自定义类型示例")
    print("=" * 50)

    # 测试内置类型扩展
    now = datetime.now()
    today = date.today()
    price = Decimal("19.99")
    uid = uuid.uuid4()

    print(f"datetime 哈希: {my_hash(now).hex()}")
    print(f"date 哈希: {my_hash(today).hex()}")
    print(f"Decimal 哈希: {my_hash(price).hex()}")
    print(f"UUID 哈希: {my_hash(uid).hex()}")

    # 测试自定义类
    product1 = Product(1, "Laptop", Decimal("999.99"), datetime.now())
    product2 = Product(1, "Laptop", Decimal("999.99"), product1.created_at)

    print(f"Product 1 哈希: {my_hash(product1).hex()}")
    print(f"Product 2 哈希: {my_hash(product2).hex()}")
    print(f"产品哈希是否一致: {my_hash(product1) == my_hash(product2)}")

    # 测试在容器中使用自定义类型
    order = {
        "order_id": uid,
        "products": [product1],
        "created_at": now,
        "total": price
    }

    print(f"订单哈希: {my_hash(order).hex()}")


if __name__ == "__main__":
    demonstrate_custom_types()