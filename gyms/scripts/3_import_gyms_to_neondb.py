"""
All-in-one Berlin Gyms Import Script (improved, robust)
--------------------------------------------------------
- Loads OSM gyms data, maps district_id by name from DB
- Cleans IDs and text fields (all as str, no float artifacts)
- Converts PLZ, district/neighb to string or None
- Imports only gyms with valid district_id
"""

import pandas as pd
import os
from sqlalchemy import create_engine, text

# === CONFIGURATION ===
DB_USER = "neondb_owner"
DB_PASS = "a9Am7Yy5r9_T7h4OF2GN"
DB_HOST = "ep-falling-glitter-a5m0j5gk-pooler.us-east-2.aws.neon.tech"
DB_PORT = "5432"
DB_NAME = "neondb"
SCHEMA = "test_berlin_data"
CSV_PATH = os.path.join('gyms/sources/gyms_with_district_and_neighborhood.csv')
TABLE_NAME = "gyms"

print(f"Loading gyms data from: {CSV_PATH}")
df = pd.read_csv(CSV_PATH)
print("First sample:")
print(df.head(3))

# Ensure email column exists (OSM/GeoJson may miss it)
if 'email' not in df.columns:
    df['email'] = None

# Rename 'postcode' to 'postal_code' (DB schema)
if 'postcode' in df.columns:
    df.rename(columns={'postcode': 'postal_code'}, inplace=True)

# Clean all IDs and keys (always string or None, never float/NaN)
def clean_id(x):
    if pd.isnull(x) or str(x).strip() == '':
        return None
    x_str = str(x).strip()
    if x_str.replace('.0', '').isdigit():
        return str(int(float(x_str)))
    return x_str

for col in ['gym_id', 'district_id', 'postal_code', 'neighborhood']:
    if col in df.columns:
        df[col] = df[col].apply(clean_id)

# Clean name/text fields (never float, always str or None)
for col in ['district', 'neighborhood']:
    if col in df.columns:
        df[col] = df[col].apply(lambda x: str(x).strip() if pd.notnull(x) else None)

# --- DB Connection + get district_id mapping ---
conn_str = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(conn_str)
with engine.begin() as conn:
    districts = pd.read_sql(f"SELECT district_id, district FROM {SCHEMA}.districts", conn)
print("Districts from DB:", len(districts))
print(districts)

# Build DB name-to-id mapping
db_name2id = {row['district'].strip().lower(): str(row['district_id']) for _, row in districts.iterrows()}
def clean_name(n): return str(n).strip().lower() if pd.notnull(n) else ""
df['district_clean'] = df['district'].apply(clean_name)
df['district_id_db'] = df['district_clean'].map(db_name2id)
df['district_id'] = df['district_id_db']
df.drop(['district_id_db', 'district_clean'], axis=1, inplace=True)

print("Sample after district mapping:")
print(df[['gym_id','district_id','district','postal_code','neighborhood']].head(3))

# --- Ensure all columns for DB (add if missing) ---
final_cols = [
    "gym_id", "district_id", "name", "address", "postal_code", "phone_number",
    "email", "coordinates", "latitude", "longitude", "neighborhood", "district"
]
if 'phone' in df.columns and 'phone_number' not in df.columns:
    df['phone_number'] = df['phone']
for col in final_cols:
    if col not in df.columns:
        df[col] = None
final_df = df[final_cols].copy()

# Only keep gyms with a mapped, valid district_id (clean)
valid_ids = set(districts['district_id'].astype(str))
final_df = final_df[final_df['district_id'].isin(valid_ids)]
print(f"Gyms to import (after mapping): {len(final_df)}")

# --- Create/prepare DB table and FK ---
with engine.begin() as conn:
    conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA};"))
    create_table_sql = f"""
    CREATE TABLE IF NOT EXISTS {SCHEMA}.{TABLE_NAME} (
        gym_id VARCHAR(20) PRIMARY KEY,
        district_id VARCHAR(20),
        name VARCHAR(200),
        address VARCHAR(200),
        postal_code VARCHAR(10),
        phone_number VARCHAR(50),
        email VARCHAR(100),
        coordinates VARCHAR(200),
        latitude DECIMAL(9,6),
        longitude DECIMAL(9,6),
        neighborhood VARCHAR(100),
        district VARCHAR(100)
    );
    """
    conn.execute(text(create_table_sql))
    fk_sql = f"""
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.table_constraints
            WHERE constraint_name = 'district_id_fk'
                AND table_schema = '{SCHEMA}'
                AND table_name = '{TABLE_NAME}'
        ) THEN
            ALTER TABLE {SCHEMA}.{TABLE_NAME}
            ADD CONSTRAINT district_id_fk
            FOREIGN KEY (district_id)
            REFERENCES {SCHEMA}.districts(district_id)
            ON DELETE RESTRICT ON UPDATE CASCADE;
        END IF;
    END$$;
    """
    conn.execute(text(fk_sql))
    conn.execute(text(f"TRUNCATE {SCHEMA}.{TABLE_NAME};"))
    print(f"Table '{SCHEMA}.{TABLE_NAME}' truncated.")

# --- Import gyms ---
final_df.to_sql(TABLE_NAME, engine, if_exists="append", index=False, schema=SCHEMA, chunksize=100)
print(f"Imported {len(final_df)} gyms into '{SCHEMA}.{TABLE_NAME}'.")

# --- PostGIS geometry ---
with engine.begin() as conn:
    add_geom_sql = f"""
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_schema='{SCHEMA}'
            AND table_name='{TABLE_NAME}'
            AND column_name='geom'
        ) THEN
            ALTER TABLE {SCHEMA}.{TABLE_NAME} ADD COLUMN geom geometry(Point, 4326);
        END IF;
    END$$;
    """
    conn.execute(text(add_geom_sql))
    update_geom_sql = f"""
    UPDATE {SCHEMA}.{TABLE_NAME}
    SET geom = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)
    WHERE geom IS NULL AND longitude IS NOT NULL AND latitude IS NOT NULL;
    """
    conn.execute(text(update_geom_sql))
    print("Geometry column updated.")


# --- Export final DataFrame as CSV (exactly what goes into DB) ---
final_df.to_csv("gyms/sources/gyms_db_ready_final.csv", index=False)
print("Exported DB-ready gyms data to gyms/sources/gyms_db_ready_final.csv")

print("🎉 All steps finished. Gyms data imported with fixed emails, correct postal_code, string types and DB-mapped district IDs!")
