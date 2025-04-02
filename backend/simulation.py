import threading
import time
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client["traffic_db"]
collection = db["intersections"]


def run_simulation():
    def loop():
        while True:
            intersection = collection.find_one({"_id": "intersection_1"})
            if not intersection:
                time.sleep(1)
                continue

            current_time = intersection["cycle"]["current_time_in_cycle"]
            duration = intersection["cycle"]["cycle_duration"]
            schedule = intersection["cycle"]["schedule"]

            # Zvýš čas
            next_time = (current_time + 1) % duration

            # Zisti, či máme zmeniť stav semaforov
            for action in schedule:
                if action["at"] == next_time:
                    for sem_id, new_state in action["set_states"].items():
                        collection.update_one(
                            {"_id": "intersection_1", "semaphores.id": sem_id},
                            {"$set": {"semaphores.$.state": new_state}}
                        )

            # Ulož nový čas
            collection.update_one(
                {"_id": "intersection_1"},
                {"$set": {"cycle.current_time_in_cycle": next_time}}
            )

            time.sleep(1)

    thread = threading.Thread(target=loop, daemon=True)
    thread.start()
