"""Bronze: download all SMARD weekly blocks and save them as raw JSON in the Volume."""

import json
import os
import time
import requests

FILTER_ID = 4169
REGION = "DE-LU"
RESOLUTION = "hour"
BASE_URL = "https://www.smard.de/app/chart_data"
OUTPUT_DIR = "/Volumes/energy_lakehouse/bronze/raw_files/smard"
REFRESH_LAST_N = 2   # always re-download the newest weeks (they may be incomplete)

# --- Part B: index ---
index_url = f"{BASE_URL}/{FILTER_ID}/{REGION}/index_{RESOLUTION}.json"
response = requests.get(index_url, timeout=30)
response.raise_for_status()
timestamps = response.json()["timestamps"]
print(len(timestamps), "weeks available")

os.makedirs(OUTPUT_DIR, exist_ok=True)
recent = timestamps[-REFRESH_LAST_N:]     # the newest 2 week numbers
downloaded = 0
skipped = 0

# --- Loop over all weeks ---
for ts in timestamps:
    file_name = f"{FILTER_ID}_{REGION}_{RESOLUTION}_{ts}.json"
    path = f"{OUTPUT_DIR}/{file_name}"

    # skip old weeks we already have
    if os.path.exists(path) and ts not in recent:
        skipped += 1
        continue

    # download one week
    block_url = f"{BASE_URL}/{FILTER_ID}/{REGION}/{file_name}"
    response = requests.get(block_url, timeout=30)
    response.raise_for_status()
    data = response.json()

    # save it unchanged
    with open(path, "w") as f:
        json.dump(data, f)
    downloaded += 1

    time.sleep(0.2)   # be polite to SMARD's server

print("Downloaded:", downloaded, "| Skipped:", skipped)