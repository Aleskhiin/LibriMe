# app.py (liegt im Projekt-Root /app)
from fastapi import FastAPI, Body
from pydantic import BaseModel
from typing import Literal

# Paketname wurde umbenannt von 'app' zu 'app_pkg'
from app_pkg.AIProcess import AIProcess, dummy_sync_task, dummy_async_task

app = FastAPI(title="LibriMe AI Module", version="0.1.0")

# Globale Prozess-Instanz mit z.B. 2 Worker-Threads
ai_process = AIProcess(num_workers=2)

@app.on_event("startup")
def on_startup():
    ai_process.start()

@app.on_event("shutdown")
def on_shutdown():
    pass

class TaskIn(BaseModel):
    kind: Literal["sync", "async"]
    name: str
    duration: int

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/status")
def status():
    return {"queued_items": ai_process.task_queue.qsize()}

@app.post("/tasks/enqueue")
def enqueue_task(task: TaskIn = Body(...)):
    if task.kind == "sync":
        ai_process.add_task(dummy_sync_task, task.name, task.duration)
    else:
        ai_process.add_task(dummy_async_task, task.name, task.duration)
    return {"accepted": True, "queue_size": ai_process.task_queue.qsize()}

@app.post("/tasks/demo")
def enqueue_demo():
    ai_process.add_task(dummy_sync_task, "A", 2)
    ai_process.add_task(dummy_sync_task, "B", 3)
    ai_process.add_task(dummy_async_task, "C", 2)
    ai_process.add_task(dummy_async_task, "D", 1)
    return {"accepted": True, "message": "Demo tasks enqueued"}