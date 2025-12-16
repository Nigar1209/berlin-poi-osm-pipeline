# Unified POIS Table for Berlin Layers

## Objective
- Combine multiple Berlin spatial data layers into:
  - One unified table for **Points of Interest (POI)**
- Designed for use in **PostgreSQL/PostGIS** and **Elasticsearch**
- Tables must include:
  - Geometry column
  - Common standardized columns
  - Additional attributes stored as JSON

## Data Types
- **Points of Interest (POI):** places such as banks, post offices, schools, and parks
- Spatial queries on POI table should leverage **R‑Tree/GiST indexing**


## Proposed Table Structure: Points of Interest (POI)

| Column Name     | Key                                | Data Type             | Description                                                   | Example |
|-----------------|------------------------------------|-----------------------|---------------------------------------------------------------|---------|
| poi_id          | Primary Key                        | varchar(50)           | Unique identifier (e.g., source + original id)                | `bank_28968292` |
| name            |                                    | varchar(255)          | Name of the place                                             | `Berliner Volksbank` |
| layer           |                                    | varchar(100)          | General category (bank, dental office, gallery, etc.)         | `bank` |
| district_id     | Foreign Key → districts(district_id) | varchar(20)          | Identifier of parent district                                 | `11001001` |
| district        |                                    | varchar(100)          | Name of the district                                          | `Mitte` |
| neighborhood_id |                                    | varchar(20)           | Neighborhood identifier                                       | `0105` |
| neighborhood    |                                    | varchar(100)          | Name of the neighborhood                                      | `Moabit` |
| latitude        |                                    | float8                | Geographic latitude                                           | `52.4866675` |
| longitude       |                                    | float8                | Geographic longitude                                          | `13.319723` |
| geometry        |                                    | geometry(Point, 4326) | Geometry column (WGS84)                                       | `POINT(13.319723 52.4866675)` |
| attributes      |                                    | jsonb                 | Additional info from source tables stored as JSON             | `{"operator":"nan","wheelchair":true,"opening_hours":"mo-fr 10:00-16:00"}` |
| nearest_pos     |                                      | jsonb.                | Showing nearest layer to long term listing                    | `{"bank": {"id":"ban-1915389761","name": "sparkasse","address": {"street": "otto-suhr-allee","house_number": null},"distance": 1011.56046421}` |
---
## Columns in DBeaver
<img width="832" height="369" alt="image" src="https://github.com/user-attachments/assets/6fe26fb4-d0fc-4bde-8238-e115a3484813" />

## Example of table in DBeaver
<img width="1655" height="268" alt="image" src="https://github.com/user-attachments/assets/0091dfc3-2e35-4dc1-909a-1e6e13e9410c" />

## attributes json doc
```json
{
  "url": "https://www.immowelt.de/expose/3ac5c0f7-bcb9-460f-a9c5-    fbfe84d751e4ln=classified_search_results&serp_view=list&search=distributionTypes%3DRent%26estateTypes%3DHouse%2CApartment%26locations%3DAD08DE8634%26projectTypes%3DNew_Build%2CFlatsharing%2CStock%26page%3D19&m=classified_search_results_classified_classified_detail_XL",
  "city": "Berlin",
  "type": "Wohnung",
  "floor": 4,
  "street": "St. Wolfgang Straße",
  "address": "St. Wolfgang Straße 2 10178 Mitte Berlin",
  "district": "Mitte",
  "price_euro": 3541,
  "surface_m2": 190.2,
  "postal_code": 10178,
  "first_tenant": "no",
  "house_number": "2",
  "neighborhood": "Mitte",
  "number_of_rooms": 4}
```

## nearest_pois json doc
```json
{
  "gyms": {
    "id": "gyms-9728794514",
    "name": "Ladycompany - Fitness für Frauen",
    "address": {
      "street": null,
      "housenumber": null
    },
    "distance": 172.38705889
  },
  "banks": {
    "id": "bank-213112439",
    "name": "Sparkasse",
    "address": {
      "street": null,
      "housenumber": null
    },
    "distance": 384.17353401
  },
  "pools": {
    "id": "pool-1048",
    "name": "Kinderbad Monbijou",
    "address": {
      "street": "Oranienburger Straße 78",
      "housenumber": null
    },
    "distance": 502.37607682
  },
  "sbahn": {
    "id": "sbah-104",
    "name": "S Hackescher Markt (Berlin)",
    "address": {
      "street": null,
      "housenumber": null
    },
    "distance": 290.64411841
  },
  "ubahn": {
    "id": "ubah-180",
    "name": "Weinmeisterstraße",
    "address": {
      "street": null,
      "housenumber": null
    },
    "distance": 654.26608037
  },
  "doctors": {
    "id": "doct-2344314518",
    "name": "Neurologie am Hackeschen Markt",
    "address": {
      "street": "Dircksenstraße",
      "housenumber": null
    },
    "distance": 437.76283357
  },
  "schools": null,
  "bus_stops": {
    "id": "bus_-674884640",
    "name": "U Museumsinsel",
    "address": {
      "street": null,
      "housenumber": null
    },
    "distance": 190.02692119
  },
  "hospitals": {
    "id": "hosp-24054786",
    "name": "St. Hedwig-Krankenhaus",
    "address": {
      "street": null,
      "housenumber": null
    },
    "distance": 738.45515057
  },
  "tram_stops": {
    "id": "tram-1633759760",
    "name": "S Hackescher Markt",
    "address": {
      "street": null,
      "housenumber": null
    },
    "distance": 183.04384516
  },
  "playgrounds": {
    "id": "play-583761432",
    "name": "unknown",
    "address": {
      "street": null,
      "housenumber": null
    },
    "distance": 534.19957991
  },
  "social_clubs": {
    "id": "soci-9577332704",
    "name": "Polnisches Institut Berlin",
    "address": {
      "street": null,
      "housenumber": null
    },
    "distance": 182.21034981
  },
  "supermarkets": {
    "id": "supe-975312179",
    "name": "Asia-Mekong",
    "address": {
      "street": null,
      "housenumber": null
    },
    "distance": 229.86427252
  },
  "kindergartens": {
    "id": "kind-1814559961",
    "name": "Kinderinsel MITTEndrin",
    "address": {
      "street": null,
      "housenumber": null
    },
    "distance": 201.65001441
  }
}
```
