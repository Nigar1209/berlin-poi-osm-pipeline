## Data Source

The primary data source for this project is a JSON file containing detailed information about **Deutsche Post** service locations within Berlin.

The data was obtained from the official [Deutsche Post](https://www.deutschepost.de/de/s/standorte.html) store locator website. Since a direct download of the location data is not provided, the file was acquired by:
1.  Using the browser's **Developer Tools** to monitor the **Network** tab.
2.  Performing a search for "Berlin" on the page.
3.  Applying a filter by selecting the "Postfiliale" service type. This action triggered the specific API request containing the desired data.

The server's response was a structured JSON file, which serves as the raw data for this project. This file includes key information for each service point, such as:

* Full address details (street, house number, zip code, city, and district).
* Geospatial coordinates (latitude and longitude).
* The name and type of the location.
* Detailed opening hours and other services stored in nested objects.

### Update Frequency

* The live data on the Deutsche Post server is updated **continuously** as locations are added, removed, or their details change. It is not on a fixed hourly or daily schedule.
* Our captured file (`raw_post.json`) represents a **snapshot** of the data at the moment it was downloaded and will not update on its own.

### Data Type

* **Source:** The source is **dynamic**. To get the most current data, the capture process must be repeated.
* **Our File:** Our `raw_post.json` is a **static, one-time import**.

### Relevant Data Fields

The raw JSON contains numerous fields. The most relevant for this project are:
* `zipCode`, `city`, `district`, `street`, `houseNo`: Full address components.
* `locationName`: The name of the service point.
* `keyWord`: The primary type of the location (e.g., *Postfiliale*).
* `geoPosition`: A nested object containing `latitude` and `longitude`.
* `pfTimeinfos`: A nested list of objects containing detailed opening hours for each day of the week.
