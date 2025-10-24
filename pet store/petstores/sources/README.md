#  touch petstores/sources/README.md

# 🐾 Pet Stores Data Layer – Sources
## Overview
This document lists initial data sources identified for building the Pet Stores data layer in Berlin.  
These sources will inform the data ingestion, modeling, and transformation steps.

---

## 1. OpenStreetMap (OSM) Overpass API
- **Origin**: https://wiki.openstreetmap.org/wiki/Overpass_API
- **Update Frequency**: Continuous (real-time updates)
- **Data Type**: Dynamic
- **Relevant Fields**: name, shop, address, coordinates, opening_hours, contact info
- **Example Query**: See `/petstores/sources/osm_query_example.txt`

---

## 2. Berlin Open Data Portal
- **Origin**: https://daten.berlin.de/
- **Update Frequency**: Monthly–Annual
- **Data Type**: Static
- **Relevant Fields**: business name, category, address, hours, website

---

## 3. Yelp Fusion API
- **Origin**: https://www.yelp.com/developers/documentation/v3
- **Update Frequency**: Dynamic (API)
- **Data Type**: Dynamic
- **Relevant Fields**: name, address, coordinates, rating, hours, website, phone

---

## 4. Google Places API (Optional Enrichment)
- **Origin**: https://developers.google.com/maps/documentation/places/web-service/overview
- **Update Frequency**: Real-time
- **Data Type**: Dynamic
- **Relevant Fields**: name, type, address, coordinates, opening_hours, rating, website

---

## Next Steps (Planned)
- Test OSM Overpass API queries for Berlin → extract sample dataset.
- Evaluate data overlap between OSM, Yelp, and Berlin Open Data.
- Design mapping model aligning `petstores` data to existing DB schema.
- Store preliminary raw data samples in `/petstores/sources/raw/`.

