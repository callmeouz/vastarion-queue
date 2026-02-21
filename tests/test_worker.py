import pytest
import multiprocessing
from unittest.mock import patch


def test_heartbeat_writes_to_redis(worker):
    worker.heartbeat()
    worker_name = multiprocessing.current_process().name
    key = f"worker:{worker_name}:heartbeat"
    value = worker.queue.redis.get(key)
    assert value is not None


def test_heartbeat_has_ttl(worker):
    worker.heartbeat()
    worker_name = multiprocessing.current_process().name
    key = f"worker:{worker_name}:heartbeat"
    ttl = worker.queue.redis.ttl(key)
    assert 0 < ttl <= 10


def test_stop_sets_running_false(worker):
    assert worker.running is True
    worker.stop()
    assert worker.running is False


@patch("time.sleep")
def test_process_task_sends_email(mock_sleep, worker):
    task = {"to": "user@test.com"}
    worker.process_task(task)


@patch("time.sleep")
def test_process_task_increments_campaign_counter(mock_sleep, worker):
    campaign_id = "test-abc"
    worker.queue.redis.set(f"campaign:{campaign_id}:sent", 0)

    task = {"to": "user@test.com", "campaign_id": campaign_id}
    worker.process_task(task)

    sent = int(worker.queue.redis.get(f"campaign:{campaign_id}:sent"))
    assert sent == 1

    worker.queue.redis.delete(f"campaign:{campaign_id}:sent")


def test_dequeue_processes_task(worker):
    worker.queue.enqueue({"to": "queued@test.com"})
    task = worker.queue.dequeue()
    assert task is not None
    assert task["to"] == "queued@test.com"
