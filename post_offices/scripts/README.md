### Test loading data into the Neon DB

**Script:** `post_offices/scripts/upload_to_test_database.ipynb`

The final step loads the cleaned and enriched dataset into a PostgreSQL database hosted on Neon DB.
* **Database Connection:** A connection is established using SQLAlchemy's `create_engine`.
* **Table Creation:** A `CREATE TABLE` statement is executed to set up the destination table (`test_berlin_data.post_offices_test`) with the correct schema.
* **Data Loading:** Data is loaded using PostgreSQL's high-performance `COPY` command. A `SET search_path` command is executed first to ensure the correct schema context for the transaction.
* **Adding Foreign Keys:** After the data is loaded, `ALTER TABLE` statements are executed to add the `FOREIGN KEY` constraints, ensuring referential integrity.
