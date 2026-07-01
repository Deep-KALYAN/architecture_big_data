# architecture_big_data
Scraping, Data Management, hdfs, Airflow, Medallion Architecture


### Docker
AzureAD+DeepKalyan@deep MINGW64 ~/IPSSI/23_Architecture_Big_Data/tp_architecture_big_data_ (INGESTION_BRONZE)
-- $ docker compose up -d

---------------------
check if user exist
(airflow)airflow users list

then delete
airflow users delete --username admin

then create
airflow users create \
  --username admin \
  --password admin \
  --firstname Admin \
  --lastname User \
  --role Admin \
  --email admin@example.com> > > > > >


### Airflow
http://localhost:8080
Username: admin
Password: admin

### Mongo db 
to fill the mongo db with csv local files
python -m ingestion.load_companies

test in VS code the string to use after clicking on connect 
mongodb://localhost:27017

<!-- Create index -->
col.create_index("bce")

### Virtual environment
1. Create the environment
python -m venv .venv
2. Activate it
.\.venv\Scripts\Activate.ps1



pip install requests pandas pymongo playwright apache-airflow
playwright install