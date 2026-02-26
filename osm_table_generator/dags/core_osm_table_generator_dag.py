import json
import logging
import os
import time
import pandas as pd
import geopandas as gpd
import requests
from datetime import datetime, timedelta
from shapely.geometry import Point
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook

# =============================================================================
# 1. GLOBAL SETTINGS
# =============================================================================
SCHEMA_NAME = "berlin_automation_nigar"
DAG_FOLDER = os.path.dirname(os.path.abspath(__file__))

# =============================================================================
# 2. FILE LOADERS
# =============================================================================

def load_core_columns():
    #Retrieves standard DB column definitions from config.
    path = os.path.join(DAG_FOLDER, 'config', 'core_columns.json')
    with open(path, 'r') as f:  
        return json.load(f)

def load_table_configs():
    #Retrieves OSM tag filters and unique column settings.
    path = os.path.join(DAG_FOLDER, 'config', 'osm_tables.json')
    with open(path, 'r') as f:
        return json.load(f)["tables"]

def load_lor_data():
    #Loads Berlin's LOR (Lebensweltlich orientierte Räume) GeoJSON.
    path = os.path.join(DAG_FOLDER, 'config', 'lor_ortsteile.geojson')
    try:
        with open(path, 'r') as f:
            return json.load(f) 
    except FileNotFoundError:
        logging.warning(f"LOR data file not found at {path}. Enrichment will return NULLs.")
        return []


# =============================================================================
# 3. OSM DATA ACQUISITION
# =============================================================================

def fetch_osm_data(tags):
    """
    Queries Overpass API with Regex support.
    Timeout set to 600s to handle high-density city areas safely.
    """
    base_url = "https://overpass-api.de/api/interpreter"
    
    # 1. Standardize tags into a list of strings for the query
    tag_filters = []
    
    # If tags is a list (like  hospitals/hotels)
    if isinstance(tags, list):
        for tag in tags:
            k = tag['key']
            v = tag['value']
            # If value is a list, join with |; otherwise use as is
            val_str = "|".join(v) if isinstance(v, list) else v
            tag_filters.append(f'["{k}"~"{val_str}"]') 
    
    # If tags is a single dict (like kindergartens/malls)
    else:
        k, v = tags['key'], tags['value']
        val_str = "|".join(v) if isinstance(v, list) else v
        tag_filters.append(f'["{k}"~"{val_str}"]')

    # Join multiple filters: ["key1"~"val1"]["key2"~"val2"]
    filters = "".join(tag_filters)


    # Using the Berlin bounding box: (52.3, 13.0, 52.7, 13.7)
    query = f"""
    [out:json][timeout:600];
    (
      node{filters}(52.3, 13.0, 52.7, 13.7);
      way{filters}(52.3, 13.0, 52.7, 13.7);
      relation{filters}(52.3, 13.0, 52.7, 13.7);
    );
    out center;
    """
    
    logging.info(f"Sending Overpass Query: {query}")
    
    response = requests.post(base_url, data={'data': query}, timeout=610)
    response.raise_for_status()
    return response.json().get('elements', [])



