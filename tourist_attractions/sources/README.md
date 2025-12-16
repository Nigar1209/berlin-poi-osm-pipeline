# Tourist Attractions Data Sources - Berlin

This directory contains information about data sources for tourist attractions in Berlin, including museums, landmarks, monuments, parks, memorials, historic sites, cultural institutions, and other points of interest commonly visited by tourists.

## Overview

This document outlines the data sources identified for building a comprehensive tourist attractions data layer for Berlin. Each source is evaluated based on its relevance, data quality, update frequency, and integration potential.

---

## Data Source 1: OpenStreetMap (OSM)

### Source and Origin
- **Source**: OpenStreetMap Overpass API
- **Data Extraction**: Query using Overpass Turbo for Berlin boundary
- **Relevant OSM Tags**:
  - `tourism=attraction`
  - `tourism=museum`
  - `tourism=gallery`
  - `tourism=artwork`
  - `tourism=viewpoint`
  - `historic=monument`
  - `historic=memorial`
  - `historic=castle`
  - `historic=ruins`
  - `leisure=park`
  - `amenity=theatre`
  - `amenity=arts_centre`

### Update Frequency
- **Continuous updates**: OSM is crowdsourced and updated daily by contributors worldwide
- **Berlin data**: Active community with regular updates
- **Recommended refresh**: Weekly or bi-weekly pulls for production

### Data Type
- **Dynamic**: Can be queried via API on-demand
- **Format**: GeoJSON, XML, or JSON from Overpass API
- **Geometry**: Point locations with lat/lon coordinates

### Relevant Fields
- `name` - Name of the attraction
- `name:en`, `name:de` - Multilingual names
- `tourism` / `historic` / `leisure` - Category/type
- `description` - Text description (if available)
- `website` - Official website URL
- `opening_hours` - Opening hours in OSM format
- `addr:street`, `addr:housenumber`, `addr:postcode`, `addr:city` - Address components
- `wheelchair` - Accessibility info (yes/no/limited)
- `fee` - Entrance fee (yes/no/value)
- `wikidata` - Wikidata ID for additional info
- `wikipedia` - Wikipedia article link

### Licensing / Reuse Notes
- **License**: ODbL (Open Database License)
- **Attribution required**: © OpenStreetMap contributors
- **Commercial use**: Allowed with attribution
- **Data sharing**: Allowed under ODbL terms

### Planned Transformations
- Normalize category values into unified `attraction_type` field
- Parse opening hours into structured format
- Geocode missing addresses or validate existing coordinates
- Map to Berlin districts (Bezirke) and neighborhoods (Ortsteile)
- Extract and structure multilingual content
- Convert wheelchair accessibility to boolean/enum
- Enrich with Wikidata/Wikipedia metadata where available

---

## Data Source 2: Berlin Open Data Portal

### Source and Origin
- **Source**: Berlin Open Data Portal (daten.berlin.de)
- **Relevant datasets**:
  - Cultural venues and museums
  - Historic monuments and memorials
  - Public parks and green spaces
  - Tourist information points

### Update Frequency
- **Varies by dataset**: Most cultural/tourism datasets updated annually or semi-annually
- **Government-maintained**: Official data from Berlin Senate departments
- **Check individual dataset metadata** for specific update schedules

### Data Type
- **Semi-static**: Downloadable files, periodically updated
- **Formats**: CSV, GeoJSON, JSON, XML, Excel
- **Official and verified**: High data quality and reliability

### Relevant Fields
- Name of institution/attraction
- Category/type (museum, memorial, park, etc.)
- Full address with district (Bezirk)
- Coordinates (latitude/longitude)
- Description/purpose
- Contact information (phone, email, website)
- Opening hours
- Accessibility information
- Public transport connections

### Licensing / Reuse Notes
- **License**: Most datasets under Creative Commons licenses (typically CC BY 3.0 DE)
- **Attribution**: Required, specify source as "Daten Berlin"
- **Check individual datasets** for specific license terms

### Planned Transformations
- Standardize address format and validate coordinates
- Map to unified attraction categories
- Merge with OSM data using name/address matching
- Extract district and neighborhood information
- Normalize opening hours format
- Deduplicate entries across different datasets

