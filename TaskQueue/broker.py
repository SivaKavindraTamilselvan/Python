import json
import redis
from task import Task

QUEUE_KEY = "restaurant:queue"
DLQ_KEY   = "restaurant:dlq"
RESULT_KEY = "result:"


class Broker:
    def __init__(self):
        self.r = redis.Redis(
            host="localhost",
            port=6379,
            db=0,
            decode_responses=True
        )

    def enqueue(self, task: Task):
        task.status = "pending"
        self.r.rpush(QUEUE_KEY, task.to_json())
        print(f"[Broker] Enqueued: {task.name} ({task.id[:8]})")

    def dequeue(self, timeout=5) -> Task:
        result = self.r.blpop(QUEUE_KEY, timeout=timeout)
        if result is None:
            return None
        _, raw = result
        return Task.from_json(raw)

    def save_result(self, task: Task):
        self.r.set(
            f"{RESULT_KEY}{task.id}",
            task.to_json(),
            ex=86400
        )


    def move_to_dlq(self, task: Task):
        task.status = "dead"
        self.r.rpush(DLQ_KEY, task.to_json())
        self.save_result(task)
        print(f"[Broker] DEAD: {task.name} — {task.error}")


    def get_result(self, task_id: str):
        raw = self.r.get(f"{RESULT_KEY}{task_id}")
        if raw is None:
            return None
        return json.loads(raw)

    def get_all_tasks(self) -> list:
        keys  = self.r.keys(f"{RESULT_KEY}*")
        tasks = []
        for key in keys:
            raw = self.r.get(key)
            if raw:
                tasks.append(json.loads(raw))
        tasks.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return tasks

    def get_dlq_tasks(self) -> list:
        items = self.r.lrange(DLQ_KEY, 0, -1)
        return [json.loads(i) for i in items]