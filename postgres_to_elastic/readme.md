# Elasticsearch & Kibana (local machine)
### How to setup and use the Kibana UI vs Python requests

## Create network if not exists
- docker network inspect elastic >/dev/null 2>&1 || docker network create elastic

## Run Elasticsearch
docker run -d \
  --name elasticsearch \
  --net elastic \
  -p 9200:9200 \
  -e "discovery.type=single-node" \
  -e "xpack.security.enabled=false" \
  docker.elastic.co/elasticsearch/elasticsearch:9.2.2

## Run Kibana
docker run -d \
  --name kibana \
  --net elastic \
  -p 5601:5601 \
  -e "xpack.security.enabled=false" \
  docker.elastic.co/kibana/kibana:9.2.2
  
---  
# Part 1 — Kibana UI Tasks

## Task 1: General Filtering & Exploring Data
### Step 1: Access Kibana Discover 

- Open Kibana in your browser
- Go to Discover from the left sidebar menu
- Select your index from the index pattern dropdown (top left)

### Step 2: Basic Filtering
- Method A: Using the Search Bar (KQL - Kibana Query Language)
  - layer:venues
  - district:Mitte
  - attributes.cuisine:italian
  - attributes.category:cafe
 
  <img width="1547" height="345" alt="image" src="https://github.com/user-attachments/assets/1ffcca84-07f9-41fb-90f3-65f74eadfaa6" />


- Method B: Using Filter Buttons
  - Find a field in the left sidebar (like "Category")
  - Click the + icon next to a value to filter for it
  - Click the - icon to exclude it

  <img width="1902" height="485" alt="image" src="https://github.com/user-attachments/assets/55790abf-990f-4aaa-bab6-be8d8e235f88" />


- Method C: Using the Add Filter Button
  - Click "Add filter" near the search bar
  - Select Field → Operator → Value
  - Example: Category is restaurant

  <img width="1652" height="476" alt="image" src="https://github.com/user-attachments/assets/1980d9b7-f7ac-4e27-8584-e099a217de03" />
  <img width="948" height="414" alt="image" src="https://github.com/user-attachments/assets/6b484097-5a07-400b-ad8c-d67651c46c99" />
---
  
## Task 2: Create Index with Mapping (Including Geo Fields)
- Here's how to create your index with proper mapping:
### Step 1: Using Kibana Dev Tools
- Go to Management -> Dev Tools in Kibana (left sidebar)
- Use this template (adjust field names based on your data):

```json
PUT /upoi_index
{
  "mappings": {
    "properties": {
      "name": {
        "type": "text",
        "fields": {
          "keyword": {
            "type": "keyword"
          }
        }
      },
      "layer": {
        "type": "keyword"
      },
      "district": {
        "type": "keyword"
      },
      "neighborhood": {
        "type": "keyword"
      },
      "location": {
        "type": "geo_point"
      }
    }
  }
}
```
Click the ▶ (play) button to execute

<img width="1747" height="594" alt="image" src="https://github.com/user-attachments/assets/6540c8bc-f6ca-4e43-a6cb-3746afc2794c" />

- Understanding Field Types:
  - text: Full-text search (analyzed, tokenized) - use for descriptions, long content
  - keyword: Exact match, filtering, aggregations - use for categories, IDs, city names
  - text with .keyword subfield: Gives you both search AND exact match capabilities
  - geo_point: Latitude/longitude coordinates for maps and geo queries
  - integer/float: Numeric values for calculations
  - date: Timestamp fields

### Step 2: Verify the Mapping
```json
- GET /upoi_index/_mapping
```
- This shows you the complete mapping structure.

### Step 3: Index Sample Data with Geo Points
- After creating the index, add some documents:

```json
POST /upoi_index/_doc
{
  "name": "Dipl.-vet.-med. Jörg Porada",
  "ditrict": "Mitte",
  "layer": "veterinaries",
  "neighborhood": "Mitte",
  "location": {
    "lat": 52.512127,
    "lon": 13.419527
  }
}
```
<img width="1451" height="648" alt="image" src="https://github.com/user-attachments/assets/7e851743-7273-480e-97c3-f037982900ea" />
---

## Task 3 - Verify the data
- Verify the Geo Field recognition
```json
GET /upoi_index/_search
{
  "query": {
    "geo_distance": {
      "distance": "2km",
      "location": {
        "lat": 52.527623,
        "lon": 13.344030
      }
    }
  }
}
```
<img width="1719" height="744" alt="image" src="https://github.com/user-attachments/assets/0a88e941-e53a-420f-be6b-fe032abe7354" />
---

