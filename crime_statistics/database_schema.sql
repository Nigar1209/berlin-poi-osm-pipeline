-- =============================================================================
-- 🚔 BERLIN CRIME ATLAS DATABASE SCHEMA
-- =============================================================================
-- Step 1: Data Modeling Phase - Crime Atlas Integration Only
-- This schema defines the database structure for Berlin Crime Atlas data

-- =============================================================================
-- 📊 MAIN CRIME STATISTICS TABLE
-- =============================================================================

-- Primary table for Berlin Crime Atlas data
CREATE TABLE crime_statistics (
    id SERIAL PRIMARY KEY,
    
    -- 🗺️ Geographic Identifiers
    area_id VARCHAR(20) NOT NULL,                    -- LOR area identifier (e.g., "1011303")
    area_name VARCHAR(255) NOT NULL,                 -- Human readable name (e.g., "Alexanderplatzviertel")
    area_type VARCHAR(50) NOT NULL,                  -- 'district', 'district_region', 'planning_area'
    bezirk_id VARCHAR(10),                          -- District ID (1-12)
    neighborhood VARCHAR(100),                       -- District name (e.g., "Mitte")
    coordinates GEOMETRY(POINT, 4326),             -- Geographic center of area (WGS84)
    area_km2 FLOAT,                                -- Area size in square kilometers
    
    -- 🚨 Crime Data
    crime_type VARCHAR(100) NOT NULL,               -- Standardized English crime category
    crime_type_german VARCHAR(100),                 -- Original German crime type
    year INTEGER NOT NULL,                          -- Year of data (2014-2023)
    absolute_cases INTEGER NOT NULL,                -- Total number of reported cases
    frequency_per_100k FLOAT NOT NULL,             -- Cases per 100,000 inhabitants
    population_base INTEGER,                        -- Population used for frequency calculation
    
    -- 📋 Data Management
    data_source VARCHAR(50) DEFAULT 'crime_atlas',  -- Source identifier
    data_quality VARCHAR(20) DEFAULT 'verified',    -- 'verified', 'interpolated', 'estimated'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- ✅ Constraints
    CONSTRAINT crime_stats_unique UNIQUE(area_id, crime_type, year),
    CONSTRAINT crime_stats_cases_positive CHECK (absolute_cases >= 0),
    CONSTRAINT crime_stats_frequency_positive CHECK (frequency_per_100k >= 0),
    CONSTRAINT crime_stats_year_valid CHECK (year >= 2014 AND year <= 2030),
    CONSTRAINT crime_stats_area_type_valid CHECK (area_type IN ('district', 'district_region', 'planning_area')),
    CONSTRAINT crime_stats_quality_valid CHECK (data_quality IN ('verified', 'interpolated', 'estimated'))
);

-- =============================================================================
-- 🗺️ SPATIAL AND LOOKUP TABLES
-- =============================================================================

-- Geographic hierarchy for Berlin LOR areas
CREATE TABLE area_hierarchy (
    id SERIAL PRIMARY KEY,
    area_id VARCHAR(20) NOT NULL UNIQUE,           -- LOR area identifier
    area_name VARCHAR(255) NOT NULL,               -- Area name
    area_type VARCHAR(50) NOT NULL,                -- Geographic level
    parent_area_id VARCHAR(20),                    -- Parent area (for hierarchy)
    bezirk_id VARCHAR(10),                        -- District ID
    neighborhood VARCHAR(100),                     -- District name
    coordinates GEOMETRY(POINT, 4326),            -- Area centroid
    boundary_geom GEOMETRY(MULTIPOLYGON, 4326),   -- Area boundary (optional)
    area_km2 FLOAT,                               -- Area size
    population_2023 INTEGER,                      -- Latest population data
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT area_hierarchy_type_valid CHECK (area_type IN ('district', 'district_region', 'planning_area'))
);

