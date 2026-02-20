import json
import redis
import time

class RetryableTask:
    def __init__(self, max_retries=3, base_delay=2):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.dead_letter_queue = TaskQueue(queue_name="dead_letter_queue")

    def execute_with_retry(self, task_data: dict, task_function):
        for attempt in range(self.max_retries):
            try:
                result = task_function(task_data)
                print(f"Success! Attempt: {attempt + 1}")
                return result
            except Exception as e:
                wait_time = self.base_delay ** (attempt + 1)
                print(f"Error: {e}. Attempt {attempt + 1}/{self.max_retries}. Waiting {wait_time}s...")
                time.sleep(wait_time)

        print(f"Task failed! Sending to dead letter queue.")
        self.dead_letter_queue.enqueue(task_data)
        return None

class TaskQueue:
    def __init__(self, queue_name="task_queue"):
        self.redis = redis.Redis(host='localhost', port=6379, db=0)
        self.queue_name = queue_name

    def enqueue(self, task_data: dict):
        task_json = json.dumps(task_data)
        self.redis.lpush(self.queue_name, task_json)

    def dequeue(self):
        task_json = self.redis.rpop(self.queue_name)
        if task_json is None:
            return None
        return json.loads(task_json)

    def size(self):
        return self.redis.llen(self.queue_name)
    
class PriorityQueue:
    def __init__(self, queue_name="priority_queue"):
        self.redis = redis.Redis(host='localhost', port=6379, db=0)
        self.queue_name = queue_name

    def enqueue(self, task_data: dict, priority: int = 2):
        task_json = json.dumps(task_data)
        self.redis.zadd(self.queue_name, {task_json: priority})

    def dequeue(self):
        result = self.redis.zpopmin(self.queue_name)
        if not result:
            return None
        task_json, score = result[0]
        return json.loads(task_json)

    def size(self):
        return self.redis.zcard(self.queue_name)