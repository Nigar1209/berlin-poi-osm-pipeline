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
TABLE = "gyms"

conn_str = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(conn_str)

def run_query(sql, description=""):
    print(f"\n{description}")
    with engine.connect() as conn:
        df = pd.read_sql(sql, conn)
        print(df)

print("\n🏋️‍♂️ === Gyms Data QA Checks ===")

# 1. Total number of gyms
run_query(
    f"SELECT COUNT(*) AS total_gyms FROM {SCHEMA}.{TABLE};",
    "1️⃣ Total gyms in table:"
)

# 2. Gyms without a district_id
run_query(
    f"SELECT COUNT(*) AS gyms_without_district FROM {SCHEMA}.{TABLE} WHERE district_id IS NULL;",
    "2️⃣ Gyms without district_id:"
)

# 3. Gyms without coordinates
run_query(
    f"SELECT COUNT(*) AS gyms_without_coordinates FROM {SCHEMA}.{TABLE} WHERE latitude IS NULL OR longitude IS NULL;",
    "3️⃣ Gyms without coordinates:"
)

# 4. Duplicate gym_ids
run_query(
    f"""SELECT gym_id, COUNT(*) AS count FROM {SCHEMA}.{TABLE} GROUP BY gym_id HAVING COUNT(*) > 1;""",
    "4️⃣ Duplicate gym_id entries:"
)

# 5. Example row
run_query(
    f"SELECT * FROM {SCHEMA}.{TABLE} LIMIT 1;",
    "5️⃣ Example row:"
)

# 6. Gyms without neighborhood
run_query(
    f"""SELECT COUNT(*) AS gyms_without_neighborhood FROM {SCHEMA}.{TABLE} WHERE neighborhood IS NULL OR neighborhood = '';""",
    "6️⃣ Gyms without neighborhood:"
)

# 7. Gyms by district
run_query(
    f"""SELECT district, COUNT(*) AS gyms FROM {SCHEMA}.{TABLE} GROUP BY district ORDER BY gyms DESC;""",
    "7️⃣ Gym count by district:"
)

# 8. Gyms by type (if column exists)
try:
    run_query(
        f"""SELECT type, COUNT(*) AS gyms FROM {SCHEMA}.{TABLE} GROUP BY type ORDER BY gyms DESC;""",
        "8️⃣ Gym count by type:"
    )
except Exception:
    print("Column 'type' does not exist — skipping type distribution.")

print("\n✅ All QA checks complete.")
