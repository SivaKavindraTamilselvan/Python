import time
import random


def cook_burger(order_id: int, quantity: int):
    """Always succeeds — tests happy path"""
    print(f"  [Kitchen] Cooking {quantity} burger(s) for order #{order_id}...")
    time.sleep(1)
    return f"{quantity} burger(s) ready for order #{order_id}"


def cook_pasta(order_id: int, quantity: int):
    """Randomly fails — tests retry logic"""
    print(f"  [Kitchen] Cooking {quantity} pasta(s) for order #{order_id}...")
    time.sleep(1)
    if random.random() < 0.6:
        raise Exception(f"Pasta burned for order #{order_id}!")
    return f"{quantity} pasta(s) ready for order #{order_id}"


def make_dessert(order_id: int):
    """Always fails — tests dead letter queue"""
    print(f"  [Kitchen] Making dessert for order #{order_id}...")
    time.sleep(1)
    raise Exception(f"Oven broken! Cannot make dessert for order #{order_id}")