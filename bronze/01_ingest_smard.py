"""Bronze: download one SMARD weekly block and save it as raw JSON in the Volume."""


import json
import os
import requests

FILTER_ID = 4169
REGION = "DE-LU"
RESOLUTION = "hour"
BASE_URL = "https://www.smard.de/app/chart_data"
OUTPUT_DIR = "/Volumes/energy_lakehouse/bronze/raw_files/smard"

# --- Part B: index ---
index_url = f"{BASE_URL}/{FILTER_ID}/{REGION}/index_{RESOLUTION}.json"

response = requests.get(index_url, timeout=30)
response.raise_for_status()

timestamps = response.json()["timestamps"]
ts = timestamps[-1]
print(len(timestamps), timestamps[0], ts)

# --- Part C: one block ---
block_url = f"{BASE_URL}/{FILTER_ID}/{REGION}/{FILTER_ID}_{REGION}_{RESOLUTION}_{ts}.json"

response = requests.get(block_url, timeout=30)
response.raise_for_status()

data = response.json()

# --- Part D: save ---
os.makedirs(OUTPUT_DIR, exist_ok=True)
file_name = f"{FILTER_ID}_{REGION}_{RESOLUTION}_{ts}.json"
path = f"{OUTPUT_DIR}/{file_name}"

with open(path, "w") as f:
    json.dump(data, f)

# --- Part E: check ---
series = data["series"]
missing = [p for p in series if p[1] is None]
print("Saved:", path)
print(len(series), "points,", len(missing), "missing")
