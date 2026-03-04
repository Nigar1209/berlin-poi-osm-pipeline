import json
import logging
import os
import pandas as pd
import geopandas as gpd
import osmnx as ox
import time
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook

# =============================================================================
# 1. SETTINGS & MAPPING
# =============================================================================
SCHEMA_NAME = "berlin_automation_nigar_sequen"
DAG_FOLDER = os.path.dirname(os.path.abspath(__file__))

# Configure OSMNx Caching
CACHE_DIR = os.path.join(DAG_FOLDER, 'osmnx_cache')
os.makedirs(CACHE_DIR, exist_ok=True)
ox.settings.use_cache = True
ox.settings.cache_folder = CACHE_DIR

DISTRICT_MAPPING = {
    'Mitte': '11001001', 'Friedrichshain-Kreuzberg': '11002002',
    'Pankow': '11003003', 'Charlottenburg-Wilmersdorf': '11004004',
    'Spandau': '11005005', 'Steglitz-Zehlendorf': '11006006',
    'Tempelhof-Schöneberg': '11007007', 'Neukölln': '11008008',
    'Treptow-Köpenick': '11009009', 'Marzahn-Hellersdorf': '11010010',
    'Lichtenberg': '11011011', 'Reinickendorf': '11012012'
}

# 2. CORE LOGIC (Using OSMNx & Vectorized Joins)
# =============================================================================

def process_single_table_task(table_config):
    start_time = time.time()
    t_name = table_config["table_name"]
    row_count = 0
    status = "STARTED"
    
    try:
        with open(os.path.join(DAG_FOLDER, 'config', 'core_columns.json')) as f: 
            core_cols = json.load(f)
        lor_gdf = gpd.read_file(os.path.join(DAG_FOLDER, 'config', 'lor_ortsteile.geojson'))
        tags = table_config.get("tags") or table_config.get("tag")
        ox_tags = {t['key']: t['value'] for t in (tags if isinstance(tags, list) else [tags])}
    except Exception as e:
        logging.error(f"Setup Error for {t_name}: {e}")
        return

    logging.info(f"--- Fetching {t_name} via OSMNx ---")
    try:
        gdf = ox.features_from_place("Berlin, Germany", tags=ox_tags)
    except Exception as e:
        logging.warning(f"No data found for {t_name} in OSM: {e}")
        status = "NO_OSM_DATA"
    else:
        # STEP 1: Extract OSM ID to a TEMP name to avoid sjoin conflicts
        # Rename the index levels so 'id' doesn't exist in the index metadata
        gdf.index.names = ['element_type', 'osmid_original'] 
        
        # Now extract our temp column
        # Rename the index levels so 'id' doesn't exist in the index metadata
        gdf.index.names = ['element_type', 'osmid_original'] 
        
        # Now extract our temp column
        gdf['osm_id_temp'] = gdf.index.get_level_values('osmid_original').astype(str)
        
        
        
        # 3. Spatial Processing
        gdf['geometry'] = gdf.to_crs(epsg=3857).centroid.to_crs(epsg=4326)
        gdf['latitude'] = gdf.geometry.y
        gdf['longitude'] = gdf.geometry.x

        # 4. Vectorized Spatial Join (No 'id' conflict now!)
        joined = gpd.sjoin(gdf.to_crs(lor_gdf.crs), lor_gdf, how="left", predicate="within")
        joined = joined[joined['BEZIRK'].notna()].copy()

        if not joined.empty:
            # STEP 2: Now we safely finalize the IDs
            joined = joined.reset_index(drop=True)
            joined['id'] = joined['osm_id_temp']
            joined['osmid'] = joined['id']
            
            joined = gpd.GeoDataFrame(joined, geometry='geometry', crs=lor_gdf.crs)

            # Data Preparation
            singular_label = t_name[:-3] + "y" if t_name.lower().endswith('ies') else t_name.rstrip('s')
            fallback_name = f"Unknown {singular_label.capitalize()}"
            
            joined['name'] = joined['name'].fillna(fallback_name)
            joined['district'] = joined['BEZIRK']
            joined['district_id'] = joined['BEZIRK'].map(DISTRICT_MAPPING)
            joined['neighborhood'] = joined['OTEIL']
            joined['neighborhood_id'] = joined['spatial_name']
            joined['last_updated'] = datetime.now()
            
            # Handle Wheelchair & Address Renaming
            if 'wheelchair' in joined.columns:
                joined['wheelchair'] = joined['wheelchair'].apply(lambda x: True if x == 'yes' else False)
            else:
                joined['wheelchair'] = False

            joined = joined.rename(columns={
                'addr:housenumber': 'addr_housenumber', 
                'addr:street': 'addr_street', 
                'addr:postcode': 'addr_postcode'
            })

            # 5. Database Upload (Upsert)
            pg_hook = PostgresHook(postgres_conn_id="neon_test")
            engine = pg_hook.get_sqlalchemy_engine()
            
            upload_df = joined.copy()
            upload_df['geometry'] = upload_df['geometry'].apply(lambda x: x.wkt if x else None)
            
            all_cols_config = core_cols['must_columns'] + core_cols['common_columns'] + table_config["unique_columns"]
            all_col_names = [c['name'] for c in all_cols_config]
            final_df = upload_df[[c for c in all_col_names if c in upload_df.columns]]

            if not final_df.empty:
                staging_table = f"temp_stage_{t_name}"
                with engine.begin() as conn:
                    # Staging
                    final_df.to_sql(staging_table, conn, schema=SCHEMA_NAME, if_exists='replace', index=False)
                    # Create Main if missing
                    conn.execute(f"CREATE TABLE IF NOT EXISTS {SCHEMA_NAME}.{t_name} (LIKE {SCHEMA_NAME}.{staging_table} INCLUDING ALL);")
                    # Check PK
                    pk_exists = conn.execute(f"SELECT 1 FROM information_schema.table_constraints WHERE table_schema='{SCHEMA_NAME}' AND table_name='{t_name}' AND constraint_type='PRIMARY KEY';").fetchone()
                    if not pk_exists:
                        conn.execute(f"ALTER TABLE {SCHEMA_NAME}.{t_name} ADD PRIMARY KEY (id);")
                    # UPSERT
                    cols = ", ".join([f'"{c}"' for c in final_df.columns])
                    upd = ", ".join([f'"{c}" = EXCLUDED."{c}"' for c in final_df.columns if c != 'id'])
                    conn.execute(f"INSERT INTO {SCHEMA_NAME}.{t_name} ({cols}) SELECT {cols} FROM {SCHEMA_NAME}.{staging_table} ON CONFLICT (id) DO UPDATE SET {upd};")
                    # Cleanup
                    conn.execute(f"DROP TABLE {SCHEMA_NAME}.{staging_table};")

                row_count = len(final_df)
                status = "SUCCESS"
            else:
                status = "NO_VALID_GEOMETRY"
        else:
            status = "ZERO_RESULTS_IN_BOUNDARIES"

    # =========================================================================
    # 6. INGESTION LOGGING (Always executes)
    # =========================================================================
    duration = round(time.time() - start_time, 2)
    pg_hook = PostgresHook(postgres_conn_id="neon_test")
    engine = pg_hook.get_sqlalchemy_engine()
    
    log_df = pd.DataFrame([{
        "table_name": t_name,
        "row_count": row_count,
        "duration_seconds": duration,
        "ingestion_timestamp": datetime.now(),
        "status": status
    }])
    
    log_df.to_sql(
        "osm_ingestion_log", 
        engine, 
        schema=SCHEMA_NAME, 
        if_exists='append', 
        index=False
    )
    logging.info(f" {t_name} log saved with status: {status}") 


