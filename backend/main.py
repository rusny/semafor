from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import get_intersection_data
from models import Intersection
from models import SemaphoreUpdate
from database import update_semaphore_state
from simulation import run_simulation
from fastapi import WebSocket
from models import IntersectionConfig
from database import save_generated_intersection
from models import IntersectionConfig
from database import save_generated_intersection

import json
import asyncio

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/state", response_model=Intersection)
def get_state():
    return get_intersection_data()


@app.put("/api/semaphore/{semaphore_id}")
def set_semaphore_state(semaphore_id: str, update: SemaphoreUpdate):
    return update_semaphore_state(semaphore_id, update.state)


run_simulation()

@app.websocket("/ws/state")
async def websocket_state(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            intersection = get_intersection_data()
            await websocket.send_text(intersection.json())
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        print("🔌 Klient sa odpojil od WebSocketu.")


@app.post("/api/configure")
def configure_intersection(config: IntersectionConfig):
    save_generated_intersection(config)
    return {"message": "Križovatka nakonfigurovaná."}
