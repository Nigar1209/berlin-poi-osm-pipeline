import pandas as pd

p=pd.read_parquet("playgrounds_parks/data/osm_parks.parquet")
g=pd.read_parquet("playgrounds_parks/data/osm_playgrounds.parquet")

req_cols={"source","category","name","operator","brand","latitude","longitude",
"addr_street","addr_housenumber","addr_postcode","addr_city","access","wheelchair",
"opening_hours","website","phone","email","surface","playground_features","sport",
"osm_id","osm_type","wikidata","wikipedia","geometry","tags_json"}

assert req_cols.issubset(p.columns), f"parks missing: {req_cols-set(p.columns)}"
assert req_cols.issubset(g.columns), f"plays missing: {req_cols-set(g.columns)}"

print("✓ schema OK")
print("parks null coords:", p['latitude'].isna().sum(), p['longitude'].isna().sum())
print("plays null coords:", g['latitude'].isna().sum(), g['longitude'].isna().sum())
