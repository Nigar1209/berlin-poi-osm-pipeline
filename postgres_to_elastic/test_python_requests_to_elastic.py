"""
Elasticsearch Python requests: Filtering, Geo-Queries, and Aggregations
"""

from elasticsearch import Elasticsearch
import json
from datetime import datetime

# ============================================================================
# SETUP: Connect to Elasticsearch
# ============================================================================

# Adjust this connection based on your setup
es = Elasticsearch(["http://localhost:9200"])

# Verify connection
print("=" * 70)
print("ELASTICSEARCH CONNECTION")
print("=" * 70)
info = es.info()
print(f"Cluster Name: {info['cluster_name']}")
print(f"Version: {info['version']['number']}")
print()

# Your index name - adjust if different
INDEX_NAME = "unified_pois"

# Check if index exists
if es.indices.exists(index=INDEX_NAME):
    count = es.count(index=INDEX_NAME)
    print(f"Index '{INDEX_NAME}' exists with {count['count']} documents")
else:
    print(f"Warning: Index '{INDEX_NAME}' not found!")
print()


# ============================================================================
# TASK 8: GENERAL FILTERING WITH PYTHON
# ============================================================================

print("=" * 70)
print("TASK 8: GENERAL FILTERING")
print("=" * 70)

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

# 8.2: Filter by city
print("\n--- Filter 2: All neighborhoods in Mitte ---")
query_city = {
    "size": 10,
    "query": {
        "term": {
            "district": "mitte"  # must be made lowercase as elasticsearch stores it that way, even if it shows as capitalised in Kibana
        }
    }
}

response = es.search(index=INDEX_NAME, body=query_city)
print(f"Found {response['hits']['total']['value']} neighborhoods in Mitte")
for hit in response['hits']['hits'][:5]:  # Show first 5
    src = hit['_source']
    print(f"  - {src.get('neighborhood', 'N/A')} ({src.get('attributes.category', 'N/A')})")

# 8.3: Combine multiple filters (Category AND City)
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


# ============================================================================
# TASK 9: GEO-DISTANCE QUERIES IN PYTHON
# ============================================================================

print("\n" + "=" * 70)
print("TASK 9: GEO-DISTANCE QUERIES")
print("=" * 70)

# Reference point: long term listing id long-WOH_2772_178_14055 (Berlin)
long_WOH_2772_178_14055 = {"lat": 52.504, "lon": 13.235}

# 9.1: Find POIs within 1km
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

