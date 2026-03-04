import json
import logging
import os
import pandas as pd
import geopandas as gpd
import osmnx as ox
import time
import pendulum
from datetime import datetime, timedelta

from airflow.decorators import dag, task
from airflow.operators.python import get_current_context
from airflow.providers.postgres.hooks.postgres import PostgresHook

# =============================================================================
# 1. SETTINGS & CONFIGURATION
# =============================================================================
SCHEMA_NAME = "berlin_automation_nigar_parallel"
DAG_FOLDER = os.path.dirname(os.path.abspath(__file__))
AIRFLOW_CONN_ID = "neon_test"

DISTRICT_MAPPING = {
    'Mitte': '11001001', 'Friedrichshain-Kreuzberg': '11002002',
    'Pankow': '11003003', 'Charlottenburg-Wilmersdorf': '11004004',
    'Spandau': '11005005', 'Steglitz-Zehlendorf': '11006006',
    'Tempelhof-Schöneberg': '11007007', 'Neukölln': '11008008',
    'Treptow-Köpenick': '11009009', 'Marzahn-Hellersdorf': '11010010',
    'Lichtenberg': '11011011', 'Reinickendorf': '11012012'
}

# Configure OSMNx Caching to avoid hitting API rate limits
CACHE_DIR = os.path.join(DAG_FOLDER, 'osmnx_cache')
os.makedirs(CACHE_DIR, exist_ok=True)
ox.settings.use_cache = True
ox.settings.cache_folder = CACHE_DIR

# =============================================================================
# 2. DAG DEFINITION
# =============================================================================

