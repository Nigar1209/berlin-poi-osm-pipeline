# 🏞️ Berlin Parks & Playgrounds Data Layer
This project focuses on modeling, transforming, and integrating data related to **parks and playgrounds in Berlin**. It is part of a broader effort to map and enrich recreational zones across the city, enabling better insights for urban planning, public services, and neighborhood enrichment.

---

## 📌 Project Overview
We follow a three-step workflow:

1. **Research & Data Modelling**
2. **Data Transformation**
3. **Database Population**

The focus is currently on two types of recreational zones:

- **Public Parks** (`Grünanlagen`)
- **Playgrounds** (`Spielplätze`)

---

## 🧪 Step 1: Research & Data Modelling
**🔀Branch Name:** `layer-data-modelling`

### 1.1 🔍 Data Source Discovery
We identified two key datasets from the Berlin city government's official portal:

### 🟢 Public Parks (Grünanlagen)
- **Source:** [Berlin Open Data - Parks Layer](https://fbinter.stadt-berlin.de/fb/index.jsp?loginkey=alphaDataStart&alphaDataId=s_gruenanlagenbestand@senstadt)
- **Origin:** Berlin Senate Department for Urban Development
- **Update Frequency:** Unknown (likely updated periodically)
- **Data Type:** Static (available as downloadable GIS files)

### 🥅 Playgrounds (Spielplätze)
- **Source:** [Berlin Open Data - Playgrounds Layer](https://fbinter.stadt-berlin.de/fb/index.jsp?loginkey=alphaDataStart&alphaDataId=s_spielplatzbestand@senstadt)
- **Origin:** Berlin Senate Department for Urban Development
- **Update Frequency:** Unknown
- **Data Type:** Static

---

### 1.2 Modelling & Planning

### 🟢 Public Parks (Grünanlagen)

- **Key Parameters Selected**
  - `Name`
  - `Type`
  - `Neigborhood`
  - `Geometry` (Polygon or Point Coordinates)
  - `Area in m²`
  - `Planning Area`
  - `Dedicated`

### 🟢 Public Parks (Grünanlagen)

- **Key Parameters Selected:**
  - `Playground Name`
  - `Type of Playground`
  - `Neigborhood`
  - `Locality`
  - `Area (total and net in m² )`
  - `Constrution Year`
  - `Coordinates` (latitude, longitude)
  

- **Schema Integration Plan:**

    - Link new data to existing `neighborhoods` and `listings` tables using coordinates and district names.

- **📐 Draft Schema:**

```sql 
parks_and_playgrounds (
  id SERIAL PRIMARY KEY,
  playground_name TEXT,
  green_area_type TEXT,
  neigborhood TEXT,
  locality TEXT,
  latitude FLOAT,
  longitude FLOAT,
  area_sqm FLOAT,
  planning_area_name TEXT,
  source TEXT,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
)
```
- **Known Data Issues:**
    - Inconsitent or missing names
    - Unstandardized District names
    - Possible GPS inaccurancies
- **Transformation Plan**
    - Normalize names and types
    - Clean GPS data
    - Match district names to internal references
    - Convert coordinate system (EPSG: 25833 to WGS84 if needed)

---

**1.3** 📂 `/sources` **Directory**
  
  - Raw data files and metadata are included in the `/sources` folder
`/sources/README.md` **Includes:**
    - Discriptions of each data source
    - Planned transformation steps
