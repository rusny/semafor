from pydantic import BaseModel, Field
from typing import List, Literal, Dict


class Lane(BaseModel):
    id: str
    from_: Literal["north", "south", "east", "west"] = Field(..., alias="from")
    allowed_directions: List[Literal["left", "straight", "right"]]


class Semaphore(BaseModel):
    id: str
    position: Literal["north", "south", "east", "west"]
    controls_directions: List[Literal["left", "straight", "right"]]
    state: Literal["green", "yellow", "red"]
    cycle_times: Dict[str, int]
    linked_lane_id: str


class ScheduleItem(BaseModel):
    at: int
    set_states: Dict[str, Literal["green", "yellow", "red"]]


class Cycle(BaseModel):
    cycle_duration: int
    current_time_in_cycle: int
    schedule: List[ScheduleItem]


class Intersection(BaseModel):
    name: str
    lanes: List[Lane]
    semaphores: List[Semaphore]
    cycle: Cycle


class SemaphoreUpdate(BaseModel):
    state: Literal["green", "yellow", "red"]
