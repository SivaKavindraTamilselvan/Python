from task import Task
from broker import Broker

broker = Broker()


def place_order(name: str, args: list, max_retries: int = 3) -> str:
    task = Task(
        name=name,
        args=args,
        max_retries=max_retries
    )
    broker.enqueue(task)
    return task.id


if __name__ == "__main__":

    print("Waiter taking orders for table 1...")

    id1 = place_order(
        name="cook_burger",
        args=[101, 2]
    )

    id2 = place_order(
        name="cook_pasta",
        args=[102, 1],
        max_retries=5
    )

    id3 = place_order(
        name="make_dessert",
        args=[103],
        max_retries=3
    )

    print()
    print("All orders placed! Workers will cook them.")
    print()
    print("Track your orders:")
    print(f"  Burger  → {id1}")
    print(f"  Pasta   → {id2}")
    print(f"  Dessert → {id3}")