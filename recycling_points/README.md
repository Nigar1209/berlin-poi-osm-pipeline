RECYCLING POINTS IN BERLIN
OpenStreetMap Data Extraction, Normalization & Enrichment
=========================================================

This project extracts, cleans, and normalizes recycling location data
for Berlin from OpenStreetMap (OSM) into an analysis-ready GeoDataFrame.

The notebook is designed to handle highly heterogeneous OSM metadata
while preserving data provenance and avoiding inferred or fabricated
information.


PROJECT GOALS
-------------

- Extract all amenity=recycling locations in Berlin from OpenStreetMap
- Interpret granular recycling:* tags into explicit material categories
- Normalize noisy, overlapping OSM metadata into user-facing fields
- Preserve ambiguity where data is unclear
- Produce a clean, structured GeoDataFrame suitable for analysis or APIs


DESIGN PRINCIPLES
-----------------

- No invented data – only explicit OSM tags are used
- Structured tags are preferred over free text
- Fallback logic is explicit and ranked
- Human readability without semantic loss
- Reproducibility over live API calls


DATA SOURCE
-----------

Primary source:
- OpenStreetMap (via OSMnx)

OSM tag used:
- amenity=recycling

Geographic scope:
- Berlin, Germany

To avoid repeated API calls and ensure reproducibility, the raw OSM
extract is persisted locally and reused throughout the notebook.


DEPENDENCIES
------------

Required Python packages:

- osmnx
- geopandas
- pandas
- numpy

Install via:
pip install osmnx geopandas pandas numpy


PROJECT STRUCTURE
-----------------
```text
.
├── scripts/
│   └── recycling_points_berlin.ipynb
├── sources/
│   ├── raw_recycling_points.geojson
│   ├── raw_recycling_points.csv
│   ├── final_recycling_points_with_district.geojson
│   └── final_recycling_points_with_district.csv
├── recycling_points_TableDocumentation.md
└── README.md
```

PROCESSING PIPELINE OVERVIEW
----------------------------

1) DATA EXTRACTION (ONE-TIME)

- Query OpenStreetMap for amenity=recycling features in Berlin
- Persist results as GeoJSON and CSV
- All further analysis loads from disk to ensure reproducibility


2) RECYCLING TAG INTERPRETATION

OpenStreetMap models recycling using hierarchical tags:

- recycling:<item>            -> acceptance (yes / no / customers)
- recycling:<item>:<subtype>  -> material details (e.g. glass color)

Derived output fields:

- accepted_recycling_items
- not_accepted_recycling_items

Note:
An intermediate field (other_recycling_items) was evaluated and intentionally dropped due to low semantic value.


Design guarantees:
- Order of tags is preserved
- Subtype detail is not collapsed
- No acceptance is inferred from ambiguous tags


3) COLUMN GROUPING STRATEGY

OSM metadata is grouped by semantic purpose rather than raw tag name.

Groups:

1. Identity
2. Geometry
3. Name & Operator
4. Address
5. Contact
6. Website
7. Recycling Types
8. Accessibility
9. Opening & Access Times
10. Metadata / Notes

Each group is:
- Explored independently
- Normalized using group-specific rules
- Collapsed into user-facing fields


NORMALIZATION HIGHLIGHTS
------------------------

NAME RESOLUTION

Produces:
- display_name   : best human-readable label
- name_metadata  : all name/operator variants with provenance
- entity_type    : classification hints (e.g. man_made, operator:type)

Priority order:
name -> short_name -> localized name -> operator (fallback)

Entity types are never used to invent names.


ADDRESS CONSTRUCTION

Primary structured address construction uses explicit OSM addr:* tags only.

Structured address fields (highest precision):
- addr:street
- addr:housenumber
- addr:postcode
- addr:suburb

Construction logic:
- Street name is mandatory for a structured address.
- House number is appended only if present.
- Postcode and suburb are grouped as a city-level component.
- Components are joined as:
  "<street> <housenumber>, <postcode> <suburb>"

If no structured components are available, the address is left as NA
so that fallback logic can be applied explicitly.

Final structured field:
- full_address


