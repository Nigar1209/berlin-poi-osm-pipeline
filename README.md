🏗️ Schema Definition
All tables in the pipeline follow a standardized schema to ensure consistency and compatibility with the unified POI table.

📊 Common Column Schema
| Column Name       | Data Type      | Constraints / Notes                                                                                                             |
| ----------------- | -------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| `id`              | `VARCHAR(20)`  | Primary Key, numeric only, no letters                                                                                           |
| `district_id`     | `VARCHAR(20)`  | Not NULL, mapped from district name; Foreign Key → `berlin_data.districts(district_id)` (ON DELETE RESTRICT, ON UPDATE CASCADE) |
| `name`            | `VARCHAR(200)` | Not NULL, defaults to `'Unknown'` if NULL                                                                                       |
| `latitude`        | `DECIMAL(9,6)` |                                                                                                                                 |
| `longitude`       | `DECIMAL(9,6)` |                                                                                                                                 |
| `geometry`        | `VARCHAR`      | Stored in `POINT()` format                                                                                                      |
| `neighborhood`    | `VARCHAR(100)` | Joined from `neighborhoods` table                                                                                               |
| `district`        | `VARCHAR(100)` | From `lor_ortsteile.geojson`                                                                                                    |
| `neighborhood_id` | `VARCHAR(20)`  | From `lor_ortsteile.geojson`                                                                                                    |

