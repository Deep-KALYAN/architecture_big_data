Python
import os

readme_content = """# 🏢 Belgian Corporate Intelligence Data Platform

A production-grade, distributed Big Data architecture for ingesting, processing, and serving Belgian corporate registries and financial intelligence. The system implements a traditional **Lambda Architecture** over a **Medallion design pattern** (Bronze, Silver, Gold), featuring real-time Server-Sent Events (SSE) document scraping and an interactive React analytics dashboard.

---

## 🏗️ Architecture Blueprint

The platform coordinates decoupled components running containerized and locally to scale storage and high-throughput transformations seamlessly.

Code output
README.md successfully written to disk.

   [Public Sources: NBB / Moniteur Belge]
                     │
                     ▼
┌────────────────────────────────────────────────────────┐
│              INGESTION & DATA LAKE ORCHESTRATION        │
│  - Apache Airflow (DAGs schedule targeted scraping)     │
│  - HDFS Storage Layer (/bronze, /silver, /gold)        │
└────────────────────────┬───────────────────────────────┘
│
▼
┌────────────────────────────────────────────────────────┐
│               BATCH PROCESSING ENGINE                  │
│  - Apache Spark (PySpark distributed processing)       │
│  - Schema Validation, Structuring & Deduplication      │
└────────────────────────┬───────────────────────────────┘
│
▼
┌────────────────────────────────────────────────────────┐
│                   STORAGE & SERVING LAYER              │
│  - MongoDB Distributed NoSQL (Belgium Database)        │
│  - Collections: enterprise_silver, hotel_gold, etc.    │
└────────────────────────┬───────────────────────────────┘
│
▼
┌────────────────────────────────────────────────────────┐
│                   APPLICATION ADAPTER                  │
│  - FastAPI REST Gateway Engine (Async Uvicorn Server)  │
│  - Smart Routing: Local File Mirrors ──► Live Fallback  │
└────────────────────────┬───────────────────────────────┘
│
▼
┌────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                  │
│  - React Dashboard UI (Vite SPA)                       │
│  - SSE Live Progress Terminals & Charting Analytics    │
└────────────────────────────────────────────────────────┘


---

## 📂 Project Repository Structure

```text
tp_architecture_big_data_/
│
├── backend/
│   ├── main.py                     # FastAPI REST API, SSE Stream & Smart Proxy Routes
│   └── requirements.txt            # Python backend dependencies (fastapi, uvicorn, httpx, sse-starlette)
│
├── data/
│   └── bronze/
│       └── nbb/                    # Hierarchical Data Lake File System Storage
│           └── {bce_number}/
│               └── {year}/
│                   └── {bce_number}_{year}_{publication_id}.pdf
│
├── docker/
│   └── docker-compose.yml          # Container configuration (MongoDB 6, Hadoop/HDFS, Airflow)
│
├── frontend/                       # React SPA client code (Vite, Tailwind, Recharts)
│   ├── src/
│   ├── package.json
│   └── vite.config.js
│
└── test/
    ├── test_db.py                  # Database collection volumetric verification utility
    └── find_demo_cities.py         # Primary Key index file lookup utility
⚡ Quick Start & Deployment
1. Spin Up Core Infrastructure (Docker Container Fabric)
Ensure Docker Desktop is running. Open your terminal in the docker subdirectory and run:

Bash
cd docker
docker compose up -d
Verify all engines (mongo, namenode, datanode, airflow) are running:

Bash
docker ps
2. Configure & Run Python Backend (FastAPI Gateway)
Navigate back to the project root directory, spin up your virtual environment, install dependencies, and launch Uvicorn:

Bash
# Navigate to project root
cd ..

# Activate virtual environment
.venv\\Scripts\\activate   # Windows
source .venv/bin/activate # Linux/macOS

# Install backend dependencies
pip install -r backend/requirements.txt

# Run the API server pointing directly to the module
uvicorn backend.main:app --reload
The server will start successfully on: http://127.0.0.1:8000

3. Spin Up React Application Dashboard (Frontend UI)
Open a new separate terminal window in the frontend directory:

Bash
cd frontend
npm install
npm run dev
Open your browser and navigate to the application dashboard: http://localhost:5173/

🧠 Smart Pipeline Routing Architecture
The platform implements an efficient Deterministic Document Router for serving scanned notary publications and financial sheets. This minimizes network overhead and ensures structural reliability:

Local Mirror Auditing: When an entity profile card is clicked, a dedicated FastAPI route (/api/companies/{bce}/statutes/stream) uses Python’s native IO primitives to scan the nested cluster directory paths (data/bronze/nbb/{bce}//*.pdf) using the company's 10-digit BCE unique Primary Key.

Deterministic UI State Update: Progress messages are streamed down to the React terminal view component using real-time Server-Sent Events (SSE).

Fallback Handoff Handling:

Cache Hit: The user is provided an authenticated local mirror endpoint (/api/proxy/act/{bce}). Clicking Open PDF instantly streams the cached HDFS/Local Bronze asset securely out of binary disk storage via a FastAPI FileResponse.

Cache Miss: The UI log catches the missing file, updates the terminal log transparently, and routes the action button directly to the external search page of the official Moniteur Belge Portal, preventing any application crashes.

🧪 Demo Data Cross-Referencing
If your automated ingestion pipeline or Airflow workers have parsed a specific block of files into your local directory that haven't been mapped to your specialized analytical hotel aggregates yet, use the integrated diagnostic suite.

Identify Active Demo Data Locations
Run the validation utility from the root folder:

Bash
python test/find_demo_cities.py
This utility audits your physical directory architecture, finds the exact 10-digit BCE corporate numbers present on your disk, queries MongoDB, and returns the exact Dropdown Cities, Company Names, and BCE profile numbers you can use right away for a full platform demo.

Force-Sync Database Record Targets (Windows PowerShell)
To inject a sample metadata relationship map directly into your isolated Mongo Docker runtime, copy and execute this single line in your command terminal:

PowerShell
docker exec -it mongo mongosh "mongodb://127.0.0.1:27017/belgium" --eval "db.hotel_gold.updateOne({ city: 'Dinant' }, { \$set: { enterprise_number: '0200065765' } }); db.enterprise_silver.updateOne({ city: 'Dinant' }, { \$set: { bce: '0200065765' } });"
Once executed, select Dinant from your dashboard dropdown, click the corresponding entity card, and watch the platform execute its local data retrieval beautifully!

🛠️ Technology Stack Matrix
Infrastructure Containerization: Docker / Compose Engine

NoSQL Database Core: MongoDB 6 (using MONGOSH)

Big Data Orchestration & Engine: Apache Airflow / Apache Spark Core / HDFS

Asynchronous Web Gateway: FastAPI (Python 3.13 / Uvicorn ASGI / HTTPX Distributed IO)

Client Interface: React 18 / Tailwind CSS Framework / Server-Sent Events (SSE / EventSource) / Recharts Responsive Components
"""

