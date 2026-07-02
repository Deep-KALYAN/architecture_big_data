from pathlib import Path
from datetime import datetime
import math

import pandas as pd
from pymongo import MongoClient, UpdateOne


# =====================================================
# CONFIG
# =====================================================

DATA = Path(r"C:\Users\DeepKalyan\IPSSI\23_Architecture_Big_Data\data\kbo")

MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "belgium"

BRONZE_COLLECTION = "companies_full"
SILVER_COLLECTION = "enterprise_silver"

BATCH_SIZE = 1000


# =====================================================
# MONGO
# =====================================================

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

bronze = db[BRONZE_COLLECTION]
silver = db[SILVER_COLLECTION]

print("Connected to MongoDB")


# =====================================================
# LOAD CODE TABLE
# =====================================================

print("Loading code.csv...")

df_codes = pd.read_csv(DATA / "code.csv", dtype=str)

# French labels only
df_codes = df_codes[df_codes["Language"] == "FR"]

label_maps = {}

for category in df_codes["Category"].unique():

    subset = df_codes[df_codes["Category"] == category]

    label_maps[category] = {
        str(row["Code"]): row["Description"]
        for _, row in subset.iterrows()
    }

print("Code dictionaries loaded")


# =====================================================
# HELPERS
# =====================================================

def normalize_date(date_str):

    if not date_str:
        return None

    try:
        return datetime.strptime(
            date_str,
            "%d-%m-%Y"
        ).strftime("%Y-%m-%d")

    except Exception:
        return date_str


def clean_nan(value):

    if isinstance(value, float):

        try:
            if math.isnan(value):
                return None
        except Exception:
            pass

    return value


def clean_document(obj):

    if isinstance(obj, dict):

        return {
            k: clean_document(v)
            for k, v in obj.items()
        }

    if isinstance(obj, list):

        return [
            clean_document(v)
            for v in obj
        ]

    return clean_nan(obj)


def deduplicate_activities(activities):

    seen = set()
    result = []

    for activity in activities:

        key = (
            activity.get("NaceCode"),
            activity.get("Classification")
        )

        if key in seen:
            continue

        seen.add(key)
        result.append(activity)

    return result


def enrich_activity(activity):

    code = activity.get("NaceCode")
    version = activity.get("NaceVersion")

    label = None

    if version == "2003":

        label = (
            label_maps
            .get("Nace2003", {})
            .get(code)
        )

    elif version == "2008":

        label = (
            label_maps
            .get("Nace2008", {})
            .get(code)
        )

    elif version == "2025":

        label = (
            label_maps
            .get("Nace2025", {})
            .get(code)
        )

    activity["NaceLabel"] = label

    activity["ClassificationLabel"] = (
        label_maps
        .get("Classification", {})
        .get(activity.get("Classification"))
    )

    activity["ActivityGroupLabel"] = (
        label_maps
        .get("ActivityGroup", {})
        .get(activity.get("ActivityGroup"))
    )

    return activity


def enrich_names(names):

    if not names:
        return []

    for name in names:

        name["LanguageLabel"] = (
            label_maps
            .get("Language", {})
            .get(name.get("Language"))
        )

    names.sort(
        key=lambda x:
        x.get("TypeOfDenomination") != "001"
    )

    return names


def get_main_name(names):

    for name in names:

        if name.get("TypeOfDenomination") == "001":
            return name.get("Denomination")

    if names:
        return names[0].get("Denomination")

    return None


def get_main_activity(activities):

    for activity in activities:

        if activity.get("Classification") == "MAIN":

            return {
                "NaceCode": activity.get("NaceCode"),
                "NaceVersion": activity.get("NaceVersion"),
                "NaceLabel": activity.get("NaceLabel"),
                "Classification": activity.get("Classification"),
                "ClassificationLabel": activity.get("ClassificationLabel")
            }

    return None


def get_rego_address(addresses):

    if not addresses:
        return None

    rego = [
        a
        for a in addresses
        if a.get("TypeOfAddress") == "REGO"
    ]

    if rego:
        return rego[0]

    return addresses[0]


def normalize_establishments(establishments):

    for est in establishments:

        est["StartDate"] = normalize_date(
            est.get("StartDate")
        )

    return establishments


# =====================================================
# INDEXES
# =====================================================

print("Creating indexes...")

silver.create_index(
    "bce",
    unique=True
)

silver.create_index(
    "enterprise.Status"
)

silver.create_index(
    "enterprise.JuridicalForm"
)

silver.create_index(
    "main_activity.NaceCode"
)

print("Indexes ready")


# =====================================================
# BUILD SILVER
# =====================================================

total = bronze.count_documents({})

print(f"Documents to process: {total:,}")

operations = []
processed = 0

cursor = bronze.find({})

