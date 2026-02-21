import logging
import multiprocessing
import time

from workers.worker import Worker

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S"
)

logger = logging.getLogger(__name__)


def run_worker():
    w = Worker()
    w.start()


if __name__ == "__main__":
    workers = []
    for i in range(2):
        p = multiprocessing.Process(target=run_worker)
        p.start()
        workers.append(p)
        logger.info("Worker-%d started", i + 1)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stopping workers...")
        for p in workers:
            p.terminate()
            p.join()
        logger.info("All workers stopped.")