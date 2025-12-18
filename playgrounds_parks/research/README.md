# Refactoring Playgrounds and Parks Layers (Step 1 - OSM Refactoring Strategy)

## 🎯 Goal
Refactor existing playground and park layers by using OpenStreetMap (OSM) data instead of legacy Berlin Open Data sources.

## 🧩 Workflow
1. **Fetch OSM data** using OSMnx (`leisure=park`, `leisure=playground`)
2. **Load legacy data** from Berlin Open Data (if available)
3. **Compare coverage and attributes**
4. **Identify gaps and enrichment opportunities**
5. **Propose replacement or hybrid strategy**

## 📊 Results (Summary)
| Dataset | Count | Key Attributes |
|----------|--------|----------------|
| OSM | ~2300 parks / ~1900 playgrounds | `name`, `operator`, `access`, `opening_hours` |
| Berlin Open Data | ~2500 parks / ~1900 playgrounds | `area_m2`, `district`, `object_id` |

- OSM has slightly fewer parks but generally up to date.
- Berlin data includes official area sizes and district codes.
- OSM provides dynamic, live, and crowd-updated features.

## 🧠 Decision
Use **OSM as the primary source** and enrich with a few legacy fields (`area`, `district_code`) when available.

## 📁 Files
| File | Description |
|------|--------------|
| `/scripts/osm_refactoring_parks_playgrounds.ipynb` | Main notebook to fetch and inspect OSM data |
| `/data/berlin_parks_playgrounds_osm.geojson` | Raw extracted data from OSM |
| `/research/refactoring_sources.md` | Detailed comparison of attributes |
| `/research/README.md` | Summary report and final recommendation |

## ✅ Next Steps
- Integrate final schema into the data pipeline
- Document attribute mapping
- Prepare enrichment logic for Step 2
