ATM Berlin – mögliche Datenquellen

Definition: ATM
Als ATM (Automated Teller Machine / Geldautomat) gelten in diesem Projekt alle von Banken betriebenen Automaten, an denen Bargeld abgehoben werden kann. Dazu zählen Geldautomaten in Bankfilialen, frei stehende Geldautomaten sowie Drive-through-Geldautomaten.
Nicht als ATM gelten Kassen in Supermärkten oder anderen Geschäften, bei denen Bargeld nur im Rahmen eines Einkaufs ausgezahlt wird.


Data Source 1
Name der Quelle:
 OpenStreetMap (OSM)
Source and origin:
 Offene, gemeinschaftlich gepflegte Kartendaten. Geldautomaten sind als Points of Interest mit dem Tag amenity=atm erfasst.
Update frequency:
 Häufig (laufende Aktualisierung durch Community).
Data type:
 Dynamisch (Abruf über Abfragen/API möglich).
Relevant fields (possible):
Eindeutige OSM-ID


Bank / Betreiber (operator)


Adresse (Straße, Hausnummer, PLZ, Ort – falls vorhanden)


Koordinaten (Latitude, Longitude)


Öffnungszeiten (optional)


Barrierefreiheit / Zugänglichkeit (optional)


Data Source 2
Name der Quelle:
 Google Maps
Source and origin:
 Kommerzielle Karten- und Standortplattform. Geldautomaten werden als Orte (POIs) angezeigt und stammen aus verschiedenen Quellen (Unternehmensangaben, Nutzerbeiträge, Drittanbieter).
Update frequency:
 Häufig (laufende Aktualisierung).
Data type:
 Dynamisch (keine offene Datenbank; Nutzung über Plattform/Services).
Relevant fields (possible):
Name des Standorts


Adresse


Koordinaten (Latitude, Longitude)


Bank / Betreiber


Öffnungszeiten (falls angegeben)


Hinweise zur Zugänglichkeit (teilweise)


Data Source 3
Name der Quelle:
 Berliner Sparkasse (stellvertretend für Bank-Websites)
Source and origin:
 Offizielle Websites von Banken mit Standort- bzw. Geldautomatensuche. Die Daten stammen direkt vom jeweiligen Bankbetreiber.
Update frequency:
 Gelegentlich (Änderungen bei Neueröffnungen, Schließungen oder Zugangszeiten).
Data type:
 Dynamisch (webbasiert; keine offene API bekannt).
Relevant fields (possible):
Name der Filiale / des Standorts


Adresse


Bank / Betreiber


Art des Automaten (Filiale, Außenautomat)


Öffnungszeiten / Zugangszeiten


Hinweise zu Einschränkungen (z. B. Nachtzugang)


Raw data or external links
OpenStreetMap (ATM-Tag): https://wiki.openstreetmap.org/wiki/Tag:amenity%3Datm
OpenStreetMap API / Overpass (Referenz): https://wiki.openstreetmap.org/wiki/Overpass_API
Google Maps (Referenz): https://www.google.com/maps
Berliner Sparkasse – Geldautomatensuche (Referenz): https://www.berliner-sparkasse.de

Planned transformation / normalization (high level)
Filterung auf das Stadtgebiet Berlin
Vereinheitlichung von Bank-/Betreibernamen
Speicherung der Koordinaten (Latitude, Longitude) als Geometrie (Point)
Zuordnung der Geldautomaten zu Bezirken und Nachbarschaften über vorhandene Gebietsgrenzen
Einordnung als Point of Interest (POI) im bestehenden Datenmodell