---

## Data Source 3: visitBerlin / Berlin.de

### Source and Origin
- **Source**: visitBerlin official tourism website and Berlin.de city portal
- **Data access**: Web scraping or potential API (to be investigated)
- **Content**: Curated list of top attractions, museums, sights

### Update Frequency
- **Continuous**: Website content updated regularly
- **No formal data release schedule**: Content-driven updates
- **Requires monitoring** for changes

### Data Type
- **Dynamic web content**: Requires scraping or API integration
- **Curated and editorial**: High-quality descriptions and imagery
- **Tourist-focused**: Prioritizes visitor-relevant information

### Relevant Fields
- Attraction name
- Category (museum, landmark, park, etc.)
- Detailed description (German and English)
- Address and location
- Opening hours and ticket prices
- Contact information
- Visitor tips and highlights
- Images and media
- Ratings and popularity indicators

### Licensing / Reuse Notes
- **License**: Terms of use need to be verified
- **Scraping considerations**: Respect robots.txt and rate limits
- **Attribution**: May be required depending on usage terms
- **Contact visitBerlin** for official data partnership options

### Planned Transformations
- Extract structured data from HTML pages
- Normalize categories to match OSM/Open Data taxonomy
- Link with existing datasets using name and address matching
- Store editorial descriptions as enrichment data
- Track popularity/prominence scores based on website hierarchy

---

## Data Source 4: Wikidata / Wikipedia

### Source and Origin
- **Source**: Wikidata Query Service and Wikipedia API
- **Query scope**: Tourist attractions, museums, monuments, historic sites in Berlin
- **Linked data**: Can be linked from OSM via wikidata tags

### Update Frequency
- **Continuous**: Community-edited, updated constantly
- **High-quality for major attractions**: Well-documented popular sites
- **Variable completeness** for smaller attractions

### Data Type
- **Dynamic API access**: SPARQL queries for Wikidata, REST API for Wikipedia
- **Structured knowledge base**: Rich relationships and properties
- **Multilingual**: Content available in many languages

### Relevant Fields
- Name (multilingual)
- Instance of (type/category)
- Coordinates
- Address
- Opening date / established date
- Architectural style
- Architect / creator
- Heritage designation
- Website
- Images from Wikimedia Commons
- Descriptions (short and long, multilingual)

### Licensing / Reuse Notes
- **Wikidata**: CC0 (Public Domain)
- **Wikipedia text**: CC BY-SA 3.0
- **Images**: Various Creative Commons licenses (check individual files)
- **Free to use** with appropriate attribution for Wikipedia content

### Planned Transformations
- Query Wikidata for Berlin attractions using SPARQL
- Enrich existing OSM/Open Data records with Wikidata properties
- Extract multilingual names and descriptions
- Link Wikipedia articles for detailed information
- Import high-quality images from Wikimedia Commons

---

## Integration Strategy

### Data Merging Approach
1. **Primary source**: OSM for comprehensive coverage and geographic data
2. **Official validation**: Berlin Open Data for verified government data
3. **Editorial enrichment**: visitBerlin for tourist-focused descriptions
4. **Knowledge enrichment**: Wikidata/Wikipedia for historical context and media

### Deduplication
- Match records using name similarity and geographic proximity
- Cross-reference addresses and coordinates
- Use Wikidata IDs as canonical identifiers where available

### Quality Assurance
- Validate coordinates are within Berlin boundaries
- Check for completeness of essential fields (name, category, location)
- Flag and review duplicate or conflicting entries
- Verify URLs and contact information

---

## Next Steps

1. ✅ Document data sources (this file)
2. ⏳ Execute Overpass query and download OSM data
3. ⏳ Download relevant datasets from Berlin Open Data Portal
4. ⏳ Investigate visitBerlin data access options
5. ⏳ Create Wikidata SPARQL query for Berlin attractions
6. ⏳ Develop data merging and transformation scripts
7. ⏳ Design database schema for tourist attractions layer
8. ⏳ Implement data pipeline and quality checks

---

## Contact

For questions about these data sources, contact the data team at webeet.io.
