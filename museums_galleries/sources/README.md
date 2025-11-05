# 🏛️ Museums & Galleries in Berlin  
## 📌 Step 1: Research & Data Modelling

---

## 🔍 Data Source Discovery

- **Primary Source:** [OpenStreetMap (OSM)](https://www.openstreetmap.org) via the `osmnx` Python library  
  - **Why OSM?** Open, free, and continuously updated. Includes location, address, and metadata for museums, galleries, public artworks, and exhibition centers in Berlin.  
  - **Query Filters Used:**  
    - `tourism`: `["museum", "gallery", "artwork"]`  
    - `amenity`: `"exhibition_center"`  
  - **Data Type:** Dynamic (queried via API)  
  - **Update Frequency:** Continuous  

- **Additional Sources (not yet integrated):**  
  - [Berlin Open Data Portal](https://daten.berlin.de) – for optional enrichment  
  - [Deutsche Digitale Bibliothek REST API](https://www.deutsche-digitale-bibliothek.de/content/api) – requires API key  
  - [Kulturgutdigital – Berliner OpenGLAM-Daten](https://openglam.berlin.de) – cultural metadata

---

## 🗂️ Raw File Creation

- Generated separate raw files for each of the four tags (`museum`, `gallery`, `artwork`, `exhibition_center`)  
- Currently evaluating whether to merge into a single table or maintain separate datasets for artworks and exhibition centers  
- Identifying common columns for potential joins

---

## ✅ To Do

### 🔧 Column Selection
- Plan to remove columns with **≥ 75% missing data**

### 🧭 Schema Planning
- Add `latitude` and `longitude` to the cleaned dataset

### 🔄 Transformation Strategy
- Rename columns for consistency across layers  
- Align naming conventions with the ERD (Entity Relationship Diagram)

---

## 🛠️ Tools & Technologies

- **Languages & Libraries:**  
  - Python  
  - `osmnx`, `geopandas`, `pandas`  
- **Environment:**  
  - Jupyter Notebook (for analysis and exploration)