## Task 4: Geo-distance Filtering
- Go to dev tools (Kibana Discovery doesnt have a way to do this in UI)
1. Perform search to find docs within certain distance of co-ordinate
```json
GET /upoi_index/_search
{
  "query": {
    "geo_distance": {
      "distance": "2km",
      "location": {
        "lat": 52.527623,
        "lon": 13.344030
      }
    }
  }
}
```
2. Can use different values
`m or meters`
`km or kilometers`
`mi or miles`
`ft or feet`
`yd or yards`

- Look at hits.total.value - this is your result count

3. Can sort the results
```json
GET /upoi_data/_search
{
  "query": {
    "geo_distance": {
      "distance": "10km",
      "location": {
        "lat": 40.758896,
        "lon": -73.985130
      }
    }
  },
  "sort": [
    {
      "_geo_distance": {
        "location": {
          "lat": 40.758896,
          "lon": -73.985130
        },
        "order": "asc",
        "unit": "km"
      }
    }
  ]
}
```
4. Find a layer with in certain distance
```json
GET /unified_pois/_search
{
  "query": {
    "bool": {
      "must": [
        {
          "term": {
            "layer": "bus_stops"
          }
        }
      ],
      "filter": {
        "geo_distance": {
          "distance": "2km",
          "location": {
            "lat": 52.504417,
            "lon": 13.234717
          }
        }
      }
    }
  }
}
```
5. Visualize with Kibana Maps 🗺️
**This is where it gets exciting!**
##### Step 1: Open Kibana Maps
- Click hamburger menu (☰) → Maps
- Click "Create map"

##### Step 2: Add Your Data Layer
- Click "Add layer" button
- Select "Documents"
- Choose your index pattern: unified_pois
- Click "Add layer"

##### Configure the layer:
- Geospatial field: Select location (your geo_point field)
- Name: "All POIs" or whatever you want
- Click "Add layer"

- You should now see all your points on the map!

##### Step 3: Add a Distance Circle
- To visualize the search radius:
  - Click "Add layer" again
  - Select "Create index" → "Upload GeoJSON" OR
  - Better option: Use "Draw shapes"
- Using Draw Shapes:
  - Click the polygon/circle tool in the toolbar
  - Hold Shift and drag to draw a circle
  - Position it over your reference point (Times Square)
- Alternative: Add Reference Point
  - Click "Add layer" → "Documents"
  - Manually create a small index with just your center point
  - Style it differently (red marker, larger size)

##### Step 4: Filter by category
- Filter the map by distance:
  - Click on your "All POIs" layer in the layers panel (left side)
  - Scroll down to "Filtering"
  - Click "Add filter"
  - Insert the filter info you need like layer:venue and category:bar
> Now the map only shows points that are a bar in the venues layer

##### Step 5: Can filter using the json code in dev tools
- Change the distance filter to see different results:
  - 500m (very focused)
  - 2km (neighborhood level)
  - 5km (city district)
  - 20km (greater metro area)
  - 50km (regional)
- Watch how the number of visible points changes!

##### Step 6: Style Your Points
- Make the visualization more informative:
  - Click your layer → "Style"
  - Color by layer:
  - Fill color → "By value"
  - Field: layer
  - Each layer gets a different color!

##### Add tooltips:
- Scroll to "Tooltip fields"
- Add: name, layer, district, neighborhood
- Hover over points to see details

##### Step 7: Add Multiple Distance Rings
- Create a visual comparison:
  - Add your first layer filtered to 2km
    - Style it blue, 50% opacity
  - Add second layer filtered to 5km
    - Style it green, 30% opacity
  - Add third layer filtered to 10km
    - Style it red, 20% opacity
-   Can see the different distance bands visually!

##### Save and Share
- Click "Save" (top right)
- Name it: "POIs within 5km of Times Square"
- Add it to a Dashboard later if needed

---
## Task 5 Geo-Bounding-Box Filtering
1) Define Geographic Bounding Boxes
- In Elasticsearch, you can use the geo_bounding_box query on a geo_point field (e.g., location).
- location → your geo_point field.
- top_left and bottom_right → define the bounding box coordinates.
  
