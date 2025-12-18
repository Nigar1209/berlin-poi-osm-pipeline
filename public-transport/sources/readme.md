# 🚊 Berlin Public Transport Data Project

## ✅ 1.1 Data Source Discovery

This section outlines the discovery and documentation of datasets used to enrich the Berlin public transport project.

### 🔹 Combined Sources

| Source Name                    | Description                                                                                                           | Type    | Update Frequency       | Format      | Origin                                                                                                         |
| ------------------------------ | --------------------------------------------------------------------------------------------------------------------- | ------- | ---------------------- | ----------- | -------------------------------------------------------------------------------------------------------------- |
| VBB GTFS Feed                  | Public transport network data for Berlin and Brandenburg (routes, stops, timetables). Includes BVG buses and ferries. | Static  | 2x weekly              | GTFS (.zip) | [vbb.de](https://www.vbb.de/search/gtfs)                                                                       |
| GTFS.de                        | Aggregates static GTFS feeds for all of Germany.                                                                      | Static  | Daily                  | GTFS        | [gtfs.de](https://gtfs.de/de/feeds/)                                                                           |
| BVG API                        | Real-time API for buses, U-Bahn, trams, and ferries in Berlin                                                         | Dynamic | Real-time              | API (JSON)  | [bvg.de](https://www.bvg.de/)                                                                                  |
| OpenStreetMap                  | Geospatial public transport nodes, lines, and POIs                                                                    | Dynamic | Community-driven       | GeoJSON/XML | [openstreetmap.org](https://www.openstreetmap.org)                                                             |
| Berlin Open Data Portal        | Government-published data on urban infrastructure, traffic, and neighborhoods                                         | Static  | Monthly                | CSV/GeoJSON | [daten.berlin.de](https://daten.berlin.de)                                                                     |
| Google Drive CSV Upload        | Final merged GTFS dataset with buses and ferries in Berlin                                                            | Static  | One-time               | CSV         | [Google Drive Folder](https://drive.google.com/drive/folders/19t58Fiz2AOSAnEYl_InCq86jjWVmnnV-?usp=share_link) |
| Berlin U-Bahn Stations         | Berlin U-Bahn stop coordinates from Wikidata via SPARQL (by Clifford Anderson)                                        | Static  | Real-time (via SPARQL) | CSV         | [GitHub Gist](https://gist.github.com/CliffordAnderson/7fb7473af31f9343f8a55518545480a0)                       |
| Berlin U-Bahn Line Connections | Station-to-station U-Bahn line connections scraped from Wikipedia                                                     | Static  | Manual updates         | CSV         | [GitHub Gist](https://gist.github.com/CliffordAnderson/7fb7473af31f9343f8a55518545480a0)                       |

---

## ✅ 1.2 Modelling & Planning

### 🔸 GTFS Key Parameters

* `route_id`, `route_type`, `route_long_name`
* `trip_id`, `shape_id`, `service_id`
* `stop_id`, `stop_name`, `stop_lat`, `stop_lon`
* `arrival_time`, `departure_time`, `stop_sequence`
* `agency_id`, `agency_name`

### 🔸 U-Bahn CSV Columns

From `03-stations.csv`:

* `station`: Station name (original)
* `lat`: Latitude
* `lng`: Longitude

From `08-connections-no-dupes.csv`:

* `point1`: Starting station
* `line`: U-Bahn line
* `point2`: Ending station

From GTFS `stop.txt` (available in the shared Google Drive folder):

* `stop_name`: Name of the stop (e.g., "U Wilmersdorfer Straße")  
* `stop_desc`: Additional stop description  
* `stop_lat`: Latitude  
* `stop_lon`: Longitude  

### 🔗 Data Linkage Plan

| Target Table       | Link Type         | Key Columns                    |
| ------------------ | ----------------- | ------------------------------ |
| neighborhoods      | Spatial join      | `stop_lat`, `stop_lon`         |
| listings           | Proximity mapping | `stop_id` → closest lat/lon    |
| ubahn\_connections | Name matching     | `point1`, `point2` ↔ `station` |

### 📑 Planned Table Schemas

#### public\_transport\_data

| Column          | Type    | Description                      |
| --------------- | ------- | -------------------------------- |
| route\_id       | STRING  | Transit route ID                 |
| route\_type     | STRING  | 'bus' or 'ferry'                 |
| trip\_id        | STRING  | GTFS trip ID                     |
| stop\_id        | STRING  | GTFS stop ID                     |
| stop\_name      | STRING  | Lowercase, cleaned stop name     |
| stop\_lat       | FLOAT   | Latitude                         |
| stop\_lon       | FLOAT   | Longitude                        |
| arrival\_time   | TIME    | Scheduled time of arrival        |
| departure\_time | TIME    | Scheduled time of departure      |
| stop\_sequence  | INTEGER | Order of stop in the trip        |
| agency\_id      | STRING  | Operator ID                      |
| agency\_name    | STRING  | Normalized agency name (cleaned) |



### ⚠️ Known Issues or Inconsistencies

* GTFS: Some trips lack shape data (no geometries)
* GTFS: Stop names have inconsistent formatting or character encoding
* GTFS: Legacy or region-specific `route_type` codes
* GTFS: Spatial drift of stops near ferries/water
* U-Bahn: Inconsistent naming with "U-Bahnhof" prefix
* U-Bahn: Missing coordinates for a few connections

### 🔄 Transformation Plan

**GTFS Workflow:**

1. Load CSVs from GTFS exports
2. Filter `route_type` for 3 (bus) and 4 (ferry)
3. Normalize: lowercase, replace spaces with `_`, trim
4. Join: `routes` + `agency` → `trips` → `stop_times` → `stops`
5. Drop duplicates, validate foreign keys
6. Output: `public_bus_ferry_data_merged.csv`

**U-Bahn Workflow:**

1. Clean station names (remove "U–Bahnhof", trim)
2. Normalize coordinate and postcode types
3. Assign  neighborhood name using coordinates or postcode (reverse geocoding or lookup table)
4. Merge station info to both `point1` and `point2`
5. Create merged connection table for analysis or routing
6. Filter `stops.csv` from the shared Google Drive folder to isolate U-Bahn stations:
   - Use `stop_name` values that start with "U" or "S+U"
   - This idea was added late to enrich the dataset
   - Reverse geocode coordinates to get postcodes per stop

---

## 🗂 1.3 /sources Directory Plan

### 📁 Folder Structure

```
/sources/
├── 03-stations.csv
├── 08-connections-no-dupes.csv
├── Google-Drive-Link.url
├── cleaned_agency.csv
├── cleaned_routes-2.csv
├── cleaned_stops.csv
├── public_bus_data_cleaned.csv
├── public_bus_ferry_data_merged.csv
├── readme.md
```

### `/sources/README.md`

# Data Sources: Public Transport Berlin
- `cleaned_routes.csv`: GTFS routes filtered to bus and ferry  
- `cleaned_agency.csv`: Transit operators  
- [cleaned_stop_times.csv](https://drive.google.com/file/d/1r8LSmX2BZqrDyeQ3Z0SoBhmHM_4IveDE/view?usp=share_link): Arrival and departure times per stop  
- `cleaned_stops.csv`: Stops with lat/lon  
- `public_bus_ferry_data_merged.csv`: Full GTFS join output  
- `public_bus_data_cleaned.csv`: Duplicate-free, no empty-column version  
- `03-stations.csv`: U-Bahn stations (name, lat/lon)  
- `08-connections-no-dupes.csv`: U-Bahn station–to–station links
-  [`Google Drive Folder →`](Google-Drive-Link.url): Contains raw transit data snapshots.

## Transformation Summary
1. Clean & normalize all GTFS and U–Bahn string fields  
2. Join GTFS tables into one consolidated transport table  
3. Spatially align stops with neighborhoods (optional)  
4. Export for use in dashboards, APIs, and spatial tools  
