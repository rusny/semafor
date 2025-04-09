from pydantic import BaseModel, Field, field_validator
from typing import Dict, List, Optional, Any


class LaneConfig(BaseModel):
    left: bool = False
    straight: bool = False
    right: bool = False


class LanesRequest(BaseModel):
    lanes: Dict[str, List[Dict[str, bool]]]
    
    @field_validator('lanes')
    @classmethod
    def validate_lanes(cls, lanes):
        valid_branches = ["north", "south", "east", "west"]
        for branch_name in lanes:
            if branch_name not in valid_branches:
                raise ValueError(f"Invalid branch name: {branch_name}")
                
            if len(lanes[branch_name]) > 3:
                raise ValueError(f"Too many lanes in branch {branch_name}")
                
            for lane_config in lanes[branch_name]:
                for direction in lane_config:
                    if direction not in ["left", "straight", "right"]:
                        raise ValueError(f"Invalid direction: {direction}")
        
        return lanes


class PhaseConfig(BaseModel):
    start: int = Field(..., ge=0)
    end: int = Field(..., gt=0)
    
    @field_validator('end')
    @classmethod
    def end_must_be_greater_than_start(cls, end, info):
        if 'start' in info.data and end <= info.data['start']:
            raise ValueError("Phase end must be greater than start")
        return end


class PhasesRequest(BaseModel):
    phases: Dict[str, Dict[str, Dict[str, int]]]
    
    @field_validator('phases')
    @classmethod
    def validate_phases(cls, phases):
        valid_branches = ["north", "south", "east", "west"]
        valid_directions = ["left", "straight", "right"]
        
        for branch_name in phases:
            if branch_name not in valid_branches:
                raise ValueError(f"Invalid branch name: {branch_name}")
                
            for direction in phases[branch_name]:
                if direction not in valid_directions:
                    raise ValueError(f"Invalid direction: {direction}")
                    
                phase = phases[branch_name][direction]
                if "start" not in phase or "end" not in phase:
                    raise ValueError(f"Missing start or end in phase for {branch_name}.{direction}")
                    
                if phase["start"] < 0 or phase["end"] <= 0 or phase["end"] <= phase["start"]:
                    raise ValueError(f"Invalid phase values: start={phase['start']}, end={phase['end']}")
        
        return phases