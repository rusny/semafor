
from pymongo import MongoClient
from models import Intersection

client = MongoClient("mongodb://localhost:27017")
db = client["traffic_db"]
collection = db["intersections"]


def get_intersection_data() -> Intersection:
    data = collection.find_one({"_id": "intersection_1"})
    if not data:
        raise Exception("Intersection not found")
    data.pop("_id", None)
    return Intersection(**data)


def update_semaphore_state(semaphore_id: str, new_state: str):
    result = collection.update_one(
        {"semaphores.id": semaphore_id},
        {"$set": {"semaphores.$.state": new_state}}
    )
    if result.matched_count == 0:
        raise Exception("Semaphore not found")
    return {"semaphore_id": semaphore_id, "new_state": new_state}