-- Crime type translation and categorization
CREATE TABLE crime_type_mapping (
    id SERIAL PRIMARY KEY,
    german_name VARCHAR(200) NOT NULL UNIQUE,      -- Original German crime type
    english_name VARCHAR(200) NOT NULL UNIQUE,     -- Standardized English name
    category VARCHAR(100) NOT NULL,                -- High-level category (e.g., 'Property Crime', 'Violent Crime')
    subcategory VARCHAR(100),                      -- Detailed subcategory
    severity_weight FLOAT DEFAULT 1.0,             -- Weight for safety score calculation (1.0-5.0)
    public_safety_relevance BOOLEAN DEFAULT TRUE,  -- Whether relevant for public safety scores
    description_german TEXT,                       -- German description
    description_english TEXT,                      -- English description
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT crime_mapping_weight_valid CHECK (severity_weight >= 0 AND severity_weight <= 5.0)
);

-- Links crime areas to existing neighborhood/listing system
CREATE TABLE neighborhood_crime_context (
    id SERIAL PRIMARY KEY,
    neighborhood_id INTEGER,                       -- FK to existing neighborhoods table
    listing_id INTEGER,                           -- FK to existing listings table (optional)
    area_id VARCHAR(20) NOT NULL,                 -- FK to crime_statistics.area_id
    distance_meters FLOAT,                        -- Distance from listing/neighborhood to crime area center
    safety_score FLOAT,                          -- Calculated safety metric (0-100, higher = safer)
    crime_risk_level VARCHAR(20),                -- 'very_low', 'low', 'medium', 'high', 'very_high'
    last_calculated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT safety_score_valid CHECK (safety_score >= 0 AND safety_score <= 100),
    CONSTRAINT crime_risk_valid CHECK (crime_risk_level IN ('very_low', 'low', 'medium', 'high', 'very_high'))
);

-- =============================================================================
-- 📈 PERFORMANCE INDEXES
-- =============================================================================

-- 🗺️ Spatial indexes for geographic queries
CREATE INDEX idx_crime_statistics_coordinates ON crime_statistics USING GIST(coordinates);
CREATE INDEX idx_area_hierarchy_coordinates ON area_hierarchy USING GIST(coordinates);
CREATE INDEX idx_area_hierarchy_boundary ON area_hierarchy USING GIST(boundary_geom);

-- 🔍 Query optimization indexes
CREATE INDEX idx_crime_statistics_area_year ON crime_statistics(area_id, year);
CREATE INDEX idx_crime_statistics_type_year ON crime_statistics(crime_type, year);
CREATE INDEX idx_crime_statistics_bezirk_year ON crime_statistics(bezirk_id, year);
CREATE INDEX idx_crime_statistics_frequency ON crime_statistics(frequency_per_100k DESC);
CREATE INDEX idx_area_hierarchy_area_id ON area_hierarchy(area_id);
CREATE INDEX idx_neighborhood_context_area ON neighborhood_crime_context(area_id);

-- 🔤 Text search indexes for German/English area names
CREATE INDEX idx_crime_statistics_area_name ON crime_statistics USING gin(to_tsvector('german', area_name));
CREATE INDEX idx_area_hierarchy_name ON area_hierarchy USING gin(to_tsvector('german', area_name));

-- =============================================================================
-- 🔗 FOREIGN KEY RELATIONSHIPS
-- =============================================================================

-- Link crime statistics to area hierarchy
ALTER TABLE crime_statistics 
ADD CONSTRAINT fk_crime_area 
FOREIGN KEY (area_id) REFERENCES area_hierarchy(area_id);

-- Link neighborhood context to crime statistics
ALTER TABLE neighborhood_crime_context 
ADD CONSTRAINT fk_context_area 
FOREIGN KEY (area_id) REFERENCES area_hierarchy(area_id);

