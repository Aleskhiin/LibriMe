import time
import threading
import queue

class TaskProcessor:
    """
    A simple multithreaded task processor that distributes tasks across worker threads.
    """

    def __init__(self, num_workers=4):
        """
        Initializes the task processor.

        Args:
            num_workers (int): Number of worker threads to start.
        """
        self.task_queue = queue.Queue()
        self.num_workers = num_workers
        self.threads = []
        self.shutdown_flag = threading.Event()

    def start_workers(self):
        """
        Starts the worker threads.
        """
        for i in range(self.num_workers):
            thread = threading.Thread(target=self.worker, name=f"Worker-{i+1}")
            thread.start()
            self.threads.append(thread)

    def stop_workers(self):
        """
        Signals all workers to stop and waits for them to finish.
        """
        self.shutdown_flag.set()
        for _ in self.threads:
            self.task_queue.put(None)  # Dummy task to unblock queue
        for thread in self.threads:
            thread.join()

    def add_task(self, task, *args, **kwargs):
        """
        Adds a task to the queue.

        Args:
            task (callable): The function to execute.
            *args: Positional arguments for the task.
            **kwargs: Keyword arguments for the task.
        """
        self.task_queue.put((task, args, kwargs))

    def worker(self):
        """
        Worker thread function that processes tasks from the queue.
        """
        while not self.shutdown_flag.is_set():
            item = self.task_queue.get()
            if item is None:
                break  # Shutdown signal
            task, args, kwargs = item
            try:
                print(f"[{threading.current_thread().name}] Processing task: {task.__name__}")
                task(*args, **kwargs)
            except Exception as e:
                print(f"[{threading.current_thread().name}] Error: {e}")
            finally:
                self.task_queue.task_done()

def example_task(name, duration):
    """
    Example task that simulates work by sleeping.

    Args:
        name (str): Name of the task.
        duration (int): Duration in seconds to simulate work.
    """
    print(f"  → Task {name} started")
    time.sleep(duration)
    print(f"  → Task {name} finished")

def main():
    """
    Main function to demonstrate task processing.
    """
    processor = TaskProcessor(num_workers=3)
    processor.start_workers()

    # Add tasks to the processor
    for i in range(10):
        processor.add_task(example_task, f"Task-{i+1}", i % 3 + 1)

    processor.task_queue.join()  # Wait until all tasks are processed
    processor.stop_workers()
    print("All tasks completed.")

if __name__ == "__main__":
    main()