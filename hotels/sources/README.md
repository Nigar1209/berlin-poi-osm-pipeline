
# STEP 1 Hotels – Berlin | Data Source Research


## Purpose
This document catalogs candidate data sources for hotel and accommodation data in Berlin,
as part of #605 (Research & Data Source Discovery).

## OpenStreetMap (OSM)

- **Provider**: OpenStreetMap
- **Link**: https://www.openstreetmap.org
- **Access method**: OpenStreetMap API / Overpass API (via tools such as OSMnx)
- **Geographic coverage**: Global (includes Berlin)
- **Update frequency**: Continuous (community-maintained)
- **Data type**: Dynamic
- **License**: Open Database License (ODbL)
- **Relevant tags for hotels**:
  - tourism=hotel
  - tourism=hostel
  - tourism=guest_house
  - tourism=apartment / aparthotel
- **Relevant fields (high-level)**:
  - name
  - accommodation type (via tourism tag)
  - latitude / longitude / geometry
  - address-related tags (if present)
  - contact / website tags (if present)

**Notes**:
OpenStreetMap provides geospatial point and polygon data for accommodation-related POIs.
Coverage and attribute completeness may vary by location and contributor activity.


## Berlin Open Data Portal

- **Provider**: Land Berlin
- **Link**: https://daten.berlin.de
- **Access method**: Dataset download (varies by dataset)
- **Geographic coverage**: Berlin
- **Update frequency**: Dataset-specific
- **Data type**: Mostly static or periodically updated
- **License**: Dataset-specific
- **Relevant fields (high-level)**:
  - aggregated tourism metrics (counts, time series)

**Research notes**:
The Berlin Open Data Portal was searched using keywords such as
"hotel", "tourismus", "Unterkunft", and "Übernachtungen".
Available datasets focus on aggregated tourism statistics
(e.g. number of overnight stays) rather than listings of
individual hotels or accommodations.

**Conclusion**:
No POI-level dataset listing individual hotels with location
information was identified. The portal is therefore not suitable
as a primary source for hotel POI data.


## VisitBerlin (Official Tourism Source)

- **Provider**: visitBerlin / Berlin Tourismus & Kongress GmbH
- **Link**: https://www.visitberlin.de
- **Access method**: Website content; no public data download identified
- **Geographic coverage**: Berlin
- **Update frequency**: Unknown
- **Data type**: Proprietary
- **License**: Proprietary (content reuse subject to terms and conditions)

**Research notes**:
VisitBerlin provides curated information about hotels and accommodations
via its website. No publicly documented open dataset or API for downloading
or reusing hotel listings was identified during research.

**Conclusion**:
VisitBerlin is not suitable as a direct data source for hotel POIs due to
licensing and lack of public data access. It may be used for reference only.


## Wikidata

- **Provider**: Wikimedia Foundation
- **Link**: https://www.wikidata.org
- **Access method**: SPARQL endpoint
- **Geographic coverage**: Global (includes Berlin)
- **Update frequency**: Continuous (community-maintained)
- **Data type**: Dynamic
- **License**: CC0
- **Relevant fields (high-level)**:
  - official name
  - description
  - website
  - identifiers

**Research notes**:
Wikidata contains structured information about notable hotels and
accommodations, often linked to Wikipedia articles. Coverage is incomplete
and biased toward well-known entities.

**Conclusion**:
Wikidata is not suitable as a primary source for hotel POIs, but can be used
as a supplementary source to enrich selected entries (e.g. official website,
descriptions, identifiers) where OSM data is incomplete.


## Commercial Booking Platforms (Reference Only)

Examples include Booking.com, Hotels.com, and Expedia.

**Research notes**:
Commercial booking platforms provide extensive hotel listings and rich
attribute data. However, their content is proprietary and subject to
restrictive terms of service. No open datasets or reusable APIs for hotel
POI data were identified.

**Conclusion**:
Booking platforms are not suitable as data sources for this project due
to licensing and reuse restrictions. They are excluded from further
consideration.

## European Data Portal

- **Provider**: European Union / Publications Office
- **Link**: https://data.europa.eu
- **Access method**: Web portal with API and SPARQL
- **Geographic coverage**: EU member states including Germany
- **Update frequency**: Continuous
- **Data type**: Meta-catalog of open data
- **License**: Mostly CC-BY-4.0; dataset-specific varies

