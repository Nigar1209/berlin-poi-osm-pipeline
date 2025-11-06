# Government Offices Data Strategy for Berlin

## Definition
By **Government Offices**, we mean official public sector entities providing administrative, civic, and public services at various levels (local, regional, or federal). This includes city halls, municipal service centers (Bürgerämter), licensing offices, social service departments, tax offices, employment agencies, and other government agencies accessible to the public.

---

## Goal: Create a Government Offices Table

### Procedures
- 🏛️ **Step 1: Research & Data Modelling**  
- 🛠️ **Step 2: Data Transformation**  
- 🧩 **Step 3: Populate Database**

---

## Result: Selected 18 Key Columns

1. `office_id` (primary_key)
2. `district_id` (foreign_key)
3. `name`
4. `office_type`
5. `street`
6. `housenumber`
7. `postal_code`
8. `district`
9. `neighborhood`
10. `phone_number`
11. `email`
12. `website`
13. `services_offered`
14. `appointment_required`
15. `openinghours`
16. `wheelchair_accessible`
17. `latitude`
18. `longitude`
19. `coordinate`

---

## Planned Schema: `government_offices_in_berlin`

| Column Name | Data Type | Description | Example |
|-------------|-----------|-------------|---------|
| `office_id` | `int` | Unique OSM ID | 98765432 |
| `district_id` | `int` | Unique district ID | 11011011 |
| `name` | `text` | Office name | Bürgeramt Mitte |
| `office_type` | `text` | Type of government office | citizen_service_center |
| `street` | `text` | Street name | Karl-Marx-Allee |
| `housenumber` | `text` | House number | 31 |
| `postal_code` | `text` | Postal code | 10178 |
| `district` | `text` | District name | Mitte |
| `neighborhood` | `text` | Local neighbourhood name | Alexanderplatz |
| `phone_number` | `text` | Contact phone | +49 30 90269-0 |
| `email` | `text` | Contact email | buergeramt@ba-mitte.berlin.de |
| `website` | `text` | Website URL | www.berlin.de/ba-mitte |
| `services_offered` | `text` | Services provided | ID cards, residence registration, certificates |
| `appointment_required` | `text` | Appointment necessity | yes |
| `openinghours` | `text` | Opening hours string | mo-fr 08:00-18:00, th 08:00-20:00 |
| `wheelchair_accessible` | `text` | Accessibility info | yes |
| `latitude` | `float` | Latitude coordinate | 52.5219 |
| `longitude` | `float` | Longitude coordinate | 13.4132 |
| `coordinate` | `text` | Geometry type | Point |

---

## Table Creation Logistic

* **Keep a unique primary key:** `office_id`
* **Remove columns with more than 85% missing values**
* **Retain address-related information:** `street`, `housenumber`, `postal_code`
* **Retain contact information:** `phone_number`, `email`, `website`
* **Retain key attributes:** `office_type`, `services_offered`, `appointment_required`, `wheelchair_accessible`, `openinghours`
* **Add location hierarchy fields:** `district_id` (used as foreign key), `district`, `neighborhood`
* **Add geographic information:** `latitude`, `longitude`, `coordinate`

---

## Examples of Government Office Names in Berlin

### Citizen Service Centers (Bürgerämter):
- Bürgeramt Mitte
- Bürgeramt Friedrichshain-Kreuzberg
- Bürgeramt Pankow
- Bürgeramt Charlottenburg-Wilmersdorf

### District Offices (Bezirksämter):
- Bezirksamt Mitte
- Bezirksamt Tempelhof-Schöneberg
- Bezirksamt Neukölln

### Specialized Government Offices:
- Finanzamt Berlin-Mitte (Tax Office)
- Kraftfahrzeug-Zulassungsstelle (Vehicle Registration Office)
- Standesamt Mitte (Registry Office)
- Jobcenter Berlin Mitte (Employment Agency)
- Sozialamt Friedrichshain-Kreuzberg (Social Services Office)
- Ausländerbehörde Berlin (Immigration Office)
- Landesamt für Bürger- und Ordnungsangelegenheiten (State Office for Citizens and Regulatory Affairs)
- Senatsverwaltung für Finanzen (Senate Department for Finance)

## 🏛️ Step 1: Research & Data Modelling

**PR Branch Name:** `government-offices-data-modelling`

This notebook documents the process for Step 1 of the "Government Offices in Berlin" project:

* **1.1 Data Source Discovery**
* **1.2 Modelling & Planning**
* **1.3 Prepare the /sources Directory**
* **1.4 Review**

### Goal:
* Identify and document relevant data sources.
* Select the key parameters for our use case.
* Draft the planned table schema.
* Plan cleaning and transformation steps before database population.

---

## 1.1 Data Source Discovery

**Topic:** Government Offices in Berlin

### Main source:

* **Name:** OpenStreetMap (OSM) via OSMnx library
* **Source and origin:** Public crowdsourced geospatial database
* **Update frequency:** Continuous (dynamic)
* **Data type:** Dynamic (API query using multiple tags:)
  * `office=government`
  * `office=administrative`
  * `amenity=townhall`
  * `amenity=public_building`
  * `office=employment_agency`
* **Reason for selection:**
  * Covers government offices across Berlin (Bürgerämter, Bezirksämter, Finanzämter, etc.)
  * Includes coordinates, names, addresses, office types, and other useful attributes
  * Open, free, and easy to query programmatically
  * Supports filtering by German administrative office names

### Optional additional sources:

* **Name:** Berlin Open Data Portal (daten.berlin.de)
* **Source and origin:** Official Berlin city government
* **Update frequency:** Varies per dataset
* **Data type:** Static or semi-static (download as CSV/GeoJSON)
* **Possible usage:** Enrich with official administrative boundaries, appointment systems, or extra metadata
* **Specific datasets to consider:**
  * Bürgeramt locations and services
  * District administrative boundaries
  * Public service facility catalogs

### Enrichment potential:

* Neighborhood/district info from Berlin shapefiles (GeoJSON)
* Office type classification (citizen services, tax offices, social services, etc.)
* Appointment requirement information
* Service categories offered by each office
* Linking to local amenities for spatial context
* Integration with official Berlin.de government service data

---

*Note: Government offices in Berlin include Bürgerämter (citizen service centers), Bezirksämter (district offices), Finanzämter (tax offices), Standesämter (registry offices), Jobcenter (employment agencies), Ausländerbehörde (immigration offices), and other administrative entities.*
