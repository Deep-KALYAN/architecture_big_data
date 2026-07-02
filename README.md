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

  
I did docker compose up --build -d

now admin admin OR airflow airflow is not working what to do?

Open your PowerShell terminal and run these two commands back-to-back:

1. Delete the auto-generated admin user
PowerShell
docker exec -it airflow airflow users delete --username admin
2. Re-create the clean admin user
Copy and paste this single-line command into PowerShell to avoid line-break errors:

PowerShell
docker exec -it airflow airflow users create --username admin --password admin --role Admin --firstname Admin --lastname User --email admin@example.com



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

 docker exec -it mongo mongosh 

### Virtual environment
1. Create the environment
python -m venv .venv
2. Activate it
.\.venv\Scripts\Activate.ps1



pip install requests pandas pymongo playwright apache-airflow
playwright install

## Silver
Feed the data in silver from bronze
🧪 Re-Run Your Test!
run your execution command in Git Bash again:
Bash
<!-- (.venv) 
AzureAD+DeepKalyan@deep MINGW64 ~/IPSSI/23_Architecture_Big_Data/tp_architecture_big_data_/docker (SILVER) -->
docker exec -it airflow python //opt/airflow/project/transformation/silver_parser.py