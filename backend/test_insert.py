from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client["traffic_db"]
collection = db["intersections"]

intersection = {
    "_id": "intersection_1",
    "name": "Testovacia krizovatka",
    "lanes": [],
    "semaphores": [],
    "cycle": {
        "cycle_duration": 60,
        "current_time_in_cycle": 0,
        "schedule": []
    }
}

collection.insert_one(intersection)
print("Testovací dokument bol vložený.")
