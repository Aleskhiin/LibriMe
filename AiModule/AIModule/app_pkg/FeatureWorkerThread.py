import asyncio
import queue
import threading


class FeatureWorkerThread(threading.Thread):
    """
    One worker thread that fetches and executes tasks from a queue.
    """
    def __init__(self, task_queue: queue.Queue, worker_id: int):
        super().__init__(daemon=True)
        self.task_queue = task_queue
        self.worker_id = worker_id

    #TODO: Integration of the FeatureWorker logic inside the run method
    def run(self):
        while True:
            try:
                # Task out of the queue
                task, args, kwargs = self.task_queue.get()
                print(f"[Worker-{self.worker_id}] Starte Aufgabe: {task.__name__}")

                # Process task (handle both async and sync functions)
                if asyncio.iscoroutinefunction(task):
                    asyncio.run(task(*args, **kwargs))
                else:
                    task(*args, **kwargs)

                print(f"[Worker-{self.worker_id}] Aufgabe beendet: {task.__name__}")
            except Exception as e:
                print(f"[Worker-{self.worker_id}] Fehler: {e}")
            finally:
                self.task_queue.task_done()