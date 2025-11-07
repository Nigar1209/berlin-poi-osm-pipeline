# 1.1 Data Source Discovery 

Topic: Libraries in Berlin
---

### Main source Details: OpenStreetMap (OSM)

The primary data for this research is sourced from the OpenStreetMap (OSM) project due to its comprehensive and current nature.

| Field | Detail |
| :--- | :--- |
| **Source and Origin** | OpenStreetMap (OSM), accessed via the OSMnx Python library or Overpass API. This is a crowd-sourced global map database. |
| **Update Frequency** | **Dynamic (Near-Real-Time)**. The underlying OSM database is updated instantly by mappers. The data accessible via the Overpass API (and thus OSMnx) is typically minutes to hours behind the main database. |
| **Data Type** | **Dynamic**. Requires an ongoing API/scraper (like OSMnx or Overpass) to ensure the most current data. |
| **Relevant Data Fields** | **Spatial & Comprehensive Metadata** |
| | **Geographic:** `geometry` (lat/lon, outlines) |
| | **Identification:** `name`, `ref:isil`, `wikidata`, `wikipedia` |
| | **Contact/Address:** `addr:street`, `addr:housenumber`, `addr:postcode`, `website`, `phone` |
| | **Operations:** `amenity=library`, `operator`, `operator:type` (crucial for distinguishing public/university/private), `opening_hours` |
| | **Services/Accessibility:** `wheelchair`, `toilets:wheelchair`, `internet_access`, `service:copy`, `books:language:*`, `room:group_study` |
---

#### ✅ Reason for Source Selection

OpenStreetMap (OSM) was selected as the **primary data source** over other potential sources (e.g., static government catalogs) for the following reasons:

1.  **Rich Metadata & Functionality:** OSM provides extensive and detailed tags like `operator:type` (crucial for distinguishing public vs. university libraries) and service tags like `service:copy`, which are often missing in basic administrative data.
2.  **Comprehensive Spatial Data:** It includes both points (`node`) and area outlines (`way`), essential for accurate spatial analysis (e.g., calculating service areas or floor space).
3.  **Data Currency:** The near-real-time updates ensure the analysis is based on the most recent operational reality of the Berlin library network.

---

## 📊 Source 2: Berlin Open Data Portal (daten.berlin.de)

The analysis confirms this source contributes **highly authoritative location data**, including unique public transport details. http://www.berlin.de/sen/kultur/_assets/statistiken/kultureinrichtungen_alle.xlsx , https://daten.berlin.de/datensaetze/standorte-institutionell-geforderter-kultureinrichtungen

| Field | Detail | Unique Contribution to the Project |
| :--- | :--- | :--- |
| **Source and Origin** | **Datenportal Berlin** (Open Data Portal of the State of Berlin). Data from the Senate Chancellery – Cultural Affairs. | **Most authoritative list of government-funded institutions**, ensuring inclusion of key state/district libraries. |
| **Update Frequency** | **Infrequent/Annual**. The dataset itself was last modified in 2016 (based on available metadata) but represents a relatively stable list of institutions. A newer, separate "Ausleihen" (loans) dataset for Pankow exists, but the location data is static. | Necessary to check the dataset page for the latest year, but generally **stable data for physical location analysis**. |
| **Data Type** | **Static Location Data**. Published as an XLSX file (convertible to CSV) that contains pre-calculated geographical coordinates. | Provides a **direct Lat/Lon point-of-interest geometry** for immediate use, eliminating the need for Geocoding. |
| **Key Relevant Data Fields** | **Official Location & Transport Info** | |
| **Geographic** | `BREITENGRAD` (Latitude), `LAENGENGRAD` (Longitude) | Directly usable **coordinates**, eliminating the need for Geocoding. |
| **Identification** | `EINRICHTUNG` (Name), `STRASSE` (Street), `PLZ` (Postcode), `ORT` (City) | **Official, standardized address fields** for cross-referencing. |
| **Operations** | `SPARTE` (Category - crucial for filtering to only "Libraries"), `OEPNV` (Public Transport Information) | **Unique Value:** Explicit **Public Transport connection details** for accessibility analysis. |

## Source 3: VÖBB/KOBV Public Library Network Portal

| Field | Detail |
| :--- | :--- |
| **Source and Origin** | Verbund der Öffentlichen Bibliotheken Berlins (VÖBB) or Kooperativer Bibliotheksverbund Berlin-Brandenburg (KOBV). These are the main catalogs and portals for Berlin's public and academic libraries. |
| **Update Frequency** | Daily/Weekly (Catalog Data). The underlying operational data (opening hours, contact, services) on their websites/portals is updated very frequently to reflect service changes, but a public, aggregate API for locations is less common and may require web scraping. |
| **Data Type** | Semi-Dynamic. The primary data is catalog data, but some scraping or searching of their "Locations & Hours" pages would be needed for geospatial data. |
| **Relevant Data Fields** | **Detailed Operational & Service Information** |
| **Identification** | Official name and location details |
| **Services** | Detailed programs, event listings, specific services like "Makerspace-Angebote" (Makerspace offerings), or "Digital-Zebra" (Digital assistance) that are not typically on OSM. |
| **Hours** | Specific service hours for different departments/branches (often more precise than OSM). |
