from pymongo import MongoClient

client = MongoClient("mongodb://mongo:27017")
db = client["belgium"]

# companies = db["companies"]
companies = db["companies_full"]
state = db["state"]