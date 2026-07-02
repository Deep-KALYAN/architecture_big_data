from datetime import datetime
from pymongo import MongoClient


client = MongoClient("mongodb://localhost:27017")

db = client["belgium"]

state = db["state_hotel"]


def mark_in_progress(bce):

    state.update_one(
        {"bce": bce},
        {
            "$set": {
                "status": "in_progress",
                "started_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        }
    )


def mark_done(bce, filings_count):

    state.update_one(
        {"bce": bce},
        {
            "$set": {
                "status": "done",
                "filings_count": filings_count,
                "completed_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "last_error": None
            }
        }
    )


def mark_error(bce, error_message):

    state.update_one(
        {"bce": bce},
        {
            "$set": {
                "status": "error",
                "updated_at": datetime.utcnow(),
                "last_error": str(error_message)
            }
        }
    )


def get_pending_companies(limit=None):

    query = {
        "status": {
            "$in": [
                "pending",
                "error"
            ]
        }
    }

    cursor = state.find(query)

    if limit:
        cursor = cursor.limit(limit)

    return list(cursor)