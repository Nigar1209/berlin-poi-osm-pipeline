# Parking Spaces Berlin

This document lists potential data sources for integrating parking related data into the Berlin data pool. For each data source the origin, update frequency, data type (static or dynamic), relevant fields and tags, links, notes, and the extracted raw geojson files are listed. 

See notebook `parking_spaces/scripts/parking_spaces_data_modelling.ipynb` for data extraction method of the raw data files in `parking_spaces/sources`

**Raw Data Fiels:**

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


## Parking Table Schema Draft

This is a **proposal** for how to map all above sources into a single raw-ish table later:

| **field name**           | **description**                                              |
|--------------------------|----------------------------------------------------------|
| source                   | `osm`, `bod_parken`, `bod_parkandride`, …                |
| source_layer             | sublayer or OSM tag combination                          |
| external_id              | id from source (OSM id, WFS id, …)                       |
| name                     | parking name or description                              |
| parking_type             | e.g. `off_street`, `on_street`, `garage`, `zone`, `P&R`  |
| operator                 | city / private / district                                |
| fee                      | boolean or string from source                            |
| time restriction         | 12h, 24h, ..                                             |
| capacity                 | integer                                                  |
| capacity_disabled        | integer if available                                     |
| street_name              | from WFS if present                                      |
| district                 | Berlin Bezirk if                                         |
| managed_zone_id          | id from parkraumbewirtschaftung                          |
| geometry_type            | point / polygon / line                                   |
| geometry                 | geom                                                     |
| last_updated_at_source   | date from feed if present                                |
| fetched_at               | timestamp of download                                    |


## Planned Data Transformation Steps

- Normalize column names (lowercase, snakecase, remove special characters)
- Select relevant columns
- Drop columns with >85% null
- Remove duplicates (deduplicate on same geometry centroid within 5–10 meters and same name)
- Remove empty geometries, fix invalid geometries, explode multiparts
- Map source-specific categories to common parking_type
  - OSM amenity=parking_space → on_street
  - WFS street parking → on_street
  - WFS P+R → park_and_ride
  - WFS parkraumbewirtschaftung → zone
  - OSM amenity=parking with parking=multi-storey → garage

## Data issues or inconsistencies

### Schema and Field Inconsistencies

**Different field names and languages**: Berlin Open Data fields are in German (bezirk, strassenname, stellplaet), while OSM uses English and underscores (capacity, fee, operator). → Requires normalization to a unified schema.

**Data types inconsistencies**: Numeric fields like capacity or fee can appear as strings in WFS responses ("30" instead of 30, "ja"/"nein" for booleans).

**Missing IDs**: Some WFS datasets have no stable unique identifier and mostly have ploygon_id, while OSM has stable unique identifiers.

### Coverage and Spatial Gaps

**Uneven spatial coverages**:

- OSM data coverage depends on community mapping (some districts may be better mapped than others)
- Park & Ride only covers specific sites and not all large parking spaces
- Parken im Straßenraum does not include private or informal street parking

**Split services**: Parken im Straßenraum is split into inner and outer S-Bahn ring WFS layers. When combining them they can cause duplicates or missing areas if one of the layers fails.

**Misaligned Geometry**: Some WFS geometries may not perfectly align with official district boundaries or OSM geometries (could give issues with spatial joins)

### Completeness & Reliablility

**Missing values**: Some columns might be outdated or have a lot of missing data

**Unverified values**: OSM attributes are entered by users and may contain typos or inconsistencies 

**Overlapping sources**:

- OSM and Parken im Straßenraum may both describe the same locations differently
- Park & Ride locations can cometimes also appear as amenity=parking in OSM

### Coordinate Reference Systems (CRS)

There are inconcistent CRS across sources (Some WFS services deliver data in EPSG:25833 (ETRS89 / UTM Zone 33N), others in EPSG:4326 (WGS84).) 

### License & Accessibility

- OSM data is under ODbL license (requires attribution)
- Berlin Open Data typically uses DL-DE Zero 2.0
- Parkopedia is commercial and cannot be redistributed without permission


