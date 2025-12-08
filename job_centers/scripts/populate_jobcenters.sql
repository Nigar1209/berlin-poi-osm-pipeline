-- job_centers/scripts/populate_jobcenters.sql

-- STEP 1: CREATE TABLE (BASED ON APPROVED SCHEMA)
-- This defines the table structure for the Jobcenter data layer.

CREATE TABLE IF NOT EXISTS berlin_data.jobcenters (
    -- Standardized POI Columns
    id VARCHAR(20) PRIMARY KEY,
    district_id VARCHAR(20) NOT NULL,
    name VARCHAR(200) NOT NULL,
    latitude DECIMAL(9,6) NOT NULL,
    longitude DECIMAL(9,6) NOT NULL,
    geometry VARCHAR NOT NULL, -- WKT format (e.g., POINT(lon lat))
    neighborhood VARCHAR(100) NOT NULL,
    district VARCHAR(100) NOT NULL,
    neighborhood_id VARCHAR(20) NOT NULL,
    
    -- Jobcenter Specific Columns
    address_full VARCHAR(250),
    operating_hours VARCHAR(250),
    services_offered TEXT, -- JSON string
    contact_phone VARCHAR(50),
    contact_website VARCHAR(200),
    operator_name VARCHAR(100),
    data_source VARCHAR(50) NOT NULL,
    
    -- Foreign Key Constraint
    CONSTRAINT district_id_fk 
      FOREIGN KEY (district_id)
      REFERENCES berlin_data.districts(district_id) 
      ON DELETE RESTRICT ON UPDATE CASCADE
);


-- STEP 2: DATA POPULATION VIA COPY COMMAND
-- This section documents the method for bulk data insertion 
-- after the Python transformation script generates the final CSV.

/*
\COPY berlin_data.jobcenters (
    id, district_id, name, latitude, longitude, geometry, neighborhood, district, 
    neighborhood_id, address_full, operating_hours, services_offered, contact_phone, 
    contact_website, operator_name, data_source
) 
FROM 'path/to/jobcenters_transformed.csv' -- Path to the clean CSV output from Step 2
DELIMITER ',' 
CSV HEADER;
*/
