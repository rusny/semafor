def validate_adjacent_lanes(intersection):
    """Validuje, či susedné pruhy nemajú zakázanú konfiguráciu."""
    for branch_name, branch in intersection.branches.items():
        lanes = branch.lanes
        
        # Kontrola susedných pruhov
        for i in range(len(lanes) - 1):
            if not lanes[i].is_active() or not lanes[i+1].is_active():
                continue
                
            # Zakázané konfigurácie
            if lanes[i].directions["straight"] and lanes[i+1].directions["left"]:
                return False, f"Zakázaná konfigurácia v {branch_name}: ↑ a ← v susedných pruhoch"
                
            if lanes[i].directions["right"] and lanes[i+1].directions["left"]:
                return False, f"Zakázaná konfigurácia v {branch_name}: → a ← v susedných pruhoch"
                
            if lanes[i].directions["right"] and lanes[i+1].directions["straight"]:
                return False, f"Zakázaná konfigurácia v {branch_name}: → a ↑ v susedných pruhoch"
                
    return True, ""

def get_opposite_branch(branch_name):
    opposites = {
        "north": "south",
        "south": "north",
        "east": "west",
        "west": "east"
    }
    return opposites.get(branch_name)

def get_right_branch(branch_name):
    right_branches = {
        "north": "east",
        "east": "south",
        "south": "west",
        "west": "north"
    }
    return right_branches.get(branch_name)

def get_left_branch(branch_name):
    left_branches = {
        "north": "west",
        "west": "south",
        "south": "east",
        "east": "north"
    }
    return left_branches.get(branch_name)

def check_conflicts(intersection, time):
    """Kontroluje konflikty v signáloch v danom čase."""
    signals = intersection.get_signals_at_time(time)
    
    for branch_name, branch_signals in signals.items():
        for signal in branch_signals:
            if signal["active"]:
                direction = signal["direction"]
                opposite_branch = get_opposite_branch(branch_name)
                right_branch = get_right_branch(branch_name)
                left_branch = get_left_branch(branch_name)
                
                # Kontrola konfliktov podľa pravidiel
                if direction == "straight":
                    # Náprotivná vetva nesmie mať voľno vľavo
                    for opp_signal in signals.get(opposite_branch, []):
                        if opp_signal["active"] and opp_signal["direction"] == "left":
                            return False, f"Konflikt: {branch_name} priamo a {opposite_branch} vľavo"
                    
                    # Vetva po pravej strane nesmie mať voľno v žiadnom smere
                    for right_signal in signals.get(right_branch, []):
                        if right_signal["active"]:
                            return False, f"Konflikt: {branch_name} priamo a {right_branch} akýkoľvek smer"
                    
                    # Vetva po ľavej strane nesmie mať voľno vľavo alebo priamo
                    for left_signal in signals.get(left_branch, []):
                        if left_signal["active"] and left_signal["direction"] in ["left", "straight"]:
                            return False, f"Konflikt: {branch_name} priamo a {left_branch} vľavo/priamo"
                
                elif direction == "left":
                    # Náprotivná vetva nesmie mať voľno vpravo alebo priamo
                    for opp_signal in signals.get(opposite_branch, []):
                        if opp_signal["active"] and opp_signal["direction"] in ["right", "straight"]:
                            return False, f"Konflikt: {branch_name} vľavo a {opposite_branch} vpravo/priamo"
                    
                    # Vetva po pravej strane nesmie mať voľno priamo alebo vľavo
                    for right_signal in signals.get(right_branch, []):
                        if right_signal["active"] and right_signal["direction"] in ["straight", "left"]:
                            return False, f"Konflikt: {branch_name} vľavo a {right_branch} priamo/vľavo"
                    
                    # Vetva po ľavej strane nesmie mať voľno vľavo alebo priamo
                    for left_signal in signals.get(left_branch, []):
                        if left_signal["active"] and left_signal["direction"] in ["left", "straight"]:
                            return False, f"Konflikt: {branch_name} vľavo a {left_branch} vľavo/priamo"
                
                elif direction == "right":
                    # Náprotivná vetva nesmie mať voľno vľavo
                    for opp_signal in signals.get(opposite_branch, []):
                        if opp_signal["active"] and opp_signal["direction"] == "left":
                            return False, f"Konflikt: {branch_name} vpravo a {opposite_branch} vľavo"
                    
                    # Vetva po ľavej strane nesmie mať voľno priamo
                    for left_signal in signals.get(left_branch, []):
                        if left_signal["active"] and left_signal["direction"] == "straight":
                            return False, f"Konflikt: {branch_name} vpravo a {left_branch} priamo"
    
    return True, ""

def validate_phases(intersection):
    """Validuje, či fázy semaforov nespôsobujú konflikty."""
    intersection.update_cycle_length()
    
    # Kontrola každého časového bodu v cykle
    for time in range(intersection.cycle_length):
        valid, message = check_conflicts(intersection, time)
        if not valid:
            return False, f"{message} v čase {time}"
    
    return True, ""
