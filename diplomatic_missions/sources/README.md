### 1.1 Data Source Discovery

- Main source: OpenStreetMap (OSM)
- Reason: Open, free, community-maintained, and continuously updated geospatial dataset with detailed tagging for diplomatic missions.
- Data type: Dynamic (can be refreshed automatically via API).
- Update frequency: Continuous (OSM data changes continuously; dataset snapshots can be generated on demand).

- Supplementary sources: Used only to fill gaps and for data validation, not as authoritative primary sources.
    - Wikidata
        - Purpose: Stable identifiers (Q-IDs), links, and cross-references.
        - License: CC0 (Public Domain).
    - Official government sources (e.g. Auswärtiges Amt, berlin.de)
        - Purpose: Verification of existence and official naming.
    - Private aggregators (e.g. EmbassyPages, Embassy-Berlin.net, CIBTvisas)
        - Purpose: Gap detection and contact detail hints.
        - Note: Not redistributed as primary data due to licensing constraints.

## OSM

Link: https://overpass-turbo.eu/ + Query

| Field | Description |
|------|-------------|
| source | OpenStreetMap via Overpass Turbo, Berlin administrative area |
| update_frequency | one-time export, constantly on the site |
| data_type | Static (one-time import) |
| license | ODbL 1.0 (Open Database License) – © OpenStreetMap contributors |

---

## Wikidata

Link: https://query.wikidata.org/ + query

| Field | Description |
|------|-------------|
| source | Wikidata (Wikidata Query Service / SPARQL), items located in Berlin |
| update_frequency | one-time export, Constantly updated on Wikidata |
| data_type | Static (one-time import) |
| license | CC0 1.0 (Public Domain) – provided by Wikidata contributors |

---

## berlin.de

Link: 

| Field | Description |
|------|-------------|
| source | Land Berlin – berlin.de (Tourismusportal: „Botschaften in Berlin“) |
| update_frequency | static |
| data_type | Static (one-time import) |
| license | © Land Berlin – Use in accordance with berlin.de terms of use |

---

## auswaertigesamt

Stand Okt 2025 aus pdf

https://www.auswaertiges-amt.de/de/reiseundsicherheit/vertretungen-anderer-staaten

| Field | Description |
|------|-------------|
| source | Auswärtiges Amt (Deutschland) – „Vertretungen anderer Staaten in Deutschland“ (PDF) |
| update_frequency | Irregular (maintained by the Auswärtiges Amt); snapshot export |
| data_type | Static (one-time import) |
| license | © Auswärtiges Amt – Use in accordance with auswaertiges-amt.de terms of use |

---

## Private pages
They serve at most for data verification or to fill in missing data.

---

### Embassy-Berlin.net

Link: https://embassy-berlin.net

| Field | Description |
|------|-------------|
| source | Embassy-Berlin.net (private, non-governmental website with address lists of diplomatic missions in Berlin) |
| update_frequency | static |
| data_type | Static (one-time import) |
| license | © Embassy-Berlin.net – Use in accordance with Embassy-Berlin.net terms of use |

---

### embassypages

Link: https://www.embassypages.com/stadt/berlin

| Field | Description |
|------|-------------|
| source | EmbassyPages (private, non-governmental website aggregating contact details of diplomatic missions worldwide) |
| update_frequency | Irregular (maintained by site operator); snapshot export |
| data_type | Static (one-time import) |
| license | © EmbassyPages – Use in accordance with embassypages.com terms of use |