```json

GET my-index/_search
{
  "query": {
    "geo_bounding_box": {
      "location": {
        "top_left": {
          "lat": 40.73,
          "lon": -74.1
        },
        "bottom_right": {
          "lat": 40.01,
          "lon": -71.12
        }
      }
    }
  }
}

```
2) Multiple Bounding Boxes
- You can run separate queries for different bounding boxes or use a bool query with should clauses
- This will return documents that fall inside either bounding box.
```json

GET my-index/_search
{
  "query": {
    "bool": {
      "should": [
        {
          "geo_bounding_box": {
            "location": {
              "top_left": { "lat": 40.73, "lon": -74.1 },
              "bottom_right": { "lat": 40.01, "lon": -71.12 }
            }
          }
        },
        {
          "geo_bounding_box": {
            "location": {
              "top_left": { "lat": 41.0, "lon": -75.0 },
              "bottom_right": { "lat": 39.5, "lon": -72.0 }
            }
          }
        }
      ]
    }
  }
}

```
3) Compare Results Across Bounding Boxes
- Run separate queries for each bounding box and note the hits.total.value.
- Or use aggregations
```json

GET my-index/_search
{
  "size": 0,
  "aggs": {
    "box1": {
      "filter": {
        "geo_bounding_box": {
          "location": {
            "top_left": { "lat": 40.73, "lon": -74.1 },
            "bottom_right": { "lat": 40.01, "lon": -71.12 }
          }
        }
      }
    },
    "box2": {
      "filter": {
        "geo_bounding_box": {
          "location": {
            "top_left": { "lat": 41.0, "lon": -75.0 },
            "bottom_right": { "lat": 39.5, "lon": -72.0 }
          }
        }
      }
    }
  }
}

```

4) Visualize in Kibana
- Use Maps or Coordinate Map visualization.
- Create filters for each bounding box or use saved searches.


<img width="1750" height="690" alt="image" src="https://github.com/user-attachments/assets/a7494b41-3422-4622-a3c7-2362989f1f73" />

## Task 6 Geo Aggregations
1. Use Geo Grid Aggregations
- Elasticsearch supports two main grid-based aggregations on geo_point fields:
  - geohash_grid: Uses geohash encoding.
  - geotile_grid: Uses Web Mercator tiles (better for maps).
- field: Your geo_point field.
- precision: Controls grid size (1 = world, 7 ≈ city blocks). Higher precision = smaller tiles.

Example using geotile_grid:
```json

GET my-index/_search
{
  "size": 0,
  "aggs": {
    "berlin_grid": {
      "geotile_grid": {
        "field": "location",
        "precision": 5
      }
    }
  }
}

```

2. Experiment with Precision Levels
- Try different values for precision:
  - Precision 3 → Large regions (country-level).
  - Precision 5 → City-level.
  - Precision 7 → Neighborhood-level.

Example with multiple precisions in one query:
```json

GET my-index/_search
{
  "size": 0,
  "aggs": {
    "grid_p3": {
      "geotile_grid": {
        "field": "location",
        "precision": 3
      }
    },
    "grid_p6": {
      "geotile_grid": {
        "field": "location",
        "precision": 6
      }
    }
  }
}

```

3. Analyze Distribution
- Each bucket represents a tile with a doc_count.
- You can sort by doc_count to find hotspots.
- Combine with sub-aggregations (e.g., average price per tile).

Example with sub-aggregation:
```json

GET my-index/_search
{
  "size": 0,
  "aggs": {
    "berlin_grid": {
      "geotile_grid": {
        "field": "location",
        "precision": 6
      },
      "aggs": {
        "avg_price": {
          "avg": { "field": "price" }
        }
      }
    }
  }
}

```
##### "aggs"
- This is the aggregations section of an Elasticsearch query.
- It tells Elasticsearch to compute summaries or groupings of your data instead of (or in addition to) returning raw documents.
- In your example, we’re asking Elasticsearch to group documents based on geographic tiles.

##### "berlin_grid"
- This is just the name of the aggregation (you can choose any name).
- It acts like a label so you can reference the results later.
- Example: If you name it "berlin_grid", the response will have a section called "aggregations.berlin_grid".

##### "geotile_grid"
- This is the type of aggregation.
- It divides the world map into a grid of tiles using the Web Mercator projection (same as most online maps).
- Each tile is identified by a zoom level (precision) and contains documents whose geo_point falls inside that tile.

##### What Happens
- Elasticsearch looks at your geo_point field (e.g., location).
- It splits the map into tiles based on the precision you specify.
- Each tile becomes a bucket with a doc_count (number of documents in that tile).
- You can add sub-aggregations (like average price per tile).

##### Precision Levels
- precision: 1 → Very large tiles (whole continents).
- precision: 5 → City-level tiles.
- precision: 7 → Neighborhood-level tiles.

