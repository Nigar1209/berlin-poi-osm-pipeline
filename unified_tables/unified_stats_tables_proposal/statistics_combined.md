
# Statistics Combined Tables

⚠️ Note: Data types are not consistent across all 6 tables.  
Not all columns are used in examples — can be added later.

---

## Why 3 Tables Instead of One
Splitting into 3 tables is cleaner and more practical:

- Some columns are highly detailed/sparse (rooms, schools, pools, crime subcategories).  
- Some tables are yearly, others static (demographics, land prices).  
- Queries on subsets (e.g., rent or crime) are faster without scanning irrelevant columns.  

✅ Benefits:
- Faster queries (ignore detailed tables when not needed).  
- Easier updates (append yearly data without touching static).  
- Cleaner schema (avoid hundreds of columns).  
- Supports analysis at multiple levels (overview vs. detailed vs. time-series).  

---

## 1️⃣ Master Table: `district_overview`
High-level snapshot per district per year.
- Contains core demographics, total crime score, total area, living space, and other high-level indicators.
- When a table doesn’t have a year, you treat its values as valid for all years in the other tables.

**Key Columns**
- `district_id` (PK)  
- `year` (PK if yearly)  
- `population_total`, `male_population`, `female_population`  
- `foreigners_pct`, `germans_pct`, `single_pct`, `married_pct`  
- `total_crimes`, `crime_score`  
- `total_area_ha`, `living_space_per_resident`  
- `avg_land_value_per_sqm`, `avg_rent_per_m2`  

**Static vs. Time-Varying**
- Time-varying: `regional_statistics`, `land_prices`, `rent_stats_per_neighborhood`  
- Static: `districts_pop_stat`, `district_level_aggregated`  
Static tables are “broadcast” across all years.

**Reasons**
- Focus on “core, high-level metrics”
- The tables have hundreds of columns, many of which are very detailed (room breakdowns, individual crime types, school types, pool types, etc.).
- If we put everything in one table, it becomes massive and unwieldy, making queries slower and harder to maintain.
- The master table serves as a compact “hub”, giving a quick overview of each district for any year.
- Detailed attributes like crime subtypes, number of pools, schools by type, rooms by size were pushed to JSON or separate child tables.
- This keeps the master table query-friendly, especially for dashboards or high-level analytics.
- Example: if you want average crime score vs average land value, you don’t need hundreds of extra columns cluttering the table.
- The primary key is district_id + year → supports time-series analysis.

---

## 2️⃣ Detailed Stats Table: `district_details`
Granular attributes (often sparse/categorical).  
Can be stored as JSON for flexibility.

**Examples**
- Room distribution  
- School counts  
- Hospital beds, pools, venues  
- Land area breakdown  
- Transport density  

**Recommended JSON Columns**
- `room_distribution_json`  
- `school_stats_json`  
- `pool_stats_json`  
- `healthcare_json`  
- `transport_json`  
- `other_details_json`  

---

## 3️⃣ Time-Series Table: `district_time_series`
Granular yearly/category stats (crime, rent, etc.).

**Key Columns**
- `district_id` (FK → `district_overview`)  
- `year` (PK)  
- `crime_type`, `crime_cases`, `frequency_100k`  
- `median_net_rent_per_m2`, `mean_net_rent_per_m2`, `number_of_cases`  

---
## Schema Hierarchy

- 📁 district_overview
  - 📄 district_details (1-to-1 or 1-to-many if detailed per year)
  - 📊 district_time_series (1-to-many, yearly / category level)


## Schema Overview

![alt text](png_files/statistics_schema.png)


