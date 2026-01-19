## Documentation Gap Analysis

Detailed column-by-column comparison (undocumented fields, constraints, data types etc.):

🔗 [View Spreadsheet: final_Documentation](https://docs.google.com/spreadsheets/d/1sKv6KyHt4UwgK85ud2Lsxf01Bdv0AiiU1brqYr1V4jc/edit?usp=sharing)
# Database vs Documentation Gap Analysis

## 1. DB vs. Documentation Mapping Analysis

### 1.1 Tables in Both (Matching)

The following tables are consistent across the database and documentation:

- banks
- long_term_listings
- playground
- schools
- districts
- milieuschutz_protection_zones
- parking_spaces
- short_term_listings
- exhibition_centers
- museums
- pools
- social_clubs_activities
- galleries
- neighborhoods
- post_offices
- ubahn
- hospitals
- parks
- public_artworks
- universities
- kindergartens
- pharmacies
- religious_institutions
- venues
- government_offices
- libraries
- petstores

### 1.2 Only in Database (Missing from Documentation)

Tables that exist in the live database but are **not** yet documented:

- bus_stops
- spaetis
- food_markets
- supermarkets
- tram_stops
- gyms
- doctors
- night_clubs
- sbahn
- recycling_points
- malls
- bike_lanes
- dental_offices

> **Note**:  
> Some tables (bus_stops, tram_stops) appear to be split versions of the documented `bus_tram_stops`.  
> `dental_offices` is marked "In Progress" in documentation but already exists in DB.

### 1.3 Only in Documentation (Missing from Database)

Tables that are documented but **do not exist** in the current database:

- bus_tram_stops
- districts_pop_stat
- regional_statistics
- vet_clinics
- crime_statistics
- land_prices
- rent_stats_per_neighborhood

> **Note**: `bus_tram_stops` was most likely replaced by separate `bus_stops` + `tram_stops` tables.

### Summary Table

| Category                     | Count |
|------------------------------|-------|
| Common Tables (Match)        | 27    |
| Only in Database             | 14    |
| Only in Documentation        | 7     |
| **Total in Database**        | **41**|
| **Total in Documentation**   | **34**|

## 2. Evaluation of Documentation Quality

- **Comprehensive Table Descriptions**: All currently defined entities have functional descriptions
- **Attribute-Level Documentation**: All documented tables have comprehensive column descriptions
- **Schema Constraints**: Some tables are missing constraint documentation  
  → see detailed gap analysis in the attached spreadsheet

## 3. Identified Issues & Technical Gaps

- Many active database columns are **undocumented**  
  → comprehensive list prepared in the attached spreadsheet

## 4. Definitions for Some Undocumented Columns

| Table name                        | Column                   | Description                                                                 |
|-----------------------------------|--------------------------|-----------------------------------------------------------------------------|
| banks                             | geometry                 | A spatial data object (Point) representing the exact geographic coordinates of the bank |
| banks                             | neighborhood             | The name or ID of the neighborhood where the bank is located               |
| dental_offices                    | geometry                 | A spatial data object representing the geographic location of the dental practice |
| dental_offices                    | district                 | The administrative district assigned to the dental office location         |
| dental_offices                    | neighborhood             | The specific neighborhood associated with the office address               |
| districts                         | neighborhood             | A list or reference of neighborhoods contained within the larger district boundaries |
| exhibition_centers                | geometry                 | Spatial coordinates (typically a Point or Polygon) for the exhibition facility |
| exhibition_centers                | district                 | The administrative district containing the center                          |
| exhibition_centers                | neighborhood             | The local neighborhood name for the facility                                |
| galleries                         | geometry                 | Geographic coordinates identifying the location of the art gallery         |
| galleries                         | district                 | The district designation for the gallery's address                          |
| galleries                         | neighborhood             | The specific neighborhood where the gallery operates                        |
| kindergartens                     | full_address             | The complete street address, including building number and postal code     |
| kindergartens                     | geometry                 | Spatial data object representing the kindergarten's physical location      |
| kindergartens                     | neighborhood_id          | A unique identifier linking the facility to a specific neighborhood record |
| long_term_listings                | name                     | The title or descriptive name of the long-term rental listing              |
| long_term_listings                | neighborhood_id          | Unique identifier for the neighborhood where the listing is located        |
| milieuschutz_protection_zones     | latitude                 | The north-south coordinate of a central point within the protection zone   |
| milieuschutz_protection_zones     | longitude                | The east-west coordinate of a central point within the protection zone     |
| milieuschutz_protection_zones     | neighborhood             | The name of the neighborhood falling under protection regulations          |
| milieuschutz_protection_zones     | neighborhood_id          | Unique identifier for the protected neighborhood area                       |
| museums                           | district                 | The administrative district where the museum is situated                    |
| museums                           | geometry                 | Spatial object (Point) for the museum's entrance or center point           |
| museums                           | neighborhood             | The specific local neighborhood for the museum                              |
| pharmacies                        | geometry                 | Spatial coordinates for the pharmacy location                               |
| pharmacies                        | neighborhood_id          | Unique identifier linking the pharmacy to a neighborhood                    |
| pools                             | geometry                 | Spatial object representing the location of the swimming pool facility     |
| pools                             | neighborhood             | The neighborhood name for the pool location                                 |
| pools                             | neighborhood_id          | Unique identifier for the associated neighborhood                           |
| public_artworks                   | district                 | The administrative district where the artwork is installed                 |
| public_artworks                   | geometry                 | Spatial coordinates (Point) of the artwork's location                      |
| public_artworks                   | neighborhood             | The local neighborhood where the artwork can be found                       |
| schools                           | geometry                 | Spatial data object representing the school campus or entrance             |
| schools                           | neighborhood             | The neighborhood associated with the school's catchment area               |
| schools                           | neighborhood_id          | Unique identifier for the neighborhood                                      |
| short_term_listings               | geometry                 | Spatial coordinates for the short-term rental property                     |
| short_term_listings               | neighborhood             | The neighborhood name where the short-term listing is located              |
| ubahn                             | name                     | The name of the U-Bahn station                                              |
| ubahn                             | geometry                 | Spatial object (Point) representing the station location                   |
| ubahn                             | neighborhood_id          | Unique identifier for the neighborhood the station serves                  |
| universities                      | geometry                 | Spatial coordinates (typically Point or Polygon) for the university campus |
| universities                      | neighborhood_id          | Unique identifier for the neighborhood                                      |
| venues                            | geometry                 | Spatial coordinates for the event or performance venue                     |
| venues                            | neighborhood_id          | Unique identifier for the neighborhood                                      |
| venues                            | operating_hours_category | A classification indicating the venue's standard opening/closing schedule  |
| post_offices                      | district                 | The administrative district for the post office branch                     |
| post_offices                      | geometry                 | Spatial object representing the physical post office location              |
| post_offices                      | neighborhood             | The neighborhood associated with the branch                                 |
| libraries                         | geometry                 | Spatial data object representing the geographic location of the library    |
| religious_institutions            | district                 | The administrative district for the institution                             |
| religious_institutions            | neighborhood             | The neighborhood where the religious institution is located                |

## 5. Documented Findings – Current Status Classification

**Incomplete but acceptable for current requirements:**

- banks
- hospitals
- public_artworks
- districts
- kindergartens
- religious_institutions
- exhibition_centers
- milieuschutz_protection_zones
- schools
- galleries
- museums
- ubahn
- neighborhoods
- pharmacies
- universities
- parking_spaces
- pools
- venues
- post_offices
- government_offices
- libraries
- long_term_listings
- short_term_listings

### Critical Observations

- **Primary Key deficiencies**:
  - `kindergartens` – no primary key defined in documentation
  - `neighborhoods` – no primary key + `neighborhood_id` documented as nullable

- **Inconsistencies**:
  - Different data types used for `opening_hour`, `wheelchair`, `phone_number` across tables

- **Completed tables** (good state):
  - parks
  - playgrounds
  - social_clubs_activities
  - petstores

## 6. Proposed Documentation Improvements

| Current Table Name       | Recommended Table Name       | Rationale                             |
|---------------------------|-------------------------------|---------------------------------------|
| long_term_listings        | long_term_rental_listings     | Improved clarity                      |
| short_term_listings       | short_term_rental_listings    | Improved clarity                      |
| playgrounds               | public_playgrounds            | Reduces ambiguity                     |
| ubahn                     | ubahn_subway                  | Better comprehension for int. users   |

### Technical Suggestions

- `short_term_listings.is_shared`: currently `int2` (binary) → **recommended**: convert to proper `boolean` type

For detailed rationale and complete column gap analysis → please refer to the **attached spreadsheet**.