ADDRESS FALLBACK LOGIC

Not all OSM features contain structured addr:* tags.
When structured address construction fails, fallback sources are used
in a controlled priority order, explicitly trading precision for coverage.

Fallback sources (ordered by decreasing reliability):
1. ref
2. description

The position field is explicitly excluded due to low semantic quality.
Reverse geocoding is used instead where coordinates are available.

Fallback validation:
- Only values that *look like addresses* are accepted.
- Heuristics include:
  - Presence of common street suffixes (e.g. Straße, Str., Platz, Allee, Damm)
  - Intersection or relative-location keywords (e.g. Ecke, ggü., gegenüber)
  - Minimum string length to avoid noise

Fallback is applied only if:
- full_address is still missing
- the candidate value passes validation

This prevents free-text contamination of otherwise clean addresses.


REVERSE GEOCODING (NOMINATIM)

If both structured and validated fallback addresses are missing,
reverse geocoding is applied as a last resort.

Reverse geocoding conditions:
- full_address is NA
- latitude and longitude are present

Implementation:
- Uses Nominatim (OpenStreetMap)
- Language set to German ("de")
- One request per second enforced via sleep

Reverse geocoding resolution order:
1. Structured road + house number (if available)
2. Postcode + city or town
3. Nominatim display_name (human-readable fallback)

If no usable information is returned, full_address remains NA.

This ensures maximum address coverage without inferring or fabricating data.


CONTACT NORMALIZATION

All phone and email variants are merged into:
- contact_combined

Original provenance is preserved via prefixed labels.


WEBSITE NORMALIZATION

Rules:
- Preserve existing URL schemes
- Assume https:// only when scheme is missing
- Leave missing values untouched

Final field:
- website_combined


ACCESSIBILITY MODELING

Core accessibility fields:
- wheelchair_access
- access_restriction
- floor_level
- unit_count

Derived summaries:
- physical_obstacles
- environmental_features
- accessibility_features

All accessibility information is derived strictly from explicit OSM tags.
Missing values are treated as unknown, not negative.


FINAL OUTPUT
------------

The final GeoDataFrame contains:

- One row per recycling location
- Geometry preserved internally for spatial analysis and exported as WKT
- Clean identity fields
- Human-readable name and address
- Explicit recycling material acceptance / rejection
- Accessibility and access-control summaries
- Contact and website information
- Administrative district and neighborhood mapping

All raw OSM noise and intermediate processing columns
(e.g. addr:*, ref, description, position) are removed
before final export.


FINAL DATASET OVERVIEW (SCHEMA SUMMARY)
======================================


| Column Name                   | Type             | Description                                                                 |
|------------------------------|------------------|-----------------------------------------------------------------------------|
| id                           | varchar(20)      | Primary key. Stable identifier for each recycling location (OSM-derived).  |
| district_id                  | varchar(20)      | Foreign key reference to berlin_source_data.districts(district_id).        |
| name                         | varchar(200)     | Human-readable name of the location. Defaults to 'Unknown' if missing.     |
| latitude                     | numeric(9,6)     | Geographic latitude (WGS84).                                                |
| longitude                    | numeric(9,6)     | Geographic longitude (WGS84).                                               |
| geometry                     | varchar          | Spatial point representation stored as WKT (e.g. POINT(lon lat)).          |
| neighborhood                 | varchar(100)     | Neighborhood name (administrative mapping).                                |
| district                     | varchar(100)     | District name (administrative mapping).                                    |
| neighborhood_id              | varchar(20)      | Neighborhood identifier.                                                   |
| entity_type                  | varchar(100)     | Entity classification hint (OSM-derived).                                  |
| landuse                      | varchar(100)     | Land use classification from OSM.                                          |
| accepted_recycling_items     | text             | Explicitly accepted recycling materials (flattened list).                  |
| not_accepted_recycling_items | text             | Explicitly rejected recycling materials (flattened list).                  |
| access_restriction           | varchar(100)     | Access limitations (e.g. private, customers-only).                          |
| wheelchair_access            | varchar(100)     | Wheelchair accessibility status (explicit tagging only).                   |
| physical_obstacles           | text             | Explicitly tagged physical barriers.                                       |
| accessibility_features       | text             | Aggregated accessibility-related features.                                 |
| is_operational               | boolean          | Operational status if explicitly tagged; NULL if unknown.                  |
| full_address                 | text             | Human-readable resolved address.                                           |
| floor_level                  | integer          | Floor or level information if explicitly tagged.                           |
| unit_count                   | integer          | Number of recycling units or containers.                                   |
| availability_info            | text             | Opening times or availability conditions.                                  |
| contact_combined             | text             | Aggregated contact information (phone, email, etc.).                       |
| website_combined             | text             | Aggregated website URLs.                                                   |
| environmental_features       | text             | Environmental or structural features.                                      |
| source                       | varchar(100)     | Source indicator for the record (e.g. OSM).                                |
| name_metadata                | varchar(200)     | Raw name/operator metadata with provenance.                                |


