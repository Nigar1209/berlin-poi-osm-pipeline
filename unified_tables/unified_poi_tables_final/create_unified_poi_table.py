# Import Librabies
import osmnx as ox # to fetch data from OpenStreetMap
import geopandas as gpd # to work with geospatial data
import pandas as pd
from sqlalchemy import create_engine, text
import warnings
import json


warnings.filterwarnings("ignore")

# Credentials
user_name=''
password=''

# Conection
host = 'localhost'
port = '5433'
database = 'layereddb'
schema='berlin_source_data'

# Connection to DB
engine = create_engine(f'postgresql+psycopg2://{user_name}:{password}@{host}:{port}/{database}')

with engine.begin() as conn:
# Step 1: Validation query for excluded tables
    validation_query = """
        DROP TABLE IF EXISTS excluded_tables_log CASCADE;

        -- Create the excluded_tables_log table
        CREATE TABLE public.excluded_tables_log (           -- Adding to public schema for now
            table_name VARCHAR(255),
            reason VARCHAR(500),
            exclusion_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        WITH all_tables AS (
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'berlin_source_data'
            AND table_name NOT ILIKE '%districts%'          -- Must not be included in final table so doesnt need to be checked
            AND table_name NOT ILIKE '%neighborhoods%'      -- Must not be included in final table so doesnt need to be checked
        ),
        -- Standard schema for each table
        expected_schema AS (
            SELECT * FROM (VALUES
                ('id', 'character varying', NULL, 'PRIMARY KEY', 'NO'),
                ('district_id', 'character varying', NULL, 'FOREIGN KEY', 'NO'),
                ('name', 'character varying', NULL, NULL, 'YES'),
                ('latitude', 'numeric', NULL, NULL, 'YES'),
                ('longitude', 'numeric', NULL, NULL, 'YES'),
                ('neighborhood', 'character varying', NULL, NULL, 'YES'),
                ('district', 'character varying', NULL, NULL, 'YES'),
                ('neighborhood_id', 'character varying', NULL, NULL, 'YES')
            ) AS t(column_name, expected_type, expected_length, constraint_type, is_nullable)
        ),
        -- Checks all columns exist
        missing_columns AS (
            SELECT tc.table_name,
                STRING_AGG(DISTINCT col, ', ' ORDER BY col) AS missing_cols
            FROM all_tables tc
            CROSS JOIN (VALUES 
                ('id'), ('name'), ('district_id'), ('district'),
                ('latitude'), ('longitude'), ('neighborhood_id'),
                ('neighborhood'), ('geometry')
            ) AS req_cols(col)
            LEFT JOIN information_schema.columns c 
                ON tc.table_name = c.table_name 
                AND c.table_schema = 'berlin_source_data'
                AND LOWER(c.column_name) = req_cols.col
            WHERE c.column_name IS NULL
            GROUP BY tc.table_name
            HAVING COUNT(*) > 0
        ),
        -- Checks all data types correct and creates and adds an error to the excluded_tables_log table when incorrect
        datatype_issues AS (
            SELECT 
                c.table_name,
                'Expected data type ' || e.expected_type || ', got ' || c.data_type AS reason
            FROM information_schema.columns c
            JOIN expected_schema e 
                ON LOWER(c.column_name) = e.column_name
            WHERE c.table_schema = 'berlin_source_data'
            AND (
                    c.data_type <> e.expected_type
                    OR (c.data_type = 'numeric' AND (c.numeric_precision || ',' || c.numeric_scale) <> e.expected_length)
            )
        ),
        -- Checks all columns that cannot contain NULL are correct and adds an error to the excluded_tables_log table when incorrect
        null_issues AS (
            SELECT c.table_name,
                'Column ' || c.column_name || ' allows NULL, expected NOT NULL' AS reason
            FROM information_schema.columns c
            JOIN expected_schema e 
                ON LOWER(c.column_name) = e.column_name
            WHERE c.table_schema = 'berlin_source_data'
            AND e.is_nullable = 'NO'
            AND c.is_nullable = 'YES'
        ),
        -- Checks primary key on id column and creates and adds an error to the excluded_tables_log table when incorrect
        pk_issues AS (
            SELECT t.table_name,
                'Missing PRIMARY KEY on id column' AS reason
            FROM all_tables t
            WHERE NOT EXISTS (
                SELECT 1
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu
                    ON kcu.constraint_name = tc.constraint_name
                    AND kcu.table_name = tc.table_name
                WHERE tc.table_schema = 'berlin_source_data'
                AND tc.table_name = t.table_name
                AND tc.constraint_type = 'PRIMARY KEY'
                AND LOWER(kcu.column_name) = 'id'
            )
        ),
        -- Checks foreign key on district_id column and creates and adds an error to the excluded_tables_log table when incorrect
        fk_issues AS (
            SELECT t.table_name,
                'Missing or incorrect foreign key on district_id' AS reason
            FROM all_tables t
            WHERE NOT EXISTS (
                SELECT 1
                FROM information_schema.table_constraints tc
                WHERE tc.table_schema = 'berlin_source_data'
                AND tc.table_name = t.table_name
                AND tc.constraint_type = 'FOREIGN KEY'
            )
        ),
        -- Combines all invalid tables into one
        invalid_tables AS (
            SELECT table_name, 'Missing columns: ' || missing_cols AS reason FROM missing_columns
            UNION ALL SELECT table_name, reason FROM datatype_issues
            UNION ALL SELECT table_name, reason FROM null_issues
            UNION ALL SELECT table_name, reason FROM pk_issues
            UNION ALL SELECT table_name, reason FROM fk_issues
        )
        -- Inserts all invalid tables into excluded_tables_log
        INSERT INTO excluded_tables_log (table_name, reason)
        SELECT table_name, reason FROM invalid_tables;
"""

    conn.execute(text(validation_query))
    print("✅ Validation query complete")

