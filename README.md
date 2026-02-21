![Vastarion Queue](assets/banner.png)

# Vastarion Queue

Vastarion Queue is a Redis-backed distributed task processing engine
supporting priority scheduling, retry strategies, dead-letter queues,
and real-time monitoring via WebSocket.

Built to understand and reimplement core concepts behind Celery and RabbitMQ.

## Why This Project?

This project was built to deeply understand how distributed task queues
work internally — including scheduling, worker coordination,
message acknowledgment, and fault tolerance.

Instead of relying on Celery, the goal was to reimplement core mechanics manually.

## Features

- FIFO Queue with Redis
- Priority Queue (urgent tasks first)
- Retry mechanism with exponential backoff
- Dead letter queue for failed tasks
- Multi-process worker pool with heartbeat monitoring
- FastAPI REST API for task submission
- WebSocket real-time queue monitoring
- Email Campaign Service with live progress tracking
- Dark elegant dashboard

## Tech Stack

- Python
- FastAPI
- Redis
- WebSocket
- Docker

## Getting Started

### Prerequisites

- Docker Desktop

### Run with Docker (Recommended)
```bash
docker-compose up --build
```
Open `http://localhost:8000` for the dashboard.

### Run Manually

```bash
docker run -d --name redis-queue -p 6379:6379 redis
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

**Terminal 1 — API:**
```bash
uvicorn api.routes:app --reload
```

**Terminal 2 — Workers:**
```bash
python main.py
```

Open `http://127.0.0.1:8000` for the dashboard.

### Tests

Coverage: FIFO queue, priority scheduling, retry logic with exponential backoff, dead-letter queue routing, worker heartbeat, graceful shutdown.

```bash
pytest tests/ -v
```

## System Architecture

Client (Dashboard / API Consumer)
        ↓
FastAPI REST Layer
        ↓
Redis (Queue + Priority + DLQ)
        ↓
Worker Pool (Multi-process)
        ↓
Email Processing + WebSocket Updates

## Internal Design

- Redis lists for FIFO task processing
- Sorted sets (ZSET) for priority scheduling
- Dedicated dead-letter namespace for failed tasks
- Retry metadata stored per task with exponential backoff logic
- Worker heartbeat persisted in Redis for liveness monitoring
- Atomic Redis operations to avoid race conditions

## Reliability Design

- Exponential backoff retry strategy
- Dead-letter queue isolation
- Worker heartbeat detection
- Graceful SIGTERM shutdown handling
- Atomic Redis operations to prevent race conditions

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/tasks/submit` | Submit a task |
| POST | `/campaign/start` | Start email campaign |
| GET | `/campaign/{id}/progress` | Track campaign progress |
| GET | `/tasks/status` | Queue status |
| DELETE | `/tasks/clear` | Clear all queues |
| WS | `/ws/tasks` | Real-time updates |

## Author

Built by [Oğuzhan Yılmaz](https://github.com/callmeouz)