def is_inside(lat, lon, polygon):
    """Ray Casting algorithm for point-in-polygon."""
    n = len(polygon)
    inside = False
    p1x, p1y = polygon[0]
    for i in range(n + 1):
        p2x, p2y = polygon[i % n]
        if lon > min(p1y, p2y):
            if lon <= max(p1y, p2y):
                if lat <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (lon - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or lat <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside


# Official Berlin District Name to 8-digit ID Mapping
DISTRICT_MAPPING = {
    'Mitte': '11001001',
    'Friedrichshain-Kreuzberg': '11002002',
    'Pankow': '11003003',
    'Charlottenburg-Wilmersdorf': '11004004',
    'Spandau': '11005005',
    'Steglitz-Zehlendorf': '11006006',
    'Tempelhof-Schöneberg': '11007007',
    'Neukölln': '11008008',
    'Treptow-Köpenick': '11009009',
    'Marzahn-Hellersdorf': '11010010',
    'Lichtenberg': '11011011',
    'Reinickendorf': '11012012'
}

# =============================================================================
# 4. GEOSPATIAL PROCESSING (ENRICHMENT)
# =============================================================================

def enrich_with_lor(elements, lor_polygons):
    """
    Performs vectorized Spatial Join.
    - Filters results to stay strictly within Berlin borders.
    - Attaches District and Neighborhood metadata.
    """
    if not elements or not lor_polygons:
        logging.warning("No elements or LOR data provided for enrichment.")
        return elements

    # Prepare DataFrames for spatial operations
    df = pd.DataFrame(elements)
    
    # Extract coordinates correctly
    df['lat_val'] = df.apply(lambda x: x.get('lat') or x.get('center', {}).get('lat'), axis=1)
    df['lon_val'] = df.apply(lambda x: x.get('lon') or x.get('center', {}).get('lon'), axis=1)

    # Drop rows that have no coordinates at all (prevents Point(NaN, NaN) errors)
    df = df.dropna(subset=['lat_val', 'lon_val'])
    
    # Create Points (GeoJSON/PostGIS order: Longitude, Latitude)
    geometry = [Point(xy) for xy in zip(df['lon_val'], df['lat_val'])]
    gdf_points = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")

    # Convert LOR JSON to GeoDataFrame
    lor_gdf = gpd.GeoDataFrame.from_features(lor_polygons['features'], crs="EPSG:4326")

    # SPATIAL JOIN: This finds which district each point is 'within'
    joined = gpd.sjoin(gdf_points, lor_gdf, how="left", predicate="within")
    # Add this right after the joined = gpd.sjoin(...) line
    logging.info(f"DEBUG: Joined columns are: {joined.columns.tolist()}")

    #Replace NaN with None and Filter for Berlin
    # This ensures only points INSIDE a Berlin LOR district are kept
    joined = joined[joined['BEZIRK'].notna()].copy()

    # This converts Pandas 'NaN' to Python 'None'
    joined = joined.where(pd.notnull(joined), None)

    # CLEANING & MAPPING
    # 1. Clean the name from GeoJSON (remove accidental spaces)
    joined['district_name_clean'] = joined['BEZIRK'].str.strip()
    
    # 2. Map the 8-digit ID
    joined['mapped_district_id'] = joined['district_name_clean'].map(DISTRICT_MAPPING)

    

    # Logging unmapped districts for debugging
    unmapped = joined[joined['BEZIRK'].notna() & joined['mapped_district_id'].isna()]['BEZIRK'].unique()
    if len(unmapped) > 0:
        logging.warning(f"Found unmapped district names in GeoJSON: {unmapped}")

    # Package back into the dictionary format the insert function expects
    enriched_results = []
    for _, row in joined.iterrows():
        item = row.to_dict()
        item['lor_data'] = {
            "district": item.get('district_name_clean'),
            "district_id": item.get('mapped_district_id'),
            "neighborhood": item.get('OTEIL'),
            "neighborhood_id": item.get('spatial_name')
        }
        enriched_results.append(item)

    return enriched_results

# =============================================================================
# 5. SQL GENERATION
# =============================================================================

def build_create_table_sql(table_name, core_columns, unique_columns):
    cols = []
    # Combine all column definitions
    all_cols = core_columns['must_columns'] + core_columns['common_columns'] + unique_columns
    
    for col in all_cols:
        cols.append(f"{col['name']} {col['type']}")
    
    col_string = ",\n    ".join(cols)
    return f"CREATE TABLE IF NOT EXISTS {SCHEMA_NAME}.{table_name} (\n    {col_string}\n);"

# =============================================================================
# 6. DATABASE OPERATIONS (POSTGIS)
# =============================================================================

def insert_records(conn, table_name, records, core_columns, unique_columns):
    """
    Inserts data into Neon Postgres using PostGIS functions.
    Implements singularization for 'Unknown' labels (e.g., Bakeries -> Bakery).
    """
    cursor = conn.cursor()
    all_cols = core_columns['must_columns'] + core_columns['common_columns'] + unique_columns
    col_names = [c['name'] for c in all_cols]

    # Singularization logic for dynamic fallback name
    if table_name.lower().endswith('ies'):
        singular_label = table_name[:-3] + "y"
    else:
        singular_label = table_name.rstrip('s')
    
    fallback_name = f"Unknown {singular_label.capitalize()}"

   # Build SQL: Wraps geometry in PostGIS function
    placeholders = []
    for col in col_names:
        if col == "geometry":
            # Wraps the GeoJSON string so Postgres interprets it as a geometry object
            placeholders.append("ST_GeomFromGeoJSON(%s)")
        else:
            placeholders.append("%s")
    
    insert_query = f"""
        INSERT INTO {SCHEMA_NAME}.{table_name} ({', '.join(col_names)}) 
        VALUES ({', '.join(placeholders)})
    """
    
    
    inserted_count = 0
    for rec in records:
        tags = rec.get('tags', {})
        lor = rec.get('lor_data', {}) or {}
        
        # 1. Extract lat/lon reliably first
        lat = rec.get('lat') or rec.get('center', {}).get('lat')
        lon = rec.get('lon') or rec.get('center', {}).get('lon')

       # Format GeoJSON Point for PostGIS
        # Important: GeoJSON is [longitude, latitude]
        geojson_point = json.dumps({
            "type": "Point",
            "coordinates": [float(lon), float(lat)]
        })

        val_map = {
            "id": str(rec.get('id')),
            "geometry": geojson_point,  # <--- Corrected here
            "name": tags.get('name') or fallback_name,
            "latitude": lat,
            "longitude": lon,
            "district": lor.get('district'),
            "district_id": lor.get('district_id'),
            "neighborhood": lor.get('neighborhood'),
            "neighborhood_id": lor.get('neighborhood_id'),
            "addr_housenumber": tags.get('addr:housenumber'),
            "addr_street": tags.get('addr:street'),
            "addr_postcode": tags.get('addr:postcode'),
            "website": tags.get('website'),
            "phone_number": tags.get('phone') or tags.get('contact:phone'),
            "email": tags.get('email'),
            "wheelchair": True if tags.get('wheelchair') == 'yes' else False,
            "last_updated": datetime.now()
        }
        
        # Populate unique category columns
        for u_col in unique_columns:
            val_map[u_col['name']] = tags.get(u_col['name'])

        values = [val_map.get(name) for name in col_names]
        cursor.execute(insert_query, values)
        inserted_count += 1
        
    conn.commit()
    cursor.close()
    return inserted_count


# =============================================================================
#  7. LOGGING HELPERS
# =============================================================================

def ensure_metadata_table_exists(conn):
    cursor = conn.cursor()
    try:
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {SCHEMA_NAME}.osm_ingestion_log (
                table_name TEXT,
                tag_key TEXT,
                tag_value TEXT,
                records_fetched INTEGER,
                records_inserted INTEGER,
                run_timestamp TIMESTAMP
            );
        """)
        conn.commit()
    except Exception as e:
        conn.rollback()
        # If the error is about the table or type already existing, just ignore it
        if "already exists" in str(e).lower():
            logging.info("Metadata table already exists, skipping creation.")
        else:
            raise e
    finally:
        cursor.close()

def insert_ingestion_log(conn, table_name, tag_key, tag_value, fetched, inserted):
    cursor = conn.cursor()
    cursor.execute(f"""
        INSERT INTO {SCHEMA_NAME}.osm_ingestion_log 
        (table_name, tag_key, tag_value, records_fetched, records_inserted, run_timestamp)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (table_name, tag_key, str(tag_value), fetched, inserted, datetime.now()))
    conn.commit()
    cursor.close()

