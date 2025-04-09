from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import os
from typing import Dict, List, Optional, Any
from schemas import Intersection
from logic import validate_adjacent_lanes, validate_phases
from models import LaneConfig, LanesRequest, PhaseConfig, PhasesRequest

fastApi = FastAPI(title="Traffic Intersection Simulation API")

# Globálna premenná pre intersection
intersection = Intersection()

@fastApi.get("/")
async def read_root():
    return FileResponse(os.path.join(fastApi.state.frontend_dir, "index.html"))

@fastApi.get("/style.css")
async def get_css():
    return FileResponse(os.path.join(fastApi.state.frontend_dir, "style.css"))

@fastApi.get("/script.js")
async def get_js():
    return FileResponse(os.path.join(fastApi.state.frontend_dir, "script.js"))

@fastApi.post("/api/create_intersection")
async def create_intersection(request: LanesRequest):
    global intersection
    intersection = Intersection()
    
    lanes_config = request.lanes
    for branch_name, branch_config in lanes_config.items():
        if branch_name in intersection.branches:
            for lane_idx, lane_config in enumerate(branch_config):
                if lane_idx < 3:  # Max 3 lanes per branch
                    for direction, enabled in lane_config.items():
                        intersection.branches[branch_name].lanes[lane_idx].set_direction(direction, enabled)
    
    # Validácia konfigurácie pruhov
    valid, message = validate_adjacent_lanes(intersection)
    if not valid:
        return JSONResponse(content={"success": False, "message": message})
    
    # Uloženie konfigurácie do simulácie
    fastApi.state.simulation.update_intersection(intersection)
    
    return {
        "success": True,
        "intersection": intersection.to_dict()
    }

@fastApi.post("/api/set_phases")
async def set_phases(request: PhasesRequest):
    global intersection
    
    phases = request.phases
    for branch_name, branch_phases in phases.items():
        if branch_name in intersection.branches:
            branch = intersection.branches[branch_name]
            for direction, phase in branch_phases.items():
                # Nájdenie pruhov s týmto smerom
                for lane in branch.lanes:
                    if lane.directions.get(direction, False):
                        lane.set_phase(phase.get('start', 0), phase.get('end', 0))
    
    # Aktualizáca dĺžky cyklu
    intersection.update_cycle_length()
    
    # Validácia fáz
    valid, message = validate_phases(intersection)
    if not valid:
        return JSONResponse(content={"success": False, "message": message})
    
    # Aktualizácia simulácie
    fastApi.state.simulation.update_intersection(intersection)
    fastApi.state.simulation.start_simulation()
    
    # Vrátenie aktuálneho stavu pre čas 0
    signals = intersection.get_signals_at_time(0)
    return {
        "success": True,
        "signals": signals,
        "cycle_length": intersection.cycle_length
    }

@fastApi.get("/api/get_signals")
async def get_signals(time: int = 0):
    global intersection
    signals = intersection.get_signals_at_time(time)
    return {
        "signals": signals,
        "time": time,
        "cycle_length": intersection.cycle_length
    }

@fastApi.get("/api/stop_simulation")
async def stop_simulation():
    """Zastav simuláciu"""
    if hasattr(fastApi.state, 'simulation'):
        fastApi.state.simulation.stop_simulation()
        return {"success": True, "message": "Simulation stopped"}
    return {"success": False, "message": "Simulation not found"}

@fastApi.get("/api/start_simulation")
async def start_simulation():
    """Spusti simuláciu"""
    if hasattr(fastApi.state, 'simulation'):
        fastApi.state.simulation.start_simulation()
        return {"success": True, "message": "Simulation started"}
    return {"success": False, "message": "Simulation not found"}