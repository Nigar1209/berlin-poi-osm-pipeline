# Data Sources: Food & Weekly Markets (Berlin)

This document outlines the research, data sources, and planned transformation strategy for the "Food & Weekly Markets" data layer.

## 1. 🎯 Final Data Strategy

Our strategy is a **hybrid approach** designed to get the best from all available sources. We will use the rich, structured data from **OpenStreetMap (OSM) as our primary "base layer"** and then use official and curated sites as "validation layers" to clean, validate, and fill gaps.

1.  **Build Base Layer (from OSM):** We'll use our optimized Overpass API query to get a broad, rich dataset with `lat/lon`, `type`, `name`, `operator`, `accessibility`, and standardized `opening_hours`.
2.  **Validate (with Official Feeds):** We'll cross-reference our OSM data with the official `berlin.de` GeoJSON feeds. This is critical for **filtering out-of-scope** ("Trödelmärkte") and **old** data (e.g., past Christmas markets) from OSM.
3.  **Fill Gaps (with Curated Lists):** We will scrape the `visitBerlin` and `wochenmarkt-deutschland.de` pages to get a "master check-list" of names/addresses. We'll use this list to find any final missing markets (e.g., "Onkel Toms Hütte," which was not found in OSM) and add them to our dataset.



---

## 2. 🗂️ Identified Data Sources

### Primary Source (Base Layer)

* **Source:** OpenStreetMap (OSM)
* **Origin:** Overpass API (`https://overpass-api.de/api/interpreter`)
* **Update Frequency:** Real-time (Dynamic)
* **Data Type:** Dynamic API
* **Licensing:** ODbL (Open Database License). Requires attribution to "© OpenStreetMap contributors".
* **Relevant Fields:** `amenity`, `xmas:feature`, `name`, `opening_hours`, `website`, `operator`, `wheelchair`, `addr:*`, `lat/lon` (from geometry).

### Official Validation Sources (Ground Truth)

These are live data feeds used to validate our OSM data.

* **Source 1: Official Weekly Markets**
    * **Origin:** `berlin.de` (Senatsverwaltung für Wirtschaft, Energie und Betriebe)
    * **Link:** `https://www.berlin.de/sen/web/service/maerkte-feste/wochen-troedelmaerkte/index.php/index/all.geojson?q=`
    * **Update Frequency:** **Irregular / Periodically (Dynamic)**
    * **Last Verified Update:** **November 2025**
    * **Data Type:** Dynamic GeoJSON Feed
    * **Licensing:** Creative Commons Attribution (CC BY 3.0 DE).

* **Source 2: Official Christmas Markets**
    * **Origin:** `berlin.de` (Senatsverwaltung für Wirtschaft, Energie und Betriebe)
    * **Link:** `https://www.berlin.de/sen/web/service/maerkte-feste/weihnachtsmaerkte/index.php/index/all.geojson?q=`
    * **Update Frequency:** **Annual / Seasonal (Dynamic)**
    * **Last Verified Update:** **November 2025**
    * **Data Type:** Dynamic GeoJSON Feed
    * **Licensing:** Creative Commons Attribution (CC BY 3.0 DE).

### Curated Validation Sources (Gap-Fillers)

These are HTML pages we will scrape to create a "check-list" of popular markets. They are not a primary data source but are used to find gaps in our data.

* **Source 3: `visitBerlin` (various pages)**
    * **Links:**
        * `https://www.visitberlin.de/en/covered-markets`
        * `https://www.visitberlin.de/en/weekly-markets`
        * `https://www.visitberlin.de/en/street-food-berlin`
    * **Data Type:** Static (HTML, requires scraping)

* **Source 4: `wochenmarkt-deutschland.de`**
    * **Link:** `https://www.wochenmarkt-deutschland.de/wochenmarkt-berlin/`
    * **Data Type:** Static (HTML, requires scraping)

---

## 3. 💡 Key Research Findings

1.  **Official Data is Messy:** Inspection of the official GeoJSON feeds revealed:
    * All relevant data is nested in a `properties.data` object.
    * Opening times are highly inconsistent and provided as unstructured free text (e.g., `oeffnungszeiten` vs. `tage`/`zeiten`), requiring custom parsers.
    * The weekly market file includes "Trödelmärkte" (flea markets), which are out of scope and must be filtered out.

2.  **OSM is Superior but Imperfect:**
    * OSM provides a richer, more structured dataset (e.g., standardized `opening_hours` tag).
    * However, it contains old data (like past Christmas markets) and has gaps (like "Wochenmarkt Onkel Toms Hütte"), proving that it **must** be validated.

3.  **OSM Query Optimization:** Initial research of the OSM Wiki and Taginfo provided candidate tags. These were then tested against the Berlin data by systematically commenting out blocks to create an optimized query:
    * `vending=street_food` was removed, as it returned no relevant results (street food markets are tagged `amenity=marketplace`).
    * `xmas:feature=market` was found to be mapped only as `nodes`.
    * `amenity=food_court` was mapped as `nodes` or `ways`.
    * `amenity=marketplace` was the most complex, using `nodes`, `ways`, and `relations`.

---

## 4. 🚀 Final Optimized Overpass Query

This is the final, optimized query used to generate `OSM-berlin_markets.json`.

```overpassql
[out:json][timeout:60];
/* Get all market types for Berlin */
area["name"="Berlin"]->.searchArea;
(
  /* 1. Marketplaces: Can be nodes, ways, or relations */
  node["amenity"="marketplace"](area.searchArea);
  way["amenity"="marketplace"](area.searchArea);
  relation["amenity"="marketplace"](area.searchArea);

  /* 2. Food Halls: Mapped as nodes or ways */
  node["amenity"="food_court"](area.searchArea);
  way["amenity"="food_court"](area.searchArea);
  
  /* 3. Christmas Markets: Mapped ONLY as nodes */
  node["xmas:feature"="market"](area.searchArea);
);
/* output geometry for ways/relations */
out center;
```

---

## 5. 🔗 Planned Transformation & Integration

1.  **Ingestion:** Download/run all sources and save raw files in this directory (e.g., `OSM-berlin_markets.json`).
2.  **Normalization (OSM):**
    * Load `OSM-berlin_markets.json`.
    * Create a `market_type` column based on the source tag (`marketplace`, `food_court`, `xmas_market`).
    * Parse the structured `opening_hours` tag.
3.  **Validation (Official Feeds):**
    * Load `official_weekly_markets.geojson`. Filter out "Trödelmärkte".
    * Load `official_xmas_markets.geojson`.
    * Cross-reference both with the OSM data. Add an `is_official: true` flag to OSM matches. Filter out any OSM entries (like old Xmas markets) that are *not* in the official lists.
4.  **Gap-Filling (Curated Lists):**
    * Scrape the `visitBerlin` and `wochenmarkt-deutschland.de` pages for a list of market `(name, address)`.
    * Compare this check-list to our validated OSM data.
    * For any missing markets, geocode their address (using Nominatim) to get a `lat/lon` and add them to the dataset.
5.  **Database Connection (Spatial Join):**
    * This is the final step to connect to the existing database.
    * We will load the `lor_ortsteile.geojson` file.
    * For every market in our final, clean dataset, we will use its `(latitude, longitude)` coordinates to perform a **spatial join** against the LOR polygons.
    * This join will identify the correct `OTEIL` (neighborhood) and `BEZIRK` (district) for each market, allowing us to populate the `neighborhood_id` and `district_id` foreign keys in our new `food_markets` table.