##### So in short:
- "aggs" = we want aggregations.
- "berlin_grid" = name of this aggregation.
- "geotile_grid" = type of aggregation that creates map tiles for geo analysis.


----

### Quick Tips for Beginners:
- Index vs Index Pattern:
  - Index = actual data storage
  - Index Pattern (in Kibana) = view/access layer for one or more indices
- Refresh Data: After adding documents, click the refresh icon in Discover
- Time Filter: If your index has date fields, adjust the time picker (top right) to see your data
- Export/Save: You can save searches and visualizations for later

| Concept        | What It Is                 | Where It Lives   | Example                  |
|----------------|----------------------------|-------------------|---------------------------|
| Index          | Actual data storage        | Elasticsearch     | upoi_data                |
| Index Pattern  | View/access configuration  | Kibana only       | .upoi_*                  |
| Document       | Single record/row          | Inside an index   | `{ "name": "Park", ... }` |

---
### Common Issues:
- If geo queries fail, check that lat/lon values are valid (-90 to 90 for lat, -180 to 180 for lon)
- Use keyword type for filtering/aggregations, text for search
- Can't change mapping after creation (need to reindex)
---
### Index vs Index Pattern: The Complete Picture
`Index = The Actual Database`
- Think of an index like a database table in SQL. It's where your actual documents (rows) are physically stored in Elasticsearch.Example indices you might have:
- eg: upoi_data - your points of interest
- Each index stores actual JSON documents.

`Index Pattern = The View/Access Layer`
- An index pattern is a Kibana concept (not Elasticsearch). It's like a "lens" or "filter" that tells Kibana which index(es) you want to work with in the UI.
- Think of it as a query template that matches one or more indices.
> Why Do We Need Index Patterns?
- Problem Without Index Patterns:
- If you have 12 indices (one per month):
  - logs_january
  - logs_february
  - logs_march
  - ... etc
- You'd have to manually switch between them constantly in Kibana. Annoying!
- Solution With Index Patterns:
> Create ONE index pattern: logs_* - The * is a wildcard that matches ALL indices starting with "logs_". Now you can search across all 12 months at once!

### How to Create an Index Pattern in Kibana
##### Step-by-Step:
- Go to Stack Management
  - Click hamburger menu (☰) → Management → Stack Management
- Navigate to Index Patterns
  - Under "Kibana" section → Index Patterns
- Create Index Pattern
  - Click "Create index pattern" button
- Define the Pattern
  - Enter your pattern: upoi_* or upoi_data
  - Kibana shows you which indices match (preview)
  - Click "Next step"
- Set Time Field (Optional)
  - If your data has timestamps: select the date field (e.g., created_date)
  - If no time data: select "I don't want to use a time filter"
- Click "Create index pattern"
---
# Part 2 — Python Tasks

## Task 7 - Connect to Elasticsearch From Python

