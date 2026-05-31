import asyncio
import inspect
import queue
import threading
from typing import Any, Callable


class FeatureWorkerThread(threading.Thread):
    """
    Worker thread that fetches tasks from a queue and executes them.

    Each queued task must have the following structure:
    (task_function, args, kwargs)

    The worker supports both synchronous and asynchronous functions.
    """

    def __init__(self, task_queue: queue.Queue, worker_id: int):
        """
        Initializes the worker thread.

        Args:
            task_queue: Queue that contains executable tasks.
            worker_id: Numeric identifier for logging/debugging.
        """

        super().__init__(daemon=True)

        self.task_queue = task_queue
        self.worker_id = worker_id
        self._running = True

    def stop(self) -> None:
        """
        Stops the worker loop after the current task has finished.
        """

        self._running = False

    def run(self) -> None:
        """
        Continuously fetches and executes tasks from the queue.
        """

        while self._running:
            task_item = None

            try:
                # Wait for a task, but only for a short time.
                # This allows the loop to check self._running regularly.
                task_item = self.task_queue.get(timeout=1)

                task, args, kwargs = task_item

                print(
                    f"[Worker-{self.worker_id}] "
                    f"Starting task: {task.__name__}"
                )

                # Execute async functions safely inside this thread.
                if inspect.iscoroutinefunction(task):
                    asyncio.run(task(*args, **kwargs))
                else:
                    result = task(*args, **kwargs)

                    # Defensive handling:
                    # If a sync function returns a coroutine, run it as well.
                    if inspect.iscoroutine(result):
                        asyncio.run(result)

                print(
                    f"[Worker-{self.worker_id}] "
                    f"Finished task: {task.__name__}"
                )

            except queue.Empty:
                # No task available. Continue and check self._running again.
                continue

            except Exception as e:
                print(
                    f"[Worker-{self.worker_id}] "
                    f"Error: {e}"
                )

            finally:
                # Mark task as done only if a task was actually fetched.
                if task_item is not None:
                    self.task_queue.task_done()