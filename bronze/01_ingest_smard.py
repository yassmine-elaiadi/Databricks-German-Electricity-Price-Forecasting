"""Bronze: download all SMARD weekly blocks for several series and save them as raw JSON."""

import json
import os
import time
import requests

SERIES = {
    "price": 4169,
    "load": 410,
    "wind_onshore": 4067,
    "wind_offshore": 1225,
    "solar": 4068,
}
REGION = "DE-LU"
RESOLUTION = "hour"
BASE_URL = "https://www.smard.de/app/chart_data"
OUTPUT_DIR = "/Volumes/energy_lakehouse/bronze/raw_files/smard"
REFRESH_LAST_N = 2

os.makedirs(OUTPUT_DIR, exist_ok=True)

for name, filter_id in SERIES.items():
    # --- index for this series ---
    index_url = f"{BASE_URL}/{filter_id}/{REGION}/index_{RESOLUTION}.json"
    response = requests.get(index_url, timeout=30)
    response.raise_for_status()
    timestamps = response.json()["timestamps"]

    recent = timestamps[-REFRESH_LAST_N:]
    downloaded = 0
    skipped = 0

    # --- loop over all weeks of this series ---
    for ts in timestamps:
        file_name = f"{filter_id}_{REGION}_{RESOLUTION}_{ts}.json"
        path = f"{OUTPUT_DIR}/{file_name}"

        if os.path.exists(path) and ts not in recent:
            skipped += 1
            continue

        block_url = f"{BASE_URL}/{filter_id}/{REGION}/{file_name}"
        response = requests.get(block_url, timeout=30)
        response.raise_for_status()
        data = response.json()

        with open(path, "w") as f:
            json.dump(data, f)
        downloaded += 1

        time.sleep(0.2)

    print(f"{name} ({filter_id}): {len(timestamps)} weeks | downloaded {downloaded} | skipped {skipped}")