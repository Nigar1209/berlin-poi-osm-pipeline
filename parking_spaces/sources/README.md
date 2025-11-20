# Parking Spaces Berlin Step 1 - Data Modelling

This document lists potential data sources for integrating parking related data into the Berlin data pool. For each data source the origin, update frequency, data type (static or dynamic), relevant fields and tags, links, notes, and the extracted raw geojson files are listed. 

See notebook `parking_spaces/scripts/parking_spaces_data_modelling.ipynb` for data extraction method of the raw data files in `parking_spaces/sources`

**Raw Data Files:**

Two geoJSON files are too big for GitHub's 100 MB file size limit and were therefore **not commited** to this repository. All other source files are included locally and can be regenerated using the WFS or OSM scripts in the notebook.

- `osm_parking_offstreet.geojson` (259.50 MB) ❌ too large for GitHub
- `osm_parking_spaces.geojson` (7.09 MB)
- `osm_parking_entrances.geojson` (4.06 MB)
- `bod_park_and_ride.geojson` (0.30)
- `bod_parking_street.geojson` (361.14 MB) ❌ too large for GitHub
- `bod_parking_zones.geojson` (0.30 MB)

## Data Sources

### OpenStreetMap (OSM)

**Source and origin:** OpenStreetMap – public geodata for Berlin, queryable via Overpass / OSM API.  

**Update frequency:** Continuous 

**Data type:** Dynamic (can be re-fetched on a schedule).  

**Relevant tags:**

- `amenity=parking` – off-street parking lots  
- `amenity=parking_space` – individual on-street spots  
- `amenity=parking_entrance` – entrances to underground / multi-storey garages  

**Relevant fields:**

- `name`
- `capacity`
- `capacity:disabled`
- `fee`
- `operator`
- `access`
- geometry (lat, lon / polygon)

**Notes:** Good spatial coverage, but attributes like `capacity` or `fee` are not always present. Should be treated as base layer.

**📄 Extracted raw data files:**

- osm_parking_entrances_2025-11-04.geojson
- osm_parking_offstreet_2025-11.04.geojson
- osm_parking_spaces_2025-11-04.geojson

### Berlin Open Data – Parken im Straßenraum (WFS)

