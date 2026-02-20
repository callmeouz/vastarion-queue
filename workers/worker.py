import time
import signal
import datetime
import multiprocessing
from core.queue import TaskQueue

class Worker:
    def __init__(self, queue_name="task_queue"):
        self.queue = TaskQueue(queue_name=queue_name)
        self.running = True

    def process_task(self, task_data: dict):
        self.heartbeat()
        print(f"[Worker {multiprocessing.current_process().name}] Sending email to: {task_data.get('to')}")
        time.sleep(1)
        
        campaign_id = task_data.get("campaign_id")
        if campaign_id:
            self.queue.redis.incr(f"campaign:{campaign_id}:sent")

        print(f"[Worker {multiprocessing.current_process().name}] Done: {task_data.get('to')}")

    def start(self):
        signal.signal(signal.SIGTERM, lambda sig, frame: self.stop())
        print(f"[Worker {multiprocessing.current_process().name}] Started. Waiting for tasks...")
        while self.running:
            self.heartbeat()
            task = self.queue.dequeue()
            if task:
                self.process_task(task)
            else:
                time.sleep(0.5)
        print(f"[Worker {multiprocessing.current_process().name}] Shut down complete.")

    def stop(self):
        print(f"[Worker {multiprocessing.current_process().name}] Stopping gracefully...")
        self.running = False

    def heartbeat(self):
        worker_name = multiprocessing.current_process().name
        timestamp = datetime.datetime.now().isoformat()
        self.queue.redis.set(f"worker:{worker_name}:heartbeat", timestamp, ex=10)