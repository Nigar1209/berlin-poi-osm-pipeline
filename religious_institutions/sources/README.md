# Religious Institutions – Data Discovery & Modelling

## 🎯 Objective
The goal of this task was to create the foundation for the **Religious Institutions Data Layer** as part of *EPIC 2: Data Foundation & Frontend Context*.  
This layer represents all publicly accessible places of worship and religious activity across different faiths within **Berlin**.

---

## 🧭 Data Source Discovery (Step 1.1)
**Primary Source:** [OpenStreetMap (OSM)](https://www.openstreetmap.org) via the **OSMnx API**  
**Tag used:** `amenity=place_of_worship`  
**Location:** Berlin, Germany  
**Update frequency:** Continuous (community-driven, real-time API)  
**Data type:** Dynamic – can be refreshed using the Overpass API or OSMnx library  

---

## 🧱 Modelling & Planning (Step 1.2)
### 🗂️ Key Attributes Defined

- `id` – Unique OpenStreetMap identifier  
- `name` – Institution name  
- `religion` – Religious affiliation (e.g., christian, muslim, jewish, buddhist)  
- `denomination` – Sub-branch (e.g., catholic, orthodox, protestant)  
- `building` – Building type or structure information  
- `addr:street`, `addr:housenumber`, `addr:postcode`, `addr:suburb`, `addr:city` – Address components  
- `operator` – Organization or managing entity  
- `website` – Official website URL  
- `contact:phone`, `contact:email` – Contact information  
- `wheelchair` – Accessibility information  
- `service_times`, `opening_hours` – Worship or visiting times (if available)  
- `heritage`, `historic` – Cultural or historical significance  
- `geom_point` – Point geometry derived from OSM geometry  
- `latitude`, `longitude` – Extracted coordinates (EPSG:4326)  
- `source` – Origin of the data entry (OSM attribution)

### 🧮 Data Preparation Steps
1. Loaded Berlin data via OSMnx with the tag `place_of_worship`  
2. Converted geometries into points (`representative_point()`)  
3. Extracted `latitude` and `longitude`  
4. Reset index to create internal `religious_id`  
5. Selected and renamed relevant columns  
6. Checked missing values and computed missing percentage per column  
7. Reviewed top religious groups (frequency analysis)  
8. Exported dataset in both **CSV** and **GeoJSON** format  

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
| Remove empty columns (>85% missing) | Keep only relevant fields |
| Standardize religion & denomination | e.g., lowercase, merge similar values |
| Combine address fields | into a single formatted string |
| Create unique IDs | using DataFrame index (`religious_id`) |
| Add district mapping | via spatial join with `districts` table |
| Deduplicate entries | based on `name + coordinates` |
| Ensure consistent CRS | EPSG:4326 for all geometries |

---

## 🧰 Output Files
| File | Format | Description |
|------|---------|-------------|
| `religions_raw.csv` | CSV | Cleaned, flattened version for database ingestion |
| `religions_raw.geojson` | GeoJSON | Geospatial representation for mapping and visualization |
| `religious_institutions_data_modelling.ipynb` | Notebook | Full workflow: data discovery, cleaning, modeling|

---

## 📜 Data Licensing
Data provided by **OpenStreetMap contributors**, licensed under the [Open Data Commons Open Database License (ODbL) v1.0](https://opendatacommons.org/licenses/odbl/1-0/).

---

## ✅ Next Steps
- Integrate `district_id` and `neighborhood_id` via spatial joins  
- Normalize and categorize religious denominations  
- Prepare transformation script for database insertion (`Step 2`)  
- Extend documentation with data enrichment sources (e.g., Wikidata)
