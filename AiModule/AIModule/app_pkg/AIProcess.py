import threading
import queue
import asyncio
from typing import Any, Dict, Callable

from .FeatureWorkerThread import FeatureWorkerThread


class AIProcess:
    """
    AIProcess for the management of multiple worker threads and a shared queue.
    """
    def __init__(self, num_workers: int = 2):
        self.task_queue: queue.Queue = queue.Queue()
        self.workers = [FeatureWorkerThread(self.task_queue, i) for i in range(num_workers)]

    def start(self):
        """Starts all worker threads."""
        for worker in self.workers:
            worker.start()

    def add_task(self, task: Callable, *args, **kwargs):
        """
        Add a task to the queue.
        task: function or coroutine
        args/kwargs: parameters for the function
        """
        self.task_queue.put((task, args, kwargs))


# Dummy tasks for demonstration
async def dummy_async_task(name: str, duration: int):
    print(f"--> Async Task {name} gestartet")
    await asyncio.sleep(duration)
    print(f"--> Async Task {name} fertig")


def dummy_sync_task(name: str, duration: int):
    import time
    print(f"--> Sync Task {name} gestartet")
    time.sleep(duration)
    print(f"--> Sync Task {name} fertig")

# TODO: Replace dummy tasks with actual AI processing tasks
if __name__ == "__main__":
    ai_process = AIProcess(num_workers=2)
    ai_process.start()

    # Add synchronous tasks
    ai_process.add_task(dummy_sync_task, "A", 2)
    ai_process.add_task(dummy_sync_task, "B", 3)

    # Add asynchronous tasks
    ai_process.add_task(dummy_async_task, "C", 2)
    ai_process.add_task(dummy_async_task, "D", 1)

    # Wait until all tasks are done
    ai_process.task_queue.join()
    print("Alle Aufgaben erledigt")