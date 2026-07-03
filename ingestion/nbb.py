import time
import requests
import pandas as pd
from io import StringIO
from pathlib import Path
from typing import List, Dict

from requests.adapters import HTTPAdapter
from urllib3 import Retry
from ingestion.state import mark_done
from ingestion.hdfs_client import upload_to_hdfs
from hdfs import InsecureClient

session = requests.Session()
client = InsecureClient("http://namenode:9870", user="root", session=session)

TMP = Path("data/bronze/nbb")
# TMP = Path("tmp/pdfs")
TMP.mkdir(parents=True, exist_ok=True)

BASE = "https://consult.cbso.nbb.be/api"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
}


def make_session(enterprise_number: str) -> requests.Session:
    session = requests.Session()
    # Define a robust retry policy for stubborn endpoints
    retries = Retry(
        total=3,                # Retry 3 times before raising an error
        backoff_factor=2,       # Wait 2s, then 4s, then 8s between retries
        status_forcelist=[429, 500, 502, 503, 504], # Catch both 429s and hidden 500 blocks
        raise_on_status=True    # Still raise an exception if all retries fail
    )
    
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    session.headers.update(HEADERS)
    page_url = f"https://consult.cbso.nbb.be/consult-enterprise/{enterprise_number}"
    session.headers.update({"Referer": page_url})
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json, text/plain, */*"
    })
    session.get(page_url)  # establishes ASLBSA, ASLBSACORS, JSESSIONID cookies
    return session


def get_deposits(session: requests.Session, enterprise_number: str) -> list:
    url = (
        f"{BASE}/rs-consult/published-deposits"
        f"?page=0&size=10&enterpriseNumber={enterprise_number}"
        f"&sort=periodEndDate,desc&sort=depositDate,desc"
    )
    r = session.get(url)
    r.raise_for_status()
    data = r.json()
    print(f"Found {data['totalElements']} filings ({data['totalPages']} pages). Loading first {len(data['content'])}.")
    return data["content"]


def download_csv(session: requests.Session, deposit_id: str) -> str:
    url = f"{BASE}/external/broker/public/deposits/consult/csv/{deposit_id}"
    r = session.get(url)
    r.raise_for_status()
    return r.text


def download_pdf(session: requests.Session, deposit: dict) -> Path:
    """Download PDF for a deposit and save to tmp/pdfs/. Returns the saved path."""
    deposit_id  = deposit["id"]
    year        = deposit["periodEndDateYear"]
    enterprise  = deposit["enterpriseNumber"]
    reference   = deposit["reference"]
    filename    = f"{enterprise}_{year}_{reference}.pdf"
    dest_dir        = TMP / enterprise / str(year)
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / filename


    if dest.exists():
        print(f"    PDF already exists: {filename}")
        return dest

    url = f"{BASE}/external/broker/public/deposits/pdf/{deposit_id}"
    r = session.get(url)
    r.raise_for_status()
    dest.write_bytes(r.content)
    print(f"    PDF saved: {filename} ({len(r.content) // 1024} KB)")
    return dest


def parse_csv(csv_text: str) -> dict:
    df = pd.read_csv(StringIO(csv_text), header=None, skiprows=1)
    codes = {}
    for _, row in df.iterrows():
        key = str(row[0]).strip()
        try:
            codes[key] = float(row[1])
        except (ValueError, TypeError):
            codes[key] = row[1]
    return codes


def compute_kpis(codes: dict) -> dict:
    def get(code):
        return codes.get(code, 0.0)

    omzet        = get("70")
    cogs         = get("60")
    depreciation = get("630")
    ebit         = get("9901")
    net_profit   = get("9904")
    cash         = get("54/58")
    equity       = get("10/15")
    total_assets = get("20/58")
    fin_debt     = get("17") + get("43")
    gross_profit = omzet - cogs
    ebitda       = ebit + depreciation

    def pct(num, denom):
        return round(num / denom * 100, 2) if denom else None

    return {
        "entity":           codes.get("Entity name"),
        "period_end":       codes.get("Accounting period end date"),
        "chiffre_affaires": omzet,
        "marge_brute":      gross_profit,
        "ebitda":           ebitda,
        "ebit":             ebit,
        "resultat_net":     net_profit,
        "taux_marge_brute": pct(gross_profit, omzet),
        "taux_ebitda":      pct(ebitda, omzet),
        "marge_nette":      pct(net_profit, omzet),
        "tresorerie":       cash,
        "dettes_fin":       fin_debt,
        "dette_nette":      fin_debt - cash,
        "fonds_propres":    equity,
        "total_actif":      total_assets,
        "autonomie_fin":    pct(equity, total_assets),
    }


def get_all_kpis(enterprise_number: str) -> List[Dict]:
    session = make_session(enterprise_number)
    
    try:
        deposits = get_deposits(session, enterprise_number)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            print("⚠️ NBB Rate Limit Hit (429)! Backing off execution...")
            time.sleep(5) # Give the external API breathing room
        raise e

    results = []
    successful_filings_count = 0

    for deposit in deposits:
        deposit_id = deposit["id"]
        year = int(deposit.get("periodEndDateYear", 0))
        bce = deposit["enterpriseNumber"]
        
        # --- REQUIREMENT: Filter >= 2021 ---
        # The document requires filtering filings dynamically based on accounting period 
        if year < 2021 or year > 2025:
            print(f"  Skipping year {year} (Out of 2021-2025 scope)")
            continue

        print(f"  Processing {year} (id={deposit_id})...")

        # Attempt PDF download and push straight to HDFS
        try:
            pdf_path = download_pdf(session, deposit)
            hdfs_path = f"/bronze/nbb/{bce}/{year}/{pdf_path.name}"
            print(f"    Uploading PDF to HDFS: {hdfs_path}")
            upload_to_hdfs(str(pdf_path), hdfs_path)
            successful_filings_count += 1
        except Exception as e:
            print(f"    ✗ PDF pipeline failed for {year}: {e}")
            raise e
        # Add a short delay right after downloading a PDF to breathe
        time.sleep(1.5)

        # CSV is only available for newer native formats
        if deposit.get("migration"):
            print(f"    Skipping CSV for {year} (migrated legacy filing)")
            continue

        try:
            csv_text = download_csv(session, deposit_id)
            codes = parse_csv(csv_text)
            kpis = compute_kpis(codes)
            kpis["year"] = year
            kpis["reference"] = deposit["reference"]
            results.append(kpis)
        except Exception as e:
            # Check if this specific CSV failed due to a 429 rate limit
            if "429" in str(e):
                print("    ⚠️ Hit 429 on CSV endpoint. Raising to trigger DAG backoff.")
                raise e
        time.sleep(2.0) # Gentle rate-limiting protection

    return results, successful_filings_count

# def get_all_kpis(enterprise_number: str) -> List[Dict]:
#     session = make_session(enterprise_number)
#     deposits = get_deposits(session, enterprise_number)

#     results = []
#     for deposit in deposits:
#         deposit_id = deposit["id"]
#         year = deposit["periodEndDateYear"]
#         bce = deposit["enterpriseNumber"]

#         if already_done(bce, "nbb", deposit_id):
#             print(f"  Skipping {year} (id={deposit_id})...")
#             continue

#         print(f"  Processing {year} (id={deposit_id})...")

#         # Always attempt PDF download (works for all years including migrated)
#         try:
#             pdf_path = download_pdf(session, deposit)
#             # ===  ADD HDFS UPLOAD HERE ===
#             hdfs_path = f"/bronze/nbb/{bce}/{year}/{pdf_path.name}"
#             print(f"    Uploading PDF to HDFS: {hdfs_path}")
#             upload_to_hdfs(str(pdf_path), hdfs_path)

#             print("DEBUG: calling mark_done")
#             mark_done(bce, "nbb", deposit_id, year, hdfs_path)
#         except Exception as e:
#             print(f"    ✗ PDF failed for {year}: {e}")
#         time.sleep(2)

#         # CSV only available for non-migrated filings
#         if deposit.get("migration"):
#             print(f"    Skipping CSV for {year} (legacy/migrated filing)")
#             continue

#         try:
#             csv_text = download_csv(session, deposit_id)
#             codes = parse_csv(csv_text)
#             kpis = compute_kpis(codes)
#             kpis["year"] = year
#             kpis["reference"] = deposit["reference"]
#             results.append(kpis)
#         except Exception as e:
#             print(f"    ✗ CSV failed for {year}: {e}")
#         time.sleep(2)

#     return results


# # --- Run ---
# enterprise_number = "0203430576"  # Apple Retail Belgium
# kpis = get_all_kpis(enterprise_number)

# df = pd.DataFrame(kpis).set_index("year").sort_index(ascending=False)
# pd.set_option("display.float_format", "{:,.2f}".format)
# pd.set_option("display.max_columns", None)
# pd.set_option("display.width", 200)

# print("\n=== KPI Summary ===")
# print(df[["entity", "period_end", "chiffre_affaires", "ebitda", "resultat_net", "marge_nette", "autonomie_fin"]])