```python
from elasticsearch import Elasticsearch, helpers
import psycopg2
from shapely import wkb
import binascii

# PostgreSQL Configuration
PG_CONFIG = {
    'host': 'localhost',
    'port': 5433,
    'database': 'database name',
    'user': 'user name',
    'password': 'user password,
    'sslmode': 'require'
}

# Elasticsearch Configuration
ES_CONFIG = {
    'hosts': ['http://localhost:9200'],
    # Uncomment below if your Elasticsearch requires authentication
    # 'basic_auth': ('elastic_user', 'elastic_password')
}

# Configuration
TABLE_NAME = 'schema.table name needed in elasticsearch'
INDEX_NAME = 'what to call the index in elasticsearch'
BATCH_SIZE = 1000  # Number of records to index at once

def fetch_data_from_postgres():
    """Fetch all data from PostgreSQL table"""
    print(f"Connecting to PostgreSQL database: {PG_CONFIG['database']}")
    
    conn = psycopg2.connect(**PG_CONFIG)
    cursor = conn.cursor()
    
    # Get geometry type and centroid for all geometry types (this makes sure the geom_point is correct
    query = f"""
        SELECT *,
               ST_GeometryType(geometry) as geom_type,
               CASE 
                   WHEN ST_GeometryType(geometry) = 'ST_Point' THEN ST_Y(geometry)
                   WHEN geometry IS NOT NULL THEN ST_Y(ST_Centroid(geometry))
                   ELSE NULL
               END as lat,
               CASE 
                   WHEN ST_GeometryType(geometry) = 'ST_Point' THEN ST_X(geometry)
                   WHEN geometry IS NOT NULL THEN ST_X(ST_Centroid(geometry))
                   ELSE NULL
               END as lon,
               ST_AsGeoJSON(geometry) as geojson
        FROM {TABLE_NAME}
    """
    cursor.execute(query)
    
    # Get column names
    columns = [desc[0] for desc in cursor.description]
    
    # Fetch all rows
    rows = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    print(f"Fetched {len(rows)} rows from PostgreSQL")
    
    # Convert to list of dictionaries
    data = []
    for row in rows:
        doc = {}
        for i, col in enumerate(columns):
            if col == 'geometry':
                # Skip the raw geometry column
                continue
            elif col == 'geojson':
                # Store GeoJSON for visualization
                if row[i]:
                    import json
                    doc['geometry_geojson'] = json.loads(row[i])
            else:
                doc[col] = row[i]
        
        # Create geo_point from lat/lon (centroid for polygons)
        lat_idx = columns.index('lat')
        lon_idx = columns.index('lon')
        
        if row[lat_idx] is not None and row[lon_idx] is not None:
            doc['location'] = {
                "lat": row[lat_idx],
                "lon": row[lon_idx]
            }
        
        data.append(doc)
    
    return data

def create_index_with_mapping(es):
    """Create index with proper geo_point mapping"""
    mapping = {
        "mappings": {
            "properties": {
                "location": {
                    "type": "geo_point"
                },
                "geometry_geojson": {
                    "type": "geo_shape"
                }
                # Other fields will be auto-mapped
            }
        }
    }
    
    # Delete existing index if it exists
    if es.indices.exists(index=INDEX_NAME):
        print(f"Deleting existing index '{INDEX_NAME}'")
        es.indices.delete(index=INDEX_NAME)
    
    print(f"Creating index '{INDEX_NAME}' with geo mappings")
    es.indices.create(index=INDEX_NAME, body=mapping)

def index_to_elasticsearch(data):
    """Index data into Elasticsearch"""
    print(f"Connecting to Elasticsearch at {ES_CONFIG['hosts'][0]}")
    
    es = Elasticsearch(**ES_CONFIG)
    
    # Check connection
    if not es.ping():
        raise Exception("Could not connect to Elasticsearch")
    
    print(f"Successfully connected to Elasticsearch")
    
    # Create index with proper mapping
    create_index_with_mapping(es)
    
    # Prepare bulk indexing
    actions = []
    for doc in data:
        action = {
            "_index": INDEX_NAME,
            "_source": doc
        }
        actions.append(action)
    
    # Bulk index
    print(f"Indexing {len(actions)} documents to index '{INDEX_NAME}'...")
    success, failed = helpers.bulk(es, actions, chunk_size=BATCH_SIZE, raise_on_error=False)
    
    print(f"Successfully indexed: {success}")
    if failed:
        print(f"Failed to index: {len(failed)}")
        for fail in failed[:5]:  # Show first 5 failures
            print(f"  - {fail}")
    
    return success, failed

def main():
    try:
        # Fetch data from PostgreSQL
        data = fetch_data_from_postgres()
        
        if not data:
            print("No data to index")
            return
        
        # Index to Elasticsearch
        success, failed = index_to_elasticsearch(data)
        
        print("\n" + "="*50)
        print("SYNC COMPLETE")
        print("="*50)
        print(f"Total records: {len(data)}")
        print(f"Successfully indexed: {success}")
        print(f"Failed: {len(failed) if failed else 0}")
        print(f"\nYou can now view this data in Kibana!")
        print(f"Index name: {INDEX_NAME}")
        print(f"\nGeometry handling:")
        print(f"  - Points: indexed as-is")
        print(f"  - Polygons/MultiPolygons: centroid used for 'location' field")
        print(f"  - Full geometry stored in 'geometry_geojson' field")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        raise

if __name__ == "__main__":
    main()
```

## Task 8 - General Filtering With Python
- Filter documents by category, city, or other attributes.

```python
# 8.1: Filter by single attribute - attributes.category
print("\n--- Filter 1: All Restaurants ---")
query_category = {
    "size": 10,
    "query": {
        "term": {
            "attributes.category": "restaurant"
        }
    }
}

response = es.search(index=INDEX_NAME, body=query_category)
print(f"Found {response['hits']['total']['value']} restaurants")
for hit in response['hits']['hits']:
    src = hit['_source']
    print(f"  - {src.get('name', 'N/A')} in {src.get('district', 'N/A')}")
```
### Output
--- Filter 1: All Restaurants ---
Found 4630 restaurants
  - Army Food in Mitte
  - Augustiner auf Bötzow in Pankow
  - Hasir in Mitte
  - Moccachino in Mitte
  - Bristol Grill in Charlottenburg-Wilmersdorf
  - Casa di Maria in Charlottenburg-Wilmersdorf
  - Aspendos in Tempelhof-Schöneberg
  - Jōnetsu in Friedrichshain-Kreuzberg
  - Habana in Friedrichshain-Kreuzberg
  - Cantina in Pankow

