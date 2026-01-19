PURPOSE
=======

The berlin_source_data.recycling_points table provides the Recycling Points
data layer for Berlin in the production database.

It contains geolocated recycling locations extracted from OpenStreetMap and
is designed to support downstream usage such as frontend visualization,
analytics, spatial analysis, and API consumption.


TARGET SCHEMA AND TABLE
=======================

Schema: berlin_source_data  
Table: recycling_points


DATA SOURCE
===========

The dataset is derived from the cleaned and normalized output of the
Recycling Points OpenStreetMap extraction and enrichment pipeline.

Source system:
- OpenStreetMap (OSM), via OSMnx

Only explicit OSM tags are used. No inferred or fabricated data is introduced.
The dataset is loaded into the production database after validation.


TABLE SCHEMA (COLUMNS)
=====================

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
- id is the primary key and uniquely identifies each recycling location.

Foreign Key
-----------
- district_id references berlin_source_data.districts(district_id)
  - Enforces that every recycling location belongs to a valid Berlin district.

Referential Rules
-----------------
- ON DELETE RESTRICT
- ON UPDATE CASCADE

Check Constraints
-----------------
- latitude must be between 52.2 and 52.8
- longitude must be between 12.9 and 13.9

Defaults
--------
- name defaults to 'Unknown'
- source defaults to 'Unknown'


VALIDATION AND QUALITY CHECKS
=============================

The following checks were performed after loading the table:

- Row count matches the cleaned dataset used for insertion.
- No duplicate primary keys (id).
- All district_id values are valid and exist in the districts table.
- No missing coordinates (latitude, longitude).
- No invalid coordinate ranges.
- Administrative mappings validated (district_id, neighborhood_id).
- Geometry successfully serialized to WKT for database storage.


NOTES
=====

This table is intended to be production-ready and consistent with Berlin
Data Platform layer conventions.

It follows a strict “no inferred data” principle:
- Missing values represent unknown information, not negative assertions.
- All semantic fields are derived from explicit OpenStreetMap tags only.

Geometry is preserved internally during processing for spatial operations
and exported as WKT for database compatibility and downstream consumption.