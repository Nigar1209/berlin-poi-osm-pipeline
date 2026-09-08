import json
import logging
from datetime import datetime , timedelta
import pandas as pd
import osmnx as ox
import os
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
import time

# FORCE THESE SETTINGS GLOBALLY
ox.settings.max_query_area_size = 2500000000 # 50km x 50km
ox.settings.requests_timeout = 300
ox.settings.log_console = True

# --- Utility Functions ---
def clean_val(val):
    """Converts NaN or None to a real Python None for Postgres."""
    if pd.isna(val) or val is None:
        return None
    return val

SCHEMA_NAME = "berlin_automation_nigar"

# --- 2️⃣ Configuration Loader Functions ---

DAG_FOLDER = os.path.dirname(os.path.abspath(__file__))

def load_core_columns():
    # This looks for the file in a sub-folder named 'config' inside your dags folder
    path = os.path.join(DAG_FOLDER, 'config', 'core_columns.json')
    with open(path, 'r') as f:  
        return json.load(f)

def load_table_configs():
    path = os.path.join(DAG_FOLDER, 'config', 'osm_tables.json')
    with open(path, 'r') as f:
        return json.load(f)["tables"]

def load_lor_data():
    path = os.path.join(DAG_FOLDER, 'config', 'lor_ortsteile.geojson')
    try:
        with open(path, 'r') as f:
            return json.load(f) 
    except FileNotFoundError:
        logging.warning(f"LOR data file not found at {path}. Enrichment will return NULLs.")
        return []

def normalize_tags(table_cfg):
    """
    Convert the tags list from osm_tables.json into the dict format expected by OSMnx.
    Supports:
    - multiple entries for same key (dedup list)
    - values as scalar or list
    """
    tags = {}
    for t in table_cfg.get("tags", []) or []:
        k = t["key"]
        v = t["value"]
        if k not in tags:
            tags[k] = v
        else:
            existing = tags[k]
            if not isinstance(existing, list):
                existing = [existing]
            if isinstance(v, list):
                existing.extend(v)
            else:
                existing.append(v)

            # de-dup preserve order
            seen = set()
            dedup = []
            for x in existing:
                if x not in seen:
                    seen.add(x)
                    dedup.append(x)
            tags[k] = dedup

    return tags
# --- 3️⃣ OSM Fetch Function ---

def fetch_osm_data_osmnx(table_config):
    """
    Uses OSMnx to fetch data based on the new JSON structure.
    Returns a list of records compatible with your existing pipeline.
    """
    # 1. Prepare the tags dictionary for OSMnx
    # Translates [{"key": "shop", "value": ["bakery"]}] -> {"shop": ["bakery"]}
    #osm_filter = {}

    osm_filter = normalize_tags(table_config)
    if 'bakery' in osm_filter:
        del osm_filter['bakery'] # Remove the 'bakery=yes' requirement for now to test
    
    logging.info(f"OSMnx fetching {table_config['table_name']} with filter: {osm_filter}")

    try:
        # 2. Fetch from your specific bounding box (to keep the "Outskirts" data)
        # Bbox order: north, south, east, west
        bbox = (52.7, 52.3, 13.7, 13.0)
        
        gdf = ox.features_from_bbox(bbox, tags=osm_filter)
        
        
        if gdf.empty:
            logging.info(f"No data found for {table_config['table_name']}")
            return []

        # 3. Convert all geometries to Points (Centroids)
        # This ensures Polygons (buildings) become Points for your database
        gdf['geometry'] = gdf.geometry.centroid

        # 4. Format for your existing pipeline
        records = []
        logging.info(f"Found {len(gdf)} features in OSMnx for {table_config['table_name']}") # ADD THIS LOG
        for idx, row in gdf.iterrows():
            # OSMnx index is (element_type, osmid)
            osm_id = idx[1] if isinstance(idx, tuple) else idx
            centroid = row.geometry.centroid
            # Create a 'tags' dictionary from the row columns
            # This allows your existing column extraction logic to work
            tag_data = row.to_dict()
            
            records.append({
                'id': osm_id,
                'lat': centroid.y,
                'lon': centroid.x,
                'tags': tag_data
            })
        logging.info(f"Successfully prepared {len(records)} records for insertion into {table_config['table_name']}")
        return records

    except Exception as e:
        logging.error(f"Error fetching {table_config['table_name']}: {e}")
        raise
