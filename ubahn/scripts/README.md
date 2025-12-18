## Step 2: Data Transformation — Postcode, Join, and Reverse Geocoding

**Branch:** `ubahn-data-transformation`  
**Focus:** Clean, enrich, and unify U-Bahn stations and connections using postcode and geographic context

---

###  2.1 Add Postcodes to Stations

**Script:** `add_postcode2.py`  
**Input:** `03-stations.csv`  
**Output:** `simoun-asmar-stations-with-postcode.csv`

This script uses the Nominatim API (OpenStreetMap) to reverse geocode each U-Bahn station’s coordinates (latitude and longitude) and extract the postcode.

- First, I loaded the original station data and cleaned column names.
- I queried the Nominatim reverse geocoding endpoint using latitude and longitude to fetch each station’s postcode.
- I appended the postcode results to each station.
- The API rate limit (`1 request/sec`) using `time.sleep(1)`.

**Run with:**
```bash
python add_postcode2.py
```

---

###  2.2 Join Station Coordinates with Line Data

**Script:** `joining_station_with_line_sql.ipynb`  
**Inputs:**
- `08-connections-no-dupes.csv`
- `simoun-asmar-stations-with-postcode.csv`  
**Output:** `merged_ubahn_line.csv`

In this step:
- I cleaned and normalized station names, removing common prefixes like "U-Bahnhof", "S-Bahnhof", etc.
- I removed any placeholder or irrelevant rows (e.g., those starting with "Q*").
- I transformed the postcode column to string format to ensure consistent formatting and avoid issues caused by floating-point values ending in .0.
- I joined the two cleaned datasets using SQLite to unify geographic coordinates and postcodes.
- After the join, I manually added latitude/longitude values for specific stations (12 stations) to avoid null values in the next steps.

---

###  2.3 Add Stadtteil via Reverse Geocoding

**Notebook:** `reverse_geo_coding_stadtteil.ipynb`  
**Input:** `merged_ubahn_line.csv`  
**Output:** `ubahn_with_stadtteil.csv`

- I performed reverse geocoding using the `geopy` library with the Nominatim API.
- For each station, I extracted either the `suburb` or `city_district` from the reverse geocode results.
- I appended this data to a new column called `stadtteil`, enriching each station with its local sub-neighborhood.

---

### 2.4 Add Neighborhood (Bezirk)

**Notebook:** `reverse_geo_coding_neighborhood.ipynb`  
**Input:** `ubahn_with_stadtteil.csv`  
**Output:** `ubahn_with_neighborhoods.csv`

- Again using `geopy` and the Nominatim API, I conducted reverse geocoding on each station’s coordinates.
- I specifically targeted Berlin’s official districts ("Bezirk") by extracting fields such as `city_district`, `borough`, or `county`.
- I appended these results to a column named `neighborhood`, providing clear district-level geographic context.
- The postcode column remained consistently formatted throughout.

---
---

### 🧹 2.5 Final Clean-Up: Remove Invalid Duplicates with Missing Lines

**Script:** `cleaned_ubahn.ipynb`  
**Input:** `ubahn_with_neighborhoods.csv`  
**Output:** `ubahn.csv`

In this last step, I refined the data by removing redundant station entries that had **no line information** (`line = null`) — but **only when** duplicates existed for the same station.

This was necessary because:
- Some stations appeared **multiple times**, each correctly associated with different U-Bahn lines (e.g. U2, U6).
- However, a few of these stations had **extra duplicate rows** with no line info, which added noise and redundancy.
- Meanwhile, stations that appeared **only once**, even if their `line` was missing, were **retained** — since they might still be valid standalone entries.
- I also ensured that only entries with valid line formats (like `U1`, `U6`) were kept. Any rows where the `line` field contained unrelated railway names (e.g. “Berliner Stadtbahn”) or was completely missing were dropped.

Finally, I manually inserted missing line values for three unique stations — Elsterwerdaer Platz (U5), Grenzallee (U7), and Weinmeisterstraße (U8) — based on verified information from the official BVG website, ensuring no remaining null entries in the `line` column.

This step ensures a final, clean dataset of Berlin U-Bahn stations with reliable geographic and line information 

---
This sequential process ensures accurate geographic enrichment of Berlin U-Bahn station data with postal codes, neighborhoods, and district-level details.
