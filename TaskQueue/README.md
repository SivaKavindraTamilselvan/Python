## Task
Distributed Task Queue

## Objective

Implement a producer-consumer task queue that distributes work across multiple worker processes. Include task serialization, retry logic with exponential backoff, dead-letter queues, and result backends.

## 📋 Requirements

- [x]  `multiprocessing` and `threading` modules
- [x]  `pickle` and `json` serialization
- [x]  Redis (via `redis-py`) as a message broker
- [x]  Socket programming basics
- [x]  Exponential backoff algorithm
- [x]  Producer-consumer and pub/sub patterns

## 💡 Use-Case

- [x]  Producer enqueues callable tasks with arguments
- [x]  Multiple worker processes poll the queue and execute tasks
- [x]  Failed tasks retry up to N times with increasing delays
- [x]  Permanently failed tasks move to a dead-letter queue
- [x]  Results stored in a backend (Redis/SQLite) for later retrieval
- [x]  Dashboard view showing task status, retries, and duration

## SCREENSHOTS
