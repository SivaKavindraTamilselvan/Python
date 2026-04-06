import uuid
import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Task:
    name: str
    args: list
    status: str = "pending"
    retry_count: int = 0
    max_retries: int = 3
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    result: Optional[str] = None
    error: Optional[str] = None

    def to_json(self) -> str:
        return json.dumps({
            "id"           : self.id,
            "name"         : self.name,
            "args"         : self.args,
            "status"       : self.status,
            "retry_count"  : self.retry_count,
            "max_retries"  : self.max_retries,
            "created_at"   : self.created_at,
            "started_at"   : self.started_at,
            "completed_at" : self.completed_at,
            "result"       : self.result,
            "error"        : self.error,
        })

    @staticmethod
    def from_json(json_data: str) -> "Task":
        data = json.loads(json_data)
        return Task(**data)

    def duration(self) -> str:
        if self.started_at and self.completed_at:
            fmt = "%Y-%m-%dT%H:%M:%S.%f"
            try:
                start = datetime.strptime(self.started_at, fmt)
                end   = datetime.strptime(self.completed_at, fmt)
                secs  = round((end - start).total_seconds(), 2)
                return f"{secs}s"
            except Exception:
                return "—"
        return "—"