CONSTRAINTS AND RELATIONAL INTEGRITY
===================================

Primary Key
-----------
- id

Foreign Keys
------------
- district_id references berlin_source_data.districts(district_id)
  - ON DELETE RESTRICT
  - ON UPDATE CASCADE

Check Constraints
-----------------
- latitude between 52.2 and 52.8
- longitude between 12.9 and 13.9

Defaults
--------
- name defaults to 'Unknown'
- source defaults to 'Unknown'


FINAL DATASET SCHEMA
===================

The final dataset is a GeoDataFrame where each row represents a single
recycling location extracted from OpenStreetMap and spatially joined
to Berlin administrative districts.

Data types reflect Pandas / GeoPandas dtypes after normalization.
Missing values represent unknown or unspecified information,
not false or negative assertions.


CORE IDENTIFIERS & GEOMETRY
--------------------------

id
  Type: string
  Description:
  Stable identifier derived from OSM element IDs.
  Cast to string for database compatibility.

geometry
  Type: geometry
  Description:
  GeoPandas geometry (Point or Polygon) in EPSG:4326.


NAME & ENTITY METADATA
---------------------

name
  Type: object (string)
  Description:
  Best human-readable name for the recycling location.
  Derived from prioritized OSM name and operator tags.

name_metadata
  Type: object
  Description:
  Collection of all available name- and operator-related tags
  with provenance preserved.

entity_type
  Type: object (string)
  Description:
  Classification hints describing the nature of the entity.
  Not used to infer names or behavior.


ADDRESS & LOCATION CONTEXT
--------------------------

full_address
  Type: string
  Description:
  Human-readable address constructed via:
  1. Structured addr:* tags
  2. Validated free-text fallback (ref, description)
  3. Reverse geocoding (Nominatim)

district
  Type: object (string)
  Description:
  Administrative district name.

neighborhood
  Type: object (string)
  Description:
  Neighborhood or locality name.

neighborhood_id
  Type: object (string)
  Description:
  Identifier associated with the neighborhood.

district_id
  Type: object (string)
  Description:
  Identifier associated with the administrative district.
  Enforced as a foreign key in the database.


DATA EXPORT & DATABASE INGESTION
================================

The final dataset is exported in two formats:
- GeoJSON (for GIS and spatial workflows)
- CSV (for tabular processing and database ingestion)

Before database insertion:
- ID is cast to string
- Latitude and longitude are cast to float
- Boolean fields are normalized
- Array-like values are flattened to PostgreSQL-safe strings
- Geometry is converted to WKT

Target database:
- PostgreSQL
- Schema: berlin_source_data
- Table: recycling_points

All constraints (primary key, foreign keys, coordinate bounds)
are enforced at the database level.


DATA TYPE NOTES
---------------

- object columns may contain strings or flattened lists
- Nullable numeric types preserve missing values
- No inferred, guessed, or derived semantic data is stored


NOTES & LIMITATIONS
-------------------

- OSM data quality varies by contributor
- Missing tags are treated as NA, not false
- Addresses are not guaranteed to be postal-grade
- Reverse geocoding is best-effort and rate-limited
- Results reflect OSM state at extraction time