for doc in cursor:

    processed += 1

    enterprise = doc.get("enterprise", {})
    activities = doc.get("activities", [])
    addresses = doc.get("addresses", [])
    names = doc.get("names", [])
    contacts = doc.get("contacts", [])
    establishments = doc.get("establishments", [])

    # -----------------------------------------
    # Enterprise enrichment
    # -----------------------------------------

    enterprise["StartDate"] = normalize_date(
        enterprise.get("StartDate")
    )

    enterprise["StatusLabel"] = (
        label_maps
        .get("Status", {})
        .get(enterprise.get("Status"))
    )

    enterprise["JuridicalFormLabel"] = (
        label_maps
        .get("JuridicalForm", {})
        .get(enterprise.get("JuridicalForm"))
    )

    enterprise["TypeOfEnterpriseLabel"] = (
        label_maps
        .get("TypeOfEnterprise", {})
        .get(enterprise.get("TypeOfEnterprise"))
    )

    enterprise["JuridicalSituationLabel"] = (
        label_maps
        .get("JuridicalSituation", {})
        .get(enterprise.get("JuridicalSituation"))
    )

    # -----------------------------------------
    # Activities
    # -----------------------------------------

    activities = deduplicate_activities(
        activities
    )

    activities = [
        enrich_activity(a)
        for a in activities
    ]

    main_activity = get_main_activity(
        activities
    )

    # -----------------------------------------
    # Address
    # -----------------------------------------

    address = get_rego_address(
        addresses
    )

    # -----------------------------------------
    # Names
    # -----------------------------------------

    names = enrich_names(
        names
    )

    main_name = get_main_name(
        names
    )

    # -----------------------------------------
    # Establishments
    # -----------------------------------------

    establishments = normalize_establishments(
        establishments
    )

    # -----------------------------------------
    # Silver document
    # -----------------------------------------

    silver_doc = {

        "bce": doc["bce"],

        "main_name": main_name,

        "enterprise": clean_document(
            enterprise
        ),

        "address": clean_document(
            address
        ),

        "main_activity": clean_document(
            main_activity
        ),

        "activities": clean_document(
            activities
        ),

        "names": clean_document(
            names
        ),

        "contacts": clean_document(
            contacts
        ),

        "establishments": clean_document(
            establishments
        )
    }

    operations.append(
        UpdateOne(
            {"bce": doc["bce"]},
            {"$set": silver_doc},
            upsert=True
        )
    )

    # -----------------------------------------
    # Bulk write
    # -----------------------------------------

    if len(operations) >= BATCH_SIZE:

        silver.bulk_write(
            operations,
            ordered=False
        )

        operations = []

        print(
            f"Processed {processed:,}"
        )

        # break  # ◄--- ADD THIS LINE TO STOP AFTER 1 BATCH

# Final batch
if operations:

    silver.bulk_write(
        operations,
        ordered=False
    )

print()
print("=" * 50)
print("SILVER BUILD COMPLETE")
print("=" * 50)
print(f"Processed: {processed:,}")



# from pathlib import Path
# from datetime import datetime

# import pandas as pd
# from pymongo import MongoClient, UpdateOne




# # =====================================================
# # CONFIG
# # =====================================================

# DATA = Path(r"C:\Users\DeepKalyan\IPSSI\23_Architecture_Big_Data\data\kbo")

# MONGO_URI = "mongodb://localhost:27017"
# DB_NAME = "belgium"

# BRONZE_COLLECTION = "companies_full"
# SILVER_COLLECTION = "enterprise_silver"

# BATCH_SIZE = 1000


# # =====================================================
# # MONGO
# # =====================================================

# client = MongoClient(MONGO_URI)
# db = client[DB_NAME]

# bronze = db[BRONZE_COLLECTION]
# silver = db[SILVER_COLLECTION]

# print("Connected to MongoDB")


# # =====================================================
# # LOAD CODE TABLE
# # =====================================================

# print("Loading code.csv ...")

# df_codes = pd.read_csv(DATA / "code.csv", dtype=str)

# # Keep only French labels
# df_codes = df_codes[df_codes["Language"] == "FR"]

# label_maps = {}

# for category in df_codes["Category"].unique():
#     subset = df_codes[df_codes["Category"] == category]

#     label_maps[category] = {
#         str(row["Code"]): row["Description"]
#         for _, row in subset.iterrows()
#     }

# print("Code dictionaries loaded")


# # =====================================================
# # HELPERS
# # =====================================================

# def normalize_date(date_str):
#     """
#     Convert DD-MM-YYYY -> YYYY-MM-DD
#     """
#     if not date_str:
#         return None

#     try:
#         return datetime.strptime(
#             date_str,
#             "%d-%m-%Y"
#         ).strftime("%Y-%m-%d")
#     except Exception:
#         return date_str


# def deduplicate_activities(activities):
#     """
#     Deduplicate using:
#     NaceCode + Classification

#     Keep different NACE versions if code differs.
#     """
#     seen = set()
#     result = []

#     for activity in activities:

