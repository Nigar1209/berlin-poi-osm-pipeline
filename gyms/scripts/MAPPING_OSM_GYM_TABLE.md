# Gym Data Layer – Modelling & Planning

## A. Field Mapping (OSM → Gym Table)

| OSM Field           | DB Field        | Example Value        | Notes                        |
|---------------------|-----------------|----------------------|------------------------------|
| name                | name            | "McFit Tempelhof"    | Name of the gym or studio    |
| leisure             | type            | "fitness_centre"     | Main type (use if present)   |
| sport               | type            | "yoga"               | Use if "leisure" missing     |
| addr:street         | street          | "Sonnenallee"        | Address street name          |
| addr:housenumber    | housenumber     | "123"                | Address house number         |
| addr:postcode       | postcode        | "12045"              | Postal code                  |
| addr:city           | city            | "Berlin"             | City, usually "Berlin"       |
| opening_hours       | opening_hours   | "Mo-Su 07:00-23:00"  | OSM opening hours format     |
| phone               | phone           | "+49 30 123456"      | Optional                     |
| website             | website         | "www.mcfit.com"      | Optional                     |
| wheelchair          | wheelchair      | "yes"                | Optional                     |
| latitude / lon      | latitude/longitude | 52.4923 / 13.4247 | Coordinates                  |
| osm_id              | osm_id          | 308190832            | OSM object ID                |
| osm_type            | osm_type        | node/way/relation    | OSM object type              |
| source              | source          | "OSM Overpass"       | Always "OSM Overpass"        |

---

## B. Table Structure (Planned Schema)

| Field        | Data Type     | Description                        |
|--------------|--------------|------------------------------------|
| gym_id       | SERIAL        | Primary key                        |
| name         | VARCHAR(255)  | Name of gym or studio              |
| type         | VARCHAR(50)   | Type ("fitness_centre", "yoga")    |
| street       | VARCHAR(255)  | Street name                        |
| housenumber  | VARCHAR(20)   | House number                       |
| postcode     | VARCHAR(10)   | Postal code                        |
| city         | VARCHAR(100)  | City                               |
| latitude     | FLOAT8        | Latitude coordinate                |
| longitude    | FLOAT8        | Longitude coordinate               |
| opening_hours| TEXT          | Opening hours (OSM format)         |
| phone        | VARCHAR(50)   | Phone number (optional)            |
| website      | VARCHAR(255)  | Website URL (optional)             |
| wheelchair   | VARCHAR(10)   | Wheelchair access (optional)       |
| osm_id       | BIGINT        | OSM object ID                      |
| osm_type     | VARCHAR(20)   | OSM object type                    |
| source       | TEXT          | Data source                        |
| created_at   | TIMESTAMP     | Creation timestamp (auto)          |

---

## C. Relation to Districts / Neighborhoods

- Gyms will be assigned to a district or neighborhood using their latitude and longitude.
- The matching will be done by comparing the gym coordinates with the geometry of the `districts` or `neighborhoods` tables in the database.
- This allows for easy connection to other city data layers.

---

## D. Known Data Issues

- Some gyms do not have complete address information.
- Some entries may be missing a name or contact details.
- The type field ("leisure" or "sport") is not always present or clear.
- OSM data can have duplicates or outdated entries.
- Not all gyms are mapped in OSM, so data coverage is not 100%.

---

## E. Transformation Plan

1. Export gym data from OSM/Overpass and save as CSV.
2. Map each OSM field to the corresponding gym table field (see mapping above).
3. Clean and normalize the data (e.g., address, phone, website).
4. Assign gyms to a district or neighborhood using spatial join with coordinates.
5. Prepare the cleaned data for database import.

---

