import datetime
import logging
import multiprocessing
import signal
import time

from core.queue import TaskQueue

logger = logging.getLogger(__name__)


class Worker:
    def __init__(self, queue_name="task_queue"):
        self.queue = TaskQueue(queue_name=queue_name)
        self.running = True

    def process_task(self, task_data: dict):
        self.heartbeat()
        logger.info("[%s] Sending email to: %s",
                     multiprocessing.current_process().name,
                     task_data.get('to'))
        time.sleep(1)

        campaign_id = task_data.get("campaign_id")
        if campaign_id:
            self.queue.redis.incr(f"campaign:{campaign_id}:sent")

        logger.info("[%s] Done: %s",
                     multiprocessing.current_process().name,
                     task_data.get('to'))

    def start(self):
        signal.signal(signal.SIGTERM, lambda sig, frame: self.stop())
        logger.info("[%s] Started. Waiting for tasks...",
                     multiprocessing.current_process().name)
        while self.running:
            self.heartbeat()
            task = self.queue.dequeue()
            if task:
                self.process_task(task)
            else:
                time.sleep(0.5)
        logger.info("[%s] Shut down complete.",
                     multiprocessing.current_process().name)

    def stop(self):
        logger.info("[%s] Stopping gracefully...",
                     multiprocessing.current_process().name)
        self.running = False

    def heartbeat(self):
        worker_name = multiprocessing.current_process().name
        timestamp = datetime.datetime.now().isoformat()
        self.queue.redis.set(f"worker:{worker_name}:heartbeat", timestamp, ex=10)