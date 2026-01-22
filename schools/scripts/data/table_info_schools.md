## schools — Table Documentation (Production Load)

### Purpose
The `berlin_source_data.schools_maximilian_burkhardt` table provides the Schools data layer for Berlin in the production database.  
It contains geolocated school points aligned to the common POI schema and is designed to support downstream usage such as frontend visualization, analytics, and API consumption.

### Target schema and table
- **Schema:** `berlin_source_data`
- **Table:** `schools_maximilian_burkhardt`

### Data source
The dataset is derived from an OSM-based schools extraction, cleaned and standardized to the common POI schema.  
Administrative attributes (`district_id`, `neighborhood_id`, `district`, `neighborhood`) are added via spatial mapping to Berlin administrative polygons.

### Table schema (columns)
| Column | Type | Description |
|-------|------|-------------|
| id | varchar | Primary key. Unique identifier for each school record. |
| district_id | varchar | District identifier. Must exist in `berlin_source_data.districts(district_id)`. |
| neighborhood_id | varchar | Neighborhood identifier (administrative mapping). |
| name | varchar | School name. Defaults to `Unknown` if missing. |
| school_type | varchar | School category/type (if available). |
| operator | varchar | Operating organization (if available). |
| address | varchar | Address string (if available). |
| postal_code | varchar | Postal code (if available). |
| phone | varchar | Contact phone number (if available). |
| email | varchar | Contact email address (if available). |
| website | varchar | Website URL (if available). |
| coordinates | varchar | Spatial point representation (POINT format or similar unified representation). |
| latitude | numeric | Geographic latitude. |
| longitude | numeric | Geographic longitude. |
| neighborhood | varchar | Neighborhood name (administrative). |
| district | varchar | District name (administrative). |
| opening_hours | varchar | Opening hours (if available). |
| geometry_wkt | varchar | WKT geometry representation of the point (debug/export helper). |

### Constraints and relational integrity
- **Primary key**
  - `id` is the primary key and uniquely identifies each school record.
- **Foreign key**
  - `district_id` references `berlin_source_data.districts(district_id)`
  - Ensures each school belongs to a valid Berlin district.
- **Referential rules**
  - `ON DELETE RESTRICT`
  - `ON UPDATE CASCADE`
- **Coordinate quality checks**
  - Latitude constrained to Berlin range: `52.3–52.7`
  - Longitude constrained to Berlin range: `13.0–13.8`

Note: A foreign key from `neighborhood_id` to `berlin_source_data.neighborhoods(neighborhood_id)` cannot be enforced because the referenced column is not UNIQUE/PK in the current `neighborhoods` layer. Integrity was validated via join checks (see Validation).

### Validation and quality checks
The following checks were performed after loading the table:

- Row count matches the cleaned dataset used for insertion (`1072` rows).
- No duplicate primary keys (`id`).
- All `district_id` values are valid and exist in the districts table.
- Administrative mappings validated (`district_id`, `neighborhood_id`) via join checks (0 missing references).
- No missing coordinates (`latitude`, `longitude`) and no invalid coordinate ranges (0 out-of-range).

### Known data quality gaps (non-blocking)
- `name = 'Unknown'`: `51`
- Missing `postal_code`: `242`

### Notes
This table follows the Berlin Data Platform layer conventions and aligns schools to the unified POI schema.  
It is production-ready in terms of relational integrity and spatial validity; remaining gaps are limited to optional content fields (e.g., address/postal code) that can be enriched later.
