# Data Sources for Schools in Berlin

This directory documents the discovered data sources for the Berlin schools data layer.
For each source we record origin, update frequency, data type, and relevant fields.

## Source Overview

| Key                | Source                                         | Link                                                                                          | Update frequency                          | Data type                                | Licence          | Short description                                  |
|--------------------|-----------------------------------------------|-----------------------------------------------------------------------------------------------|-------------------------------------------|-------------------------------------------|------------------|----------------------------------------------------|
| SCHULEN_WMS        | Schools [WMS], Berlin Open Data Portal      | http://daten.berlin.de/datensaetze/schulen-wms-ddb39227                    | Irregular, at least roughly yearly        | Dynamic (WMS geo service / API)          | DL-DE Zero 2.0   | Official geodata layer of all school locations     |
| SCHULVERZEICHNIS_WEB | School Directory & School Profiles Berlin   | https://www.bildung.berlin.de/Schulverzeichnis/                                              | At least yearly per school year, ongoing  | Dynamic (web application, HTML)          | Website T&Cs     | Detailed information for each school (profiles etc.) |
| OSM_SCHOOLS        | OpenStreetMap  `amenity=school` (Berlin)     | https://overpass-turbo.eu/ (with a query restricted to Berlin)                               | Continuous (community-maintained)         | Dynamic (Overpass API / OSM export)      | ODbL             | Crowd-sourced geodata for school locations         |
| WIKIDATA_SCHOOLS   | Wikidata – schools in Berlin                  | https://www.wikidata.org/                                                                    | Continuous (community-maintained)         | Dynamic (SPARQL endpoint / knowledge graph) | CC0            | Optional metadata enrichment (founding year, links) |

---

## 1. SCHULEN_WMS for Schools in [WMS] Berlin Open Data Portal

- **Origin**  
  Berlin Open Data Portal, dataset “Schulen [WMS]” provided by the Senate Department for Education, Youth and Family.

- **Link**  
  http://daten.berlin.de/datensaetze/schulen-wms-ddb39227

- **Update frequency**  
  According to the portal’s metadata the dataset is updated when required (irregular, but relatively up to date).  
  For modelling we treat it as a reasonably current official snapshot.

- **Data type**  
  WMS geo service (dynamic map/layer service) in WMS.

- **Relevant fields (examples)**  
  - School name  
  - School type (e.g. primary school, secondary school, vocational, special needs)  
  - Address (street, house number, postal code, locality)  
  - District  
  - Public vs. private  
  - Contact information (phone, website, email – if available)  
  - Geometry / coordinates (point or polygon)

- **Planned usage**  
  Primary base dataset for all school locations in Berlin.  
  Will be spatially matched to existing `districts` / `neighborhoods` tables using geometry.

---

## 2. SCHULVERZEICHNIS_WEB – School Directory & School Profiles

- **Origin**  
  Official school directory (“Schulverzeichnis & Schulporträts”) of the Senate Department for Education, Youth and Family.

- **Link**  
  https://www.bildung.berlin.de/Schulverzeichnis/

- **Update frequency**  
  The UI allows selection by school year (e.g. 2025/26).  
  Data is maintained at least yearly and updated on an ongoing basis.

- **Data type**  
  Dynamic web application (HTML/JavaScript).  
  There is no direct bulk download!

- **Relevant fields (examples)**  
  - School name and potentially a school ID/code  
  - School type  
  - District and locality  
  - Offered languages  
  - Special profiles and programmes (e.g. all-day school, music focus)  
  - Notes on accessibility (e.g. wheelchair access, inclusive settings)  
  - Contact details (address, phone, email, website)

- **Planned usage**  
  Enrichment and validation of the WMS layer.  
  Source for additional feature columns such as taught languages, specific profiles, and accessibility flags.

---

## 3. OSM_SCHOOLS for OpenStreetMap (filtered by `amenity=school`)

- **Origin**  
  OpenStreetMap (OSM) database, filtered to `amenity=school` within the Berlin area.

- **Links**  
  - Tag documentation: https://wiki.openstreetmap.org/wiki/Tag:amenity%3Dschool  
  - Overpass-Turbo: https://overpass-turbo.eu/

- **Update frequency**  
  Continuous and the OSM is maintained by a global volunteer community.

- **Data type**  
  Dynamic geodata, retrievable via Overpass API or other OSM export mechanisms.

- **Relevant fields (examples)**  
  - `name` (school name)  
  - `amenity=school`  
  - `addr:*` (street, house number, postcode, city, neighbourhood)  
  - `operator` / `operator:type` (e.g. public, private, religious)  
  - `isced:level`, `grades`, `min_age`, `max_age` (if present)  
  - `contact:*` (phone, website, email)  
  - `school:language` / `language:*` (instruction language, if present)  
  - Geometry (point or polygon)

- **Planned usage**  
  Plausibility checks and optional enrichment of coordinates and attributes.  
  Can help to fill gaps or cross-check official data, especially for smaller or newly created schools.

---

## 4. WIKIDATA_SCHOOLS in Wikidata

- **Origin**  
  Wikidata items representing schools located in Berlin.

- **Link**  
  https://www.wikidata.org/ (with SPARQL queries to retrieve schools in the federal state of Berlin).

- **Update frequency**  
  Continuously maintained by the Wikidata community.

- **Data type**  
  Dynamic knowledge graph, accessible via SPARQL endpoint.

- **Relevant fields (examples)**  
  - Label (school name)  
  - Coordinates (point)  
  - Instance of / type of institution (e.g. school, international school)  
  - Inception / founding year  
  - Links to Wikipedia articles  
  - Official website links

- **Planned usage**  
  Optional enrichment of the school layer, e.g. adding founding year, international school flags, or external links.  
  Not expected to be complete, but useful for specific subsets of schools.
