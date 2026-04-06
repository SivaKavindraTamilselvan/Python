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
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/bf4d7577-e34a-4541-acdc-69aa050f55c7" />
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/1dcf209b-f05c-4d4a-8f06-96927eedf0e7" />
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/66c8eb93-d16b-42e7-bc70-4920ede87806" />
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/0b6ed1d8-73cc-44d4-aa32-56cfe667c673" />