# 9.2: Find POIs within 5km
print("\n--- Query 2: Within 5km of long-WOH_2772_178_14055 ---")
query_5km = {
    "size": 10,
    "query": {
        "geo_distance": {
            "distance": "5km",
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

response = es.search(index=INDEX_NAME, body=query_5km)
print(f"Found {response['hits']['total']['value']} POIs within 5km")
for hit in response['hits']['hits'][:5]:
    src = hit['_source']
    distance = hit['sort'][0]
    print(f"  - {src.get('name', 'N/A')}: {distance:.2f} km away")

# 9.3: Find POIs within 200mtrs
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

response = es.search(index=INDEX_NAME, body=query_10km)  # size=0 for count only (doesnt show list)
print(f"Found {response['hits']['total']['value']} POIs within 200mtrs")

# 9.4: Compare different radii
print("\n--- Comparison: Different Radii ---")
radii = ["500m", "1km", "2km", "5km"]
for radius in radii:
    query = {
        "size": 10,
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

# 9.5: Geo-distance with category filter
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

# ============================================================================
# TASK 10: GEO-BOUNDING-BOX QUERIES IN PYTHON
# ============================================================================

print("\n" + "=" * 70)
print("TASK 10: GEO-BOUNDING-BOX QUERIES")
print("=" * 70)

# bounding box (approximate)
print("\n--- Query 1: POIs in Berlin ---")
berlin_box = {
    "size": 10,
    "query": {
        "geo_bounding_box": {
          "location": {
            "top_left": {
              "lat": 52.54,
              "lon": 13.37
            },
            "bottom_right": {
              "lat": 52.5,
              "lon": 13.43
            }
            }
        }
    }
}

response = es.search(index=INDEX_NAME, body=berlin_box)
print(f"Found {response['hits']['total']['value']} POIs in Berlin bounding box")
for hit in response['hits']['hits'][:5]:
    src = hit['_source']
    loc = src.get('location', {})
    print(f"  - {src.get('name', 'N/A')} at ({loc.get('lat', 'N/A')}, {loc.get('lon', 'N/A')})")


#  Bounding box with category filter
print("\n--- Query 4: Restaurants in Berlin ---")
berlin_restaurants = {
    "size": 10,
    "query": {
        "bool": {
            "must": [
                {"term": {"attributes.category": "restaurant"}}
            ],
            "filter": {
                "geo_bounding_box": {
                    "location": {
                        "top_left": {"lat": 52.54, "lon": 13.37},
                        "bottom_right": {"lat": 52.5, "lon": 13.43}
                    }
                }
            }
        }
    }
}

response = es.search(index=INDEX_NAME, body=berlin_restaurants)
print(f"Found {response['hits']['total']['value']} restaurants in Berlin bounding box")
for hit in response['hits']['hits'][:5]:
    src = hit['_source']
    print(f"  - {src.get('name', 'N/A')} at ({src.get('location', {})})")  


#  Bounding box with category filter
print("\n---  Restaurants in Berlin ---")
berlin_restaurants = {
    "size": 10,
    "query": {
        "bool": {
            "must": [
                {"term": {"attributes.category": "restaurant"}}
            ],
            "filter": {
                "geo_bounding_box": {
                    "location": {
                        "top_left": {"lat": 52.54, "lon": 13.37},
                        "bottom_right": {"lat": 52.5, "lon": 13.43}
                    }
                }
            }
        }
    }
}

response = es.search(index=INDEX_NAME, body=berlin_restaurants)
print(f"Found {response['hits']['total']['value']} restaurants in Berlin bounding box")
for hit in response['hits']['hits'][:5]:
    src = hit['_source']
    print(f"  - {src.get('name', 'N/A')} at ({src.get('location', {})})")  

# Multiple bounding box with category filter
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

# ============================================================================
# TASK 11: GEO AGGREGATIONS IN PYTHON
# ============================================================================

print("\n" + "=" * 70)
print("TASK 11: GEO AGGREGATIONS")
print("=" * 70)

# Geotile grid aggregation (for map tiles)
print("\n---  Geotile Grid (Zoom level 10) ---")
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

# Geohash grid aggregation - Medium precision (neighborhood level)
print("\n---  Geohash Grid (Precision 6 - ~1.2km cells) ---")
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

# Geo centroid aggregation (find center point)
print("\n---  Geo Centroid (Average Location) ---")
agg_centroid = {
    "size": 0,
    "aggs": {
        "centroid": {
            "geo_centroid": {
                "field": "location"
            }
        }
    }
}

response = es.search(index=INDEX_NAME, body=agg_centroid)
centroid = response['aggregations']['centroid']['location']
count = response['aggregations']['centroid']['count']
print(f"Center point of all {count} POIs:")
print(f"  Latitude: {centroid['lat']:.6f}")
print(f"  Longitude: {centroid['lon']:.6f}")

# Geo bounds aggregation (find bounding box)
print("\n---  Geo Bounds (Min/Max Coordinates) ---")
agg_bounds = {
    "size": 0,
    "aggs": {
        "bounds": {
            "geo_bounds": {
                "field": "location"
            }
        }
    }
}

response = es.search(index=INDEX_NAME, body=agg_bounds)
bounds = response['aggregations']['bounds']['bounds']
print(f"Bounding box of all POIs:")
print(f"  Top-left:     ({bounds['top_left']['lat']:.6f}, {bounds['top_left']['lon']:.6f})")
print(f"  Bottom-right: ({bounds['bottom_right']['lat']:.6f}, {bounds['bottom_right']['lon']:.6f})")
