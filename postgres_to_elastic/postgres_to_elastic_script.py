# Connect Postgres table to Elasticsearch Index with Python 
# This has been setup on locally

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
