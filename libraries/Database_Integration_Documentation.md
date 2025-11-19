# 📚 Task: Integration of the Libraries Data Layer

---
**EPIC 2: Data Foundation & Frontend Context**

After completing the finalized schema and a successful test insert into test_berlin_data, this task ensures that the finalized **Libraries** table is deployed to the development database, validated with real constraints, and formally added to the project’s ERD.

This task also includes updating all documentation to keep the data platform consistent and aligned with schema standards.

---

## 🎯 Objectives

- Deploy the finalized **Libraries** table to the development database.
- Validate all constraints, foreign keys, and references using the cleaned dataset.
- Insert the full cleaned dataset and confirm successful ingestion.
- Add the Libraries layer to the project ERD:
    - Add table + attributes
    - Add relationship (district_id → districts.district_id)
- Update the Libraries documentation section in the project Wiki.

---

## 🔗 Required Links

ERD (Lucidchart):
https://lucid.app/lucidchart/9cc54dd7-0cba-4516-b9d0-a0c242733036/edit?viewport_loc=-9909%2C1310%2C22766%2C11582%2C0_0&invitationId=inv_9094a36f-60eb-4f9e-9ffa-788f9f1d6346

Table Documentation Wiki:
https://github.com/webeet-io/layered-populate-data-pool-da/wiki/Layered-DB-:-Berlin-Data-Source-table-info

--
## 0️⃣ Prepare Environment

Before deployment, ensure:

- libraries_data_transformation.ipynb is finalized.
- The final SQL **CREATE TABLE** script for the Libraries layer is ready.
- You are connected to the **development database** (not test_berlin_data).
- The cleaned Libraries dataset is the same version used during the test deployment.

---
## 1️⃣ Deploy Table to Development DB

Run the finalized Libraries CREATE TABLE script in the dev environment.

The table must include:

* district_id as a foreign key

* All required constraints:

    - PRIMARY KEY
    - NOT NULL
    - UNIQUE
    - CHECK constraints for latitude, longitude, and operating hours

- Standard administrative layer fields

- Library-specific fields (e.g., opening_hours, operator, accessibility features)

---

**1.2 Table Schema Definition**

To properly integrate the Libraries layer, create the table via an explicit SQL CREATE TABLE statement — do not load data directly. This ensures you can:

- Define constraints that enforce data quality and relationships
- Establish foreign-key references to existing layers (e.g., berlin_data.districts)

---

🧱 **Understanding Constraints**

| **Type** | **Example** | **Purpose** |
|-----------|------------------|---------------|
| **PRIMARY KEY** | institution_id VARCHAR(20) PRIMARY KEY | Uniquely identifies each record |
| **FOREIGN KEY** | district_id REFERENCES berlin_data.districts(district_id) | Enforces valid district linkage |
| **NOT NULL** | name VARCHAR(200) NOT NULL | Ensures essential data is always present |
| **UNIQUE** | email UNIQUE | Avoids duplicate entries |
| **CHECK** |CHECK(latitude BETWEEN 52.3 AND 52.6) | Validates coordinate ranges |

---
💾 **Example Schema**

CREATE TABLE IF NOT EXISTS libraries (
    library_id BIGINT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    amenity VARCHAR(50) NOT NULL,
    operator_type VARCHAR(100),
    operator VARCHAR(500),
    street VARCHAR(150),
    housenumber VARCHAR(10),
    postcode VARCHAR(10) NOT NULL,
    city VARCHAR(50) NOT NULL,
    country VARCHAR(50) NOT NULL,
    latitude NUMERIC(9, 6) NOT NULL,
    longitude NUMERIC(9, 6) NOT NULL,
    district_id VARCHAR(50) NOT NULL,
    district VARCHAR(100) NOT NULL,
    neighbourhood VARCHAR(100),
    neighbourhood_id VARCHAR(100),
    final_email VARCHAR(255),
    final_phone VARCHAR(100),
    website_url VARCHAR(255),
    opening_hours VARCHAR(255),
    isil_code VARCHAR(100),
    wheelchair_accessible VARCHAR(10),
    toilets_wheelchair VARCHAR(10),
    internet_access VARCHAR(100),
    "level" VARCHAR(10),
    geom_point GEOMETRY(Point, 4326),
    CONSTRAINT district_id_fk
        FOREIGN KEY (district_id)
        REFERENCES berlin_source_data.districts(district_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

---

## 🧩 Constraints & References — Explanation

**Why reference berlin_data.districts(district_id):**

- Ensures every libraries is associated with a valid Berlin district
- Supports spatial and relational consistency across layers
- Keeps all location-based data harmonized in the platform

**Why use ON DELETE RESTRICT:**

- Prevents deletion of districts that still have linked institutions
- Protects referential integrity and avoids orphan records

**Why use ON UPDATE CASCADE:**

- Keeps child records synchronized if district IDs are updated
- Maintains consistent relationships across the platform

---

**Summary of Referential Rules**

| **Rule** | **Purpose** | **Effect** |
|-----------|------------------|---------------|
| REFERENCES berlin_data.districts(district_id) | Establish relational link | Ensures valid district mapping |
| ON DELETE RESTRICT | Prevent data loss | Blocks deletion of active parent records |
| ON UPDATE CASCADE | Maintain consistency | Auto-updates IDs across linked tables |

---

## ✅ 1.3 Validation & Quality Checks

- Verify no duplicate rows remain
- Confirm district_id and neighborhood_id mappings via spatial joins
- Ensure coordinates fall within Berlin’s boundaries
- Validate foreign key integrity and schema compliance
- Check column naming, types, and constraints against the defined schema
- Confirm row counts match cleaned datasets

---

## 2. Test Insert

- Insert finalized data into the test_berlin_data schema (Neon DB)
- Ensure no constraint violations (primary or foreign keys)
- Validate that all district_id values exist in test_berlin_data.districts
- Check for correct address and coordinate formatting
- Verify URLs, phone numbers, and emails follow standardized formats

---
## 3. Documentation

Add a Markdown summary to your notebook covering:

- All cleaning, transformation, and mapping steps
- Assumptions, data issues, and how they were handled
- Justification for constraint and reference design
- Spatial mapping methods used (with GitHub links)

---

