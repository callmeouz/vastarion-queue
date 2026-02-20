import multiprocessing
import time
from workers.worker import Worker


def run_worker():
    w = Worker()
    w.start()


if __name__ == "__main__":
    workers = []
    for i in range(2):
        p = multiprocessing.Process(target=run_worker)
        p.start()
        workers.append(p)
        print(f"Worker-{i+1} started")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping workers...")
        for p in workers:
            p.terminate()
            p.join()
        print("All workers stopped.")