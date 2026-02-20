import pytest
from core.queue import TaskQueue, PriorityQueue


class TestTaskQueue:
    def setup_method(self):
        self.queue = TaskQueue(queue_name="test_queue")
        self.queue.redis.delete("test_queue")

    def test_enqueue_and_dequeue(self):
        self.queue.enqueue({"id": 1, "to": "test@test.com"})
        result = self.queue.dequeue()
        assert result["id"] == 1
        assert result["to"] == "test@test.com"

    def test_fifo_order(self):
        self.queue.enqueue({"id": 1})
        self.queue.enqueue({"id": 2})
        first = self.queue.dequeue()
        second = self.queue.dequeue()
        assert first["id"] == 1
        assert second["id"] == 2

    def test_empty_queue_returns_none(self):
        result = self.queue.dequeue()
        assert result is None

    def test_size(self):
        self.queue.enqueue({"id": 1})
        self.queue.enqueue({"id": 2})
        assert self.queue.size() == 2


class TestPriorityQueue:
    def setup_method(self):
        self.pq = PriorityQueue(queue_name="test_priority")
        self.pq.redis.delete("test_priority")

    def test_priority_order(self):
        self.pq.enqueue({"id": 1}, priority=3)
        self.pq.enqueue({"id": 2}, priority=1)
        self.pq.enqueue({"id": 3}, priority=2)
        first = self.pq.dequeue()
        assert first["id"] == 2

    def test_size(self):
        self.pq.enqueue({"id": 1}, priority=1)
        assert self.pq.size() == 1