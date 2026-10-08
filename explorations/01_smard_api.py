"""
Exploration: how does the SMARD chart_data API work?

Questions: which filter is the price, which resolutions exist,
how far back does the data go, how long is one data block?
"""

import requests
from datetime import datetime, timezone

# --- Settings ---
BASE = "https://www.smard.de/app/chart_data"
FILTER = 4169        # day-ahead price (confirmed)
REGION = "DE-LU"
RESOLUTION = "quarterhour"

# --- Part 1: which data blocks exist? ---
index_url = f"{BASE}/{FILTER}/{REGION}/index_{RESOLUTION}.json"
index = requests.get(index_url, timeout=10).json()

timestamps = index["timestamps"]
print("Number of blocks:", len(timestamps))
print("First timestamp:", timestamps[0])
print("Last timestamp:", timestamps[-1])

# --- Part 2: readable dates ---
def to_date(ms):
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc)

print("Data starts:", to_date(timestamps[0]))
print("Last block starts:", to_date(timestamps[-1]))

# --- Part 3: one data block ---
last_ts = timestamps[-1]
data_url = f"{BASE}/{FILTER}/{REGION}/{FILTER}_{REGION}_{RESOLUTION}_{last_ts}.json"
data = requests.get(data_url, timeout=10).json()

series = data["series"]          # list of [timestamp, value] pairs
print("Points in block:", len(series))
print("First 5 points:", series[:5])
print("Block starts:", to_date(series[0][0]))
print("Block ends:", to_date(series[-1][0]))