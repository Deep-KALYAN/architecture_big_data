import pandas as pd
from pymongo import MongoClient, UpdateOne
import random

def run_silver_transformation():
    client = MongoClient("mongodb://mongo:27017/")
    db = client["belgium"]
    
    state_coll = db["state_hotel"]
    companies_coll = db["companies_full"]
    silver_coll = db["enterprise_silver"]
    
    # Drop the old single-key unique index to clear the error path
    try:
        silver_coll.drop_index("bce_1")
    except Exception:
        pass  # Index didn't exist or already handled
        
    # Create a proper compound unique index: One record per company PER year
    silver_coll.create_index([("bce", 1), ("year", 1)], unique=True)
    
    completed_companies = list(state_coll.find({"status": "done"}))
    print(f"Found {len(completed_companies)} ingested companies to process for Silver layer.")

    operations = []

    for comp in completed_companies:
        bce = comp["bce"]
        
        master_info = companies_coll.find_one({"bce": bce})
        
        company_name = "Unknown Hotel"
        if master_info and "names" in master_info and len(master_info["names"]) > 0:
            company_name = master_info["names"][0].get("Denomination", "Unknown Hotel")
            
        zipcode = "Unknown"
        city = "Unknown"
        if master_info and "addresses" in master_info and len(master_info["addresses"]) > 0:
            zipcode = master_info["addresses"][0].get("Zipcode", "Unknown")
            city = master_info["addresses"][0].get("MunicipalityNL", "Unknown")

        for year in range(2021, 2026):
            simulated_turnover = round(random.uniform(200000, 1500000), 2)
            simulated_staff = round(simulated_turnover * random.uniform(0.25, 0.45), 2)
            simulated_net = round(simulated_turnover * random.uniform(-0.05, 0.15), 2)
            
            clean_record = {
                "bce": bce,
                "company_name": company_name,
                "sector": "Hotel",
                "zipcode": zipcode,
                "city": city,
                "year": year,
                "turnover": simulated_turnover,
                "staff_costs": simulated_staff,
                "net_profit": simulated_net,
                "staff_efficiency_ratio": round(simulated_staff / simulated_turnover, 4) if simulated_turnover > 0 else 0.0,
                "profit_margin": round(simulated_net / simulated_turnover, 4) if simulated_turnover > 0 else 0.0
            }
            
            # Use Bulk Upsert: Identifies rows matching (bce + year) and updates or inserts them safely
            operations.append(
                UpdateOne(
                    {"bce": bce, "year": year},
                    {"$set": clean_record},
                    upsert=True
                )
            )

    # Execute resilient bulk operation
    if operations:
        result = silver_coll.bulk_write(operations)
        print(f"🥈 Silver Layer Sync Complete!")
        print(f"   - Total records handled: {len(operations)}")
        print(f"   - Inserted/Upserted: {result.upserted_count + result.modified_count}")
    else:
        print("⚠️ No structural records generated.")

if __name__ == "__main__":
    run_silver_transformation()

# import pandas as pd
# from pymongo import MongoClient

# def run_silver_transformation():
#     # 1. Connect to Mongo
#     client = MongoClient("mongodb://mongo:27017/") # Internal Docker DNS
#     db = client["belgium"]
    
#     # We read from the target state ledger
#     state_coll = db["state_hotel"]
#     silver_coll = db["enterprise_silver"]
    
#     # Find all companies that have been marked as done in Bronze
#     completed_companies = list(state_coll.find({"status": "done"}))
#     print(f"Found {len(completed_companies)} ingested companies to process for Silver layer.")

#     # Standard NBB General Accounting Plan (PCN) code mapping
#     # 70 = Turnover, 62 = Personnel costs, etc.
#     NBB_CODE_MAP = {
#         "70": "turnover",
#         "61": "services_and_diverse_goods",
#         "62": "staff_costs",
#         "9901": "operating_profit_loss",
#         "9904": "net_profit_loss"
#     }

#     silver_records = []

#     for comp in completed_companies:
#         bce = comp["bce"]
        
#         # Pull the financial data that your bronze layer structured 
#         # (Assuming it was logged to a collection like 'companies_full' or stored alongside state)
#         # For this transformation step, we map raw codes to structured entities:
        
#         raw_company_data = db["companies_full"].find_one({"bce": bce})
        
#         if not raw_company_data or "filings" not in raw_company_data:
#             # Fallback mock/placeholder pattern to test the pipeline mapping if data collection is deep
#             continue
            
#         for filing in raw_company_data.get("filings", []):
#             year = filing.get("year")
#             raw_codes = filing.get("raw_accounting_codes", {}) # e.g. {"70": 450000, "62": 120000}
            
#             # Map standard columns
#             clean_record = {
#                 "bce": bce,
#                 "sector": "Hotel",
#                 "year": int(year),
#                 "turnover": float(raw_codes.get("70", 0)),
#                 "staff_costs": float(raw_codes.get("62", 0)),
#                 "operating_profit": float(raw_codes.get("9901", 0)),
#                 "net_profit": float(raw_codes.get("9904", 0))
#             }
            
#             # Calculate an Enriched KPI: Staff cost vs Turnover efficiency
#             if clean_record["turnover"] > 0:
#                 clean_record["staff_efficiency_ratio"] = round(clean_record["staff_costs"] / clean_record["turnover"], 4)
#             else:
#                 clean_record["staff_efficiency_ratio"] = 0.0
                
#             silver_records.append(clean_record)

#     # 2. Upsert/Write back to Silver Collection
#     if silver_records:
#         # Clear old rows to prevent duplicates on rerun
#         silver_coll.delete_many({"sector": "Hotel"})
        
#         # Insert clean dataset
#         silver_coll.insert_many(silver_records)
#         print(f"🥈 Silver Layer Sync Complete: Inserted {len(silver_records)} structured rows into 'enterprise_silver'!")
#     else:
#         print("⚠️ No new records structured. Check if 'companies_full' contains data keys.")

# if __name__ == "__main__":
#     run_silver_transformation()
