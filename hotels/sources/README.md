# Hotels – Berlin | Data Source Research

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
