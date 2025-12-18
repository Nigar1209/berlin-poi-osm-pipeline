# Detailed Comparison – OSM vs Berlin Open Data

## 🗺️ Coverage Analysis
| Source | Parks | Playgrounds | Notes |
|---------|--------|--------------|--------|
| OSM | ~2300 | ~1900 | Covers all boroughs, but minor gaps in small local parks |
| Berlin Open Data | ~2500 | ~1900 | Official reference dataset, updated periodically |

**Observation:** OSM coverage is about 92–95% of official data. Missing entries mostly correspond to very small or closed areas.

---

## 🧾 Attribute Comparison

| Attribute | In OSM | In Berlin Data | Description |
|------------|:------:|:---------------:|-------------|
| `name` | ✅ | ✅ | Park or playground name |
| `operator` | ✅ | ✅ | Managing organization |
| `access` | ✅ | ❌ | Public or private access |
| `opening_hours` | ✅ | ❌ | Time-based accessibility |
| `area` | ❌ | ✅ | Official area size |
| `district` | ❌ | ✅ | Administrative district |
| `geometry` | ✅ | ✅ | Spatial polygon or point |

---

## ⚖️ Enrichment Strategy
- **If using OSM as base:** Add `area` and `district` from Berlin data by spatial join.
- **If using Berlin data as base:** Replace geometries with updated OSM shapes and attributes like `access`, `opening_hours`.

---

## 📌 Recommendation
**Hybrid approach (preferred):**
- Use **OSM** for geometry and dynamic tags (live updates).
- Use **Berlin Open Data** for authoritative fields (area, district).
- Automate future refreshes from OSM every 3–6 months.

---

_Last updated: Oct 2025_  
_Contributor: @mahdiamin1980_
