import pandas as pd
from pathlib import Path
from pymongo import MongoClient

# -----------------------------
# CONFIG
# -----------------------------
DATA = Path(r"C:\Users\DeepKalyan\IPSSI\23_Architecture_Big_Data\data\kbo")

MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "belgium"
COLLECTION = "companies_full"

CHUNK_SIZE = 20000   # ✅ safe for big data


# -----------------------------
# CONNECT MONGO
# -----------------------------
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
col = db[COLLECTION]

# reset (only for testing)
col.delete_many({})

# create index
col.create_index("bce")


# -----------------------------
# HELPERS
# -----------------------------
def clean(x):
    return x.replace(".", "") if pd.notna(x) else x


# -----------------------------
# LOAD SMALL TABLES (FULL)
# -----------------------------
print("Loading small tables...")

df_denomination = pd.read_csv(DATA / "denomination.csv", dtype=str)
df_address      = pd.read_csv(DATA / "address.csv", dtype=str)
df_contact      = pd.read_csv(DATA / "contact.csv", dtype=str)
df_establishment = pd.read_csv(DATA / "establishment.csv", dtype=str)

# Clean keys
df_denomination["EntityNumber"] = df_denomination["EntityNumber"].map(clean)
df_address["EntityNumber"]      = df_address["EntityNumber"].map(clean)
df_contact["EntityNumber"]      = df_contact["EntityNumber"].map(clean)
df_establishment["EnterpriseNumber"] = df_establishment["EnterpriseNumber"].map(clean)

# Group
print("Grouping small tables...")
grp_denom = df_denomination.groupby("EntityNumber")
grp_addr  = df_address.groupby("EntityNumber")
grp_cont  = df_contact.groupby("EntityNumber")
grp_est   = df_establishment.groupby("EnterpriseNumber")


# -----------------------------
# LOAD LARGE TABLE (ACTIVITY) IN MEMORY (OPTIONAL)
# -----------------------------
# ⚠ This is huge: 34M rows
# Option 1 (safe): load FULL but may use RAM
# Option 2 (better): chunked processing (advanced)

print("Loading activities (may take time)...")

df_activity = pd.read_csv(DATA / "activity.csv", dtype=str)
df_activity["EntityNumber"] = df_activity["EntityNumber"].map(clean)

grp_act = df_activity.groupby("EntityNumber")


# -----------------------------
# MAIN LOOP (CHUNKED ENTERPRISE)
# -----------------------------
print("Processing enterprises...")

reader = pd.read_csv(DATA / "enterprise.csv", dtype=str, chunksize=CHUNK_SIZE)

total_inserted = 0

for chunk_id, df_enterprise in enumerate(reader):

    print(f"\nProcessing chunk {chunk_id + 1}")

    df_enterprise["EnterpriseNumber"] = df_enterprise["EnterpriseNumber"].map(clean)

    docs = []

    for _, row in df_enterprise.iterrows():
        bce = row["EnterpriseNumber"]

        doc = {
            "bce": bce,

            "enterprise": row.to_dict(),

            "names": grp_denom.get_group(bce).to_dict("records")
                if bce in grp_denom.groups else [],

            "addresses": grp_addr.get_group(bce).to_dict("records")
                if bce in grp_addr.groups else [],

            "activities": grp_act.get_group(bce).to_dict("records")
                if bce in grp_act.groups else [],

            "contacts": grp_cont.get_group(bce).to_dict("records")
                if bce in grp_cont.groups else [],

            "establishments": grp_est.get_group(bce).to_dict("records")
                if bce in grp_est.groups else [],
        }

        docs.append(doc)

    # insert batch
    if docs:
        col.insert_many(docs)
        total_inserted += len(docs)

    print(f"Inserted {total_inserted} documents so far...")

    # ◄--- ADD THESE TWO LINES TO STOP AFTER 1 BATCH
    print("Test chunk complete. Exiting loop.")
    break


print("\nDONE ✅")
print(f"Total inserted: {total_inserted}")


# import pandas as pd
# from pathlib import Path
# from ingestion.mongo import companies

# DATA = Path(r"C:\Users\DeepKalyan\IPSSI\23_Architecture_Big_Data\data\kbo")

# # Load CSVs
# df_enterprise   = pd.read_csv(DATA / "enterprise.csv", dtype=str)
# df_denomination = pd.read_csv(DATA / "denomination.csv", dtype=str)
# df_address      = pd.read_csv(DATA / "address.csv", dtype=str)


# # --- Clean BCE format ---
# def clean_bce(x):
#     return x.replace(".", "") if pd.notna(x) else x


# df_enterprise["EnterpriseNumber"] = df_enterprise["EnterpriseNumber"].apply(clean_bce)
# df_denomination["EntityNumber"]   = df_denomination["EntityNumber"].apply(clean_bce)
# df_address["EntityNumber"]        = df_address["EntityNumber"].apply(clean_bce)


# # --- Keep MAIN denomination only (TypeOfDenomination = 001) ---
# df_name = df_denomination[df_denomination["TypeOfDenomination"] == "001"]

# # Keep only 1 name per company
# df_name = df_name.drop_duplicates("EntityNumber")


# # --- Keep only REGO (registered address) ---
# df_addr = df_address[df_address["TypeOfAddress"] == "REGO"]
# df_addr = df_addr.drop_duplicates("EntityNumber")


# # --- Merge ---
# df = df_enterprise.merge(df_name, left_on="EnterpriseNumber", right_on="EntityNumber", how="left")
# df = df.merge(df_addr, left_on="EnterpriseNumber", right_on="EntityNumber", how="left")


# # --- Build Mongo documents ---
# docs = []

# # create the index no.entreprise
# # What is binary research?
# for _, row in df.iterrows():
#     doc = {
#         "bce": row["EnterpriseNumber"],
#         "status": row["Status"],
#         "juridical_form": row["JuridicalForm"],
#         "start_date": row["StartDate"],

#         "name": row.get("Denomination"), #"name": row["Denomination"],

#         "address": {
#             "zipcode": row.get("Zipcode"),
#             "city": row.get("MunicipalityFR") or row.get("MunicipalityNL"),
#             "street": row.get("StreetFR") or row.get("StreetNL"),
#             "number": row.get("HouseNumber"),
#         }
#     }
#     docs.append(doc)


# # --- Insert into Mongo ---
# companies.delete_many({})   # reset (only first time)
# companies.insert_many(docs)

# print(f"Inserted {len(docs)} companies into MongoDB")