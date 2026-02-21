import pytest
from core.queue import TaskQueue, PriorityQueue, RetryableTask
from workers.worker import Worker


@pytest.fixture
def clean_queue():
    """Temiz bir FIFO queue olusturur, test sonrasi temizler."""
    q = TaskQueue(queue_name="test_queue")
    q.redis.delete("test_queue")
    yield q
    q.redis.delete("test_queue")


@pytest.fixture
def clean_priority_queue():
    """Temiz bir priority queue olusturur, test sonrasi temizler."""
    pq = PriorityQueue(queue_name="test_priority")
    pq.redis.delete("test_priority")
    yield pq
    pq.redis.delete("test_priority")


@pytest.fixture
def retryable_task():
    """RetryableTask olusturur, DLQ'yu test sonrasi temizler."""
    rt = RetryableTask(max_retries=3, base_delay=2)
    rt.dead_letter_queue.redis.delete("dead_letter_queue")
    yield rt
    rt.dead_letter_queue.redis.delete("dead_letter_queue")


@pytest.fixture
def worker():
    """Temiz bir worker olusturur, test sonrasi temizler."""
    w = Worker(queue_name="test_worker_queue")
    w.queue.redis.delete("test_worker_queue")
    yield w
    w.queue.redis.delete("test_worker_queue")
    for key in w.queue.redis.scan_iter("worker:*:heartbeat"):
        w.queue.redis.delete(key)
