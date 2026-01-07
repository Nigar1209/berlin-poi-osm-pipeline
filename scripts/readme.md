
## 🏗️ Schema Definition

All tables in the pipeline follow a standardized schema to ensure consistency and compatibility with the unified POI table.
These are main columns, additional columns have no strict rules

### 📊 Common Column Schema

```sql
id VARCHAR(20) PRIMARY KEY,                 -- Numeric only, no letters
district_id VARCHAR(20) NOT NULL,           -- Mapped from district name
name VARCHAR(200) NOT NULL,                 -- Defaults to 'Unknown' if NULL
latitude DECIMAL(9,6),                      
longitude DECIMAL(9,6), 
geometry VARCHAR,                           -- POINT() format
neighborhood VARCHAR(100),                  -- Joined from neighborhoods table
district VARCHAR(100),                      -- From lor_ortsteile.geojson
neighborhood_id VARCHAR(20),                -- From lor_ortsteile.geojson
CONSTRAINT district_id_fk 
  FOREIGN KEY (district_id)
  REFERENCES berlin_data.districts(district_id) 
  ON DELETE RESTRICT ON UPDATE CASCADE
```