-- Note: Foreign keys to existing neighborhood/listing tables to be added after confirmation
-- ALTER TABLE neighborhood_crime_context 
-- ADD CONSTRAINT fk_context_neighborhood 
-- FOREIGN KEY (neighborhood_id) REFERENCES neighborhoods(id);

-- =============================================================================
-- 📊 ANALYTICAL VIEWS
-- =============================================================================

-- District-level safety summary
CREATE OR REPLACE VIEW district_safety_summary AS
SELECT 
    cs.neighborhood,
    cs.year,
    COUNT(DISTINCT cs.crime_type) as crime_types_reported,
    SUM(cs.absolute_cases) as total_crimes,
    ROUND(AVG(cs.frequency_per_100k), 2) as avg_frequency_per_100k,
    ROUND(SUM(cs.absolute_cases)::NUMERIC / AVG(cs.population_base) * 100000, 2) as district_crime_rate,
    ah.population_2023,
    ah.area_km2 as total_area_km2
FROM crime_statistics cs
LEFT JOIN area_hierarchy ah ON cs.bezirk_id = ah.area_id
WHERE cs.area_type = 'district'
GROUP BY cs.neighborhood, cs.year, ah.population_2023, ah.area_km2
ORDER BY cs.neighborhood, cs.year;

-- Crime type analysis across all areas
CREATE OR REPLACE VIEW crime_type_analysis AS
SELECT 
    ctm.english_name as crime_type,
    ctm.category,
    ctm.severity_weight,
    COUNT(cs.id) as total_records,
    SUM(cs.absolute_cases) as total_cases,
    ROUND(AVG(cs.frequency_per_100k), 2) as avg_frequency_per_100k,
    MIN(cs.year) as first_year,
    MAX(cs.year) as last_year
FROM crime_statistics cs
JOIN crime_type_mapping ctm ON cs.crime_type = ctm.english_name
GROUP BY ctm.english_name, ctm.category, ctm.severity_weight
ORDER BY total_cases DESC;

-- Area safety rankings
CREATE OR REPLACE VIEW area_safety_rankings AS
SELECT 
    cs.area_id,
    cs.area_name,
    cs.neighborhood,
    cs.year,
    SUM(cs.absolute_cases) as total_crimes,
    ROUND(AVG(cs.frequency_per_100k), 2) as avg_frequency_per_100k,
    RANK() OVER (PARTITION BY cs.year ORDER BY AVG(cs.frequency_per_100k) ASC) as safety_rank,
    CASE 
        WHEN AVG(cs.frequency_per_100k) <= 1000 THEN 'very_safe'
        WHEN AVG(cs.frequency_per_100k) <= 2000 THEN 'safe'
        WHEN AVG(cs.frequency_per_100k) <= 4000 THEN 'moderate'
        WHEN AVG(cs.frequency_per_100k) <= 6000 THEN 'elevated'
        ELSE 'high_risk'
    END as risk_category
FROM crime_statistics cs
WHERE cs.area_type = 'district_region'
GROUP BY cs.area_id, cs.area_name, cs.neighborhood, cs.year
ORDER BY cs.year DESC, safety_rank ASC;

-- =============================================================================
-- 🧮 UTILITY FUNCTIONS
-- =============================================================================

-- Validate LOR area ID format
CREATE OR REPLACE FUNCTION validate_area_id(area_id_input TEXT) RETURNS BOOLEAN AS $$
BEGIN
    -- LOR area IDs: 7 digits (BPGBNPR) or 1-2 digits for districts
    RETURN area_id_input ~ '^[0-9]{7}$' OR area_id_input ~ '^[0-9]{1,2}$';
END;
$$ LANGUAGE plpgsql;

-- Calculate composite safety score for an area and year
CREATE OR REPLACE FUNCTION calculate_safety_score(
    area_id_param VARCHAR(20), 
    year_param INTEGER
) RETURNS FLOAT AS $$
DECLARE
    safety_score FLOAT;
    total_weighted_crimes FLOAT;
    population INTEGER;
    max_possible_score FLOAT := 10000; -- Normalization factor