**Research notes**:
The portal aggregates metadata for open datasets from multiple national and local catalogs.
No specific hotel POI dataset was immediately apparent, but it is a central place to search for open datasets relating to accommodations if such datasets are published.

**Conclusion**:
While not a direct hotel POI dataset, this portal indexes potentially relevant datasets and provides unified access mechanisms.


## Open Data / Knowledge Graph Project (Germany Tourism)

- **Provider**: German National Tourist Board / state tourism organizations
- **Link**: https://open-data-germany.org (project description)
- **Access method**: Project initiative, not dataset download
- **Geographic coverage**: Germany (incl. major cities)
- **Update frequency**: Ongoing
- **Data type**: Knowledge graph vision / linked open data
- **License**: Depends on constituent sources

**Research notes**:
This initiative aims to standardize and integrate tourism data including accommodation POIs across Germany, but does not yet provide an immediately usable dataset for Berlin hotels.

**Conclusion**:
Worth noting as an overarching project that may yield future opportunities; not directly usable at this time.


## Planned Transformation (High-Level)

Based on the identified data sources and downstream requirements, the following
high-level transformation steps are expected in later stages:

- Standardization of naming and categorization across sources
- Validation and normalization of geospatial data
- Deduplication of overlapping records within and across sources
- Selective enrichment from supplementary sources where primary data is incomplete
- Alignment with the standardized POI schema used by other layers
- Exclusion of records already covered by existing POI layers

