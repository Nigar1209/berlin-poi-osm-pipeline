# Here are the instructions to connect to your PostgreSQL database and perform the requested operations:

## Connecting to the PostgreSQL Database
You can connect to your PostgreSQL database using the psql command-line tool.

Open your terminal or command prompt.

Execute the following command to connect:

**psql -h layered-data-warehouse.cdg2ok68acsn.eu-central-1.rds.amazonaws.com -p 5432 -U postgres -d berlin_project_db -W**

-h: Specifies the host name of the PostgreSQL server.

-p: Specifies the port number the server is listening on (default is 5432).

-U: Specifies the username to connect as.

-d: Specifies the database name to connect to.

-W: Prompts for the password (you will be asked for password after running the command).

Enter your password when prompted. The password is **b319nnlsekSOfIiVDpRC**.

## Setting the Default Schema
Once connected to the database, you can set the default search path to include your berlin_data schema. This allows you to reference tables in that schema without explicitly prefixing them with berlin_data..

After successfully connecting, execute the following SQL command:

**SET search_path TO berlin_data, public;**

This command tells PostgreSQL to look for tables first in the berlin_data schema, then in the public schema.

## Creating a Table
To create a new table in your database, you use the CREATE TABLE SQL command. You need to specify the table name and define the columns, including their data types and any constraints (e.g., PRIMARY KEY, NOT NULL).

Here's a general syntax and an example:

CREATE TABLE your_schema_name.your_table_name (  

    column1_name data_type [CONSTRAINT],  
    
    column2_name data_type [CONSTRAINT],  
    
    -- Add more columns as needed  
    
    PRIMARY KEY (column1_name) -- Example of a primary key constraint  
    
);

Example: Creating an employees table in the berlin_data schema

CREATE TABLE berlin_data.employees ( 

    id SERIAL PRIMARY KEY, 
    
    name VARCHAR(255) NOT NULL, 
    
    email VARCHAR(255) UNIQUE, 
    
    hire_date DATE DEFAULT CURRENT_DATE, 
    
    salary DECIMAL(10, 2) 
    
);

id SERIAL PRIMARY KEY: Creates an auto-incrementing integer column id that serves as the primary key for the table.

name VARCHAR(255) NOT NULL: Creates a string column name that cannot be empty and can store up to 255 characters.

email VARCHAR(255) UNIQUE: Creates a string column email that must be unique across all rows.

hire_date DATE DEFAULT CURRENT_DATE: Creates a date column hire_date that defaults to the current date if not specified.

salary DECIMAL(10, 2): Creates a decimal number column salary that can store up to 10 digits in total, with 2 digits after the decimal point.

## Checking Tables in a Schema
To list all tables within a specific schema (e.g., berlin_data), use the following query:

SELECT table_name\

FROM information_schema.tables\

WHERE table_schema = 'berlin_data';

## Checking Constraints in a Table
To inspect the constraints (like primary keys, foreign keys, unique constraints) on a specific table (e.g., employees in the berlin_data schema), you can use either a SQL query or a psql meta-command.

Option 1: Using a SQL Query  

SELECT  

    tc.constraint_name,  
    
    tc.constraint_type,  
    
    kcu.column_name  
    
FROM  

    information_schema.table_constraints AS tc  
    
JOIN  

    information_schema.key_column_usage AS kcu  
    
ON  

    tc.constraint_name = kcu.constraint_name  
    
AND  

    tc.table_schema = kcu.table_schem  
    
WHERE  

    tc.table_schema = 'berlin_data' AND tc.table_name = 'employees';

Option 2: Using psql Meta-Command (Easier)
While connected to psql, you can use the \d+ command followed by the table name:

**\d+ berlin_data.employees**

This command provides a detailed description of the table, including columns, types, and constraints.

## Populating a Table with a CSV File
To import data from a CSV file into a table, use the \copy command within the psql terminal. This command is executed on the client-side (your local machine), so the CSV file path should be accessible from where you run psql.

Example:
**\copy berlin_data.employees (id, name) FROM '/path/to/your/employees.csv' DELIMITER ',' CSV HEADER;**

berlin_data.employees: The target table to insert data into.

(id, name): Specifies the columns in the table that correspond to the data in the CSV file. Adjust this list to match your table's columns and the order in your CSV.

FROM '/path/to/your/employees.csv': The full path to your CSV file on your local machine. Remember to replace /path/to/your/employees.csv with the actual path.

DELIMITER ',': Specifies that the values in the CSV are separated by commas.

CSV HEADER: Indicates that the first line of your CSV file is a header row and should be skipped during import. If your CSV does not have a header, omit this keyword.

