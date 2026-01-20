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
|------------------|-----------------------------------------------------------------------------|
| source           | [OpenStreetMap (OSM) - API](https://overpass-api.de/api/interpreter), global crowdsourced geo DB                |
| update_frequency | Monthly / as published                                                                                          |
| data_type        | Dynamic (crowdsourced data accessed via API)                                                                    |
| relevant_fields  | name,addr:street,addr:housenumber,addr:postcode,addr:city,level,opening_hours,check_date,healthcare:speciality,wheelchair,wheelchair:description,phone,email,website,geometry,health_facility:type,health_specialty:oral_surgery,health_specialty:orthodontics,health_specialty:periodontology |

## Transformation Plan
1. Normalize names and addresses (strip whitespace, standardize capitalization).  
2. Map OSM nodes/ways to point coordinates.  
3. Enrich each record with neighborhood and demographic information.  
4. Export cleaned data into the table `dental_offices_berlin`.  

---
## Licensing Notes

- **OpenStreetMap data** is licensed under the **Open Database License (ODbL 1.0)**.  
  Any use, redistribution, or publication of derived datasets must include proper
  attribution to OpenStreetMap contributors and comply with the share-alike
  requirements of the license.

---
## Files in this folder
- Raw CSV (from OpenStreetMap)
- Raw GEOJSON (from OpenStreetMap)
- `README.md` (this file)  
