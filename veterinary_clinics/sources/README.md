# Sources for Veterinary Clinics in Berlin

This folder stores raw data files and documentation for all data sources used in the vet clinics layer.  
The main goal is to build a reproducible, well-documented pipeline starting from open geospatial data.

## 1. OpenStreetMap – Vet clinics in Berlin

We use OpenStreetMap (OSM) as the primary open data source for veterinary clinics in Berlin.  
Vet clinics are mapped using the tag `amenity = veterinary`. Data is extracted via Overpass Turbo or equivalent OSM export tools.

### Local raw OSM snapshots

- `raw_osm_berlin_vet_clinics_20251209.geojson`  
  Main OSM GeoJSON snapshot for Berlin vet clinics (tag `amenity = veterinary`), downloaded on **2025-12-09** via Overpass Turbo.  
  This file is the **primary input** for the new vet clinics data model and cleaning pipeline.

- `raw_osm_berlin_vet_clinics_2025-09-25.csv`  
  Older OSM export of Berlin vet clinics (snapshot from **2025-09-25**).  
  Kept **only for comparison and QA** (e.g. checking how many clinics were added/removed or verifying that the cleaning pipeline behaves consistently over time).  
  This file is **not used** as the main source for the final dataset.

*(If additional raw snapshots are added in the future, they should be listed and described here in a similar way.)*

### Typical OSM fields

Depending on the export configuration, the OSM snapshots usually include:

- OSM element identifiers (`id`, `osm_type`, etc.)
- Geometry / coordinates (`lat`, `lon` or explicit geometry in GeoJSON)
- Name: `name`
- Address tags: `addr:street`, `addr:housenumber`, `addr:postcode`, `addr:city`
- Contact data: `phone`, `contact:phone`, `website`, `contact:website`, `email`, `contact:email`
- Opening hours: `opening_hours`
- Operator / brand: `operator`, `brand`
- Additional attributes when available: `veterinary:speciality`, `emergency`, accessibility tags, etc.

These raw fields are later normalized and mapped into the internal schema of the vet clinics layer.

---

## 2. Berlin LOR / neighborhood boundaries

- `raw_berlin_lor_ortsteile.geojson`  
  Berlin LOR (Lebensweltlich orientierte Räume) neighborhood and district boundaries.  
  This dataset is used to assign each vet clinic to:
  - a district (Bezirk)
  - a neighborhood (Ortsteil)

The file is treated as a **static** reference layer. Changes in the LOR boundaries are rare, but if an updated version is published by the city, a new file can be added and documented here.

---

## 3. Notes on usage and licensing

- OpenStreetMap data is licensed under the ODbL; proper attribution to *OpenStreetMap contributors* is required.
- The LOR / neighborhood boundaries inherit their licensing conditions from the Berlin open data portal or the original provider.
- Additional external sources (official emergency lists, private directories, etc.) may be used **only as reference** unless their terms explicitly allow reuse and redistribution.
