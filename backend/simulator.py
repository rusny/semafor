import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict

router = APIRouter()

class IntersectionSimulator:
    def __init__(self):
        self.phases = {}  # Uloženie nastavených fáz semaforov
        self.intersection = {}  # Uloženie smerovania pruhov
        self.cycle_length = 0  # Celková dĺžka cyklu
        self.clients = set()  # Websocket klienti
        self.running = False

    def setup(self, phases: Dict, intersection: Dict):
        self.phases = phases
        self.intersection = intersection
        self.cycle_length = self.calculate_cycle_length()
        self.running = True

    def calculate_cycle_length(self) -> int:
        max_time = 0
        for branch in self.phases.values():
            for lane_times in branch.values():
                max_time = max(max_time, lane_times["end"])
        return max_time

    def get_signals_for_time(self, t: int) -> Dict:
        signals = {"north": [], "south": [], "east": [], "west": []}
        time_in_cycle = t % self.cycle_length

        for direction, lanes in self.intersection.items():
            for idx, movement in enumerate(lanes):
                active = False
                phase_info = self.phases.get(direction, {}).get(movement)
                if phase_info:
                    if phase_info["start"] <= time_in_cycle < phase_info["end"]:
                        active = True
                signals[direction].append({
                    "lane": idx,
                    "direction": movement,
                    "active": active
                })
        return signals

    async def run(self):
        t = 0
        while self.running:
            signals = self.get_signals_for_time(t)
            await self.broadcast(signals)
            await asyncio.sleep(1)
            t += 1

    async def broadcast(self, signals: Dict):
        for client in self.clients:
            try:
                await client.send_json({"signals": signals})
            except WebSocketDisconnect:
                self.clients.remove(client)

# Jedna globálna inštancia simulátora
simulator = IntersectionSimulator()

# API pre websocket na prijímanie signálov
@router.websocket("/ws/simulate")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    simulator.clients.add(websocket)
    try:
        while True:
            await websocket.receive_text()  # WebSocket vyžaduje, aby klient posielal niečo, inak zatvorí spojenie
    except WebSocketDisconnect:
        simulator.clients.remove(websocket)

# API na spustenie simulácie (po nakonfigurovaní križovatky)
@router.post("/start-simulation/")
async def start_simulation(data: Dict):
    phases = data["phases"]
    intersection = data["intersection"]
    simulator.setup(phases, intersection)
    asyncio.create_task(simulator.run())
    return {"message": "Simulation started."}
