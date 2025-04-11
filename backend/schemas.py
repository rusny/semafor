class Lane:
    def __init__(self):
        self.directions = {
            "left": False,
            "straight": False,
            "right": False
        }
        self.phase = {"start": 0, "end": 0}
        
    def is_active(self):
        return any(self.directions.values())
        
    def set_direction(self, direction, value):
        if direction in self.directions:
            self.directions[direction] = value
            
    def set_phase(self, start, end):
        self.phase = {"start": start, "end": end}


class Branch:
    def __init__(self, name):
        self.name = name
        self.lanes = [Lane(), Lane(), Lane()]  # 3 pruhy pre každý smer
        
    def get_active_lanes(self):
        return [lane for lane in self.lanes if lane.is_active()]


class Intersection:
    def __init__(self):
        self.branches = {
            "north": Branch("north"),
            "south": Branch("south"),
            "east": Branch("east"),
            "west": Branch("west")
        }
        self.cycle_length = 0
        
    def update_cycle_length(self):
        max_end = 0
        for branch_name, branch in self.branches.items():
            for lane in branch.lanes:
                if lane.is_active() and lane.phase["end"] > max_end:
                    max_end = lane.phase["end"]
        self.cycle_length = max_end
        
    def get_signals_at_time(self, time):
        time_in_cycle = time % self.cycle_length if self.cycle_length > 0 else 0
        signals = {}
        
        for branch_name, branch in self.branches.items():
            branch_signals = []
            for i, lane in enumerate(branch.lanes):
                if lane.is_active():
                    active = (lane.phase["start"] <= time_in_cycle < lane.phase["end"])
                    for direction, enabled in lane.directions.items():
                        if enabled:
                            branch_signals.append({
                                "lane": i,
                                "direction": direction,
                                "active": active
                            })
            signals[branch_name] = branch_signals
            
        return signals
        
    def to_dict(self):
        intersection_dict = {}
        for branch_name, branch in self.branches.items():
            branch_directions = []
            for lane in branch.lanes:
                for direction, enabled in lane.directions.items():
                    if enabled:
                        branch_directions.append(direction)
            intersection_dict[branch_name] = branch_directions
        return intersection_dict
