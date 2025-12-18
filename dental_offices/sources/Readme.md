# Sources for Dental Offices in Berlin

This folder contains raw data and documentation for the project layer **Dental Offices in Berlin**.

---

## 1. OpenStreetMap (OSM)
- **Origin:** Public API
- **Endpoint:** https://overpass-api.de/api/interpreter
- **Data:** `amenity=dentist` nodes/ways/relations
- **Update frequency:** Dynamic (community updates)
- **Type:** API
- **Notes:** Provides dental office names, addresses, coordinates, opening hours, wheelchair accessibility, contact info.

---

## 2. Berlin Open Data Portal
- **Origin:** Public datasets
- **URL:** https://daten.berlin.de
- **Data:** Official business registry, including dental offices
- **Update frequency:** Monthly / as published
- **Type:** Static (CSV)
- **Notes:** Can enrich addresses, districts, and business categories.

---

## 3. Optional Enrichment Sources
- **Google Maps / Places API** (dynamic, requires API key, optional)
- **Yellow Pages / Gelbe Seiten** (scraper, optional)
- **Berlin Neighborhood Demographics** (population, median income by district, static)

---

## Transformation Plan
1. Normalize names and addresses (strip whitespace, standardize capitalization).  
2. Deduplicate entries across sources using fuzzy matching on `name + address`.  
3. Map OSM nodes/ways to point coordinates.  
4. Enrich each record with neighborhood and demographic information.  
5. Export cleaned data into the table `dental_offices_berlin`.  

---

## Files in this folder
- Raw CSVs (from Berlin Open Data or other sources)  
- `README.md` (this file)  
