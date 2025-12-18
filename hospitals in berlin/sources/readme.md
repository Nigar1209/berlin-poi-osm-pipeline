🏥 Hospitals in Berlin

🧪 Step 1: Research & Data Modelling

For datasets and statistics in Germany I went through the websites below and I couldn't find the approprite dataset for Hospitals in Berlin
   1. https://www.destatis.de/EN/Home/_node.html
   2. https://www-genesis.destatis.de/datenbank/online
   3. https://daten.berlin.de/datensaetze

As per Berlin Health Excellence there are:
   * More than 80 hospitals with about 20,000 beds.
   * More than 9,300 hospital physicians.
   * More than 9,200 outpatient resident physicians.
   * More than 13,000 enterprises of the healthcare industry.
   * More than 30 pharmacological enterprises.

I got the dataset for Hospitals in Berlin from DKV website:

   Source and origin: https://www.deutsches-krankenhaus-verzeichnis.de/app/suche/ergebnis

   Update frequency: Annualy 

   Data type: static

Process for data collection and cleaning:
   1. I copied the data form the DKV website and pasted it in the spreedsheet.
   2. Through REGEXEXTRACT I extracted post code from the name.
   3. By clicking on the hyperlink I got the address and location for the google maps.
   4. Then I cleaned the Distance column by using Text to column function.
   5. And removed the decimal from the rest numerical columns.

| column 	 | dtype  |
|------------|--------|
| name       | object |
| address	 | object |
| post_code  | int64  |
| coordinates| object |
| distance	 | float64|
| beds       | int64  |
| cases      | int64  |

   
* Where ever the cases is 0 the hospital's data was not updated by the last quality report.



🛠 Step 2: Data Transformation

   1. The coordinates column was split into latitude and longitude respectively.
   2. With GeoJSON file spatial data was loaded and locality and neighborhood was merged in dataframe.
   3. To visualize the data folium library was used and the neighborhood and hospitals were mapped.
   4. The columns were renamed and rearranged as follows for ERD process.

| column 	   | dtype        |
|--------------|--------------|
| name         | VARCHAR(200) |
| address	   | VARCHAR(200) |
| coordinates  | VARCHAR(100) |
| latitude     | DECIMAL(9,6) |
| longitude    | DECIMAL(9,6) |
| locality     | VARCHAR(100) |
| neighborhood | VARCHAR(100) |
| distance	   | DECIMAL(10,2)|
| beds         | INT          |
| cases        | INT          |



🧩 Step 3: Populate Database

   1. As per the script provided the hospitals table was created. (
   2. With the DB url the engine was created and connection was established.
   3. And with CREATE TABLE statement a table with column name, data type and constraints was created.
   4. Then with a query the table was verified and accessed.

Author: Mehul
