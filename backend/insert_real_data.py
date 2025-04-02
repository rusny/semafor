from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client["traffic_db"]
collection = db["intersections"]

intersection = {
    "_id": "intersection_1",
    "name": "Krizovatka Full",
    "lanes": [
        {"id": "lane_north_1", "from": "north", "allowed_directions": ["left"]},
        {"id": "lane_north_2", "from": "north", "allowed_directions": ["straight", "right"]}
    ],
    "semaphores": [
        {
            "id": "semaphore_north_1",
            "position": "north",
            "controls_directions": ["left"],
            "state": "red",
            "cycle_times": {"green": 15, "yellow": 3, "red": 42},
            "linked_lane_id": "lane_north_1"
        },
        {
            "id": "semaphore_north_2",
            "position": "north",
            "controls_directions": ["straight", "right"],
            "state": "green",
            "cycle_times": {"green": 30, "yellow": 3, "red": 27},
            "linked_lane_id": "lane_north_2"
        }
    ],
    "cycle": {
        "cycle_duration": 60,
        "current_time_in_cycle": 0,
        "schedule": [
            {
                "at": 0,
                "set_states": {
                    "semaphore_north_1": "green",
                    "semaphore_north_2": "red"
                }
            },
            {
                "at": 15,
                "set_states": {
                    "semaphore_north_1": "yellow"
                }
            },
            {
                "at": 18,
                "set_states": {
                    "semaphore_north_1": "red",
                    "semaphore_north_2": "green"
                }
            },
            {
                "at": 48,
                "set_states": {
                    "semaphore_north_2": "yellow"
                }
            },
            {
                "at": 51,
                "set_states": {
                    "semaphore_north_2": "red"
                }
            }
        ]
    }
}

collection.replace_one({"_id": "intersection_1"}, intersection, upsert=True)
print("✅ Dáta boli úspešne vložené do MongoDB.")
