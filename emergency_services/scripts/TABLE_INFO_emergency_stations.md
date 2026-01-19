## emergency_stations — Table Documentation (Production Load)

### Purpose
The `berlin_source_data.emergency_stations` table provides the Emergency Stations data layer for Berlin in the production database.  
It contains geolocated emergency service points and is designed to support downstream usage such as frontend visualization, analytics, and API consumption.

### Target schema and table
- **Schema:** `berlin_source_data`
- **Table:** `emergency_stations`

### Data source
The dataset is derived from the cleaned and transformed Emergency Services pipeline output and loaded into the production database after validation.

### Table schema (columns)
| Column | Type | Description |
|-------|------|-------------|
| id | varchar(20) | Primary key. Unique identifier for each emergency station. |
| district_id | varchar(20) | Foreign key reference to districts. Must exist in `berlin_source_data.districts(district_id)`. |
| name | varchar(200) | Emergency station name. Defaults to `Unknown` if missing. |
| station_type | varchar(100) | Category/type of emergency service (e.g. police, fire, ambulance). |
| latitude | numeric(9,6) | Geographic latitude. |
| longitude | numeric(9,6) | Geographic longitude. |
| geometry | varchar | Spatial point representation (POINT format). |
| neighborhood | varchar(100) | Neighborhood name (administrative). |
| district | varchar(100) | District name (administrative). |
| neighborhood_id | varchar(20) | Neighborhood identifier (administrative mapping). |
| operator | varchar(200) | Operator / organization responsible for the service location. |
| country | varchar(100) | Country value from the enriched dataset. |
| city | varchar(100) | City value from the enriched dataset. |
| street | varchar(200) | Street name. |
| housenumber | varchar(20) | House number. |
| postcode | varchar(10) | Postal code. |
| phone | varchar(50) | Contact phone number (if available). |
| email | varchar(200) | Contact email address (if available). |
| website | varchar(200) | Website URL (if available). |
| source | varchar(100) | Source indicator for the record. |

### Constraints and relational integrity
- **Primary key**
  - `id` is the primary key and uniquely identifies each emergency station.
- **Foreign key**
  - `district_id` references `berlin_source_data.districts(district_id)`
  - Enforces that every emergency station belongs to a valid Berlin district.
- **Referential rules**
  - `ON DELETE RESTRICT`
  - `ON UPDATE CASCADE`

### Validation and quality checks
The following checks were performed after loading the table:

- Row count matches the cleaned dataset used for insertion.
- No duplicate primary keys (`id`).
- All `district_id` values are valid and exist in the districts table.
- No missing coordinates (`latitude`, `longitude`) and no invalid coordinate ranges.
- Administrative mappings validated (`district_id`, `neighborhood_id`).

### Notes
This table is intended to be production-ready and consistent with Berlin Data Platform layer conventions. It follows the standard unified POI alignment approach and supports integration with existing spatial and administrative layers.
