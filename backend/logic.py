__all__ = ["validate_adjacent_lanes", "validate_phases"]

from typing import Dict, List, Tuple, Optional, Any


def validate_adjacent_lanes(intersection: 'Intersection') -> Tuple[bool, str]:
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


def _get_opposite_branch(branch_name: str) -> Optional[str]:
    opposites = {
        "north": "south",
        "south": "north",
        "east": "west",
        "west": "east"
    }
    return opposites.get(branch_name)


def _get_right_branch(branch_name: str) -> Optional[str]:
    right_branches = {
        "north": "east",
        "east": "south",
        "south": "west",
        "west": "north"
    }
    return right_branches.get(branch_name)


def _get_left_branch(branch_name: str) -> Optional[str]:
    left_branches = {
        "north": "west",
        "west": "south",
        "south": "east",
        "east": "north"
    }
    return left_branches.get(branch_name)


def _check_conflicts(intersection: 'Intersection', time: int) -> Tuple[bool, str]:
    """Kontroluje konflikty v signáloch v danom čase."""
    signals = intersection.get_signals_at_time(time)

    for branch_name, branch_signals in signals.items():
        for signal in branch_signals:
            if signal["active"]:
                direction = signal["direction"]
                opposite_branch = _get_opposite_branch(branch_name)
                right_branch = _get_right_branch(branch_name)
                left_branch = _get_left_branch(branch_name)

                if direction == "straight":
                    for opp_signal in signals.get(opposite_branch, []):
                        if opp_signal["active"] and opp_signal["direction"] == "left":
                            return False, f"Konflikt: {branch_name} priamo a {opposite_branch} vľavo"

                    for right_signal in signals.get(right_branch, []):
                        if right_signal["active"]:
                            return False, f"Konflikt: {branch_name} priamo a {right_branch} akýkoľvek smer"

                    for left_signal in signals.get(left_branch, []):
                        if left_signal["active"] and left_signal["direction"] in ["left", "straight"]:
                            return False, f"Konflikt: {branch_name} priamo a {left_branch} vľavo/priamo"

                elif direction == "left":
                    for opp_signal in signals.get(opposite_branch, []):
                        if opp_signal["active"] and opp_signal["direction"] in ["right", "straight"]:
                            return False, f"Konflikt: {branch_name} vľavo a {opposite_branch} vpravo/priamo"

                    for right_signal in signals.get(right_branch, []):
                        if right_signal["active"] and right_signal["direction"] in ["straight", "left"]:
                            return False, f"Konflikt: {branch_name} vľavo a {right_branch} priamo/vľavo"

                    for left_signal in signals.get(left_branch, []):
                        if left_signal["active"] and left_signal["direction"] in ["left", "straight"]:
                            return False, f"Konflikt: {branch_name} vľavo a {left_branch} vľavo/priamo"

                elif direction == "right":
                    for opp_signal in signals.get(opposite_branch, []):
                        if opp_signal["active"] and opp_signal["direction"] == "left":
                            return False, f"Konflikt: {branch_name} vpravo a {opposite_branch} vľavo"

                    for left_signal in signals.get(left_branch, []):
                        if left_signal["active"] and left_signal["direction"] == "straight":
                            return False, f"Konflikt: {branch_name} vpravo a {left_branch} priamo"

    return True, ""


def validate_phases(intersection: 'Intersection') -> Tuple[bool, str]:
    """Validuje, či fázy semaforov nespôsobujú konflikty."""
    intersection.update_cycle_length()

    for time in range(intersection.cycle_length):
        valid, message = _check_conflicts(intersection, time)
        if not valid:
            return False, f"{message} v čase {time}"

    return True, ""