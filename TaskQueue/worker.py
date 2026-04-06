import importlib
import multiprocessing
import random
import time
from datetime import datetime
from broker import Broker


def resolve_function(name: str):
    module = importlib.import_module("tasks")
    return getattr(module, name)


def compute_backoff(retry_count: int) -> float:
    delay  = 2 ** retry_count
    jitter = random.uniform(0, 1)
    return round(delay + jitter, 2)


def run_chef(chef_id: int):
    broker = Broker()
    print(f"[Chef {chef_id}] Ready!")

    while True:
        task = broker.dequeue(timeout=5)

        if task is None:
            continue

        print(f"\n[Chef {chef_id}] Picked up: {task.name} ({task.id[:8]})")

        task.status     = "running"
        task.started_at = datetime.now().isoformat()

        try:
            fn     = resolve_function(task.name)
            result = fn(*task.args)

            task.status       = "success"
            task.result       = result
            task.completed_at = datetime.now().isoformat()
            broker.save_result(task)
            print(f"[Chef {chef_id}] SUCCESS: {task.name} → {result}")
            print(f"[Chef {chef_id}] Duration: {task.duration()}")

        except Exception as e:
            task.error        = str(e)
            task.completed_at = datetime.now().isoformat()

            if task.retry_count < task.max_retries:
                task.retry_count += 1
                task.status       = "retrying"
                delay             = compute_backoff(task.retry_count)
                print(f"[Chef {chef_id}] FAILED: {e}")
                print(f"[Chef {chef_id}] Retrying in {delay}s (attempt {task.retry_count}/{task.max_retries})")
                broker.save_result(task)
                time.sleep(delay)
                broker.enqueue(task)

            else:
                print(f"[Chef {chef_id}] GIVING UP after {task.retry_count} attempts")
                broker.move_to_dlq(task)


def start_kitchen(num_chefs: int = 3):
    print(f"Opening kitchen with {num_chefs} chefs...")
    processes = []

    for i in range(1, num_chefs + 1):
        p = multiprocessing.Process(
            target=run_chef,
            args=(i,),
            daemon=True #tells if the process to die if main program ends
        )
        p.start()
        processes.append(p)
        print(f"[Kitchen] Chef {i} hired!")

    try:
        for p in processes:
            p.join()
    except KeyboardInterrupt:
        print("\n[Kitchen] Closing kitchen...")
        for p in processes:
            p.terminate()


if __name__ == "__main__":
    start_kitchen(num_chefs=3)