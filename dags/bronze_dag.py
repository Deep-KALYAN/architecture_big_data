import sys
from pathlib import Path
sys.path.append("/opt/airflow/project")

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

from ingestion.state import get_pending_targets, mark_in_progress, mark_done, mark_failed
from ingestion.nbb import get_all_kpis


def run_production_nbb():
    # Fetch a targeted execution batch of pending hotels
    targets = get_pending_targets(limit=100)
    print(f"Acquired {len(targets)} pending hotel targets for scraping.")

    for target in targets:
        bce = target["bce"]
        print(f"\nStarting targeted scrape for BCE: {bce}")
        
        # Transition tracking flag state to prevent concurrent scraping tasks
        mark_in_progress(bce)
        
        try:
            # Execute scraper and retrieve counts for valid years (2021-2025)
            kpi_results, filings_count = get_all_kpis(bce)
            
            # Save final status flag updates
            mark_done(bce, filings_count)
            print(f"✓ Successfully processed BCE {bce}. Filings uploaded: {filings_count}")
            
        except Exception as err:
            print(f"❌ Error encountered handling BCE {bce}: {err}")
            mark_failed(bce, str(err))
            
            # If we hit an explicit 429 rate limit, break the loop to save container resource identity
            if "429" in str(err):
                print("Terminating batch run early due to upstream API rate limit blocks.")
                break


with DAG(
    "silver_hotel_ingestion",
    start_date=datetime(2026, 1, 1),
    schedule_interval=None, # Trigger manually or set to routine schedule
    catchup=False,
    default_args={
        "retries": 1,
        "retry_delay": timedelta(minutes=2)
    }
) as dag:

    task_nbb_hotel = PythonOperator(
        task_id="fetch_nbb_hotel_sector",
        python_callable=run_production_nbb
    )


# import sys
# from pathlib import Path

# sys.path.append("/opt/airflow/project")

# from airflow import DAG
# from airflow.operators.python import PythonOperator
# from datetime import datetime

# from ingestion.mongo import companies

# from ingestion.nbb import get_all_kpis
# from ingestion.notaire import get_all_statutes, get_session


# # --- TASKS ---

# def run_nbb():
#     for c in companies.find().limit(50):   # ✅ LIMIT
#         bce = c["bce"]
#         print(f"NBB → {bce}")
#         print("DEBUG BCE:", c["bce"])
#         try:
#             get_all_kpis(bce)
#         except Exception as e:
#             print(f"Error NBB: {bce} → {e}")


# def run_notaire():
#     session = get_session()

#     for c in companies.find().limit(50):   # ✅ LIMIT
#         bce = c["bce"]
#         print(f"NOTAIRE → {bce}")

#         try:
#             get_all_statutes(bce, session=session)
#         except Exception as e:
#             print(f"Error NOTAIRE: {bce} → {e}")


# # --- DAG ---

# with DAG(
#     "bronze_ingestion",
#     start_date=datetime(2024, 1, 1),
#     schedule_interval="@daily",
#     catchup=False
# ) as dag:

#     task_nbb = PythonOperator(
#         task_id="fetch_nbb",
#         python_callable=run_nbb
#     )

#     task_notaire = PythonOperator(
#         task_id="fetch_notaire",
#         python_callable=run_notaire
#     )

#     task_nbb >> task_notaire