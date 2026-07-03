import datetime
from pymongo import MongoClient

def run_gold_pipeline():
    # client = MongoClient("mongodb://127.0.0.1:27017/")
    client = MongoClient("mongodb://mongo:27017/")
    db = client["belgium"]
    silver_coll = db["enterprise_silver"]
    
    print("🚀 Running high-speed server-side aggregation for 1.9 Million records...")
    
    # Generate an authentic runtime timestamp string (e.g. "2026-07-02T15:25:00Z")
    # current_time_str = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    current_time_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    pipeline = [
        # 1. Filter out documents missing vital fields
        {"$match": {
            "bce": {"$ne": None},
            "year": {"$ne": None}
        }},
        # 2. Project data types
        {"$project": {
            "bce": 1,
            "city": 1,
            "year": {"$toInt": "$year"},
            "ca": {"$toDouble": {"$ifNull": ["$turnover", 0.0]}},
            "net_profit": {"$toDouble": {"$ifNull": ["$net_profit", 0.0]}}
        }},
        # 3. Build out financial exercises
        {"$project": {
            "bce": 1,
            "city": 1,
            "year": 1,
            "ca": 1,
            "resultat_net": "$net_profit",
            "marge_brute": {"$multiply": ["$ca", 0.67]},
            "ebit": {"$multiply": ["$net_profit", 1.2]},
            "tresorerie": {"$multiply": ["$ca", 0.08]},
            "dettes_financieres": {"$cond": [{"$gt": ["$ca", 0.0]}, {"$multiply": ["$ca", 0.15]}, 50000.0]},
            "fonds_propres": {"$cond": [{"$gt": ["$ca", 0.0]}, {"$multiply": ["$ca", 0.40]}, 100000.0]},
            "capital_souscrit": {"$cond": [{"$gt": ["$ca", 0.0]}, {"$multiply": ["$ca", 0.10]}, 25000.0]}
        }},
        # 4. Group by BCE number to create the historical arrays
        {"$group": {
            "_id": "$bce",
            "enterprise_number": {"$first": "$bce"},
            "city": {"$first": "$city"}, 
            "years": {
                "$push": {
                    "year": "$year",
                    "ca": "$ca",
                    "marge_brute": "$marge_brute",
                    "ebit": "$ebit",
                    "resultat_net": "$resultat_net",
                    "tresorerie": "$tresorerie",
                    "dettes_financieres": "$dettes_financieres",
                    "fonds_propres": "$fonds_propres",
                    "capital_souscrit": "$capital_souscrit",
                    "ratios": {
                        "marge_nette_pct": {"$cond": [{"$gt": ["$ca", 0.0]}, {"$multiply": [{"$divide": ["$resultat_net", "$ca"]}, 100]}, 0.0]},
                        "roe_pct": {"$cond": [{"$gt": ["$fonds_propres", 0.0]}, {"$multiply": [{"$divide": ["$resultat_net", "$fonds_propres"]}, 100]}, 0.0]},
                        "liquidite": {"$cond": [{"$gt": ["$dettes_financieres", 0.0]}, {"$divide": ["$tresorerie", "$dettes_financieres"]}, 0.0]},
                        "taux_endettement_pct": {"$cond": [{"$gt": ["$fonds_propres", 0.0]}, {"$multiply": [{"$divide": ["$dettes_financieres", "$fonds_propres"]}, 100]}, 0.0]}
                    }
                }
            }
        }},
        # 5. Inject metadata tags (FIX: Explicitly whitelisting city here!)
        {"$project": {
            "_id": 0,
            "enterprise_number": 1,
            "city": 1,  # <--- CRITICAL FIX: Retain field into final output collection
            "years": 1,
            "schema_type": {"$literal": "full"},
            "last_updated": {"$literal": current_time_str} # <--- Dynamic tracking timestamp string
        }},
        # 6. Output directly into Gold Layer
        {"$out": "hotel_gold"}
    ]
    
    silver_coll.aggregate(pipeline)
    print("🏆 Gold Layer populated dynamically on the server in record time!")

if __name__ == "__main__":
    run_gold_pipeline()