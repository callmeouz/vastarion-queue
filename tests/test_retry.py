import pytest
from unittest.mock import patch


def test_successful_execution(retryable_task):
    task = {"id": 1, "to": "test@test.com"}
    result = retryable_task.execute_with_retry(task, lambda t: "ok")
    assert result == "ok"


@patch("time.sleep")
def test_retry_then_success(mock_sleep, retryable_task):
    call_count = {"n": 0}

    def flaky_task(data):
        call_count["n"] += 1
        if call_count["n"] < 3:
            raise Exception("temporary failure")
        return "recovered"

    result = retryable_task.execute_with_retry({"id": 2}, flaky_task)

    assert result == "recovered"
    assert call_count["n"] == 3


@patch("time.sleep")
def test_exponential_backoff_delays(mock_sleep, retryable_task):
    def always_fail(data):
        raise Exception("fail")

    retryable_task.execute_with_retry({"id": 3}, always_fail)

    delays = [call.args[0] for call in mock_sleep.call_args_list]
    assert delays == [2, 4, 8]


@patch("time.sleep")
def test_max_retry_sends_to_dlq(mock_sleep, retryable_task):
    def always_fail(data):
        raise Exception("permanent failure")

    result = retryable_task.execute_with_retry({"id": 4}, always_fail)

    assert result is None
    assert retryable_task.dead_letter_queue.size() == 1


@patch("time.sleep")
def test_dlq_contains_original_task(mock_sleep, retryable_task):
    task = {"id": 5, "to": "fail@test.com"}

    def always_fail(data):
        raise Exception("fail")

    retryable_task.execute_with_retry(task, always_fail)

    dlq_task = retryable_task.dead_letter_queue.dequeue()
    assert dlq_task["id"] == 5
    assert dlq_task["to"] == "fail@test.com"


@patch("time.sleep")
def test_multiple_failures_accumulate_in_dlq(mock_sleep, retryable_task):
    def always_fail(data):
        raise Exception("fail")

    retryable_task.execute_with_retry({"id": 10}, always_fail)
    retryable_task.execute_with_retry({"id": 11}, always_fail)

    assert retryable_task.dead_letter_queue.size() == 2
