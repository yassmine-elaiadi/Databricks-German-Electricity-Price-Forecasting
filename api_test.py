import requests  # library for sending HTTP requests (talking to websites/APIs)

# --- Test 1: Open-Meteo ---
url = "https://api.open-meteo.com/v1/forecast"   # the API endpoint
params = {                                        # what we ask for
    "latitude": 50.58,                            # Gießen
    "longitude": 8.68,
    "hourly": "temperature_2m",                   # hourly temperature, 2 m above ground
}

# Send the request. timeout=10: give up after 10 seconds instead of waiting forever
response = requests.get(url, params=params, timeout=10)

print("Open-Meteo status:", response.status_code)  # 200 = success
print(response.text[:300])                         # first 300 characters of the reply


# --- Test 2: SMARD ---
response = requests.get("https://www.smard.de", timeout=10)
print("SMARD status:", response.status_code)