from datetime import datetime
from pymongo import MongoClient


# =====================================================
# CONFIG
# =====================================================

MONGO_URI = "mongodb://localhost:27017"

DB_NAME = "belgium"

SILVER_COLLECTION = "enterprise_silver"
HOTEL_COLLECTION = "hotel_targets"
STATE_COLLECTION = "state_hotel"


# =====================================================
# HOTEL NACE CODES
# =====================================================

HOTEL_NACE_CODES = {
    "55100",
    "55201",
    "55202",
    "55203",
    "55204",
    "55209",
    "55300",
    "55400",
    "55900"
}


# =====================================================
# EXCLUDED LEGAL FORMS
# =====================================================

EXCLUDED_FORMS = {
    "110", "114", "116", "117",
    "301", "302", "303",
    "310", "320", "330", "340", "350",
    "400", "411", "412", "413", "414",
    "415", "416", "417", "418", "419", "420"
}


# =====================================================
# MONGO
# =====================================================

client = MongoClient(MONGO_URI)

db = client[DB_NAME]

silver = db[SILVER_COLLECTION]
hotel_targets = db[HOTEL_COLLECTION]
state = db[STATE_COLLECTION]

# reset
hotel_targets.delete_many({})
state.delete_many({})

# indexes
hotel_targets.create_index("bce", unique=True)
state.create_index("bce", unique=True)

print("Collections reset")
print("Indexes created")


# =====================================================
# MAIN
# =====================================================

hotel_docs = []
state_docs = []

now = datetime.utcnow()

count = 0

for doc in silver.find({}):

    enterprise = doc.get("enterprise", {})
    main_activity = doc.get("main_activity")

    if not main_activity:
        continue

    if enterprise.get("Status") != "AC":
        continue

    if enterprise.get("TypeOfEnterprise") != "2":
        continue

    if enterprise.get("JuridicalForm") in EXCLUDED_FORMS:
        continue

    if main_activity.get("Classification") != "MAIN":
        continue

    if main_activity.get("NaceCode") not in HOTEL_NACE_CODES:
        continue

    hotel_docs.append(doc)

    state_docs.append({
        "bce": doc["bce"],

        "source": "nbb",

        "status": "pending",

        "filings_count": 0,

        "started_at": None,
        "completed_at": None,

        "last_error": None,

        "created_at": now,
        "updated_at": now
    })

    count += 1


if hotel_docs:
    hotel_targets.insert_many(hotel_docs)

if state_docs:
    state.insert_many(state_docs)

print()
print("=" * 50)
print(f"HOTEL COMPANIES FOUND: {count:,}")
print("=" * 50)


# from pymongo import MongoClient, UpdateOne


# # =====================================================
# # CONFIG
# # =====================================================

# MONGO_URI = "mongodb://localhost:27017"

# DB_NAME = "belgium"

# SILVER_COLLECTION = "enterprise_silver"
# HOTEL_COLLECTION = "hotel_targets"
# STATE_COLLECTION = "state_hotel"


# # =====================================================
# # HOTEL NACE CODES
# # =====================================================

# HOTEL_NACE_CODES = {
#     "55100",
#     "55201",
#     "55202",
#     "55203",
#     "55204",
#     "55209",
#     "55300",
#     "55400",
#     "55900"
# }


# # =====================================================
# # EXCLUDED JURIDICAL FORMS
# # =====================================================

# EXCLUDED_FORMS = {
#     "110", "114", "116", "117",
#     "301", "302", "303",
#     "310", "320", "330", "340", "350",
#     "400", "411", "412", "413", "414",
#     "415", "416", "417", "418", "419", "420"
# }


# # =====================================================
# # MONGO
# # =====================================================

# client = MongoClient(MONGO_URI)

# db = client[DB_NAME]

# silver = db[SILVER_COLLECTION]
# hotel_targets = db[HOTEL_COLLECTION]
# state = db[STATE_COLLECTION]


# # =====================================================
# # RESET TARGET COLLECTION
# # =====================================================

# hotel_targets.delete_many({})
# state.delete_many({})

# print("Collections reset")


# # =====================================================
# # INDEXES
# # =====================================================

# hotel_targets.create_index(
#     "bce",
#     unique=True
# )

# state.create_index(
#     "bce",
#     unique=True
# )

# print("Indexes created")


# # =====================================================
# # FILTER
# # =====================================================

# count = 0

# hotel_docs = []
# state_docs = []

# cursor = silver.find({})

# for doc in cursor:

#     enterprise = doc.get("enterprise", {})
#     activity = doc.get("main_activity")

#     if not activity:
#         continue

#     # -------------------------------------
#     # Status = AC
#     # -------------------------------------

#     if enterprise.get("Status") != "AC":
#         continue

#     # -------------------------------------
#     # TypeOfEnterprise = 2
#     # -------------------------------------

#     if enterprise.get("TypeOfEnterprise") != "2":
#         continue

#     # -------------------------------------
#     # MAIN activity only
#     # -------------------------------------

#     if activity.get("Classification") != "MAIN":
#         continue

#     # -------------------------------------
#     # NACE hotel code
#     # -------------------------------------

#     nace = activity.get("NaceCode")

#     if nace not in HOTEL_NACE_CODES:
#         continue

#     # -------------------------------------
#     # Excluded juridical forms
#     # -------------------------------------

#     jf = enterprise.get("JuridicalForm")

#     if jf in EXCLUDED_FORMS:
#         continue

#     hotel_docs.append(doc)

#     state_docs.append(
#         {
#             "bce": doc["bce"],
#             "source": "nbb",
#             "status": "pending",
#             "filings_count": 0
#         }
#     )

#     count += 1


# # =====================================================
# # INSERT
# # =====================================================

# if hotel_docs:

#     hotel_targets.insert_many(
#         hotel_docs
#     )

# if state_docs:

#     state.insert_many(
#         state_docs
#     )


# print()
# print("=" * 50)
# print(f"HOTEL COMPANIES FOUND: {count:,}")
# print("=" * 50)