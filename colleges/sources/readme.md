I did not compare three documents, as i found first document of all universities on wikipedia, which is nice, but unfortunately does not contain any university ratings. So i decide not to use data from Wikipedia. 
Current data souce which was used located here:
https://edurank.org/geo/de-berlin/
This data was last updated on March 02, 2025 and updated at least once yearly, as it takes into account all scientific ratings/citation/quotation of all universities in Europe, including Germany. Even this page is static somehow, it is most reliable and objective resource in my opinion. For the creation of this datasource, I did not include ratings of Berlin universities in Europe, as they are not good enough, comparing with other universities within Germany as LMU München or TU München for example. Feel free to add European ratings, if you think, it will be helpful for potential clients.

# Summary of this project.

1) Found and scrapped full universities in berlin data using beatiful soup Pythin Library (Initial Info- University name, Rank in Berlin-Brandenburg, Rank in Berlin)

2) Added geodata(Longitude, Latitude, Postalcode(plz), Neighborhood (District info) using Google Maps API (required registration).

3) Decide to add addiotional info to datasource.  Scrapped source web site again from scratch using beatiful soup adding new columns as Founded, Enrollment and Acceptance Rate)

4) Merged newly scrapped file with previous file, which already contained geo data.

5) Cleaned null values in postal code and replaced them with "unknown" and also removed column "acceptance rate" as it has only 80 % of Null Values  as 7 from 35.

# Documentation

I renamed three Python motebooks, by main steps of the project progress as following:  

a) Part 1 -Initial scrapping using Beatiful Soup (bs4)

b) Part 2 -adding Geodata using Google Maps API

c) Part 3 -Scrapping second time with more columns captured using bs4 and merging initial geodata file from Part3, with new version containing 3 more columns. 