# =============================================================================
# 8. AIRFLOW PIPELINE ORCHESTRATION
# =============================================================================

def process_single_table(table_config):
    """Main execution block for each task in the DAG loop."""
    core_columns = load_core_columns()
    lor_data = load_lor_data()
    
    hook = PostgresHook(postgres_conn_id="neon_test")
    conn = hook.get_conn()
    
    try:
        ensure_metadata_table_exists(conn)
        
        table_name = table_config["table_name"]
        # Handle different JSON structures for tags
        tags = table_config.get("tags") or table_config.get("tag")
        
        logging.info(f"Processing table: {table_name}")
        
        elements = fetch_osm_data(tags)
        enriched = enrich_with_lor(elements, lor_data)
        
        create_sql = build_create_table_sql(table_name, core_columns, table_config["unique_columns"])
        
        cursor = conn.cursor()
        cursor.execute(create_sql)
        #conn.commit()
        
        # Ensure table is clean before inserting fresh data
        cursor.execute(f"TRUNCATE TABLE {SCHEMA_NAME}.{table_name};")
        conn.commit() # Commit the truncate before inserting new records

        inserted = insert_records(conn, table_name, enriched, core_columns, table_config["unique_columns"])
        
        # Determine primary tag for logging
        log_key = tags[0]['key'] if isinstance(tags, list) else tags['key']
        log_val = tags[0]['value'] if isinstance(tags, list) else tags['value']
        
        insert_ingestion_log(conn, table_name, log_key, log_val, len(elements), inserted)
        logging.info(f" Finished processing {table_name}: Fetched {len(elements)}, Inserted {inserted}")
        time.sleep(30)
    except Exception as e:
        logging.error(f" Error processing table {table_config.get('table_name')}: {e}")
        raise # Fail the Airflow task    
        
    finally:
        conn.close()
        

# =============================================================================
# 9. DAG INSTANTIATION
# =============================================================================

with DAG(
    dag_id="core_osm_table_generator",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    max_active_runs=1, # Prevents multiple DAG runs from fighting for API slots
    tags=["osm", "berlin","geopandas","core", "mvp"]
) as dag:

    # 1. Load your configurations (this must return a list of dictionaries)
    all_table_configs = load_table_configs()

    # 2. Variable to track the "previous" task for chaining
    prev_task = None

    # Dynamically generate tasks for each category. 
    for config in all_table_configs:
    # 'config' is now defined for this specific iteration
      task = PythonOperator(
        task_id=f"process_{config['table_name']}",
        python_callable=process_single_table,
        op_kwargs={'table_config': config},
        dag=dag,
        retries=5,
        retry_delay=timedelta(minutes=5)
      )

        # Chaining tasks: sequentially processing avoids Overpass API Rate Limits
      if prev_task:
            prev_task >> task
        
        # Move the pointer to the current task
      prev_task = task