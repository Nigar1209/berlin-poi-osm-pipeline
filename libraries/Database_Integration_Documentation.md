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

# 2️⃣ Validate Constraints & References

Insert the cleaned Libraries dataset into the dev table.

**Validate:**

✅ **Key Integrity**

- All district_id values map to existing districts.district_id

✅ **Schema Consistency**

- All nullability rules respected
- Data types match the schema
- CHECK constraints pass (coordinate ranges, valid opening hours format, etc.)

✅ **Data Quality Checks**
- Row count matches the cleaned dataset
- Address fields correctly standardized
- Contact information (phone, email, website) follows platform-wide rules
- Opening hours follow the adopted formatting standard (e.g. Mo–Fr 10:00–18:00)

---

# 3️⃣ ERD Update

Update the official ERD in Lucidchart.

**Tasks:**

- Add **Libraries** as a new table/object.
- Include all attributes from the finalized schema.
- Add the relationship:
    
    **libraries.district_id → districts.district_id**
- Ensure correct cardinality:
    
    **Many Libraries → One District**
- Save and publish the updated ERD.

**Required Output:**
    
- Screenshot or embedded snippet of the updated ERD in the transformation notebook.

---

# 4️⃣ Documentation & Wiki Update

Update the official table documentation wiki:

- Add a new Libraries section under the Layered DB documentation.

- Include:

    - Table overview
    - Column list + data types
    - Definitions for each column
    - Data validation logic
    - Notes about library type, operators, or accessibility fields

Update your transformation notebook to include:

- Confirmation of successful dev deployment
- Constraint validation results
- Screenshot/snippet of the ERD
- Any notes or schema considerations for future layers

---