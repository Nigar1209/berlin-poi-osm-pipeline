
# Unified POI Table 

```sql
ALTER TABLE berlin_source_data.hospitals_refactored RENAME TO hospitals;
```

```sql
ALTER TABLE berlin_source_data.food_markets RENAME COLUMN market_id TO id;
```

```sql
ALTER TABLE berlin_source_data.short_term_listings ALTER COLUMN id TYPE varchar(20) USING id::varchar(20);
ALTER TABLE berlin_source_data.short_term_listings ALTER COLUMN "name" TYPE varchar(200) USING "name"::varchar(200);

```
- created notebook to correct tables with missing columns (table_corrections)
    - neighborhood_id
        - On short_term_listinmgs not all id's pulled through as some neighbourhoods are street name in table
    - neighborhood name and district name column added in where missing
    - id (add if missing and check all only contain numbers) (ubahn table)
    - most tables missing geometry so used a loop to add the column in POINT()
    - if missing neighborhood and neighborhood id, used NOMANATIM to addd the neighborhood and then joined to neighborhood table to get the id
    - recreated the short term listings table to include the name column



```sql
id VARCHAR(20) PRIMARY KEY, -- dont use any letter, must only be numeric
district_id VARCHAR(2) NOT NULL, -- use mapping on district name
name VARCHAR(200) NOT NULL, -- If NULL use 'Unknown'
latitude DECIMAL(9,6), 
longitude DECIMAL(9,6), 
geometry VARCHAR, -- must be in POINT() format
neighborhood VARCHAR(100), -- Use spatial_name on geo-json file
district VARCHAR(100), -- get from geo-json file
neighborhood_id VARCHAR(20), -- join to neighborhoods table to get
CONSTRAINT district_id_fk -- please dont change this name
FOREIGN KEY (district_id)
 REFERENCES berlin_data.districts(district_id) ON DELETE RESTRICT ON UPDATE CASCADE
```

