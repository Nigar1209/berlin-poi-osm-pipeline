import os, json, time
from pathlib import Path
import requests
import pandas as pd

OVERPASS_URL = os.getenv("OVERPASS_URL", "https://overpass-api.de/api/interpreter")

# Overpass QL:
# 1) Find the Berlin administrative area
# 2) Return all nodes/ways/relations tagged shop=mall within that area
#    with tags and a geometry center for ways/relations.
query = r"""
[out:json][timeout:120];
area
  ["boundary"="administrative"]
  ["name"="Berlin"]
  ["admin_level"~"^4|6$"]->.a;
(
  node["shop"="mall"](area.a);
  way["shop"="mall"](area.a);
  relation["shop"="mall"](area.a);
);
out tags center;
"""

def main():
    Path("malls/sources").mkdir(parents=True, exist_ok=True)

    r = requests.post(OVERPASS_URL, data={"data": query})
    r.raise_for_status()
    data = r.json()

    # Save raw JSON
    stamp = time.strftime("%Y%m%d")
    raw_path = Path(f"malls/sources/osm_malls_berlin_raw_{stamp}.json")
    raw_path.write_text(json.dumps(data, ensure_ascii=False, indent=2))

    # Flatten to CSV of relevant fields
    rows = []
    for el in data.get("elements", []):
        tags = el.get("tags", {})
        rows.append({
            "osm_type": el.get("type"),
            "osm_id": el.get("id"),
            "name": tags.get("name"),
            "website": tags.get("website"),
            "opening_hours": tags.get("opening_hours"),
            "addr_street": tags.get("addr:street"),
            "addr_housenumber": tags.get("addr:housenumber"),
            "addr_postcode": tags.get("addr:postcode"),
            "addr_city": tags.get("addr:city"),
            "lat": el.get("lat") or el.get("center", {}).get("lat"),
            "lon": el.get("lon") or el.get("center", {}).get("lon"),
            "wheelchair": tags.get("wheelchair"),
            "operator": tags.get("operator"),
            "brand": tags.get("brand"),
            "start_date": tags.get("start_date"),
            "level": tags.get("level"),
            "source": "OSM Overpass"
        })
    df = pd.DataFrame(rows)
    df.to_csv(f"malls/sources/osm_malls_berlin_{stamp}.csv", index=False)
    print(f"Wrote {len(df)} malls → {raw_path} and CSV.")

if __name__ == "__main__":
    main()
