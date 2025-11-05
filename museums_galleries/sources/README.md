## Museums & Galleries in Berlin
### Step 1 - Research & Data Modelling

## A. Data Source Discovery
- **Main source:** OpenStreetMap (OSM) via the OSMnx Python library.
- **Reason:** Open, free, and continuously updated. Contains location, address, and other details for all banks in Berlin.
- **Data type:** Dynamic (queried via API using `"tourism": ["museum", "gallery", "artwork"]` & `"amenity" "exhibition-center"` filters).
- **Update frequency:** Continuous.
- **Extra sources:** Berlin Open Data Portal (optional enrichment), Deutsche Digitale Bibliothek REST API (need an API key) or kulturgutdigital - Berliner OpenGLAM-Daten.

## Created raw files
- Created a raw file for all 4 tags before finding common columns to join on
- Needed to figure out if 1 table is a good idea or if it is better to create a seperate one for artworks
  
---

## B. Selected Columns 
- Removed columns with percentage or more missing data - each table % different to keep certain columns)
---

## C. Planned Schema

---

## D. Transformation Plan

---
  
## E. Populate Database