Detailed transformation logic and implementation will be addressed in Step 2 (#606)
(Data Transformation & Preprocessing).


## Step 2 – Data Transformation & Enrichment (#606)

This section documents the data transformation and enrichment work performed in Step #606,
building on the data source research outlined above.

### Base Dataset

- **Primary source**: OpenStreetMap (OSM)
- **Scope**: Hotel and accommodation-related POIs in Berlin
- **Geometry**: Standardized to point geometries (EPSG:4326)
- **Identifier strategy**:
  - OSM identifier retained as stable `id`
  - Provenance tracked via `data_source` and `source_ids`

OSM serves as the authoritative base layer. All additional sources are used in a
*supplementary, non-overwriting* manner.

---

### Amenities & Accessibility

**Amenities**

Raw OSM tags were analyzed to identify potential enrichment opportunities
(e.g. Wi-Fi, air conditioning, breakfast, restaurant, spa).

**Findings**
- Amenity tagging is highly inconsistent across records
- Coverage varies significantly by contributor and location
- No reliable open external enrichment source was identified

**Conclusion**  
Amenities were derived **only from existing OSM tags**. No external enrichment was applied.

**Accessibility**

Accessibility information (e.g. wheelchair access, elevators) was derived directly from
OSM tags where present. No external enrichment source was identified.

---

### Contact Information (Phone, Website, Email)

Contact information was derived and standardized using **OpenStreetMap tags only**.

**Fields**
- `phone`
- `website`
- `email`

**Method**
- Relevant OSM contact-related tags (e.g. `contact:phone`, `phone`, `contact:website`, `website`,
  `contact:email`, `email`) were consolidated into unified contact fields.
- When multiple tag variants existed, values were coalesced into a single canonical column
  per contact type.
- Common string artifacts (e.g. empty strings) were cleaned during normalization.

**External enrichment assessment**
- No reliable open external data source providing contact information for Berlin hotels
  was identified.
- Wikidata coverage for contact details was found to be sparse and inconsistent.

**Conclusion**
Contact information remains **purely OSM-derived**.

---
### Room Count

- Column: `rooms`
- Source: OpenStreetMap only

**Findings**
- Room count is sparsely populated in OSM
- No reliable open dataset providing room counts for Berlin hotels was identified
- Commercial platforms were excluded due to licensing restrictions

**Conclusion**  
Room count remains a **pure OSM-derived field** with no external enrichment.

---

### Wikidata Enrichment – Star Rating (P10290)

Wikidata was used as a **supplementary enrichment source** for hotel star ratings.

**Rationale**
- Structured hotel rating property (P10290)
- CC0 license allows reuse
- Partial but valuable coverage for well-known hotels

Wikidata was **not** used as a primary source and **never overwrites existing OSM values**.

**Enrichment process (Cell 57)**

1. Only hotels with a known `wikidata_id` were considered  
2. Only records with missing `star_rating` were eligible  
3. A SPARQL query was executed against the Wikidata endpoint  
4. Results were exported as a CSV snapshot and stored under `hotels/sources/`  
5. Star ratings were merged without overwriting existing values  
6. Provenance was recorded in `data_source` and `source_ids`

https://query.wikidata.org/

**SPARQL query used**

SELECT ?hotel ?hotelLabel ?ratingLabel  
(xsd:integer(REPLACE(?ratingLabel, "^(\\d+).*", "$1")) AS ?stars)  
WHERE {  
  VALUES ?hotel {  
    /* Wikidata IDs collected in cell 57 */  
  }  
  ?hotel wdt:P10290 ?rating .  
  ?rating rdfs:label ?ratingLabel .  
  FILTER(LANG(?ratingLabel) = "en")  
  FILTER(REGEX(?ratingLabel, "^[0-9]+-star"))  

  SERVICE wikibase:label {  
    bd:serviceParam wikibase:language "en".  
  }  
}

**Query output**  
The result of this query is stored as a static snapshot at  
`hotels/sources/wikidata_stars_candidates.csv`.

---

### Address Enrichment (Nominatim)

Address components were enriched using **Nominatim reverse geocoding** based on each hotel’s
latitude and longitude.

**Method**
- For each hotel with missing address components, a reverse geocoding request was sent to
  the Nominatim API.
- The response `address` object was parsed to extract street-level information.
- Street name was resolved using the following fallback order when available:
  `road` → `pedestrian` → `footway` → `path`.

**Fill policy**
- Only missing values were filled.
- Existing OSM address data was never overwritten.

**Fields enriched**
- `street`
- `house_number`
- `postal_code`

After enrichment, a full `address` string was constructed from the available components
for downstream compatibility where required.

---

### Administrative Area Enrichment (LOR)

Administrative area information was enriched using **official Berlin LOR (Lebensweltlich orientierte Räume) Ortsteile** boundaries.

**Data source**
- File: `mapping/lor_ortsteile.geojson`
- Provider: Land Berlin
- Content: Official polygon geometries for Berlin districts and neighborhoods (Ortsteile)

**Method**
- Hotel point geometries were spatially joined with the LOR Ortsteile polygons.
- Each hotel was assigned to the polygon it falls within.
- Official naming and coding conventions from the LOR dataset were preserved.

**Fields enriched**
- `district` — Berlin district name
- `neighborhood` — Berlin neighborhood (Ortsteil) name
- `district_id` — Official Berlin district code
- `neighborhood_id` — Official neighborhood identifier

---

### Deduplication

Duplicate records can arise due to multiple OSM elements (e.g. node + way)
or closely located representations of the same hotel.

**Deduplication rule**
- Same normalized hotel name
- Within **10 meters** spatial distance

Deduplication was applied **after all enrichment steps** to avoid data loss.

---

## Final Dataset Schema

**Bold columns are mandatory according to #606.**

| Column | Description |
|------|-------------|
| **id** | Stable unique identifier derived from OSM |
| **name** | Hotel or accommodation name |
| **hotel_type** | Accommodation type (hotel, hostel, guest house, etc.) |
| star_rating | Official star rating (1–5), from OSM or Wikidata |
| amenities | Derived list of amenities from OSM tags |
| accessibility | Accessibility features derived from OSM tags |
| rooms | Number of rooms (if available from OSM) |
| phone | Contact phone number |
| website | Official website URL |
| email | Contact email address |
| address | Full address string (constructed) |
| street | Street name |
| house_number | House number |
| postal_code | Postal code |
| **latitude** | Latitude coordinate (WGS84) |
| **longitude** | Longitude coordinate (WGS84) |
| **geometry** | Point geometry (EPSG:4326) |
| **district** | Berlin district name |
| **neighborhood** | Berlin neighborhood (Ortsteil) |
| **district_id** | Official Berlin district code |
| neighborhood_id | Official neighborhood identifier |
| **data_source** | Source provenance summary |
| **source_ids** | Source-specific identifiers |

---

## Transformation Summary (High-Level)

The Berlin hotels dataset was produced by:

- Extracting hotel-related POIs from OpenStreetMap  
- Normalizing core attributes and geometry  
- Deriving amenities and accessibility from raw OSM tags  
- Enriching selected fields using Wikidata and Nominatim  
- Assigning official administrative areas using Berlin LOR data  
- Tracking provenance for all enrichment steps  
- Deduplicating records using name normalization and 10 m proximity  
- Aligning the final output with the standardized POI schema  

