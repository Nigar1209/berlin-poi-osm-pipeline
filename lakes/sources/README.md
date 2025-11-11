# Lakes in Berlin — Sources (Step 1 Discovery)

This document lists and describes the data sources identified so far for the **Lakes in Berlin** layer.  
It includes their origin, update frequency, data type, key fields, and notes on usability.

---

##  OSM Berlin Lakes
**Origin:** Overpass Turbo / OpenStreetMap  
**URL:** https://overpass-turbo.eu  
**Query:** All water bodies within administrative boundary “Berlin”  
**Data type:** Dynamic (API / GeoJSON)  
**Update frequency:** Continuous (community maintained)  
**Relevant fields:** `name`, `natural`, `water` (lake | pond | reservoir), geometry  
**File saved as:** `osm_berlin_lakes.geojson`  
**License:** ODbL (OpenStreetMap Foundation)  
**Notes:** Excellent spatial coverage, but naming and type tags are not always consistent.

---

##  Dämeritzsee in-situ Data (FRED – IGB Berlin)
**Origin:** Freshwater Research and Environmental Database (FRED)  
**URL:** [https://fred.igb-berlin.de/data/package/169](https://fred.igb-berlin.de/data/package/169)  
**Dataset:** Dämeritzsee in-situ measurements (1992–1993)  
**Parameters:** Temperature, Conductivity, Depth, pH, Oxygen saturation, Oxygen concentration, Secchi depth  
**Data type:** Static (one-time in-situ dataset)  
**Update frequency:** Historical (archived)  
**Contact:** thomas.hintze@igb-berlin.de  
**License:** All rights reserved – contact IGB Berlin for reuse permission  
**Notes:** High-quality limnological measurements for potential depth / water-quality enrichment.

---

##  Next Planned Sources
| Source | URL / Portal | Status |
|:---|:---|:---|
| Gewässerkarte Berlin (WFS) | Berlin Open Data Portal | To be added |
| ALKIS Gewässer / Vegetation | Berlin Open Data Portal | To be added |
| EEA WISE Surface Water Bodies | EEA Datasets | To be added |
| Wasserportal Berlin (Time Series) | https://wasserportal.berlin.de | To be added |

tes from IGB data (by name and location).