### Compare results with the same filters executed in Kibana.
<img width="817" height="419" alt="image" src="https://github.com/user-attachments/assets/ed453b14-b761-4863-a3fc-0e041a3dfeef" />


Combine multiple filters to see how Elasticsearch handles them.
```python
# Combine multiple filters (Category AND District)
print("\n--- Filter 3: Restaurants in Mitte ---")
query_combined = {
    "size": 10,
    "query": {
        "bool": {
            "must": [
                {"term": {"attributes.category": "restaurant"}},
                {"term": {"district": "mitte"}}
            ]
        }
    }
}

response = es.search(index=INDEX_NAME, body=query_combined)
print(f"Found {response['hits']['total']['value']} restaurants in Mitte")
for hit in response['hits']['hits'][:5]:
    src = hit['_source']
    print(f"  - {src.get('name', 'N/A')}")

# 8.4: Multiple filters with OR logic
print("\n--- Filter 4: Restaurants OR Cafes ---")
query_or = {
    "size": 10,
    "query": {
        "bool": {
            "should": [
                {"term": {"attributes.category": "restaurant"}},
                {"term": {"attributes.category": "cafe"}}
            ],
            "minimum_should_match": 1
        }
    }
}

response = es.search(index=INDEX_NAME, body=query_or)
print(f"Found {response['hits']['total']['value']} restaurants or cafes")
for hit in response['hits']['hits'][:5]:
    src = hit['_source']
    print(f"  - {src.get('name', 'N/A')} ({src.get('attributes.category', 'N/A')})")
```
### Output
--- Filter 3: Restaurants in Mitte ---
Found 903 restaurants in Mitte
  - Army Food
  - Hasir
  - Moccachino
  - Hung Anh
  - Bistro Ribelle

--- Filter 4: Restaurants OR Cafes ---
Found 7096 restaurants or cafes
  - Five Elephant (N/A)
  - Çarik Kuruyemiş & Cafe (N/A)
  - Ja Dilo (N/A)
  - Karaca (N/A)
  - Café Hexe 2.0 (N/A)

### Compare results with the same filters executed in Kibana.
<img width="736" height="544" alt="image" src="https://github.com/user-attachments/assets/6dc97a94-6317-46da-be79-3349db9ea938" />

<img width="579" height="488" alt="image" src="https://github.com/user-attachments/assets/d5fd4cfe-d685-4536-ad5d-ab224a3ce01d" />
---

## Task 9 - Geo-Distance Queries in Python
- Find documents within a certain distance of a specific point.
```python
# ============================================================================
# TASK 9: GEO-DISTANCE QUERIES IN PYTHON
# ============================================================================

print("\n" + "=" * 70)
print("TASK 9: GEO-DISTANCE QUERIES")
print("=" * 70)

# Reference point: long term listing id long-WOH_2772_178_14055 (Berlin)
long_WOH_2772_178_14055 = {"lat": 52.504, "lon": 13.235}

# Find POIs within 1km
print("\n--- Query 1: Within 1km of long-WOH_2772_178_14055 ---")
query_1km = {
    "size": 10,
    "query": {
        "geo_distance": {
            "distance": "1km",
            "location": long_WOH_2772_178_14055
        }
    },
    "sort": [
        {
            "_geo_distance": {
                "location": long_WOH_2772_178_14055,
                "order": "asc",
                "unit": "km"
            }
        }
    ]
}

response = es.search(index=INDEX_NAME, body=query_1km)
print(f"Found {response['hits']['total']['value']} POIs within 1km")
for hit in response['hits']['hits'][:5]:
    src = hit['_source']
    distance = hit['sort'][0]
    print(f"  - {src.get('name', 'N/A')}: {distance:.2f} km away")

# Find POIs within 200mtrs
print("\n--- Query 3: Within 200mtrs of long-WOH_2772_178_14055 ---")
query_10km = {
    "size": 0,
    "query": {
        "geo_distance": {
            "distance": "200m",
            "location": long_WOH_2772_178_14055
        }
    }
}
```
--- Query 1: Within 1km of long-WOH_2772_178_14055 ---
Found 193 POIs within 1km
  - Wohnung zur Miete 2.772 € 4 Zimmer 178 m² frei ab 01.09.2025 Stallupöner Allee 33 Westend Berlin 14055: 0.05 km away
  - Stallupöner Allee: 0.11 km away
  - Stallupöner Allee: 0.12 km away
  - Stallupöner Allee: 0.13 km away
  - Kranzallee: 0.17 km away

