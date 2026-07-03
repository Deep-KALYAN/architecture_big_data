import asyncio
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse,StreamingResponse
from pymongo import MongoClient
from sse_starlette.sse import EventSourceResponse
import httpx
import glob
import json
import os

app = FastAPI(title="Belgium Enterprise Analytics API - Day 3")

# Enable CORS so your React frontend can talk to this API seamlessly
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect to MongoDB
mongo_client = MongoClient("mongodb://127.0.0.1:27017/")
db = mongo_client["belgium"]

@app.get("/")
def read_root():
    return {"status": "online", "layer": "Gold & Silver Backend Ready"}

### 🌆 0. Get Existing Cities directly from the Gold Layer
@app.get("/api/cities")
def get_existing_cities():
    """
    Returns unique cities straight from Gold, falling back to Silver if Gold isn't populated.
    """
    try:
        pipeline = [
            {"$match": {"city": {"$ne": None, "$gt": ""}}},
            {"$group": {"_id": "$city"}},
            {"$sort": {"_id": 1}},
            {"$limit": 550}
        ]
        
        # 1. Try pulling from the optimized hotel_gold layer
        cities = [doc["_id"] for doc in db["hotel_gold"].aggregate(pipeline)]
        
        # 2. Fallback if Gold is empty or hasn't finished processing yet
        if not cities:
            print("⚠️ hotel_gold collection is empty! Pulling temporary live cities from enterprise_silver...")
            cities = [doc["_id"] for doc in db["enterprise_silver"].aggregate(pipeline)]
            
        return cities
    except Exception as e:
        print(f"❌ CITIES ENDPOINT ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


### 🔍 1. Company Search Endpoint (Deduplicated)
@app.get("/api/companies/search")
def search_companies(q: str = Query(..., min_length=2)):
    """
    Search for companies by BCE number or name, grouped to avoid duplicates
    """
    try:
        pipeline = [
            # Match the search term against name, bce, or city
            {"$match": {
                "$or": [
                    {"bce": {"$regex": q, "$options": "i"}},
                    {"company_name": {"$regex": q, "$options": "i"}},
                    {"city": {"$regex": q, "$options": "i"}}
                ]
            }},
            # Sort by year descending so we grab the most recent administrative data
            {"$sort": {"year": -1}},
            # Group by BCE to eliminate year duplicates
            {"$group": {
                "_id": "$bce",
                "bce": {"$first": "$bce"},
                "company_name": {"$first": "$company_name"},
                "city": {"$first": "$city"},
                "zipcode": {"$first": "$zipcode"},
                "sector": {"$first": "$sector"}
            }},
            {"$limit": 220}
        ]
        
        results = list(db["enterprise_silver"].aggregate(pipeline))
        return results

    except Exception as e:
        print(f"❌ SEARCH ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Backend Search Error: {str(e)}")


### 📊 2. Complete Company Profile Sheet
@app.get("/api/companies/{bce}")
def get_company_profile(bce: str):
    """
    Combines Silver structural details with Gold financial indicators
    """
    try:
        # Fetch the most recent administrative details from Silver
        silver_data = db["enterprise_silver"].find_one(
            {"bce": bce}, 
            {"_id": 0},
            sort=[("year", -1)]
        )
        
        if not silver_data:
            raise HTTPException(status_code=404, detail="Company not found in Silver layer.")
        
        # Fetch unified financial tracking sheets from Gold
        gold_data = db["hotel_gold"].find_one({"enterprise_number": bce}, {"_id": 0})
        
        return {
            "metadata": {
                "bce": silver_data.get("bce", bce),
                "company_name": silver_data.get("company_name", "Unknown Name"),
                "city": silver_data.get("city", "Unknown City"),
                "zipcode": silver_data.get("zipcode", "")
            },
            "financials": gold_data.get("years", []) if gold_data else [],
            "schema_type": gold_data.get("schema_type", "unknown") if gold_data else "unknown"
        }
    except Exception as e:
        print(f"❌ PROFILE ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Backend Profile Error: {str(e)}")

# ### 🔀 3. Smart Notary Statutes SSE Streaming Endpoint
@app.get("/api/companies/{bce}/statutes/stream")
async def stream_company_statutes(bce: str):
    async def event_generator():
        yield {"event": "message", "data": json.dumps({"status": "initializing", "message": f"Auditing Bronze Data Lake for entity {bce}..."})}
        await asyncio.sleep(0.3)

        # 📂 Scan the actual structure: data/bronze/nbb/0465885159/**/*.pdf
        search_pattern = os.path.join("data", "bronze", "nbb", bce, "**", "*.pdf")
        local_files = glob.glob(search_pattern, recursive=True)

        yield {"event": "message", "data": json.dumps({"status": "scraping", "message": "Evaluating cluster storage records..."})}
        await asyncio.sleep(0.3)

        if local_files:
            # Found matching local documents! Grab the first available file
            found_file = local_files[0]
            file_name = os.path.basename(found_file)
            
            yield {
                "event": "message", 
                "data": json.dumps({
                    "status": "document_found", 
                    "message": f"🟢 Success! Found local archive copy: {file_name}",
                    "doc": {
                        "type": "NBB Financial Filing (Local Mirror)",
                        "date": "Stored Locally",
                        "url": f"http://127.0.0.1:8000/api/proxy/act/{bce}" 
                    }
                })
            }
        else:
            # Fallback path if it hasn't been cached yet
            external_federal_url = "https://www.ejustice.just.fgov.be/tsv/tsvn.htm"
            yield {
                "event": "message", 
                "data": json.dumps({
                    "status": "document_found", 
                    "message": "裁 Notice: File not found in local Bronze cache. Please reference the official registry site.",
                    "doc": {
                        "type": "Moniteur Belge Portal (External Link)",
                        "date": "External Site Link",
                        "url": external_federal_url
                    }
                })
            }

        yield {"event": "message", "data": json.dumps({"status": "completed", "message": "Scraping pipeline successfully finalized."})}

    return EventSourceResponse(event_generator())

# ### 🔀 3. Smart Notary Statutes SSE Streaming Endpoint
# @app.get("/api/companies/{bce}/statutes/stream")
# async def stream_company_statutes(bce: str):
#     """
#     Deterministic Document Router:
#     1. Audits the local Bronze data storage layer using the BCE primary key.
#     2. If found locally, serves an internal URL to display the PDF in a new tab.
#     3. If missing, alters the message status and provides the official external site link.
#     """
#     async def event_generator():
#         yield {"event": "message", "data": json.dumps({"status": "initializing", "message": f"Checking local Bronze Storage volumes for BCE Key: {bce}..."})}
#         await asyncio.sleep(0.4)

#         # 📂 1. Deterministic local file check using our Primary Key structure
#         local_file_path = f"./data/bronze/statutes/{bce}.pdf"
#         local_pdf_exists = os.path.exists(local_file_path)

#         yield {"event": "message", "data": json.dumps({"status": "scraping", "message": "Evaluating cluster cache records..."})}
#         await asyncio.sleep(0.4)

#         if local_pdf_exists:
#             # ✅ CONDITION A: Found inside our local storage infrastructure!
#             yield {
#                 "event": "message", 
#                 "data": json.dumps({
#                     "status": "document_found", 
#                     "message": "🟢 Success! Found authentic copy locally inside the Bronze Storage layer.",
#                     "doc": {
#                         "type": "Statuts Constitutifs (Local Mirror)",
#                         "date": "Stored Locally",
#                         # This points to our proxy route which serves the local file
#                         "url": f"http://127.0.0.1:8000/api/proxy/act/{bce}" 
#                     }
#                 })
#             }
#         else:
#             # ❌ CONDITION B: Cache Miss. Direct the user to the source engine.
#             print(f"⚠️ Primary Key {bce} not found in Bronze storage directory. Routing to fallback.")
            
#             # Direct link to the official Moniteur Belge portal page where the legal acts live
#             external_federal_url = "https://www.ejustice.just.fgov.be/tsv/tsvn.htm"
            
#             yield {
#                 "event": "message", 
#                 "data": json.dumps({
#                     "status": "document_found", 
#                     "message": "🟡 Notice: File not found in local Bronze cache. Please reference the official registry site.",
#                     "doc": {
#                         "type": "Moniteur Belge Portal (External Link)",
#                         "date": "External Site Link",
#                         "url": external_federal_url
#                     }
#                 })
#             }

#         yield {"event": "message", "data": json.dumps({"status": "completed", "message": "Scraping pipeline successfully finalized."})}

#     return EventSourceResponse(event_generator())

@app.get("/api/documents/download/{bce}")
def download_bronze_pdf(bce: str):
    """
    Serves the raw PDF directly from your local project repository's Bronze folder storage
    """
    # Look for the file inside your local file system data repository structure
    local_file_path = f"./data/bronze/statutes/{bce}.pdf"
    
    if os.path.exists(local_file_path):
        return FileResponse(
            path=local_file_path, 
            filename=f"BCE_{bce}_Statutes.pdf", 
            media_type="application/pdf"
        )
    else:
        # If the file hasn't been physically downloaded to disk yet, throw a clean 404 message
        raise HTTPException(
            status_code=404, 
            detail=f"The raw document for BCE {bce} hasn't been fully downloaded into the Bronze storage folder yet."
        )
    
@app.get("/api/proxy/act/{bce}")
async def proxy_notaire_act(bce: str):
    """
    Dynamically routes local PDF assets from the hierarchical NBB folder structure.
    """
    search_pattern = os.path.join("data", "bronze", "nbb", bce, "**", "*.pdf")
    local_files = glob.glob(search_pattern, recursive=True)
    
    if local_files:
        found_file = local_files[0]  # Grab the first available file path
        file_name = os.path.basename(found_file)
        print(f"📦 Cache Hit! Serving {file_name} dynamically from local cluster storage.")
        return FileResponse(
            path=found_file, 
            filename=file_name, 
            media_type="application/pdf"
        )
        
    # Final fallback if missing completely
    raise HTTPException(
        status_code=404, 
        detail="The document for this company could not be found in local or external repositories."
    )

@app.get("/api/analytics/finance")
def get_finance_analytics():
    # 🔌 FIX 1: Use 127.0.0.1 because FastAPI runs directly on Windows host
    client = MongoClient("mongodb://127.0.0.1:27017/") 
    db = client["belgium"]
    records = list(db["hotel_gold"].find({}))
    
    total_turnover = 0
    total_margin = 0
    margin_count = 0
    top_company = "N/A"
    max_turnover = -1
    
    for r in records:
        # 📌 FIX 2: Parse the nested "years" array from your actual schema
        years_data = r.get("years", [])
        if years_data:
            # Sort to extract the highest/latest year block (e.g., 2025)
            latest_year_data = sorted(years_data, key=lambda x: x.get("year", 0), reverse=True)[0]
            
            turnover = latest_year_data.get("ca", 0) or 0
            margin = latest_year_data.get("marge_brute", 0) or 0
            
            total_turnover += turnover
            if margin:
                total_margin += margin
                margin_count += 1
                
            # Track the top market leader using the enterprise identifier
            if turnover > max_turnover:
                max_turnover = turnover
                # Use enterprise_number since company_name isn't in root
                top_company = f"Enterprise {r.get('enterprise_number', 'Unknown')} - {r.get('city', 'Unknown')}"
                
    avg_margin = total_margin / margin_count if margin_count > 0 else 0
    
    return {
        "total_turnover": total_turnover,
        "average_margin": avg_margin,
        "market_leader": top_company,
        "market_leader_revenue": max_turnover if max_turnover != -1 else 0
    }
    


# @app.get("/api/analytics/finance")
# def get_finance_analytics():
#     # Connect directly to your hotel_gold serving collection
#     client = MongoClient("mongodb://127.0.0.1:27017/") # Or mongo:27017 inside Docker
#     db = client["belgium"]
#     gold_coll = db["hotel_gold"]
    
#     # Grab all 161 records
#     records = list(gold_coll.find({}))
    
#     total_turnover = 0
#     total_margin = 0
#     margin_count = 0
#     top_company = "N/A"
#     max_turnover = -1
    
#     for r in records:
#         # Pull financials array (usually has multiple years; grab latest)
#         financials = r.get("financials", [])
#         if financials:
#             # Sort to get the latest reported year exercise
#             latest = sorted(financials, key=lambda x: x.get("year", ""), reverse=True)[0]
#             turnover = latest.get("ca", 0) or 0
#             margin = latest.get("marge_brute", 0) or 0
            
#             total_turnover += turnover
#             if margin:
#                 total_margin += margin
#                 margin_count += 1
                
#             # Track the top market leader
#             if turnover > max_turnover:
#                 max_turnover = turnover
#                 top_company = r.get("metadata", {}).get("company_name", r.get("company_name", "Unknown"))
                
#     avg_margin = total_margin / margin_count if margin_count > 0 else 0
    
#     return {
#         "total_turnover": total_turnover,
#         "average_margin": avg_margin,
#         "market_leader": top_company,
#         "market_leader_revenue": max_turnover
#     }