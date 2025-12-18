# Pools Data: Legacy ↔ OSM Enrichment (README)

This repository/notebook builds a **simple, repeatable pipeline** to compare your **legacy pools** dataset with **OpenStreetMap (OSM)** and produce:
1) a list of **legacy rows to enrich** with OSM attributes, and  
2) a list of **new, named OSM pools** to add to your dataset.

---

## 🧭 What’s here

- **Notebook**
  - `Refactoring_pools_layer.ipynb` — the end-to-end pipeline with clear, numbered sections and bullet-point explanations.

- **Inputs**
  - `pools.csv` — legacy source (your current list).
  - `osm_pools_wide.csv` — OSM “wide” export (either built by the notebook or provided).

- **Outputs (CSV in project root)**
  - `legacy_enrichment_list.csv` — Legacy↔OSM candidate pairs (same place) for **enrichment**.
  - `osm_new_public_named.csv` — OSM **new** pools (not matched to legacy) with a **non-empty name**.

---

## 🎯 Why I did this

- **Enrich**: OSM has strong **contact & accessibility** data (website, opening_hours, phone, wheelchair).  
- **Add**: OSM covers more venues than legacy but the data is not very reliable - open scource contains entries from any user;in result we add **named** ones that don’t match legacy.  
- **Stay clean**: We use straightforward matching rules (exact normalized name OR ≤ distance threshold) to keep results deterministic and easy to review.

---

## 🔢 Latest run snapshot 

- **Legacy rows:** 144  
- **OSM public subset:** 307  
- **Enrichment candidates (`legacy_enrichment_list`):** 47  
- **New OSM (named) to add (`osm_new_public_named`):** 24  
- **Parameters:** `DIST_M=100 m`, `STRICT_PUBLIC=False`

**Takeaway:** OSM is great for contact/accessibility; legacy is stronger on naming. Length/depth are sparse in both sources.  
**Recommendation:** **Hybrid enrichment** — keep legacy as the backbone, enrich with OSM attributes, add new named OSM pools.

---

## 🧪 What the notebook does (section-by-section)

1) **Configure paths & parameters**  
   Set file locations and knobs:
   - `DIST_M` — maximum distance (meters) to treat two records as the same place.
   - `STRICT_PUBLIC` — OSM public-access strictness (`False` = lenient).

2) **(Optional) Build OSM wide export**  
   - Geocode area, query OSM features:
     - `leisure=swimming_pool`
     - `leisure=sports_centre` filtered to `sport=swimming`
     - `leisure=swimming_area`
   - Keep useful attributes; compute accurate centroids (UTM33N → WGS84).
   - Write `osm_pools_wide.csv`.

3) **Helper functions (normalization, mapping)**  
   - Normalize names (accent fold, lowercase, strip punctuation).
   - **Coalesce OSM names** from `name`, `official_name`, `short_name`, `alt_name`, `name:*`, `brand`, `operator`.
   - Map Legacy and OSM to a **unified schema**; apply OSM public filter.

4) **Load CSVs & map**  
   Produce `legacy_db` and `osm_db` with consistent columns and normalized names.

5) **Build `legacy_enrichment_list` (candidates to enrich)**  
   - Light **blocking** via first 10 chars of `name_norm`.
   - Compute Haversine distance; keep pairs if:
     - **exact normalized name match**, OR
     - **distance ≤ `DIST_M`**.
   - Export columns include `dist_m`, `name_match` + OSM contact fields.

6) **Build `osm_new_public_named` (new & named)**  
   - From OSM public rows **not matched** above.
   - Keep only **non-empty coalesced name**.

7) **Save outputs + summary**  
   - Write **CSV only** to project root:
     - `legacy_enrichment_list.csv`
     - `osm_new_public_named.csv`
   - Print a compact run summary.

---

## ▶️ How to run

1. Place `pools.csv` (legacy) next to the notebook.  
2. If you need to (re)build OSM data:
   - In section **1**, set `MAKE_OSM_WIDE = True`.
   - Run section **2** to create `osm_pools_wide.csv`.  
   - Then set `MAKE_OSM_WIDE = False` for future runs.
3. Run the notebook from top to bottom.

**Tip:** If you already have `osm_pools_wide.csv`, keep `MAKE_OSM_WIDE=False`.

---

## 🔧 Parameters you can tune

- **`DIST_M`** (default: `100.0`)  
  - Lower (e.g., 50 m) → **fewer** distance-based matches → **more** items appear as “new”.  
  - Higher (e.g., 150 m) → **more** matches → larger enrichment set, fewer “new”.

- **`STRICT_PUBLIC`** (default: `False`)  
  - `False` (lenient): includes `""|yes|public|permissive` and treats missing as public.  
  - `True` (strict): keeps only explicit `yes|public`.

---

## 🧩 Acceptance criteria mapping

- **Script exists**: The notebook can be extracted into a script later (logic is modular and clean).
- **Defined schema output**: OSM wide export + unified mapping (name/operator/brand, lat/lon, address fields, wheelchair, opening_hours, etc.).
- **Comparison completed**:
  - **Coverage**: legacy vs OSM counts.
  - **Attributes compared**: in-memory completeness comparison for common columns; OSM-only `name_source` identified.
  - **Gaps**: length/depth are sparse; OSM excels on contact/accessibility; legacy strongest on names.
- **Decision proposal**:
  - **Hybrid enrichment**: legacy as canonical list; OSM to enrich contact/accessibility/address; treat pool specs (length/depth) as a separate sourcing task.

---

## 📦 Output semantics

- **`legacy_enrichment_list.csv`**  
  Pairs likely referring to the **same facility**; use to enrich legacy with OSM fields.  
  Helpful columns: `dist_m`, `name_match`, `website`, `opening_hours`, `wheelchair`, `phone`, `address`.

- **`osm_new_public_named.csv`**  
  **Genuinely new** OSM pools not in legacy, with a non-empty name.  
  Add these to your dataset.