--- Query 3: Within 200mtrs of long-WOH_2772_178_14055 ---
Found 8 POIs within 200mtrs (only asked for count using size = 0)
     
- Experiment with different radii to see how results change.
```python
print("\n--- Comparison: Different Radii ---")
radii = ["500m", "1km", "2km", "5km"]
for radius in radii:
    query = {
        "size": 0,       # only shows the count and not list
        "query": {
            "geo_distance": {
                "distance": radius,
                "location": long_WOH_2772_178_14055
            }
        }
    }
    response = es.search(index=INDEX_NAME, body=query)
    count = response['hits']['total']['value']
    print(f"  {radius:>6}: {count:>5} POIs")
```
--- Comparison: Different Radii ---
    - 500m:    38 POIs
    -  1km:   193 POIs
    -  2km:   642 POIs
    -  5km:  9012 POIs

- Show restaurants within 5kms
```python
print("\n--- Query 4: Restaurants within 5km ---")
query_geo_category = {
    "size": 10,
    "query": {
        "bool": {
            "must": [
                {"term": {"attributes.category": "restaurant"}}
            ],
            "filter": {
                "geo_distance": {
                    "distance": "5km",
                    "location": long_WOH_2772_178_14055
                }
            }
        }
    },
    "sort": [
        {
            "_geo_distance": {
                "location": long_WOH_2772_178_14055,
                "order": "asc",
                "unit": "km"
            }
        }
    ]
}

response = es.search(index=INDEX_NAME, body=query_geo_category)
print(f"Found {response['hits']['total']['value']} restaurants within 5km")
for hit in response['hits']['hits'][:5]:
    src = hit['_source']
    distance = hit['sort'][0]
    print(f"  - {src.get('name', 'N/A')}: {distance:.2f} km away")
```
--- Query 4: Restaurants within 5km ---
Found 401 restaurants within 5km
  - Tiroler Stuben: 0.52 km away
  - Sardegna A Tavola Im Waldhaus: 0.68 km away
  - Preußisches Landwirtshaus: 0.80 km away
  - Il Porto: 1.03 km away
  - Rafih: 1.60 km away
    
- Compare Python results with equivalent Kibana queries.

<img width="1241" height="508" alt="image" src="https://github.com/user-attachments/assets/0083c11f-9e21-44ac-a9ea-3e37285f5df7" />
<img width="910" height="471" alt="image" src="https://github.com/user-attachments/assets/ad575ea8-f7fc-4a28-ba43-5280607b49e2" />

## Task 10 -  Geo-Bounding-Box Queries in Python
- Define bounding boxes in Python and filter documents within them.
```python
print("\n--- Restaurants in Berlin - multi bounding boxes ---")
berlin_restaurants = {
    "size": 10,
    "query": {
        "bool": {
            "must": [
                {"term": {"attributes.category.keyword": "restaurant"}}
            ],
            "should": [
                {
                    "geo_bounding_box": {
                        "location": {
                            "top_left": {"lat": 52.54, "lon": 13.37},
                            "bottom_right": {"lat": 52.5, "lon": 13.43}
                        }
                    }
                },
                {
                    "geo_bounding_box": {
                        "location": {
                            "top_left": {"lat": 52.53, "lon": 13.45},
                            "bottom_right": {"lat": 52.5, "lon": 13.51}
                        }
                    }
                }
            ],
            "minimum_should_match": 1
        }
    }
}



response = es.search(index=INDEX_NAME, body=berlin_restaurants)
print(f"Found {response['hits']['total']['value']} restaurants in Berlin multi bounding box")
for hit in response['hits']['hits'][:5]:
    src = hit['_source']
    print(f"  - {src.get('name', 'N/A')} at ({src.get('location', {})})")  
```
### Output
--- Restaurants in Berlin - multi bounding boxes ---
- Found 1146 restaurants in Berlin multi bounding box
  - Army Food at ({'lat': 52.50835, 'lon': 13.389846})
  - Augustiner auf Bötzow at ({'lat': 52.529637, 'lon': 13.41675})
  - Hasir at ({'lat': 52.523819, 'lon': 13.401103})
  - Jōnetsu at ({'lat': 52.513154, 'lon': 13.462049})
  - Habana at ({'lat': 52.511884, 'lon': 13.456796})