@dag(
    dag_id="berlin_osmnx_parallel",
    default_args={
        'owner': 'nigar',
        'retries': 2,
        'retry_delay': timedelta(minutes=5)
    },
    start_date=pendulum.today('UTC').add(days=-1),
    schedule=None,
    catchup=False,
    max_active_tasks=6,
    tags=["berlin", "osmnx", "parallel"]
)
def berlin_poi_pipeline():

    @task
    def pre_flight_checks():
        """
        One-stop setup: Creates schema, extensions, log table, 
        and primes the OSMNx cache sequentially to prevent race conditions.
        """
        # --- DB Setup ---
        hook = PostgresHook(postgres_conn_id=AIRFLOW_CONN_ID)
        engine = hook.get_sqlalchemy_engine()
        
        logging.info(f"Initializing Schema: {SCHEMA_NAME}")
        with engine.begin() as conn:
            conn.execute(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA_NAME};")
            conn.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
        
        # Ensure log table exists
        cols = ["table_name", "row_count", "duration_seconds", "ingestion_timestamp", "status"]
        empty_log = pd.DataFrame(columns=cols)
        empty_log.to_sql("osm_ingestion_log", engine, schema=SCHEMA_NAME, if_exists='append', index=False)

        # --- Cache Priming ---
        logging.info(" Downloading Berlin boundaries to prime local cache...")
        # This downloads the map once so parallel tasks can read from disk
        ox.geocode_to_gdf("Berlin, Germany")
        
        return "READY"

    @task
    def process_table(table_config: dict):
        """
        Processes a single OSM table in parallel.
        Uses MultiIndex extraction to ensure real OSM IDs are captured.
        """
        start_time = time.time()
        t_name = table_config["table_name"]
        
        # Define hook/engine immediately to prevent UnboundLocalError in 'except' block
        hook = PostgresHook(postgres_conn_id=AIRFLOW_CONN_ID)
        engine = hook.get_sqlalchemy_engine()
        ctx = get_current_context()
        run_ts = ctx["logical_date"]
        
        row_count = 0
        status = "STARTED"

        try:
            # 1. Load Local Configs
            core_path = os.path.join(DAG_FOLDER, 'config', 'core_columns.json')
            lor_path = os.path.join(DAG_FOLDER, 'config', 'lor_ortsteile.geojson')
            
            with open(core_path) as f: core_cols = json.load(f)
            lor_gdf = gpd.read_file(lor_path)
            
            tags_list = table_config.get("tags") or table_config.get("tag")
            ox_tags = {t['key']: t['value'] for t in (tags_list if isinstance(tags_list, list) else [tags_list])}

            # 2. Fetch Data (Hits local cache primed by pre_flight)
            gdf = ox.features_from_place("Berlin, Germany", tags=ox_tags)
            
            if gdf is None or gdf.empty:
                raise ValueError(f"No OSM data found for tags: {ox_tags}")

            # --- STAGE 0: ID EXTRACTION (MultiIndex Level 1) ---
            # We grab this BEFORE reset_index()
            gdf['id'] = gdf.index.get_level_values(1).astype(str)
            gdf['osmid'] = gdf.index.get_level_values(1).astype(str)

            # --- STAGE 1: GEOMETRY & PROJECTION ---
            # Using centroid (or representative_point for better accuracy)
            gdf['geometry'] = gdf.to_crs(epsg=3857).centroid.to_crs(epsg=4326)
            gdf['latitude'] = gdf.geometry.y
            gdf['longitude'] = gdf.geometry.x

            # --- STAGE 2: SPATIAL JOIN ---
            gdf = gdf.reset_index(drop=True)
            joined = gpd.sjoin(gdf.to_crs(lor_gdf.crs), lor_gdf, how="left", predicate="within")
            joined = joined[joined['BEZIRK'].notna()].copy()
            
            if joined.empty:
                raise ValueError("All fetched points fall outside Berlin LOR boundaries")
                
            # --- STAGE 3: DATA MAPPING ---
            joined = gpd.GeoDataFrame(joined, geometry='geometry', crs=lor_gdf.crs)
            
            # Name fallback logic
            label = t_name[:-3] + "y" if t_name.lower().endswith('ies') else t_name.rstrip('s')
            joined['name'] = joined['name'].fillna(f"Unknown {label.capitalize()}")
            
            joined['district'] = joined['BEZIRK']
            joined['district_id'] = joined['BEZIRK'].map(DISTRICT_MAPPING)
            joined['neighborhood'] = joined['OTEIL']
            joined['neighborhood_id'] = joined['spatial_name']
            joined['last_updated'] = run_ts

            # Standardize Address Columns
            addr_map = {'addr:housenumber': 'addr_housenumber', 'addr:street': 'addr_street', 'addr:postcode': 'addr_postcode'}
            joined = joined.rename(columns=addr_map)
            
            # Select only columns defined in core + unique configs
            allowed = [c['name'] for c in (core_cols['must_columns'] + core_cols['common_columns'] + table_config["unique_columns"])]
            joined['geometry'] = joined['geometry'].apply(lambda x: x.wkt if x else None)
            final_df = joined[[c for c in allowed if c in joined.columns]].copy()

            # 4. Final Load to Neon
            final_df.to_sql(t_name, engine, schema=SCHEMA_NAME, if_exists='replace', index=False)
            row_count = len(final_df)
            status = "SUCCESS"

        except Exception as e:
            logging.error(f" Failed to process {t_name}: {e}")
            status = f"FAILED: {str(e)[:50]}"

        # 5. Guaranteed Logging
        duration = round(time.time() - start_time, 2)
        log_entry = pd.DataFrame([{
            "table_name": t_name, "row_count": row_count, 
            "duration_seconds": duration, "ingestion_timestamp": run_ts, "status": status
        }])
        log_entry.to_sql("osm_ingestion_log", engine, schema=SCHEMA_NAME, if_exists='append', index=False)
        
        return {"table": t_name, "rows": row_count}
    
    @task
    def validate_ingestion(results):
        """
        Final Validation: Checks the internal results list to ensure 
        no critical table returned 0 rows.
        """
        hook = PostgresHook(postgres_conn_id=AIRFLOW_CONN_ID)
        
        logging.info(" Starting Data Validation Check...")
        for r in results:
            table = r['table']
            rows = r['rows']
            if rows == 0:
                logging.warning(f" Table {table} was processed but contains 0 rows.")
            else:
                logging.info(f" Table {table}: {rows} rows verified.")
        
        return "Validation Complete"
    
    @task
    def log_summary(results):
        """Aggregates results and logs final stats to Airflow logs."""
        total_rows = sum(r['rows'] for r in results)
        success_count = sum(1 for r in results if r['rows'] > 0)
        
        logging.info("========================================")
        logging.info(f" DAG COMPLETE")
        logging.info(f"Tables Processed: {len(results)} ({success_count} successful)")
        logging.info(f"Total POIs Inserted: {total_rows}")
        logging.info("========================================")

    # --- EXECUTION FLOW ---
    # Load table list from config
    with open(os.path.join(DAG_FOLDER, 'config', 'osm_tables.json')) as f:
        tables_list = json.load(f)["tables"]

    # 1. Run Pre-flight (DB + Cache)
    setup_ready = pre_flight_checks()
    
    # 2. Map Parallel Tasks (Passes the setup signal to enforce dependency)
    processing = process_table.expand(table_config=tables_list)
    
    # 3. Validation and Summary
    validation = validate_ingestion(processing)
    summary = log_summary(processing)

    # --- ENFORCE THE ORDER HERE ---
    # This ensures setup finishes BEFORE processing starts
    setup_ready >> processing >> validation >> summary

# Instantiate the pipeline
berlin_poi_pipeline()