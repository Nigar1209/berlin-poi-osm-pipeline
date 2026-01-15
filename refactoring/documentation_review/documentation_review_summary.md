Find the google document in the next link: https://docs.google.com/document/d/1YiIJGN-C4xAxfeNXf8wKbdyD9N9qm3LqDfNtI_ZrHa8/edit?usp=sharing

Find link of the spreadsheet for the purpose reference of the final gap analsis work:- https://docs.google.com/spreadsheets/d/1sKv6KyHt4UwgK85ud2Lsxf01Bdv0AiiU1brqYr1V4jc/edit?usp=sharing

# DB vs. Documentation Mapping Analysis

[cite_start]This summary outlines the consistency and discrepancies between the live database (DB) environment and the current project documentation[cite: 1].

---

## 1. Table Synchronization Status

### 1.1 Tables in Both (Matching)
[cite_start]The following **27 tables** are consistent across both the database and documentation[cite: 2, 3, 15]:

| | | | |
| :--- | :--- | :--- | :--- |
| Banks | long_term_listings | playground | schools |
| districts | milieuschutz_protection_zones | parking_spaces | short_term_listings |
| exhibition_centers | museums | pools | social_clubs_activities |
| galleries | neighborhoods | post_offices | ubahn |
| hospitals | parks | public_artworks | universities |
| kindergartens | pharmacies | religious_institutions | venues |
| government_offices | libraries | petstores | |

### 1.2 Only in Database (Missing from Documentation)
[cite_start]The following **14 tables** exist in the live environment but have not been recorded in the documentation yet[cite: 5, 6, 15]:

| | | | |
| :--- | :--- | :--- | :--- |
| bus_stops | spaetis | food_markets | supermarkets |
| tram_stops | gyms | doctors | night_clubs |
| sbahn | recycling_points | malls | bike_lanes |
| dental_offices | | | |

> [cite_start]**Note:** Some tables (like `bus_stops` and `tram_stops`) appear to be split versions of the documented `bus_tram_stops`[cite: 8]. [cite_start]The table `dental_offices` is active in the DB despite being marked "In Progress" in documentation[cite: 9].

### 1.3 Only in Documentation (Missing from Database)
[cite_start]The following **7 tables** are documented but do not currently exist in the database[cite: 10, 11, 15]:

* [cite_start]`bus_tram_stops` (Likely replaced by the separate bus/tram tables) [cite: 13]
* `districts_pop_stat`
* `regional_statistics`
* `vet_clinics`
* `crime_statistics`
* `land_prices`
* `rent_stats_per_neighborhood`

---

## 2. Evaluation of Documentation Quality

* [cite_start]**Comprehensive Table Descriptions:** All entities currently defined in the documentation include functional descriptions[cite: 17].
* [cite_start]**Attribute-Level Documentation:** Comprehensive descriptions are provided for all defined columns within the documented tables[cite: 18].
* [cite_start]**Schema Constraints Discrepancy:** A subset of tables documented does not include constraints[cite: 19].
* [cite_start]**Detailed Gap Analysis:** Please refer to the attached spreadsheet for a detailed analysis of these missing constraints[cite: 20].

---

## 3. Identified Issues & Technical Gaps

### Undocumented Schema Attributes
[cite_start]Several active database columns lack corresponding documentation[cite: 22]. [cite_start]A comprehensive list of these undocumented fields has been compiled in the attached spreadsheet for immediate review[cite: 23].

### Proposed Definitions for Undocumented Columns
[cite_start]The following definitions are proposed to resolve identified gaps[cite: 25, 26]:

| Table | Column | Description |
| :--- | :--- | :--- |
| **banks** | geometry | Spatial data object (Point) representing exact geographic coordinates. |
| | neighborhood | The name or ID of the neighborhood where the bank is located. |
| **dental_offices** | geometry | Spatial data object representing the geographic location of the practice. |
| | district | The administrative district assigned to the dental office location. |
| | neighborhood | The specific neighborhood associated with the office address. |
| **districts** | neighborhood | A list or reference of neighborhoods within the district boundaries. |
| **exhibition_centers** | geometry | Spatial coordinates (Point or Polygon) for the facility. |
| | district | The administrative district containing the center. |
| **kindergartens** | full_address | Complete street address, including building number and postal code. |
| | neighborhood_id | Unique identifier linking the facility to a specific neighborhood record. |
| **long_term_listings** | name | The title or descriptive name of the long-term rental listing. |
| | neighborhood_id | Unique identifier for the neighborhood where the listing is located. |
| **ubhan** | name | The name of the U-Bahn station. |
| | geometry | Spatial object (Point) representing the station location. |
| **venues** | operating_hours_category | Classification indicating the venue's standard schedule. |
| **post_offices** | district | The administrative district for the post office branch. |

---

## 4. Documented Findings

[cite_start]Based on the gap analysis, the following tables are categorized as **incomplete but acceptable** for current requirements[cite: 29, 30]:

| | | |
| :--- | :--- | :--- |
| banks | hospitals | public_artworks |
| districts | kindergartens | religious_institutions |
| exhibition_centers | milieuschutz_protection_zones | schools |
| galleries | museums | ubahn |
| neighborhoods | pharmacies | universities |
| parking_spaces | pools | venues |
| post_offices | government_offices | libraries |
| long_term_listings | short_term_listings | |

> [cite_start]**Completed Tables:** `parks`, `playgrounds`, `social_clubs_activities`, and `petstores` are marked as complete[cite: 36].

---

## 5. Critical Observations & Technical Suggestions

### Primary Key Deficiencies
* **kindergartens:** Lacks a defined primary key in the documentation[cite: 32].
* [cite_start]**neighborhoods:** Lacks a primary key; additionally, `neighborhood_id` is documented as nullable[cite: 33].

### Inconsistencies & Data Types
* **Standardization:** Data types for `opening_hour`, `wheelchair`, and `phone_number` vary across tables and should be standardized[cite: 34, 35].
* **Optimization:** In `short_term_listings`, the `is_shared` column uses `int2`. [cite_start]It is recommended to convert this to **boolean**[cite: 40, 41].

### Recommended Naming Improvements
| Current Table Name | Recommended Table Name | Rationale |
| :--- | :--- | :--- |
| `long_term_listings` | `long_term_rental_listings` | [cite_start]Improved clarity[cite: 38]. |
| `short_term_listings` | `short_term_rental_listings` | [cite_start]Improved clarity[cite: 38]. |
| `playgrounds` | `public_playgrounds` | [cite_start]Reduces ambiguity[cite: 38]. |
| `ubahn` | `ubahn_subway` | [cite_start]International comprehension[cite: 38]. |

---
[cite_start]*For a detailed rationale regarding these findings, please refer to the attached spreadsheet[cite: 42].*