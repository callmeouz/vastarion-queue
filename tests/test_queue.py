import pytest
from core.queue import TaskQueue, PriorityQueue


def test_enqueue_and_dequeue(clean_queue):
    clean_queue.enqueue({"id": 1, "to": "test@test.com"})
    result = clean_queue.dequeue()
    assert result["id"] == 1
    assert result["to"] == "test@test.com"


def test_fifo_order(clean_queue):
    clean_queue.enqueue({"id": 1})
    clean_queue.enqueue({"id": 2})
    first = clean_queue.dequeue()
    second = clean_queue.dequeue()
    assert first["id"] == 1
    assert second["id"] == 2


def test_empty_queue_returns_none(clean_queue):
    result = clean_queue.dequeue()
    assert result is None


def test_queue_size(clean_queue):
    clean_queue.enqueue({"id": 1})
    clean_queue.enqueue({"id": 2})
    assert clean_queue.size() == 2


def test_priority_order(clean_priority_queue):
    clean_priority_queue.enqueue({"id": 1}, priority=3)
    clean_priority_queue.enqueue({"id": 2}, priority=1)
    clean_priority_queue.enqueue({"id": 3}, priority=2)
    first = clean_priority_queue.dequeue()
    assert first["id"] == 2


def test_priority_size(clean_priority_queue):
    clean_priority_queue.enqueue({"id": 1}, priority=1)
    assert clean_priority_queue.size() == 1