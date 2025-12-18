# get_osm_gyms.py
# Script to fetch gyms/fitness studios in Berlin from the OpenStreetMap Overpass API
# and save the results as a CSV file for further use.
#
# Requirements: requests, pandas
# Usage:
#   python get_osm_gyms.py
#
# Output:
#   A CSV file (named with today's date) in ../sources/

import requests
import json
import os
import pandas as pd
import datetime

# --- Step 1: Define the Overpass API query ---
# This query will find all objects tagged as "fitness_centre" or with "sport=yoga" in the administrative area "Berlin".
overpass_query = """
[out:json][timeout:60];
area["name"="Berlin"]["boundary"="administrative"]->.searchArea;
(
  node["leisure"="fitness_centre"](area.searchArea);
  way["leisure"="fitness_centre"](area.searchArea);
  relation["leisure"="fitness_centre"](area.searchArea);
  node["sport"="yoga"](area.searchArea);
  way["sport"="yoga"](area.searchArea);
  relation["sport"="yoga"](area.searchArea);
);
out center tags;
"""


# --- Step 2: Request data from Overpass API ---
url = "https://overpass-api.de/api/interpreter"
print("Requesting data from Overpass API...")
response = requests.post(url, data=overpass_query)
response.raise_for_status()

# --- Parse response as JSON (GeoJSON) ---
data = response.json()

# --- Step 3: Extract relevant fields for each gym ---
gyms = []
for el in data['elements']:
    tags = el.get('tags', {})
    gym = {
        "name": tags.get("name", ""),
        "leisure": tags.get("leisure", ""),
        "sport": tags.get("sport", ""),
        "street": tags.get("addr:street", ""),
        "housenumber": tags.get("addr:housenumber", ""),
        "postcode": tags.get("addr:postcode", ""),
        "city": tags.get("addr:city", ""),
        "opening_hours": tags.get("opening_hours", ""),
        "phone": tags.get("phone", ""),
        "email": tags.get("email", ""),
        "website": tags.get("website", ""),
        "wheelchair": tags.get("wheelchair", ""),
        # Some elements are 'nodes', some are 'ways' or 'relations'. Ways/relations use 'center' for coordinates.
        "latitude": el.get("lat") or el.get("center", {}).get("lat"),
        "longitude": el.get("lon") or el.get("center", {}).get("lon"),
        "osm_id": el.get("id"),
        "osm_type": el.get("type"),
        "source": "OSM Overpass"
    }
    gyms.append(gym)

# --- Step 4: Save the data as CSV ---
df = pd.DataFrame(gyms)

today = datetime.date.today().isoformat()

csv_file = f"gyms/sources/gyms_osm_berlin_{today}.csv"
df.to_csv(csv_file, index=False)
print(f"Exported {len(df)} gyms to {csv_file}")