**Source and origin:** Berlin Open Data Portal – parking in the street space. Describes all street parking spaces in the state of Berlin. ([WFS](https://gdi.berlin.de/services/wfs/parkplaetze))

**Update frequency:** Marked as last updated **26.06.2025** on the portal.

**Data type:** static (WFS, GeoJSON) 

**Relevant fields (from portal description):**

- `errechnete_anzahl_parkplaetze`
- `beschraenkungen_variieren_ueber_wochentage`
- `polygon_id`
- `ausrichtung`
- `parkort`
- `parkgebuehr`
- `strassenname`
- `carsharing`
- `nur_schwerbehinderte`
- `bewirtschaftungszeit`
- `zone`
- `oeffentliches_strassenland`
- `bezirk`
- `planungsraum`
- `bezirksregion`
- `coordinates`

**Notes:** Service split into inner/outer ring → both needed for full Berlin coverage.

**Link:** Berlin Open Data - [Parken im Strassenraum](https://daten.berlin.de/datensaetze/parken-im-strassenraum-wfs-2eb40df3)

**📄 Extracted raw data files:** bod_parking_street.geojson (includes parking inside and outside the S-Bahn)


### Berlin Open Data - Park and Ride-Anlagen (WFS)

**Sources and origin**: Berlin Open Data - Park and Ride-Anlagen, published by Senatsverwaltung Mobilität, Verkehr, Klimaschutz und Umwelt. Locations and information on Park and Ride (P+R) facilities in the state of Berlin ([WFS](https://gdi.berlin.de/services/wfs/park_and_ride))

**Update frequency**: as published by Senatsverwaltung

**Data Type**: Static WFS (Web Feature Service) providing georeferenced locations of Park & Ride facilities in Berlin.

**Relevant fields**: 

- `bezirk`
- `anlagennam` (Name of the facility)
- `bahnhofsna` (Station name)
- `anzahl_anl` (Count of P+R facilities at station)
- `stellplaet` (Total parking spaces)
- `steplaetze` (Disabled spaces)
- `stellpla_1` (Short-term parking)
- `stellpla_2` (Motorbike spaces)
- `auslastung` (Average occupancy during peak)
- `art` (Type of parking (surface, garage, etc.))
- `belag` (Surface type (asphalt, gravel, etc.))
- `einschraen` (Time restriction (e.g., 24h, 12h))
- `bewirtscha` (Managed/Unmanaged)
- `art_bewirt` (Type of management (free, paid, permit))
- `anzahl_b_u` (Number of bicycle+ride spaces)

**Notes:** Enrichment parking layer with transit-oriented parking

**Links**: Berlin Open Data - [Park and Ride-Anlagen](https://daten.berlin.de/datensaetze/park-and-ride-anlagen-wfs-c9d9f2e4)

**📄 Extracted raw data files:** bod_park_and_ride.geojson


### Berlin Open Data – Parkraumbewirtschaftung (managed parking zones)

**Source and origin:** Berlin Open Data – parkraumbewirtschaftungsgebiete (zones where parking is controlled). Shows polygons of zones managed by the Bezirke. ([WFS](http://gdi.berlin.de/services/wfs/parkraumbewirtschaftung?REQUEST=GetCapabilities&SERVICE=wfs))

**Update frequency:** Published by districts; assume occasional changes 

**Data type:** Static 

**Relevant fields:**

- zone `id` / name
- `Bezirk`
- `Zeiten` 
- `gebuehr`
- `geometry` (polygon)

**Links**: Berlin Open Data - [Parkraumbewirtschaftung](https://daten.berlin.de/datensaetze/parkraumbewirtschaftung-wfs-86a217cc)

**Notes:** Enrichment point parking data with zone information (spatial join).

**Planned transformation steps:**

- Normalize columns (snake- and lower-case)
- Delete duplicates

**📄 Extracted raw data files:** bod_parking_zones.geojson

### Parkopedia - Dynamic Parking Availability

**Source and origin**: Parkopedia (business.parkope­dia.com), global parking data provider (static + dynamic). 

**Update frequency**: Unknown (must request from Parkopedia).

**Data type**: API/feed (commercial/licensed) — likely dynamic + static.

**Relevant data fields**: 

- `parking location` (lat/lon)
- `name`
- `operator`
- `capacity`
- `fee/paid status`
- `on-street` vs `off-street`
- `dynamic availability` (where supported).

**Notes**: Commercial/licensed product. Licensing terms must be reviewed before ingestion; determine whether Berlin/Germany coverage is sufficient and allowed for our product.  →  Contact sales/licensing to obtain access.

**Links:** [Parkopedia](https://business.parkopedia.com/parking-data)

# Parking Spaces Berlin Step 2 - Data Transformation & Integration

See notebook `parking_spaces/scripts/parking_spaces_data_transformation.ipynb` for full pipeline for data extraction, transformation, integration, and validation of the unified berlin parking data.|

## Applied Data Transformation Steps

- **Column normalization** (lowercase, snake_case, standardized field names)
- **Source harmonization** (mapping source-specific fields to the unified schema)
- **Geometry validation** and projection to WGS84 (EPSG:4326)
- **Spatial joins** to assign districts and managed parking zones
- **Deduplication** and **null handling** (removing duplicates, standardizing nulls)
- **Conflict detection** (setting verification flags for mismatches)
- **Schema alignment** and export to the final table

## Data Validation

- **CRS Consistency:** All geometries reprojected to WGS84 (EPSG:4326).  
- **Geometry Validity:** Verified no invalid, empty, or self‑intersecting geometries.  
- **Spatial Extent:** All features confirmed to fall within the Berlin administrative boundary.  
- **Missing street names:** Street names were enriched using a two‑stage spatial nearest‑street matching pipeline. (from 53,263 missing street names to 1,635 missing street names)
- **Cross‑Source Consistency:** Checked fee, time restrictions, and zone attributes for mismatches across sources.  
- **Duplication Check:** Identified duplicate polygons and overlapping points, retaining the most complete record.  

## Architecture Decision: One Unified Parking Table (AD‑001)

During exploration, we evaluated whether to maintain **multiple source‑specific tables** (e.g., OSM off-street, OSM on-street, BOD street parking, Park & Ride) or to **merge all records into one harmonized, unified table**.

### Exploration Summary

- Each data source exposes a different schema, inconsistent field naming, and heterogeneous geometry types.
- Many attributes overlap semantically even when named differently (`fee`, `parkgebuehr`, `bewirtscha`, etc.).
- Multiple sources describe *the same parking objects* with varying completeness → requiring deduplication.
- District and subdistrict assignment must be spatially derived and consistent across sources.
- Introducing separate tables would require additional integration logic, more foreign keys, and more complex joins in downstream analytics.

### ✅ Final Decision: Keep One Unified Table

We chose a **single integrated parking table** because it provides:

- **Consistent schema** across all parking data in Berlin  
- **Easier deduplication** and conflict resolution  
- **Simpler QA/validation** (one table → one validation layer)  
- **Faster downstream queries** for maps, dashboards, and APIs  
- **Better compatibility with MVP scope** of the Berlin Data Pool  

The unified table preserves source metadata (`source`, `source_layer`, `external_id`) so we maintain full lineage without fragmenting the data model. We also introduced a column `parking_category` (on street, off street, other) for easy filtering with simplified categories. `parking_type` still contains the original type of the parking. 

## Test Upload to Neon Database

To validate schema correctness, constraints, and foreign key relationships, we performed a **test ingestion** into the `test_berlin_data` schema in NeonDB.

### What was tested?

- Table creation with:
  - `PRIMARY KEY (parking_id)`
  - `NOT NULL` enforcement
  - Foreign keys to `districts` and the composite key of `district_id`
- A full test load of ~308k processed parking records using `pandas.to_sql`.

### Outcome

- Table created successfully with all constraints.
- Upload completed without corruption.
- Foreign key checks ensured proper spatial assignment of districts and neighborhoods.
- Schema validated at production scale (~144 MB table size after insert).

This confirms that the unified parking table design is aligned with the structural requirements of the Berlin Data Pool and is ready for integration into the main data foundation.

## Final Parking Table Schema

The following table describes the unified schema used for the integrated parking table after all harmonization and transformation steps:

| **field name**           | **description**                                                                 |
|--------------------------|-------------------------------------------------------------------------------|
| parking_i                | Unique identifier (PK)                                                        |
| source                   | Data origin (`osm`, `bod_parking_street`, `bod_park_and_ride`, etc.)          |
| source_layer             | Source sublayer or OSM tag combination                                        |
| external_id              | Unique identifier from the source (OSM id, WFS id, etc.)                      |
| name                     | Parking facility name or description                                          |
| parking_type             | Distinct parking type (`underground`, `kurb`, `garage`, `zone`, `park_and_ride`, etc.) |
| parking_category         | Simplified parking type (`off_street`, `on_street`, `other`)                  |
| operator                 | Operator or managing entity                                                   |
| fee_raw                  | Fee information as provided by source (string or boolean)                     |
| fee_amount_euro          | Numeric field with parking price per hour in euro                             |                                      |
| has_fee_bool             | Boolean value True/False                                                      |
| time_restriction         | Time restrictions or allowed parking times (e.g., `12h`, `24h`)               |
| capacity                 | Total parking capacity (integer)                                              |
| capacity_disabled        | Number of disabled parking spaces (integer, if available)                     |
| street_name              | Name of the street (if present)                                               |
| district_id              | Unique identifier for the district                                            |
| neighborhood_id          | Unique identifier for the subdistrict                                         |
| managed_zone_id          | Identifier for managed parking zone (if applicable)                           |
| geometry_type            | Geometry type (`Point`, `Polygon`, `LineString`, etc.)                        |
| geometry                 | Geometry in WGS84 (EPSG:4326), as WKT or GeoJSON                              |
| last_updated_at_source   | Date of last update from the data source                                      |
| fetched_at               | Timestamp when the data was ingested                                          

## Final Database Upload

Data has been uploaded to the Layered database and ERD has been updated with the `parking_spaces` table.