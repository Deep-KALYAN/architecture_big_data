import sys
from pathlib import Path

sys.path.append("/opt/airflow/project")

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

from ingestion.mongo import companies

from ingestion.nbb import get_all_kpis
# from ingestion.notaire import get_all_statutes, get_session


# --- TASKS ---

def run_nbb():
    for c in companies.find().limit(5):   # ✅ LIMIT
        bce = c["bce"]
        print(f"NBB → {bce}")
        print("DEBUG BCE:", c["bce"])
        try:
            get_all_kpis(bce)
        except Exception as e:
            print(f"Error NBB: {bce} → {e}")


# def run_notaire():
#     session = get_session()

#     for c in companies.find().limit(20):   # ✅ LIMIT
#         bce = c["bce"]
#         print(f"NOTAIRE → {bce}")

#         try:
#             get_all_statutes(bce, session=session)
#         except Exception as e:
#             print(f"Error NOTAIRE: {bce} → {e}")


# --- DAG ---

with DAG(
    "bronze_ingestion",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@daily",
    catchup=False
) as dag:

    task_nbb = PythonOperator(
        task_id="fetch_nbb",
        python_callable=run_nbb
    )

    # task_notaire = PythonOperator(
    #     task_id="fetch_notaire",
    #     python_callable=run_notaire
    # )

    # task_nbb >> task_notaire