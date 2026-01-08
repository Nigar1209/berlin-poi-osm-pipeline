# Emergency Services Berlin — Data Sources

This document describes the data sources used to model Police, Fire, and Ambulance services in Berlin.  
The goal is to gather reliable, openly accessible, and regularly updated datasets that can be integrated into the WeBeet data platform.

---

## 1. OpenStreetMap (OSM)

**Description:**  
OpenStreetMap is a collaborative, open geospatial database. It provides detailed and frequently updated information contributed by a global community.

**Relevant Tags:**  
- `amenity = police`  
- `amenity = fire_station`  
- `emergency = ambulance_station`

**Data Type:**  
Dynamic (community-maintained)

**Update Frequency:**  
Multiple times per day (planet diffs)

**Key Fields:**  
- `name`  
- `address` (street, housenumber, postcode)  
- `latitude`, `longitude`  
- `opening_hours`  
- `contact_info`  
- `operator`  
- `geometry`

**Source Links:**  
- https://www.openstreetmap.org  
- Tag documentation: https://wiki.openstreetmap.org/wiki/Key:amenity

---

## 2. Berlin Open Data Portal

**Description:**  
Official datasets provided by the State of Berlin. These include verified and curated data from public authorities.

**Relevant Datasets:**  
- Fire Stations (Berliner Feuerwehr)  
- Police Stations (Polizei Berlin)  
- Rescue Services / Ambulance Infrastructure  
- Hospital & Emergency Departments (if available)

**Data Type:**  
Static (CSV, XLSX, GeoJSON)

**Update Frequency:**  
Irregular — typically annually or when new data is released

**Key Fields:**  
- `name`  
- `address`  
- `district`  
- `contact_info`  
- `service_type`  
- `coordinates`  
- `operator`

**Source Link:**  
- https://daten.berlin.de

---

## 3. Wikidata

**Description:**  
Wikidata is a structured collaborative database. It is particularly useful for enriching missing attributes (e.g., operators, coordinates, alternative names).

**Data Type:**  
Dynamic (queryable via SPARQL)

**Update Frequency:**  
Continuous — community-driven

**Key Fields:**  
- `label` (name)  
- `coordinates`  
- `instance_of` (police station, fire station, etc.)  
- `operator`  
- `inception`  
- `location` (district, neighborhood)

**Source Links:**  
- https://www.wikidata.org  
- Query Service: https://query.wikidata.org

---

# Planned Transformation Workflow

This section outlines how raw datasets will be processed into a unified schema suitable for the emergency services layer.

---

## 1. Data Collection

- Retrieve OSM entries via Overpass API  
- Download official datasets from Berlin Open Data Portal  
- Use Wikidata to fill missing fields or validate attributes  

---

## 2. Data Cleaning

- Normalize names (trim, lowercase, remove special characters)  
- Standardize address fields  
- Harmonize latitude/longitude formats  
- Remove duplicates across sources  
- Validate coordinate positions within Berlin boundaries  

---

## 3. Data Normalization

Mapping raw fields to the standardized schema:

| Standard Field | Description |
|---------------|------------|
| `id` | Unique identifier |
| `district_id` | Foreign key referencing Berlin districts |
| `name` | Cleaned location name |
| `latitude`, `longitude` | Geospatial coordinates |
| `geometry` | POINT format |
| `service_type` | Police / Fire / Ambulance |
| `contact_info` | Phone, email, website |
| `operating_hours` | Standardized opening times |
| `accessibility_features` | Wheelchair access, parking, etc. |
| `data_source` | OSM / Open Data / Wikidata |

---

## 4. Spatial Enrichment

- Reverse geocoding to identify districts and neighborhoods  
- Join with LOR / Ortsteil tables for consistent hierarchy  
- Validate spatial correctness (within Berlin boundaries)  

---

## 5. Quality Assurance

- Check for missing or inconsistent fields  
- Validate foreign key relationships  
- Remove duplicate POIs across sources  
- Ensure geometry is correctly formatted for the database layer  

---

## 6. Final Export & Database Insertion

- Export cleaned data to CSV / GeoJSON  
- Insert into `emergency_services_table`  
- Verify referential integrity (districts / neighborhoods)  
- Prepare for incremental updates if needed  

---

## Scope & Current Status (Step 2 – Data Transformation & Preprocessing)

This repository implements **Step 2: Data Transformation & Preprocessing**  
for the Emergency Services data layer as defined in the project issues.

### OSM-first Principle

- OpenStreetMap (OSM) is used as the **primary and authoritative data source**.
- Only attributes already present in OSM are cleaned and normalized.
- Missing values (e.g. `operator`, `contact_info`, `operating_hours`) are  
  **intentionally not backfilled from external sources** at this stage.

### Use of External Data Sources

- Berlin Open Data Portal and Wikidata are documented as **potential enrichment sources**.
- External datasets are **not automatically merged** into the unified dataset in Step 2.
- These sources may be used in later enrichment steps if OSM is missing  
  critical or verified information.

### Known Data Gaps & Design Decisions

- The `operator` field is partially missing, especially for:
  - volunteer fire stations
  - some ambulance locations
- Address-level attributes are inconsistently available across OSM entries.
- These gaps are preserved to maintain transparency and to comply with the  
  OSM-first integration strategy.

### Output of This Step

- A unified emergency services dataset (Police, Fire, Ambulance) with:
  - standardized schema
  - validated geometry (EPSG:4326)
  - spatial enrichment (district & neighborhood)
- The dataset is prepared for database ingestion and further enrichment.

---

## Summary

This document outlines:
- All identified data sources  
- Key relevant fields  
- How datasets are standardized  
- The complete transformation plan required for Step 2 (Data Transformation & Preprocessing)
