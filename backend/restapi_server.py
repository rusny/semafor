from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import os
from typing import Any
from schemas import Intersection
from logic import validate_adjacent_lanes, validate_phases
from models import PhaseConfig, PhasesRequest

semaphoreApp = FastAPI(title="Traffic Intersection Simulation API")

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
semaphoreApp.state.frontend_dir = os.path.join(parent_dir, "frontend")

# MOUNT CONFIGURE
semaphoreApp.mount("/configure", StaticFiles(directory=os.path.join(semaphoreApp.state.frontend_dir, "configure"), html=True), name="configure")

# MOUNT VISUALIZE
semaphoreApp.mount("/visualize", StaticFiles(directory=os.path.join(semaphoreApp.state.frontend_dir, "visualize"), html=True), name="visualize")

@semaphoreApp.get("/style.css")
async def get_css():
    return FileResponse(os.path.join(semaphoreApp.state.frontend_dir, "style.css"))

@semaphoreApp.get("/script.js")
async def get_js():
    return FileResponse(os.path.join(semaphoreApp.state.frontend_dir, "script.js"))

@semaphoreApp.post("/set_phases")
async def set_phases(request: PhasesRequest) -> Any:
    semaphoreApp.state.intersection = Intersection()

    phases = request.phases

    for branch_name, branch_phases in phases.items():
        if branch_name in semaphoreApp.state.intersection.branches:
            branch = semaphoreApp.state.intersection.branches[branch_name]
            # Nastavenie smerov pre jediný pruh vo vetve (vždy lane 0)
            lane = branch.lanes[0]  # použijeme prvý pruh pre danú vetvu
            for direction in ["left", "straight", "right"]:
                lane.set_direction(direction, True)
                phase_data = branch_phases[direction]
                lane.set_phase(direction, phase_data["start"], phase_data["end"])


    valid, message = validate_adjacent_lanes(semaphoreApp.state.intersection)
    if not valid:
        return JSONResponse(content={"success": False, "message": message})

    semaphoreApp.state.intersection.update_cycle_length()

    valid, message = validate_phases(semaphoreApp.state.intersection)
    if not valid:
        return JSONResponse(content={"success": False, "message": message})

    if hasattr(semaphoreApp.state, 'simulation'):
        semaphoreApp.state.simulation.update_intersection(semaphoreApp.state.intersection)
        semaphoreApp.state.simulation.start_simulation()

    signals = semaphoreApp.state.intersection.get_signals_at_time(0)
    return {"success": True, "signals": signals, "cycle_length": semaphoreApp.state.intersection.cycle_length}

@semaphoreApp.get("/get_signals")
async def get_signals(time: int = 0) -> Any:
    signals = semaphoreApp.state.intersection.get_signals_at_time(time)
    return {"signals": signals, "time": time, "cycle_length": semaphoreApp.state.intersection.cycle_length}

@semaphoreApp.get("/stop_simulation")
async def stop_simulation() -> Any:
    if hasattr(semaphoreApp.state, 'simulation'):
        semaphoreApp.state.simulation.stop_simulation()
        return {"success": True, "message": "Simulation stopped"}
    return {"success": False, "message": "Simulation not found"}

@semaphoreApp.get("/start_simulation")
async def start_simulation() -> Any:
    if hasattr(semaphoreApp.state, 'simulation'):
        semaphoreApp.state.simulation.start_simulation()
        return {"success": True, "message": "Simulation started"}
    return {"success": False, "message": "Simulation not found"}
