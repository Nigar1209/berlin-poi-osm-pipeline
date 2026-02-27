import json
import logging
import os
import time
import pandas as pd
import geopandas as gpd
import requests
import psycopg2
from datetime import datetime, timedelta
from shapely.geometry import Point

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook

# =============================================================================
# 1. SETTINGS & MAPPING
# =============================================================================
SCHEMA_NAME = "berlin_automation_nigar"
DAG_FOLDER = os.path.dirname(os.path.abspath(__file__))

DISTRICT_MAPPING = {
    'Mitte': '11001001', 'Friedrichshain-Kreuzberg': '11002002',
    'Pankow': '11003003', 'Charlottenburg-Wilmersdorf': '11004004',
    'Spandau': '11005005', 'Steglitz-Zehlendorf': '11006006',
    'Tempelhof-Schöneberg': '11007007', 'Neukölln': '11008008',
    'Treptow-Köpenick': '11009009', 'Marzahn-Hellersdorf': '11010010',
    'Lichtenberg': '11011011', 'Reinickendorf': '11012012'
}

# =============================================================================
# 2. CORE LOGIC (Adapted for Airflow)
# =============================================================================

def fetch_osm_data_area(tags, retries=3, backoff_factor=60):
    base_url = "https://overpass-api.de/api/interpreter"
    tag_list = tags if isinstance(tags, list) else [tags]
    tag_filters = "".join([f'["{t["key"]}"~"{"|".join(t["value"]) if isinstance(t["value"], list) else t["value"]}"]' for t in tag_list])

    query = f"""
    [out:json][timeout:600];
    area["name"="Berlin"]["admin_level"="4"]->.searchArea;
    (
      node{tag_filters}(area.searchArea);
      way{tag_filters}(area.searchArea);
      relation{tag_filters}(area.searchArea);
    );
    out center;
    """
    for i in range(retries):
        try:
            response = requests.post(base_url, data={'data': query}, timeout=610)
            response.raise_for_status()
            return response.json().get('elements', [])
        except Exception as e:
            if i < retries - 1:
                logging.info(f"Rate limit or error. Retrying in {backoff_factor}s...")
                time.sleep(backoff_factor)
            else: raise e

def process_and_enrich(elements, lor_geojson):
    if not elements: return []
    raw_df = pd.DataFrame(elements)
    tags_df = pd.json_normalize(raw_df['tags'])
    df = pd.concat([raw_df.drop('tags', axis=1), tags_df], axis=1)
    
    # Handle lat/lon for nodes and ways/relations
    df['lat'] = df['lat'].fillna(df['center'].apply(lambda x: x.get('lat') if isinstance(x, dict) else None))
    df['lon'] = df['lon'].fillna(df['center'].apply(lambda x: x.get('lon') if isinstance(x, dict) else None))
    df = df.dropna(subset=['lat', 'lon'])
    
    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.lon, df.lat), crs="EPSG:4326")
    lor_gdf = gpd.GeoDataFrame.from_features(lor_geojson['features'], crs="EPSG:4326")
    
    joined = gpd.sjoin(gdf, lor_gdf, how="left", predicate="within")
    joined = joined[joined['BEZIRK'].notna()].copy()
    
    results = []
    for _, row in joined.iterrows():
        dist_name = str(row.get('BEZIRK', '')).strip()
        res = row.to_dict()
        res['lor_data'] = {
            "district": dist_name, "district_id": DISTRICT_MAPPING.get(dist_name),
            "neighborhood": row.get('OTEIL'), "neighborhood_id": row.get('spatial_name')
        }
        results.append(res)
    return results

def build_create_table_sql(table_name, core_columns, unique_columns):
    all_cols = core_columns['must_columns'] + core_columns['common_columns'] + unique_columns
    cols = [f"{col['name']} {col['type']}" for col in all_cols]
    return f"CREATE TABLE IF NOT EXISTS {SCHEMA_NAME}.{table_name} ({', '.join(cols)});"

# =============================================================================
# 3. AIRFLOW TASK WRAPPER
# =============================================================================

