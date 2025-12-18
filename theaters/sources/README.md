# 🎭 Theaters & Cinemas in Berlin — Data Source Discovery

## ⚡ Executive Summary
- **Primary source**: OpenStreetMap (OSM) for `amenity=theatre|cinema` in Berlin.  
- **Supplementary sources**: Wikidata (capacity, inception, official website), LOR Berlin (districts & neighborhoods), Nominatim (address backfill), optional Wheelmap (accessibility), optional review links (Google/Yelp/Tripadvisor).  
- **Coverage reality**: Names/coordinates are strong; metadata like opening hours, genre, and emails are sparse in OSM.  
- **Outcome**: Clear enrichment plan using Wikidata + LOR; optional extras for accessibility and discovery.



## 🎯 Objective
Document authoritative, open sources to build a high-quality geospatial dataset of Berlin theatres and cinemas, and define how each source contributes to filling missing attributes.

---

## 📂 Primary Source (OSM)

**OpenStreetMap (via OSMnx / Overpass)**  
- **What**: Canonical list of venues with geometry and basic tags.  
- **Access**: OSMnx / Overpass API  
- **Example**:
  ```python
  import osmnx as ox
  tags = {"amenity": ["theatre", "cinema"]}
  gdf = ox.features_from_place("Berlin, Germany", tags)
  ```
- **Key tags**:
  - Identity: `name`, `amenity`
  - Address: `addr:street`, `addr:housenumber`, `addr:postcode`, `addr:city`
  - Contact: `phone`, `contact:phone`, `website`, `contact:website`, `email`, `contact:email`
  - Hours & details: `opening_hours`, `theatre:genre`, `theatre:type`, `cinema:type`
  - Accessibility: `wheelchair`
  - Links: `wikidata` (critical for enrichment)
- **Update cadence**: Continuous, community-maintained  
- **Format**: GeoJSON/JSON via API (reproducible queries)

---

## 📂 Supplementary Sources

### 1) Wikidata (SPARQL)
- **Purpose**: Fill metadata that’s often missing in OSM.  
- **Useful properties**:  
  - `P1083` capacity, `P571` inception, `P856` official website, `P137` operator, `P625` coordinates  
- **Join**: Prefer OSM `wikidata` tag → Wikidata `QID`; fallback to `name_key` + proximity.  
- **Example**:
  ```sparql
  SELECT ?item ?itemLabel ?coordinate_location ?capacity ?inception ?official_site WHERE {
    ?item wdt:P31/wdt:P279* wd:Q24354.     # theatre (incl. subclasses)
    ?item wdt:P131 wd:Q64.                  # located in Berlin
    OPTIONAL { ?item wdt:P1083 ?capacity. }
    OPTIONAL { ?item wdt:P571  ?inception. }
    OPTIONAL { ?item wdt:P856  ?official_site. }
    OPTIONAL { ?item wdt:P625  ?coordinate_location. }
    SERVICE wikibase:label { bd:serviceParam wikibase:language "de,en". }
  }
  ```

### 2) LOR Berlin (Administrative Boundaries)
- **Purpose**: Add `district` and `neighborhood` via spatial join.  
- **What**: LOR full + Ortsteile polygons (EPSG:4326).  
- **Join**: `within` predicate (point-in-polygon) after ensuring venue CRS=4326.

### 3) Nominatim (Reverse Geocoding) — *Optional, targeted*
- **Purpose**: Patch missing address components for edge cases.  
- **Notes**: Respect rate limits (≈1 req/sec); use only for gaps you cannot parse.

### 4) Wheelmap API — *Optional*
- **Purpose**: Enrich/validate wheelchair accessibility beyond OSM `wheelchair`.  
- **Join**: By coordinates / bounding search.

### 5) External Review Links — *Optional, outbound only*
- **Purpose**: Discovery links (no scraping): Google, Yelp, Tripadvisor search URLs.  
- **Columns**: `reviews_url_google`, `reviews_url_yelp`, `reviews_url_tripadvisor`.

---

## 📊 Baseline Coverage (Indicative)
Typical sparsity in OSM for Berlin (your exact pull may vary):

| Field             | Missing % (approx) |
|-------------------|--------------------|
| `cinema:type`     | ~99%               |
| `theatre:type`    | ~92%               |
| `opening_hours`   | ~83%               |
| `theatre:genre`   | ~82%               |
| `email`           | ~72%               |
| `phone`           | ~43%               |
| `wheelchair`      | ~26%               |
| `address`         | ~22%               |
| `website`         | ~18%               |
| `name`            | ~1–2%              |
| `amenity/geom`    | ~0%                |

---

## 📖 Proposed Final Columns by Source

| Column                 | Source(s)           | Notes |
|------------------------|---------------------|-------|
| `name`, `place_type`   | OSM (`amenity`)     | `place_type ∈ {theatre, cinema}` |
| `addr:street` / `addr:housenumber` / `addr:postcode` / `addr:city` | OSM / parsed / Nominatim | Keep raw vs. parsed for audit |
| `phone`, `email`       | OSM / Berlin data   | Coalesce `contact:*` tags |
| `website`              | OSM / Wikidata      | Prefer WD if OSM missing |
| `opening_hours`        | OSM                 | Keep OSM string as-is |
| `theatre:genre` / `theatre:type` / `cinema:type` | OSM | Often sparse |
| `wheelchair`           | OSM / Wheelmap      | Wheelmap optional enrich |
| `capacity_wd`          | Wikidata `P1083`    | Validate plausible range |
| `inception_wd`         | Wikidata `P571`     | Year or full date |
| `official_website_wd`  | Wikidata `P856`     | For coalescing with `website` |
| `operator`             | OSM / Berlin Data   | If available |
| `district` / `neighborhood` | LOR            | Spatial join |
| `lon` / `lat`          | Geometry            | From WGS84 point |
| `source`, `last_updated` | Pipeline          | Provenance + timestamp |

---

## ✅ Next Steps
- **Prepare join keys**: `wikidata_id`, normalized `name_key`, and numeric `lat_num` / `lon_num`.  
- **Enrich** via Wikidata (capacity/inception/website), coalesce with OSM.  
- **Add LOR context** via spatial join (`within`).  
- **Address QA**: parse + backfill selective gaps with Nominatim (respect rate limits).  
- **Accessibility (optional)**: add Wheelmap status.  
- **Discovery (optional)**: generate outbound review/search URLs.  
- **Document provenance**: set `source` flags (`osm`, `wd`, `osm+wd`) and `last_updated`.

---

**Licensing:**  
- OSM: ODbL (attribution required)  
- Wikidata: CC0  
- LOR Berlin: per dataset license on the Berlin Open Data portal
