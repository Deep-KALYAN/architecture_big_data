from datetime import datetime
from pymongo import MongoClient

MONGO_URI = "mongodb://mongo:27017" # Using container name inside Docker network
DB_NAME = "belgium"
STATE_COLLECTION = "state_hotel"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
state_col = db[STATE_COLLECTION]

def get_pending_targets(limit=50):
    """Fetch hotel targets ready for scraping."""
    return list(state_col.find({"status": "pending"}).limit(limit))

def mark_in_progress(bce: str):
    """Lock the record so other workers/tasks don't process it simultaneously."""
    state_col.update_one(
        {"bce": bce},
        {
            "$set": {
                "status": "in_progress",
                "started_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        }
    )

def mark_done(bce: str, filings_count: int):
    """Mark the target company completely scraped successfully."""
    state_col.update_one(
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

def mark_failed(bce: str, error_msg: str):
    """Log failures safely to allow future retries."""
    state_col.update_one(
        {"bce": bce},
        {
            "$set": {
                "status": "pending",  # Return to pending pool or leave as failed
                "last_error": error_msg,
                "updated_at": datetime.utcnow()
            }
        }
    )


# from pymongo import MongoClient
# from datetime import datetime

# client = MongoClient("mongodb://mongo:27017")
# db = client["belgium"]
# state = db["state"]

# state.create_index(
#     [("bce", 1), ("source", 1), ("doc_id", 1)],
#     unique=True
# )


# def already_done(bce, source, doc_id):
#     return state.find_one({
#         "bce": bce,
#         "source": source,
#         "doc_id": doc_id,
#         "status": "done"
#     }) is not None


# def mark_done(bce, source, doc_id, year, path):
#     state.update_one(
#         {
#             "bce": bce,
#             "source": source,
#             "doc_id": doc_id
#         },
#         {
#             "$set": {
#                 "year": year,
#                 "status": "done",
#                 "path": path,
#                 "timestamp": datetime.utcnow()
#             }
#         },
#         upsert=True
#     )


# # from ingestion.mongo import state
# # from datetime import datetime

# # def already_done(bce, source, doc_id, file_type):
# #     return state.find_one({
# #         "bce": bce,
# #         "source": source,
# #         "doc_id": doc_id,
# #         "type": file_type,
# #         "status": "done"
# #     }) is not None


# # def mark_done(bce, source, doc_id, year, file_type, path):
# #     state.update_one(
# #         {
# #             "bce": bce,
# #             "source": source,
# #             "doc_id": doc_id,
# #             "type": file_type
# #         },
# #         {
# #             "$set": {
# #                 "year": year,
# #                 "status": "done",
# #                 "path": path,
# #                 "timestamp": datetime.utcnow()
# #             }
# #         },
# #         upsert=True
# #     )