# --- 4️⃣ LOR Enrichment Function ---

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

DISTRICT_MAPPING = {
    "Mitte": "11001001",
    "Friedrichshain-Kreuzberg": "11002002",
    "Pankow": "11003003",
    "Charlottenburg-Wilmersdorf": "11004004",
    "Spandau": "11005005",
    "Steglitz-Zehlendorf": "11006006",
    "Tempelhof-Schöneberg": "11007007",
    "Neukölln": "11008008",
    "Treptow-Köpenick": "11009009",
    "Marzahn-Hellersdorf": "11010010",
    "Lichtenberg": "11011011",
    "Reinickendorf": "11012012",
}

def enrich_with_lor(records, lor_geojson):
    """
    Enriches records with LOR data and the new numeric District IDs.
    """
    enriched = []
    for rec in records:
        lat, lon = rec['lat'], rec['lon']
        match = {
            "district": None,
            "district_id": None,
            "neighborhood": None,
            "neighborhood_id": None
        }
        
        for poly_feat in lor_geojson['features']:
            if is_inside(lat, lon, poly_feat):
                props = poly_feat['properties']
                d_name = props.get('BEZIRK') # Ensure this matches your GeoJSON key
                
                match = {
                    "district": d_name,
                    "district_id": DISTRICT_MAPPING.get(d_name),
                    "neighborhood": props.get('OTEIL'),
                    "neighborhood_id": props.get('spatial_alias')
                }
                break # Stop searching once found
        
        rec.update(match)
        enriched.append(rec)
    return enriched

# --- 5️⃣ Schema Builder Function ---

def build_create_table_sql(table_name, core_columns, unique_columns):
    cols = []
    # Combine all column definitions
    all_cols = core_columns['must_columns'] + core_columns['common_columns'] + unique_columns
    
    for col in all_cols:
        cols.append(f"{col['name']} {col['type']}")
    
    col_string = ",\n    ".join(cols)
    return f"CREATE TABLE IF NOT EXISTS {SCHEMA_NAME}.{table_name} (\n    {col_string}\n);"

# --- 6️⃣ Insert Function ---

def insert_records(conn, table_name, records, core_columns, unique_columns):
    cursor = conn.cursor()
    all_cols = core_columns['must_columns'] + core_columns['common_columns'] + unique_columns
    col_names = [c['name'] for c in all_cols]
    
    # Keeping your original sequential query style
    insert_query = f"INSERT INTO {SCHEMA_NAME}.{table_name} ({', '.join(col_names)}) VALUES ({', '.join(['%s'] * len(col_names))})"
    
    inserted_count = 0
    for rec in records:
        # OSMnx provides data in a flat row; we ensure it's treated as a dict
        tags = rec.get('tags', {})
        
        # We use the top-level keys we added in the enrichment step
        lat = rec.get('lat')
        lon = rec.get('lon')

        # GeoJSON is strictly [longitude, latitude]
        geojson_point = json.dumps({
            "type": "Point",
            "coordinates": [float(lon), float(lat)]
        })

        val_map = {
            "id": str(rec.get('id')),
            "geometry": json.dumps({"type": "Point", "coordinates": [float(lon), float(lat)]}),
            "name": tags.get('name'),
            "latitude": lat,
            "longitude": lon,
            "district": rec.get('district'),
            "district_id": rec.get('district_id'),
            "neighborhood": rec.get('neighborhood'),
            "neighborhood_id": rec.get('neighborhood_id'),
            "addr_housenumber": tags.get('addr:housenumber'),
            "addr_street": tags.get('addr:street'),
            "addr_postcode": tags.get('addr:postcode'),
            "website": tags.get('website'),
            "phone_number": tags.get('phone') or tags.get('contact:phone'),
            "email": tags.get('email'),
            "wheelchair": True if tags.get('wheelchair') == 'yes' else False,
            "last_updated": datetime.now()
        }
        
        # Add the table-specific columns from your new JSON
        for u_col in unique_columns:
            val_map[u_col['name']] = tags.get(u_col['name'])

        # This applies clean_val to every single entry in the map
        val_map = {k: clean_val(v) for k, v in val_map.items()}    

        values = [val_map.get(name) for name in col_names]
        
        try:
            cursor.execute(insert_query, values)
            inserted_count += 1
        except Exception as e:
            logging.error(f"Failed to insert record {rec.get('id')} into {table_name}: {e}")
            conn.rollback() # Rollback only this specific failed record
            continue # Move to the next record immediately
        
    conn.commit()
    cursor.close()
    return inserted_count

