# Berlin Pools — Hybrid Refactoring (Legacy + OSM)

This repository/notebook implements a **hybrid enrichment pipeline** for Berlin swimming pools, keeping the **legacy source as the backbone** and using **OpenStreetMap (OSM)** to fill a few selected attributes (when present). The final deliverable is a clean CSV suitable for downstream layers and a mirrored table in PostgreSQL.

---

## Decision at a glance

- **OSM does not fully replace the legacy source today** (names are sparse; technical specs like length/depth/lanes are largely missing).
- **Best choice: hybrid enrichment.** Keep **legacy** as the canonical base; use **OSM** to supplement:
  - `website` (fallback if legacy is missing or to confirm the same URL),
  - `opening_hours` (when present),
  - `wheelchair` accessibility flag,
  - small **address fixes** and alternative names.
- **Specs (length/depth/lanes)** remain **out of scope** for now — keep them in a **separate specs table/backlog** until a reliable source is secured.

**Observed coverage (current snapshot):**
- Most OSM enrichment fields are empty or ≤ **~1%** filled.
- `wheelchair` ~ **14%** coverage → useful as an accessibility indicator.
- `website` ~ **9%** coverage, but the **primary** website data is the official Bäder pages (via baederleben.de); OSM is a **secondary fallback**.

---

## What this notebook does

1. **Loads the legacy dataset** exported from the Bäder search:  
   - Source: <https://baederleben.de/abfragen/baeder-suche.php>  
   - Expected local file: **`baederleben_berlin.csv`** (place it next to the notebook).

2. **(Optional) Fetches/uses OSM data** (Overpass via `osmnx`) to build a **named public pools subset**:  
   - Intermediate: **`osm_public_named.csv`**.

3. **Geocodes / maps to Berlin administrative geographies** using **lor_ortsteile.geojson**:
   - Input: **`lor_ortsteile.geojson`** (place next to the notebook).
   - Produces `district`, `district_id`, `neighborhood`, `neighborhood_id` via spatial join and/or reverse geocoding cache (**`reverse_geocode_cache.csv`**).

4. **Cleans, de-duplicates, and merges** legacy + OSM using rules:
   - Deduplicate by **normalized name** + **proximity** (≈ `DIST_M = 250` meters).
   - Exclude **private** entries (`access=private`).
   - Prefer legacy for core identity fields; use OSM to **fill gaps or confirm** values.
   - Keep IDs and codes as **strings**.

5. **Writes the final CSV**: **`pools_master_minimal.csv`**.

6. **Publishes to PostgreSQL** (append mode) into: **`berlin_source_data.pools_refactored`**.

---

## Quick start

1. Download the latest CSV from the Bäder search and save it as **`baederleben_berlin.csv`** next to the notebook:  
   <https://baederleben.de/abfragen/baeder-suche.php>
2. Place **`lor_ortsteile.geojson`** in the same folder as the notebook.
3. (Optional) If you want to refresh OSM, run the OSM cells (Overpass via `osmnx`). This will produce **`osm_public_named.csv`**.
4. Run the notebook **top → bottom**.
5. Collect outputs:
   - **CSV:** `pools_master_minimal.csv`
   - **DB table:** `berlin_source_data.pools_refactored` (PostgreSQL)

> If you change filenames/paths, update the configuration constants at the top of the notebook.

---

## Inputs & outputs

### Required inputs
- **`baederleben_berlin.csv`** — exported from baederleben.de (official Bäder links).
- **`lor_ortsteile.geojson`** — Berlin LOR administrative boundaries (Ortsteile).

### Optional/Intermediate
- **`reverse_geocode_cache.csv`** — improves speed and consistency of address/LOR mapping.
- **`osm_public_named.csv`** — OSM subset (public pools with names).

### Final outputs
- **`pools_master_minimal.csv`** — master file for downstream layers.
- **PostgreSQL table:** **`berlin_source_data.pools_refactored`** (append mode).

