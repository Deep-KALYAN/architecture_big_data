from ingestion.mongo import state
from datetime import datetime

def already_done(bce, source, doc_id, file_type):
    return state.find_one({
        "bce": bce,
        "source": source,
        "doc_id": doc_id,
        "type": file_type,
        "status": "done"
    }) is not None


def mark_done(bce, source, doc_id, year, file_type, path):
    state.update_one(
        {
            "bce": bce,
            "source": source,
            "doc_id": doc_id,
            "type": file_type
        },
        {
            "$set": {
                "year": year,
                "status": "done",
                "path": path,
                "timestamp": datetime.utcnow()
            }
        },
        upsert=True
    )