# Step 2: Drop unified_pois and processed_tables_log if they exist, then create them again from scratch

    conn.execute(text("DROP TABLE IF EXISTS unified_pois CASCADE;"))
    conn.execute(text("DROP TABLE IF EXISTS processed_tables_log CASCADE;"))

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS public.unified_pois (                                                                    -- Adding to public schema for now
            poi_id VARCHAR(50) PRIMARY KEY,
            name VARCHAR(200),
            layer VARCHAR(100),
            district_id VARCHAR(20),
            district VARCHAR(100),
            neighborhood_id VARCHAR(20),
            neighborhood VARCHAR(100),
            latitude DECIMAL(9,6),
            longitude DECIMAL(9,6),
            geometry GEOMETRY, 
            attributes JSONB,
            nearest_pois JSONB
        );
    """))
    conn.execute(text("""                                                                                                   
        CREATE TABLE IF NOT EXISTS public.processed_tables_log (                                                            -- Adding to public schema for now (Creates log of processed tables)
            table_name VARCHAR(255) PRIMARY KEY,
            processed_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """))
    print("✅ Unified table and log table ready")

    # Step 3: Get new tables to process
    valid_tables_sql = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'berlin_source_data'
            AND table_name NOT ILIKE '%districts%'                                                                          -- doesn't need to be included in final table
            AND table_name NOT ILIKE '%neighborhoods%'                                                                      -- doesn't need to be included in final table
            AND table_name NOT IN (SELECT table_name FROM excluded_tables_log)                                              -- Exclude invalid tables
            AND table_name IN ('galleries', 'food_markets','long_term_listings', 'banks', 'malls')                          -- This line is just for testing purposes so can load a few tables at a time , 'bike_lanes'
    ;
    """

    new_tables = [row[0] for row in conn.execute(text(valid_tables_sql))]                                                    # Get list of tables to process
    print(f"✅ New tables to process: {new_tables}")

    # Step 4: Insert only new tables
    if new_tables:
        union_queries = []                                                                                                   # Reset union_queries for new tables
        for table in new_tables:
            union_queries.append(f"""
                SELECT 
                    CONCAT(SUBSTRING('{table}' FROM 1 FOR 4), '-', t.id) AS poi_id,                                          -- Unique poi_id created so no duplicates can happen in error
                    t.name,
                    '{table}' AS layer,
                    t.district_id,
                    t.district,
                    t.neighborhood_id,
                    t.neighborhood,
                    t.latitude,
                    t.longitude,
                    ST_SetSRID(ST_GeomFromEWKT(t.geometry), 4326) AS geometry,                                                -- Ensure geometry is in correct SRID
                    (to_jsonb(t) - 'id' - 'name' - 'district_id' - 'neighborhood_id' - 'latitude' - 'longitude' - 'geometry') AS attributes     -- All other columns as attributes in JSONB
                FROM berlin_source_data.{table} t
            """)
        union_sql = " UNION ALL ".join(union_queries)                                                                          # Combine all SELECTs into one UNION ALL query (one for each valid table)

        insert_sql = f"""
            WITH all_pois AS (
                {union_sql}
            ),
            unique_layers AS (
                SELECT DISTINCT layer FROM all_pois WHERE layer <> 'long_term_listings'                                          -- Won't add the listing itself to the nearest_pois json doc
            ),
            pois_with_nearest AS ( 
                SELECT 
                    ap.poi_id,
                    ap.name,
                    ap.layer,
                    ap.district_id,
                    ap.district,
                    ap.neighborhood_id,
                    ap.neighborhood,
                    ap.latitude,
                    ap.longitude,
                    ap.geometry,
                    ap.attributes,
                (
                    SELECT jsonb_object_agg(layername, nearestinfo)                                                               -- Create jsonb object for nearest pois to the listing
                    FROM (
                        SELECT 
                            ul.layer AS layername,
                            (
                                SELECT jsonb_build_object(
                                    'id', p.poi_id,
                                    'name', p.name,
                                    'distance', ST_Distance(ap.geometry, p.geometry),
                                    'address', jsonb_build_object(
                                        'street', p.attributes->>'street',
                                        'housenumber', p.attributes->>'housenumber'
                                    )
                                )
                                FROM all_pois p
                                WHERE p.layer = ul.layer 
                                ORDER BY ap.geometry <-> p.geometry
                                LIMIT 1
                            ) AS nearestinfo
                        FROM unique_layers ul
                        WHERE ap.layer = 'long_term_listings' AND ul.layer <> 'long_term_listings'                                -- Only add nearest pois for long_term_listings layer
                    ) AS layer_nearest
                ) AS nearest_pois
            FROM all_pois ap
        )
        INSERT INTO unified_pois 
            (poi_id, name, layer, district_id, district, neighborhood_id, neighborhood, 
             latitude, longitude, geometry, attributes, nearest_pois)
        SELECT 
            poi_id, name, layer, district_id, district, neighborhood_id, neighborhood,
            latitude, longitude, geometry, attributes, nearest_pois
        FROM pois_with_nearest;
    """
    
    conn.execute(text(insert_sql))

    for table in new_tables:
        conn.execute(text(f"""
            INSERT INTO public.processed_tables_log (table_name)                                                                    -- Create a list of tables that have been processed
            VALUES ('{table}') ON CONFLICT DO NOTHING;
        """))
                    
        print(f"✅ Adding {table} to unified_pois.")
    else:
        print(f"✅ Insert complete.")

    # Step 5: Create spatial index
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_poi_geom ON unified_pois                                                                   -- Create an INDEX so queries run faster on GIST
        USING GIST (geometry);
    """))
        
    print("✅Spatial index created.")
