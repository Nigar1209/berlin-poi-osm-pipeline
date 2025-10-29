### Script: `venues_operating_hours_category_column.ipynb`

**Purpose:** This script adds a new column, `operating_hours_category`, to the existing `berlin_source_data.venues` table in the PostgreSQL database. This column categorizes each venue based on its opening hours, which is essential for the subsequent **labelling** of districts based on nightlife activity.

**Input:** Reads the `opening_hours_dict` column from the `venues` table. This column contains structured opening hours data.

**Logic:**
The script defines and applies a function (`determine_nightlife_category_with_nodata`) to the `opening_hours_dict` column. It assigns one of the following categories to each venue:

1.  **`No Data`**: If the `opening_hours_dict` is missing, empty, or cannot be parsed correctly.
2.  **`Not Late (Before 9 pm)`**: If the venue closes before 21:00 according to the available data.
3.  **`Evening (9pm-11pm)`**: If the venue is open at or after 21:00, but its latest closing time is at or before 23:00.
4.  **`Late (After 11pm)`**: If the venue is open after 23:00, closes after 23:00 (including midnight or later), or has explicit keywords like 'late' or '24/7'.

**Process:**

1.  **Calculate in Pandas:** The category is calculated for every row in the `venues` DataFrame and stored in the new `operating_hours_category` column.
2.  **Add Column to DB:** An `ALTER TABLE` command adds the `operating_hours_category` column (as `VARCHAR(30)`) to the `berlin_source_data.venues` table if it doesn't already exist.
3.  **Update DB:**
    * A temporary table is created in PostgreSQL.
    * The `venue_id` and calculated `operating_hours_category` from the Pandas DataFrame are efficiently loaded into this temporary table using the `COPY` command.
    * An `UPDATE` statement joins the main `venues` table with the temporary table on `venue_id` to populate the new `operating_hours_category` column with the correct values.
    * The temporary table is dropped.

**Output:** The `berlin_source_data.venues` table is updated with the new `operating_hours_category` column, ready for use in district labelling analysis.
