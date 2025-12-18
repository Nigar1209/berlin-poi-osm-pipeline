

## A. Data Source Discovery
- **Main source:** OpenStreetMap (OSM) via the OSMnx Python library.
- **Reason:** Open, free, and continuously updated. Contains location, address, and other details for all banks in Berlin.
- **Data type:** Dynamic (queried via API using `amenity=bank` filter).
- **Update frequency:** Continuous.
- **Extra sources:** Berlin Open Data Portal (optional enrichment).

---

## B. Selected Columns (14 total)
1. bank_id 
2. name  
3. brand  
4. operator  
5. street  
6. housenumber  
7. postcode  
8. opening_hours  
9. atm  
10. wheelchair 
11. latitude  
12. longitude  
13. district 
14. district_id
 
---

## C. Planned Schema
- Table name: `banks`
- Data types chosen to match expected content (text, float).
- `latitude` and `longitude` extracted from geometry.
- `district` will be added later via geopy.geocoders /Nominatim.

---

## D. Transformation Plan
1. Fetch data from OSM (`amenity=bank`, Berlin).
2. Convert column names to snake_case.
3. Standardize column names and types
4. Drop irrelevant / redundant columns
5. Handle missing values
6. Normalize categories 
7. Opening hours normalization
8. Enrich with district and district_id information.
9. Save cleaned and transformed dataset (CSV).

---
  
## E. Populate Database
1. Create empty table 'banks'.
2. Send data frame to the database
3. Query data

---

## F. Files in `/sources` 
- **banks_raw.geojson** — raw data with geometry.
- **banks_raw.csv** — raw data without geometry.
- **final_banks_with_districts.csv** - data enriched with district information.

---

## G. Files in `/scripts` 
- **banks_data_transformation.jpynb** — jupyter notebook

---

## H. Files in `/banks` 
- **README.md** — this file.
