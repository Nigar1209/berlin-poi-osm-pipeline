# Data Sources

## Evaluated Sources

The following data sources were evaluated during the planning phase of the project:

### 1. OpenStreetMap (OSM)
- **Origin:** Public API
- **Endpoint:** https://overpass-api.de/api/interpreter
- **Data:** `amenity=dentist` nodes/ways/relations
- **Update frequency:** Dynamic (community updates)
- **Type:** API
- **Notes:** Provides dental office names, addresses, coordinates, opening hours, wheelchair accessibility, contact info.

### 2. Berlin Open Data Portal
- **Origin:** Public datasets
- **URL:** https://daten.berlin.de
- **Data:** Official business registry, including dental offices
- **Update frequency:** Monthly / as published
- **Type:** Static (CSV)
- **Notes:** Can enrich addresses, districts, and business categories.
  
### 3. KZV Berlin (Kassenzahnärztliche Vereinigung – official registry)
- **Origin:** Official registry of contracted dentists (Kassenzahnärztliche Vereinigung Berlin)  
- **URL:** [https://www.kzv-berlin.de/fuer-patienten/zahnarztsuche](https://www.kzv-berlin.de/fuer-patienten/zahnarztsuche)  
- **Data:** Directory of all licensed dentists and dental practices in Berlin, including names, practice addresses, specialties, and contact details  
- **Update frequency:** Dynamic / event-based (continuously maintained by KZV when practices are licensed, deregistered, or change address)  
- **Type:** Web directory (HTML search; no officially documented open CSV/API export)  
- **Notes:**
  - Considered the authoritative official registry for contracted dentists in Berlin, with very high data reliability.  
  - Technically accessible only via the web interface; using it as a dataset requires separate agreements or custom scraping and must be reviewed for licensing and data‑protection compliance.

---
After evaluation, **OpenStreetMap (OSM)** was selected as the primary and sole data
source used in the data pipeline.

OSM is the only source that provides **continuously updated, dynamic data** that can
be accessed programmatically with minimal technical overhead. Data can be retrieved
via standard APIs or extracts without requiring browser automation or additional
infrastructure such as Selenium or WebDriver.

Other sources, while valuable for validation and legal reference, were not used
directly in this project. The Berlin Open Data Portal mainly provides static or
infrequently updated datasets, while the KZV Berlin registry does not offer an
official API or bulk export and would require complex scraping approaches.

---

### OpenStreetMap (OSM)

| Field            | Description                                                                                                     |
|------------------|-----------------------------------------------------------------------------------------------------------------|
| source           | [OpenStreetMap (OSM) - API](https://overpass-api.de/api/interpreter), global crowdsourced geo DB                |
| update_frequency | Monthly / as published                                                                                          |
| data_type        | Dynamic (crowdsourced data accessed via API)                                                                    |
| relevant_fields | name, addr:street, addr:housenumber, addr:postcode, addr:city,<br>level, addr:floor, description, opening_hours,<br>check_date:opening_hours, check_date,<br>healthcare:speciality,<br>wheelchair, wheelchair:description, toilets:wheelchair,<br>phone, contact:website, contact:email, contact:phone, email, url, website,<br>geometry, health_facility:type,<br>health_specialty:oral_surgery, health_specialty:orthodontics, health_specialty:periodontology |


---

## Transformation Plan

1. Normalize names and addresses (trim whitespace, standardize casing).
2. Convert OSM nodes and ways into point geometries.
3. Normalize and consolidate accessibility, contact, and specialty attributes.
4. Enrich each record with administrative and spatial context (district, neighborhood).
5. Remove duplicate or overlapping entities using external reference datasets.
6. Export cleaned and validated data into the table `dental_offices_berlin`.

---

## External Reference Data

### Doctors Registry (`doctors_202601211553.csv`)

This file contains a curated list of medical practices and doctors that is used as a **reference dataset** during data processing.

**Purpose in the pipeline:**
- Identify overlapping entities between OpenStreetMap dental offices and existing doctor records.
- Prevent duplicate representation of the same real-world entity across datasets.

**Usage:**
- Records are matched via a shared `id` field.
- Any dental office record whose `id` already exists in the doctors dataset is removed from the final dental offices dataset.

This ensures:
- Clear separation between *doctor* and *dental office* entities
- No duplicate locations or practices in downstream analytics and databases

---

## Deduplication Logic (High-Level)

During data preparation:
1. Load the doctors reference dataset.
2. Compute the intersection of IDs between OSM dental offices and doctors.
3. Remove overlapping IDs from the dental offices dataset.
4. Continue processing only with unique dental office records.

This step is critical to maintain data integrity when combining multiple healthcare-related sources.

---

## Files in this Folder

- `raw_osm_dental_offices_v_01_19_2026.csv`  -> Raw OpenStreetMap dental office data in tabular format.
- `raw_osm_dental_offices_v_01_19_2026.geojson`  -> Raw OpenStreetMap dental office data including geospatial features.
- `doctors_202601211553.csv`  ->Reference dataset used to detect and remove overlapping medical entities.
- `README.md`  -> Documentation describing data sources, transformation logic, and licensing.

---

## Licensing Notes

- **OpenStreetMap data** is licensed under the **Open Database License (ODbL 1.0)**.  
  Any use, redistribution, or publication of derived datasets must include proper
  attribution to OpenStreetMap contributors and comply with the share-alike
  requirements of the license.

- **Doctors registry data** may be subject to separate licensing or usage restrictions  
  depending on its origin and must be handled accordingly.