Columns typically include (subject to availability):
- Identity & geography: `pool_id`, `name`, `pool_type`, `street`, `postal_code`, `district`, `district_id`, `neighborhood`, `neighborhood_id`, `latitude`, `longitude`, `open_all_year`.
- OSM enrichments (when present): `website`, `opening_hours`, `wheelchair`, `osm_id`.

---

## Environment & dependencies

Python packages used in the notebook (non‑exhaustive):
```
pandas, numpy, geopandas, shapely, osmnx, geopy, sqlalchemy, nbformat, nbconvert, unicodedata
```
Additional runtime notes:
- **PostgreSQL** with the `psycopg2` driver (`postgresql+psycopg2`).
- **openpyxl** may be required if you export to Excel anywhere.
- Ensure `gdal`/`fiona` stack is available for `geopandas` (if missing, install via your OS/conda).

Install example (pip):
```bash
pip install pandas numpy geopandas shapely osmnx geopy sqlalchemy psycopg2-binary openpyxl
```

---

## Database publishing

The notebook appends to **`berlin_source_data.pools_refactored`** using `pandas.DataFrame.to_sql(...)`.

```

If you are connecting through an **SSH tunnel**, ensure the tunnel is open and that your `DB_HOST/DB_PORT` match the local forward (e.g., `localhost:5433`).

---

## Merge logic & data quality rules

- **Backbone:** legacy fields remain authoritative for `name`, `pool_type`, address, and geography.
- **OSM additions (when present):** `website` (fallback), `opening_hours`, `wheelchair`, minor address/alt name fixes, `osm_id` for traceability.
- **De‑duplication:** normalized names + spatial proximity (≈ **250 m**).
- **Exclusions:** ignore `access=private` pools.
- **IDs/dtypes:** keep ID fields as **strings** (e.g., `district_id`, `neighborhood_id`). LOR codes follow Berlin’s official scheme.
- **Auditing:** keep OSM identifiers to support future refresh/comparisons.

---

## Known limitations

- **OSM sparsity/volatility:** enrichment fields (hours/website/wheelchair) are incomplete and may change. We use OSM as **enrichment only** and log coverage for refreshes.
- **Specs (length/depth/lanes):** not reliably available in OSM; parked in a separate track until a trusted upstream is found.
- **Websites:** prefer official Bäderbetrieb pages (source via baederleben.de); only use OSM as fallback.

---

## Refresh strategy

- Re‑run the notebook quarterly to refresh OSM and update coverage metrics (`wheelchair`, `website`, `opening_hours`).
- Keep a small report (counts/coverage) to decide when/if the strategy should change (e.g., if OSM fill rates improve).

---

## Troubleshooting

- **`ModuleNotFoundError: No module named 'sqlalchemy'`** → `pip install sqlalchemy` (and `psycopg2-binary`).
- **Excel writer errors** → install `openpyxl`.
- **`read_sql` interface errors** → ensure you pass a **SQLAlchemy engine** to `pandas.read_sql`, not a raw DB-API cursor.
- **Missing files** → verify that `baederleben_berlin.csv` and `lor_ortsteile.geojson` are in the same folder as the notebook, or update paths.
- **No rows in DB** → check your `schema`, connection string, and whether the table was created successfully.

---

## Attribution & licensing

- **OpenStreetMap** data © OpenStreetMap contributors, licensed under **ODbL 1.0**.
- **Bäder search** data is accessed via <https://baederleben.de/abfragen/baeder-suche.php>, which links to official Bäder pages.
- **LOR (Ortsteile)** data: please respect the licensing terms provided by the data publisher (e.g., Geoportal Berlin).

---

## Changelog (project‑level)

- **v1.0** — Initial hybrid pipeline: legacy backbone + OSM enrichment; LOR mapping; CSV + Postgres publish (`pools_master_minimal.csv`, `berlin_source_data.pools_refactored`).