#         key = (
#             activity.get("NaceCode"),
#             activity.get("Classification")
#         )

#         if key in seen:
#             continue

#         seen.add(key)
#         result.append(activity)

#     return result


# def enrich_activity_labels(activity):
#     code = activity.get("NaceCode")
#     version = activity.get("NaceVersion")

#     label = None

#     if version == "2003":
#         label = label_maps.get(
#             "Nace2003",
#             {}
#         ).get(code)

#     elif version == "2008":
#         label = label_maps.get(
#             "Nace2008",
#             {}
#         ).get(code)

#     elif version == "2025":
#         label = label_maps.get(
#             "Nace2025",
#             {}
#         ).get(code)

#     if label:
#         activity["NaceLabel"] = label

#     activity["ClassificationLabel"] = (
#         label_maps.get("Classification", {})
#         .get(activity.get("Classification"))
#     )

#     activity["ActivityGroupLabel"] = (
#         label_maps.get("ActivityGroup", {})
#         .get(activity.get("ActivityGroup"))
#     )

#     return activity


# def get_rego_address(addresses):

#     if not addresses:
#         return None

#     rego = [
#         a
#         for a in addresses
#         if a.get("TypeOfAddress") == "REGO"
#     ]

#     if rego:
#         return rego[0]

#     return addresses[0]


# def sort_names(names):

#     if not names:
#         return []

#     names.sort(
#         key=lambda x:
#         x.get("TypeOfDenomination") != "001"
#     )

#     return names


# # =====================================================
# # INDEXES
# # =====================================================

# print("Creating indexes...")

# silver.create_index("bce", unique=True)
# silver.create_index("enterprise.Status")
# silver.create_index("enterprise.JuridicalForm")
# silver.create_index("activities.NaceCode")

# print("Indexes ready")


# # =====================================================
# # SILVER BUILD
# # =====================================================

# total = bronze.count_documents({})

# print(f"Documents to process: {total:,}")

# operations = []
# processed = 0

# cursor = bronze.find({})

# for doc in cursor:

#     processed += 1

#     enterprise = doc.get("enterprise", {})
#     activities = doc.get("activities", [])
#     names = doc.get("names", [])
#     addresses = doc.get("addresses", [])

#     # -------------------------------------------------
#     # DATE NORMALIZATION
#     # -------------------------------------------------

#     enterprise["StartDate"] = normalize_date(
#         enterprise.get("StartDate")
#     )

#     # -------------------------------------------------
#     # LABELS
#     # -------------------------------------------------

#     enterprise["StatusLabel"] = (
#         label_maps.get("Status", {})
#         .get(enterprise.get("Status"))
#     )

#     enterprise["JuridicalFormLabel"] = (
#         label_maps.get("JuridicalForm", {})
#         .get(enterprise.get("JuridicalForm"))
#     )

#     enterprise["TypeOfEnterpriseLabel"] = (
#         label_maps.get("TypeOfEnterprise", {})
#         .get(enterprise.get("TypeOfEnterprise"))
#     )

#     enterprise["JuridicalSituationLabel"] = (
#         label_maps.get("JuridicalSituation", {})
#         .get(enterprise.get("JuridicalSituation"))
#     )

#     # -------------------------------------------------
#     # ACTIVITIES
#     # -------------------------------------------------

#     activities = deduplicate_activities(activities)

#     activities = [
#         enrich_activity_labels(a)
#         for a in activities
#     ]

#     # -------------------------------------------------
#     # ADDRESS
#     # -------------------------------------------------

#     address = get_rego_address(addresses)

#     # -------------------------------------------------
#     # NAMES
#     # -------------------------------------------------

#     names = sort_names(names)

#     # -------------------------------------------------
#     # BUILD SILVER DOC
#     # -------------------------------------------------

#     silver_doc = {
#         "bce": doc["bce"],

#         "enterprise": enterprise,

#         "names": names,

#         # Day 2 -> unique registered address
#         "address": address,

#         "activities": activities,

#         "contacts": doc.get(
#             "contacts",
#             []
#         ),

#         "establishments": doc.get(
#             "establishments",
#             []
#         )
#     }

#     operations.append(
#         UpdateOne(
#             {"bce": doc["bce"]},
#             {"$set": silver_doc},
#             upsert=True
#         )
#     )

#     # -------------------------------------------------
#     # BULK WRITE
#     # -------------------------------------------------

#     if len(operations) >= BATCH_SIZE:

#         silver.bulk_write(
#             operations,
#             ordered=False
#         )

#         operations = []

#         print(
#             f"Processed: "
#             f"{processed:,}/{total:,}"
#         )

# # Final batch
# if operations:

#     silver.bulk_write(
#         operations,
#         ordered=False
#     )

# print()
# print("====================================")
# print("SILVER BUILD COMPLETE")
# print("====================================")
# print(
#     f"Total processed: {processed:,}"
# )