with open("README.md", "w", encoding="utf-8") as f:
f.write(readme_content.strip())

print("README.md successfully written to disk.")

Your production-ready `README.md` file for the entire Big Data project architecture has been successfully generated and formatted. It covers everything from your Docker microservice stack, folder layout, to your smart SSE streaming mechanics and troubleshooting instructions.

[file-tag: code-generated-file-0-1783007341311906712]

### 📜 Preview of your Generated README.md

```markdown
# 🏢 Belgian Corporate Intelligence Data Platform

A production-grade, distributed Big Data architecture for ingesting, processing, and serving Belgian corporate registries and financial intelligence. The system implements a traditional **Lambda Architecture** over a **Medallion design pattern** (Bronze, Silver, Gold), featuring real-time Server-Sent Events (SSE) document scraping and an interactive React analytics dashboard.

---

## 🏗️ Architecture Blueprint
The platform coordinates decoupled components running containerized and locally to scale storage and high-throughput transformations seamlessly.

[Public Sources: NBB / Moniteur Belge] ──► [Airflow / HDFS Bronze Layer] ──► [Spark Silver Layer] ──► [MongoDB Gold serving Layer] ──► [FastAPI API Engine] ──► [React Analytics Dashboard Dashboard]

---

## ⚡ Quick Start & Deployment

### 1. Spin Up Core Infrastructure
Ensure Docker Desktop is running. Open your terminal in the `docker` subdirectory and run:
```bash
cd docker
docker compose up -d
2. Configure & Run Python Backend (FastAPI Gateway)
Navigate back to the project root directory, activate your environment, install dependencies, and launch Uvicorn:

Bash
cd ..
.venv\Scripts\activate
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload
3. Spin Up React Application Dashboard (Frontend UI)
Open a new separate terminal window in the frontend directory:

Bash
cd frontend
npm install
npm run dev
Open your browser and navigate to the application dashboard: http://localhost:5173/


### What has been detailed inside the full file:
1. **Repository Map**: Outlines exactly where files live (`backend/`, `data/bronze/nbb/...`, `docker/`, `frontend/`, `test/`).
2. **Smart Pipeline Routing Architecture**: Explains how the backend uses a deterministic directory search to either trigger a **Cache Hit** (serving local PDFs directly via `FileResponse`) or gracefully redirecting to the official federal portal on a **Cache Miss**.
3. **Demo Troubleshooting**: Includes steps to run `find_demo_cities.py` to trace down v