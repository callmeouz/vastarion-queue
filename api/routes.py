from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, WebSocket
from core.queue import TaskQueue, PriorityQueue
from api.schemas import TaskSubmit, EmailCampaign
import asyncio
import json
import uuid

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

queue = TaskQueue()
priority_queue = PriorityQueue()

app.mount("/assets", StaticFiles(directory="assets"), name="assets")


@app.get("/")
def serve_dashboard():
    return FileResponse("dashboard.html")

@app.post("/tasks/submit")
def submit_task(task: TaskSubmit):
    if task.priority is not None:
        priority_queue.enqueue(task.task_data, task.priority)
        size = priority_queue.size()
    else:
        queue.enqueue(task.task_data)
        size = queue.size()
    return {"status": "queued", "queue_size": size}

@app.get("/tasks/status")
def get_status():
    return {
        "queue_size": queue.size(),
        "priority_queue_size": priority_queue.size()
    }

@app.get("/tasks/dead-letter")
def get_dead_letter():
    dlq = TaskQueue(queue_name="dead_letter_queue")
    return {
        "size": dlq.size()
    }

@app.delete("/tasks/clear")
def clear_queues():
    queue.redis.delete("task_queue")
    queue.redis.delete("priority_queue")
    queue.redis.delete("dead_letter_queue")
    return {"status": "all queues cleared"}

@app.websocket("/ws/tasks")
async def task_updates(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            workers = []
            for key in queue.redis.scan_iter("worker:*:heartbeat"):
                worker_name = key.decode().split(":")[1]
                last_beat = queue.redis.get(key).decode()
                workers.append({"name": worker_name, "last_heartbeat": last_beat})

            status = {
                "queue_size": queue.size(),
                "priority_queue_size": priority_queue.size(),
                "dead_letter_size": TaskQueue(queue_name="dead_letter_queue").size(),
                "workers_online": len(workers),
                "workers": workers
            }
            await websocket.send_text(json.dumps(status))
            await asyncio.sleep(2)
    except Exception:
        pass

@app.post("/campaign/start")
def start_campaign(campaign: EmailCampaign):
    campaign_id = str(uuid.uuid4())[:8]
    
    for email in campaign.emails:
        task = {
            "campaign_id": campaign_id,
            "to": email,
            "subject": campaign.subject,
            "body": campaign.body
        }
        queue.enqueue(task)
    
    queue.redis.set(f"campaign:{campaign_id}:total", len(campaign.emails))
    queue.redis.set(f"campaign:{campaign_id}:sent", 0)
    
    return {
        "campaign_id": campaign_id,
        "total_emails": len(campaign.emails),
        "queue_size": queue.size()
    }

@app.get("/campaign/{campaign_id}/progress")
def get_progress(campaign_id: str):
    total = queue.redis.get(f"campaign:{campaign_id}:total")
    sent = queue.redis.get(f"campaign:{campaign_id}:sent")
    
    total = int(total) if total else 0
    sent = int(sent) if sent else 0
    
    return {
        "campaign_id": campaign_id,
        "total": total,
        "sent": sent,
        "progress": f"{(sent/total*100) if total > 0 else 0:.1f}%"
    }