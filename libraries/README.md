# Libraries in Berlin – Data Discovery & Modelling

## 🎯 Objective
The goal of this task was to create the foundation for the **Libraries in Berlin Data Layer** as part of *EPIC 2: Data Foundation & Frontend Context*.  
This layer represents all publicly accessible libraries across Berlin, including: Public and district libraries (VÖBB network), University and research libraries or specialized archives, Mobile/digital library facilities etc

The aim is to enrich the platform **layer**, linking libraries spatially to districts and neighborhoods.

---

## 🧭 Data Source Discovery (Step 1.1)
**Primary Source:** [OpenStreetMap (OSM)](https://www.openstreetmap.org) via the **OSMnx  Python library or Overpass API**. This is a crowd-sourced global map database.
**Tag used:** `amenity=library`  
**Location:** Berlin, Germany  
**Update frequency:** Dynamic (Near-Real-Time). The underlying OSM database is updated instantly by mappers. The data accessible via the Overpass API (and thus OSMnx) is typically minutes to hours behind the main database.
**Data type:** Dynamic – can be refreshed using the Overpass API or OSMnx library  

#### ✅ Reason for Source Selection

OpenStreetMap (OSM) was selected as the **primary data source** over other potential sources (e.g., static government catalogs) for the following reasons:

1.  **Rich Metadata & Functionality:** OSM provides extensive and detailed tags like `operator:type` (crucial for distinguishing public vs. university libraries) and service tags like `service:copy`, which are often missing in basic administrative data.
2.  **Comprehensive Spatial Data:** It includes both points (`node`) and area outlines (`way`), essential for accurate spatial analysis (e.g., calculating service areas or floor space).
3.  **Data Currency:** The near-real-time updates ensure the analysis is based on the most recent operational reality of the Berlin library network.

---

## 🧱 Modelling & Planning (Step 1.2)
### 🗂️ Relevant Data Fields
| **Relevant Data Fields** | **Spatial & Comprehensive Metadata** |
| | **Geographic:** `geometry` (lat/lon, outlines) |
| | **Identification:** `name`, `ref:isil`, `wikidata`, `wikipedia` |
| | **Contact/Address:** `addr:street`, `addr:housenumber`, `addr:postcode`, `website`, `phone` |
| | **Operations:** `amenity=library`, `operator`, `operator:type` (crucial for distinguishing public/university/private), `opening_hours` |
| | **Services/Accessibility:** `wheelchair`, `toilets:wheelchair`, `internet_access`, `service:copy`, `books:language:*`, `room:group_study` |

### 🧮 Data Preparation Steps
1. Loaded Berlin data via OSMnx with the tag `library`  
2. Converted geometries into points (`representative_point()`)  
3. Extracted `latitude` and `longitude`  
4. Reset index to create internal `library_id`  
5. Selected and renamed relevant columns  
6. Checked missing values and computed missing percentage per column   
7. Exported dataset in both **CSV** and **GeoJSON** format  

---

## 🗺️ Integration Plan
The table will connect to existing layers using **geospatial joins**:  
- `district_id` → joined via polygon boundaries of Berlin districts (using geometry)  
- `neighborhood_id` → optional link to finer subdivisions  
This allows each religious institution to be associated with its correct administrative area.

---

## 🧹 Transformation & Normalization Plan
| Task | Description |
|------|--------------|
| Remove empty columns (>80% missing) | Keep only relevant fields |
| Standardization | e.g., lowercase, merge similar values |
| Combine address fields | into a single formatted string |
| Create unique IDs | using DataFrame index (`library_id`) |
| Add district mapping | via spatial join with `districts` table |
| Deduplicate entries | based on `name + coordinates` |
| Ensure consistent CRS | EPSG:4326 for all geometries |

---

## 🧰 Output Files
| File | Format | Description |
|------|---------|-------------|
| `library_raw.csv` | CSV | Cleaned, flattened version for database ingestion |
| `library_raw.geojson` | GeoJSON | Geospatial representation for mapping and visualization |
| `libraries_data_transformation.ipynb` | Notebook | Full workflow: data discovery, cleaning, modeling|

---

## 📜 Data Licensing
Data provided by **OpenStreetMap contributors**, licensed under the [Open Data Commons Open Database License (ODbL) v1.0](https://opendatacommons.org/licenses/odbl/1-0/).

---

## ✅ Next Steps
- Integrate `district_id` and `neighborhood_id` via spatial joins  
- Normalize and categorize columns  
- Prepare transformation script for database insertion (`Step 2`)  
- Extend documentation with data enrichment sources (e.g., Wikidata)