# --- 7️⃣ Metadata Table Helpers ---

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

# --- 8️⃣ Main Processing Function ---

def process_single_table(table_config):
    core_columns = load_core_columns()
    lor_data = load_lor_data()
    
    hook = PostgresHook(postgres_conn_id="neon_test")
    conn = hook.get_conn()
    
    try:
        ensure_metadata_table_exists(conn)
        
        table_name = table_config["table_name"]
        # Handle different JSON structures for tags
        tags = table_config.get("tags")
        
        logging.info(f"Processing table: {table_name}")

        if not tags:
            logging.error(f"No tags found for {table_name}")
            return
        
        elements = fetch_osm_data_osmnx(table_config)
        enriched = enrich_with_lor(elements, lor_data)
        
        create_sql = build_create_table_sql(table_name, core_columns, table_config["unique_columns"])
        
        cursor = conn.cursor()
        cursor.execute(create_sql)
        #conn.commit()
        
        # Ensure table is clean before inserting fresh data
        cursor.execute(f"TRUNCATE TABLE {SCHEMA_NAME}.{table_name};")
        conn.commit() # Commit the truncate before inserting new records

        inserted = insert_records(conn, table_name, enriched, core_columns, table_config["unique_columns"])
        
       # 4. Refined Logging Logic for List Values
        # If value is ['hotel', 'hostel'], we join it to a string 'hotel, hostel' for the log
        first_tag = tags[0] if isinstance(tags, list) else tags
        log_key = first_tag['key']
        raw_val = first_tag['value']
        log_val = ", ".join(raw_val) if isinstance(raw_val, list) else raw_val
        
        insert_ingestion_log(conn, table_name, log_key, log_val, len(elements), inserted)
        logging.info(f" Finished processing {table_name}: Fetched {len(elements)}, Inserted {inserted}")
        time.sleep(30)
    except Exception as e:
        logging.error(f" Error processing table {table_config.get('table_name')}: {e}")
        conn.rollback() # Rollback any uncommitted changes for this table
        raise # Fail the Airflow task    
        
    finally:
        conn.close()
        

# --- DAG Definition ---

with DAG(
    dag_id="osm_table_generator",
    #default_args=default_args,
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    max_active_runs=1, # Prevents multiple DAG runs from fighting for API slots
    tags=["osm", "core", "mvp"],
    # Apply a global timeout of 1 hour for the whole DAG
    dagrun_timeout=timedelta(hours=1)
) as dag:

    # 1. Your list of tables (usually read from your JSON config)
    #tables_to_process = ["bakeries", "hospitals", "hotels", "kindergartens", "malls", "museums"]

    # 1. Load your configurations (this must return a list of dictionaries)
    all_table_configs = load_table_configs()

    # 2. Variable to track the "previous" task for chaining
    prev_task = None

# 3. The Loop must contain the task definition
    for config in all_table_configs:
    # 'config' is now defined for this specific iteration
      task = PythonOperator(
        task_id=f"process_{config['table_name']}",
        python_callable=process_single_table,
        op_kwargs={'table_config': config},
        #dag=dag,
        execution_timeout=timedelta(minutes=30),
        retries=3,
        retry_delay=timedelta(minutes=5)
      )

        # This is the "Magic" that creates the one-by-one sequence
      if prev_task:
            prev_task >> task
        
        # Move the pointer to the current task
      prev_task = task