BEGIN
    -- Get population base for the area
    SELECT AVG(population_base) INTO population 
    FROM crime_statistics 
    WHERE area_id = area_id_param AND year = year_param;
    
    -- Calculate weighted crime score
    SELECT COALESCE(SUM(cs.absolute_cases * ctm.severity_weight), 0) INTO total_weighted_crimes
    FROM crime_statistics cs
    JOIN crime_type_mapping ctm ON cs.crime_type = ctm.english_name
    WHERE cs.area_id = area_id_param 
    AND cs.year = year_param
    AND ctm.public_safety_relevance = TRUE;
    
    -- Calculate safety score (0-100, higher = safer)
    IF population > 0 AND total_weighted_crimes >= 0 THEN
        safety_score := GREATEST(0, 100 - (total_weighted_crimes / population * max_possible_score / 100));
        safety_score := LEAST(100, safety_score); -- Cap at 100
    ELSE
        safety_score := NULL;
    END IF;
    
    RETURN ROUND(safety_score, 2);
END;
$$ LANGUAGE plpgsql;

-- Get crime risk level based on frequency
CREATE OR REPLACE FUNCTION get_crime_risk_level(frequency_per_100k FLOAT) RETURNS VARCHAR(20) AS $$
BEGIN
    CASE 
        WHEN frequency_per_100k IS NULL THEN RETURN 'unknown';
        WHEN frequency_per_100k <= 1000 THEN RETURN 'very_low';
        WHEN frequency_per_100k <= 2000 THEN RETURN 'low';
        WHEN frequency_per_100k <= 4000 THEN RETURN 'medium';
        WHEN frequency_per_100k <= 6000 THEN RETURN 'high';
        ELSE RETURN 'very_high';
    END CASE;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- 📊 SAMPLE DATA QUERIES
-- =============================================================================

-- Example queries for testing after data import:

/*
-- Get crime statistics for a specific district in the latest year
SELECT * FROM crime_statistics 
WHERE neighborhood = 'Mitte' AND year = 2023 
ORDER BY frequency_per_100k DESC;

-- Find safest areas by crime frequency
SELECT area_name, neighborhood, AVG(frequency_per_100k) as avg_frequency
FROM crime_statistics 
WHERE year = 2023 
GROUP BY area_id, area_name, neighborhood
ORDER BY avg_frequency ASC 
LIMIT 10;

-- Crime trends over time for bicycle theft
SELECT year, SUM(absolute_cases) as total_cases, AVG(frequency_per_100k) as avg_frequency
FROM crime_statistics 
WHERE crime_type = 'Bicycle Theft'
GROUP BY year 
ORDER BY year;

-- Areas within 1km of a specific location with safety scores
SELECT cs.area_name, cs.neighborhood, 
       calculate_safety_score(cs.area_id, 2023) as safety_score,
       ST_Distance(cs.coordinates, ST_GeomFromText('POINT(13.4050 52.5200)', 4326)) as distance_meters
FROM crime_statistics cs
WHERE ST_DWithin(cs.coordinates, ST_GeomFromText('POINT(13.4050 52.5200)', 4326), 1000)
AND year = 2023
GROUP BY cs.area_id, cs.area_name, cs.neighborhood, cs.coordinates
ORDER BY safety_score DESC;
*/

-- =============================================================================
-- 🎯 SUMMARY
-- =============================================================================
-- This schema provides:
-- ✅ Primary crime_statistics table for Berlin Crime Atlas data
-- ✅ Geographic hierarchy and area management
-- ✅ Crime type translation and categorization
-- ✅ Integration points with existing neighborhood/listing system
-- ✅ Performance indexes for spatial and analytical queries
-- ✅ Analytical views for common use cases
-- ✅ Utility functions for safety calculations
-- ✅ Comprehensive constraints and data validation