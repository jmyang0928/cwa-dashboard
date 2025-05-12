"""
Weather Forecast Web App – Data Fetching and Database Script
Usage:
    python hw4.py fetch          # Fetch data and write to data.db
    python hw4.py regions        # List stored regions
    python hw4.py dump 北部地區   # Print all records for a specific region
"""
import os
import sys
import sqlite3
import requests
from dotenv import load_dotenv

# Load .env file
load_dotenv()

DB_FILE = "data.db"
# Read CWA_TOKEN from environment variables, default to None if not set
CWA_TOKEN = os.getenv("CWA_TOKEN")
if not CWA_TOKEN:
    raise SystemExit("[Error] CWA_TOKEN is not set. Please check if the .env file exists and is configured correctly.")

API_URL = "https://opendata.cwa.gov.tw/fileapi/v1/opendataapi/F-A0010-001"  

def fetch_json():
    """Fetch JSON data from the API."""
    resp = requests.get(
        API_URL,
        params={"Authorization": CWA_TOKEN, "format": "JSON"},
        timeout=10
    )
    print("⤷ Request URL:", resp.url)
    if resp.status_code != 200:
        raise SystemExit(f"[Error] Failed to fetch data: HTTP {resp.status_code}")
    return resp.json()

def parse_records(j):
    """Parse JSON data and return a list of records [{regionName, dataDate, mint, maxt}, ...]."""
    out = []
    try:
        locations = j["cwaopendata"]["resources"]["resource"]["data"]["agrWeatherForecasts"]["weatherForecasts"]["location"]
    except KeyError:
        raise SystemExit("[Error] Unable to parse JSON structure. Please verify the API response format.")

    for loc in locations:
        region = loc["locationName"]
        elements = loc["weatherElements"]
        maxt_list = elements.get("MaxT", {}).get("daily", [])
        mint_list = elements.get("MinT", {}).get("daily", [])

        for maxt, mint in zip(maxt_list, mint_list):
            out.append({
                "regionName": region,
                "dataDate": maxt["dataDate"],
                "maxt": float(maxt["temperature"]),
                "mint": float(mint["temperature"])
            })
    return out

def init_db(conn):
    """Initialize the database and create the TemperatureForecasts table if it does not exist."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS TemperatureForecasts(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            regionName TEXT NOT NULL,
            dataDate   TEXT NOT NULL,
            mint REAL, maxt REAL,
            UNIQUE(regionName, dataDate)
        )
    """)
    conn.commit()

def upsert(conn, rows):
    """Insert or update records in the TemperatureForecasts table."""
    conn.executemany("""
        INSERT OR REPLACE INTO TemperatureForecasts(regionName,dataDate,mint,maxt)
        VALUES(:regionName,:dataDate,:mint,:maxt)
    """, rows)
    conn.commit()

def main():
    """Main function to handle different commands."""
    conn = sqlite3.connect(DB_FILE)
    init_db(conn)

    if len(sys.argv)==1 or sys.argv[1]=="fetch":
        # Fetch data from the API and update the database
        print("Fetching CWA data …")
        rows = parse_records(fetch_json())
        upsert(conn, rows)
        print(f"✔ {len(rows)} records have been written/updated.")
    elif sys.argv[1]=="regions":
        # List all distinct regions in the database
        for r, in conn.execute("SELECT DISTINCT regionName FROM TemperatureForecasts"):
            print(r)
    elif sys.argv[1]=="dump":
        # Print all records for a specific region
        if len(sys.argv)<3:
            print("Usage: python hw4.py dump <region_name>")
            sys.exit(1)
        for row in conn.execute("""
                SELECT dataDate,mint,maxt FROM TemperatureForecasts
                WHERE regionName=? ORDER BY datetime(dataDate)
            """, (sys.argv[2],)):
            print(row)
    else:
        # Print usage instructions
        print(main.__doc__)

if __name__ == "__main__":
    main()