def process_single_table_task(table_config):
    """Execution logic for a single Airflow task."""
    # 1. Load Configs
    with open(os.path.join(DAG_FOLDER, 'config', 'core_columns.json')) as f: core_cols = json.load(f)
    with open(os.path.join(DAG_FOLDER, 'config', 'lor_ortsteile.geojson')) as f: lor_json = json.load(f)
    
    t_name = table_config["table_name"]
    tags = table_config.get("tags") or table_config.get("tag")
    
    # 2. Database Connection using Airflow Hook
    pg_hook = PostgresHook(postgres_conn_id="neon_test") # Use your neon connection ID
    conn = pg_hook.get_conn()
    
    try:
        # 3. Fetch & Process
        logging.info(f"--- Starting Table: {t_name} ---")
        raw = fetch_osm_data_area(tags)
        clean = process_and_enrich(raw, lor_json)
        logging.info(f" {len(clean)} records ready for {t_name}")

        # 4. Prepare Table
        with conn.cursor() as cur:
            cur.execute(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA_NAME};")
            cur.execute(build_create_table_sql(t_name, core_cols, table_config["unique_columns"]))
            cur.execute(f"TRUNCATE TABLE {SCHEMA_NAME}.{t_name};")
            conn.commit()

        # 5. Insert Records
        cursor = conn.cursor()
        # --- ADD THIS LINE TO HANDLE SINGULAR NAME ---
        # Logic: remove trailing 's', or handle 'ies' -> 'y'
        singular_label = t_name[:-3] + "y" if t_name.lower().endswith('ies') else t_name.rstrip('s')
        fallback_name = f"Unknown {singular_label.capitalize()}"
        # ---------------------------------------------
        all_cols = core_cols['must_columns'] + core_cols['common_columns'] + table_config["unique_columns"]
        col_names = [c['name'] for c in all_cols]
        placeholders = ["ST_GeomFromGeoJSON(%s)" if c == "geometry" else "%s" for c in col_names]
        insert_query = f"INSERT INTO {SCHEMA_NAME}.{t_name} ({', '.join(col_names)}) VALUES ({', '.join(placeholders)})"
        
        for rec in clean:
            lat, lon = rec.get('lat'), rec.get('lon')
            geojson_point = json.dumps({"type": "Point", "coordinates": [float(lon), float(lat)]})
            lor = rec.get('lor_data', {})
            
            val_map = {
                "id": str(rec.get('id')), "geometry": geojson_point, "name": rec.get('name') if pd.notnull(rec.get('name')) else fallback_name,
                "latitude": lat, "longitude": lon, "district": lor.get('district'), "district_id": lor.get('district_id'),
                "neighborhood": lor.get('neighborhood'), "neighborhood_id": lor.get('neighborhood_id'),
                "addr_housenumber": rec.get('addr:housenumber'), "addr_street": rec.get('addr:street'),
                "addr_postcode": rec.get('addr:postcode'), "website": rec.get('website'),
                "phone_number": rec.get('phone'), "email": rec.get('email'),
                "wheelchair": True if rec.get('wheelchair') == 'yes' else False, "last_updated": datetime.now()
            }
            for u_col in table_config["unique_columns"]: val_map[u_col['name']] = rec.get(u_col['name'])
            cursor.execute(insert_query, [val_map.get(name) for name in col_names])
        
        conn.commit()
        logging.info(f" Success: {t_name} populated.")
        
        # Mandatory cool-down to protect API
        time.sleep(30)
        
    finally:
        conn.close()

# =============================================================================
# 4. DAG DEFINITION
# =============================================================================

default_args = {
    'owner': 'nigar',
    'retries': 3,
    'retry_delay': timedelta(minutes=2)
}

with DAG(
    dag_id="sequential_berlin_osm_generator",
    default_args=default_args,
    start_date=datetime(2024, 1, 1),
    schedule=None, # Trigger manually for now
    catchup=False,
    max_active_runs=1,
    tags=["berlin", "osm", "sequential"]
) as dag:

    # Load table names from config to create tasks
    with open(os.path.join(DAG_FOLDER, 'config', 'osm_tables.json')) as f:
        tables = json.load(f)["tables"]

    prev_task = None

    for config in tables:
        task_id = f"process_{config['table_name']}"
        
        task = PythonOperator(
            task_id=task_id,
            python_callable=process_single_table_task,
            op_kwargs={'table_config': config}
        )

        # SEQUENTIAL CHAINING: This forces the tables to wait for each other
        if prev_task:
            prev_task >> task
        
        prev_task = task