# =============================================================================
# NEW POSITION: Move this here!
# =============================================================================
def log_total_runtime(**context):
    """Calculates and logs the full duration of the DAG run."""
    dag_run = context['dag_run']
    start_time = dag_run.start_date
    end_time = datetime.now(start_time.tzinfo) 
    duration = end_time - start_time
    minutes, seconds = divmod(duration.total_seconds(), 60)
    logging.info(f" TOTAL DAG RUNTIME: {int(minutes)}m {int(seconds)}s")

# =============================================================================
# 3. DAG DEFINITION (PARALLEL STRUCTURE)
# =============================================================================

# Add this small function right before the DAG definition
def setup_log_table():
    """Ensures the log table exists before parallel tasks start to avoid race conditions."""
    pg_hook = PostgresHook(postgres_conn_id="neon_test")
    engine = pg_hook.get_sqlalchemy_engine()
    
    # Create an empty template of the log table
    empty_log = pd.DataFrame(columns=[
        "table_name", "row_count", "duration_seconds", 
        "ingestion_timestamp", "status"
    ])
    # if_exists='append' will check if table exists; if not, it creates it.
    empty_log.to_sql(
        "osm_ingestion_log", 
        engine, 
        schema=SCHEMA_NAME, 
        if_exists='append', 
        index=False
    )
    logging.info("Log table ready.")

default_args = {
    'owner': 'nigar',
    'retries': 3,
    'retry_delay': timedelta(minutes=2)
}

with DAG(
    dag_id="berlin_osmnx_sequential",
    default_args=default_args,
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    #max_active_runs=1,
    max_active_tasks=6,
    tags=["berlin", "osmnx", "sequential"]
) as dag:
    
    # 1. Load table configurations
    with open(os.path.join(DAG_FOLDER, 'config', 'osm_tables.json')) as f:
        tables = json.load(f)["tables"]
    

    # 2. Define Control Tasks
    setup_task = PythonOperator(
        task_id="setup_log_table",
        python_callable=setup_log_table
    )

    # 3. Define the Final Summary Task
    summary_task = PythonOperator(
        task_id="log_total_runtime",
        python_callable=log_total_runtime,
        #provide_context=True,
        trigger_rule="all_success" # Only runs when EVERY table is finished
    )    
    
   # 4. Build Sequential Pipeline (Linear)
    last_task = setup_task  # Start the chain with the setup task

    for config in tables:
        current_sync_task = PythonOperator(
            task_id=f"sync_{config['table_name']}",
            python_callable=process_single_table_task,
            op_kwargs={'table_config': config}
        )

        # LINKING: This creates a single straight line
        # setup -> table1 -> table2 -> table3 ...
        last_task >> current_sync_task
        
        # Update last_task so the NEXT loop iteration points to this one
        last_task = current_sync_task

    # 5. Attach the summary task to the very last table in the chain
    last_task >> summary_task