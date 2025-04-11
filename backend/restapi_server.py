from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import os
from typing import Dict, List, Optional, Any
from schemas import Intersection
from logic import validate_adjacent_lanes, validate_phases
from models import LaneConfig, LanesRequest, PhaseConfig, PhasesRequest

# Premenovaná premenná z fastApi na semaphoreApp
semaphoreApp = FastAPI(title="Traffic Intersection Simulation API")

# Inicializácia premennej intersection v state namiesto použitia globálnej premennej
semaphoreApp.state.intersection = Intersection()
semaphoreApp.state.frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")

# Endpointy pre statické súbory
@semaphoreApp.get("/style.css")
async def get_css():
    return FileResponse(os.path.join(semaphoreApp.state.frontend_dir, "style.css"))

@semaphoreApp.get("/script.js")
async def get_js():
    return FileResponse(os.path.join(semaphoreApp.state.frontend_dir, "script.js"))



@semaphoreApp.post("/set_phases")
async def set_phases(request: PhasesRequest) -> Dict[str, Any]:
    # Reset intersection - toto nahrádza create_intersection
    semaphoreApp.state.intersection = Intersection()
    
    phases = request.phases
    for branch_name, branch_phases in phases.items():
        if branch_name in semaphoreApp.state.intersection.branches:
            branch = semaphoreApp.state.intersection.branches[branch_name]
            for direction, phase in branch_phases.items():
                # Nájdenie a povolenie pruhov s týmto smerom
                # Pruh je povolený, len ak je pre daný smer definovaná fáza
                for lane_idx, lane in enumerate(branch.lanes):
                    if lane_idx < 3:  # Max 3 lanes per branch
                        # V JSON sú len povolené smery, takže keď ich nájdeme, povolíme ich
                        lane.set_direction(direction, True)
                        lane.set_phase(phase.get('start', 0), phase.get('end', 0))
    
    # Validácia konfigurácie pruhov (pôvodne v create_intersection)
    valid, message = validate_adjacent_lanes(semaphoreApp.state.intersection)
    if not valid:
        return JSONResponse(content={"success": False, "message": message})
    
    # Aktualizáca dĺžky cyklu
    semaphoreApp.state.intersection.update_cycle_length()
    
    # Validácia fáz
    valid, message = validate_phases(semaphoreApp.state.intersection)
    if not valid:
        return JSONResponse(content={"success": False, "message": message})
    
    # Aktualizácia simulácie
    if hasattr(semaphoreApp.state, 'simulation'):
        semaphoreApp.state.simulation.update_intersection(semaphoreApp.state.intersection)
        semaphoreApp.state.simulation.start_simulation()
    
    # Vrátenie aktuálneho stavu pre čas 0
    signals = semaphoreApp.state.intersection.get_signals_at_time(0)
    return {
        "success": True,
        "signals": signals,
        "cycle_length": semaphoreApp.state.intersection.cycle_length
    }

@semaphoreApp.get("/get_signals")
async def get_signals(time: int = 0) -> Dict[str, Any]:
    signals = semaphoreApp.state.intersection.get_signals_at_time(time)
    return {
        "signals": signals,
        "time": time,
        "cycle_length": semaphoreApp.state.intersection.cycle_length
    }

@semaphoreApp.get("/stop_simulation")
async def stop_simulation() -> Dict[str, Any]:
    """Zastav simuláciu"""
    if hasattr(semaphoreApp.state, 'simulation'):
        semaphoreApp.state.simulation.stop_simulation()
        return {"success": True, "message": "Simulation stopped"}
    return {"success": False, "message": "Simulation not found"}

@semaphoreApp.get("/start_simulation")
async def start_simulation() -> Dict[str, Any]:
    """Spusti simuláciu"""
    if hasattr(semaphoreApp.state, 'simulation'):
        semaphoreApp.state.simulation.start_simulation()
        return {"success": True, "message": "Simulation started"}
    return {"success": False, "message": "Simulation not found"}