- Observe results and compare with the same queries executed in Kibana.
<img width="1438" height="552" alt="image" src="https://github.com/user-attachments/assets/254062a8-34f8-4d32-81fd-2d7c6a63ca8e" />

## Task 11 - Geo Aggregations in Python
- Perform grid-based geo aggregations at multiple precision levels.
```python
# Geotile grid aggregation (for map tiles)
print("\n--- Aggregation 4: Geotile Grid (Zoom level 10) ---")
agg_geotile = {
    "size": 0,
    "aggs": {
        "berlin_grid": {
            "geotile_grid": {
                "field": "location",
                "precision": 7
            }
        }
    }
}

response = es.search(index=INDEX_NAME, body=agg_geotile)
buckets = response['aggregations']['berlin_grid']['buckets']
print(f"Found {len(buckets)} geotile cells (zoom 10)")
for bucket in buckets[:10]:
    print(f"  Tile {bucket['key']}: {bucket['doc_count']} POIs")
```
### Output
--- Aggregation 4: Geotile Grid (Zoom level 10) ---
Found 2 geotile cells (zoom 10)
  - Tile 7/68/41: 91230 POIs
  - Tile 7/68/42: 43173 POIs

```python
# Geohash grid aggregation - Medium precision (neighborhood level)
print("\n--- Aggregation 2: Geohash Grid (Precision 6 - ~1.2km cells) ---")
agg_geohash_6 = {
    "size": 0,
    "aggs": {
        "geo_grid": {
            "geohash_grid": {
                "field": "location",
                "precision": 6
            }
        }
    }
}

response = es.search(index=INDEX_NAME, body=agg_geohash_6)
buckets = response['aggregations']['geo_grid']['buckets']
print(f"Found {len(buckets)} geohash cells (precision 6)")
for bucket in buckets[:10]:
    print(f"  Cell {bucket['key']}: {bucket['doc_count']} POIs")
```
### Output
--- Aggregation 2: Geohash Grid (Precision 6 - ~1.2km cells) ---
Found 1806 geohash cells (precision 6)
  - Cell u33dbc: 1183 POIs
  - Cell u33d8g: 909 POIs
  - Cell u33ddm: 892 POIs
  - Cell u33dbg: 755 POIs
  - Cell u33d9e: 652 POIs
  - Cell u33dc5: 594 POIs
  - Cell u33df2: 578 POIs
  - Cell u33dce: 564 POIs
  - Cell u33dcn: 560 POIs
  - Cell u33d9u: 547 POIs

- Examine distribution patterns and analyze results.
- Compare results with Kibana visualizations.


## Task 12 -  Summarize Learnings
## 12. Summarize Learnings

### Differences Observed Between Kibana and Python Query Behavior
When comparing Kibana and Python queries, it was observed that Kibana makes it easier to explore data using a visual interface. Filters such as `attributes.category` (for example, restaurants and cafés) and switching between different layers like `long_term_listings` can be applied quickly in Kibana. In Python, the same filters must be written explicitly in the query, which requires a clearer understanding of field names and index structure. This showed that Kibana is well suited for exploration, while Python offers more control but requires more careful query setup.

### Behavior of Geo Queries with Different Distances or Bounding Boxes
Geo queries behaved differently depending on whether distance-based queries or bounding boxes were used. Distance queries returned documents within a specified radius from a point, while bounding box queries only returned documents that fell within a defined geographic area. Small changes to distance values or bounding box coordinates affected the number of results returned, especially when filtering for specific categories such as restaurants or cafés. This highlighted the importance of choosing the correct geo query type based on the analysis goal.

### Influence of Mapping Choices on Query Results
Mapping choices had a direct impact on query results. Location fields needed to be correctly mapped as `geo_point` for geo queries to function properly. In addition, how fields such as `attributes.category` were mapped influenced how accurately documents could be filtered. Aggregations like geohash grids grouped documents into geographic areas instead of returning individual records, which affected how results were interpreted when visualized on maps.

### Challenges Encountered During Querying and Analysis
Several challenges were encountered during the querying and analysis process. One challenge was understanding why aggregation results, such as geohash grid keys, could not be used directly as filters in Kibana Maps. Another challenge was interpreting geohash keys and understanding the geographic areas they represented. Differences between Kibana and Python results initially caused confusion, but this was resolved by ensuring the same filters, categories, and layers were applied consistently. Overall, this process improved understanding of how geo queries and aggregations work in Elasticsearch.





