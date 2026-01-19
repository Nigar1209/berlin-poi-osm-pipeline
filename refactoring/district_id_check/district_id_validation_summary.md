# Database Table Analysis

## Overview

This document contains a complete inventory of all physically existing base tables
available in the `berlin_source_data` schema.  
The list is derived from `information_schema.tables` and reflects the tables that are
currently visible and accessible to the executing database role.

## Key Insights

- The dataset represents **structural metadata only**, not table contents.
- Only **BASE TABLES** are included; views, temporary tables, and system objects are excluded.
- The table list can be used as a **single source of truth** for downstream data engineering,
  data quality checks, or ingestion pipelines.
- The ordering by table name enables **deterministic comparisons** across environments
  or over time (e.g. schema drift detection).
- The result does **not** provide information about row counts, column definitions,
  data freshness, or data volume.
- Many broken relationships come from different IDs because they are mapped with VarChar instead of INT. In the district and neighborhood tables, the IDs often start with a leading zero, while in the other tables this leading zero is missing.

| Revise | Table Name | Column | Constraint Issue | Missing / Orphan IDs | ID Character varying | is nullable | Logical Notes |
|--------|------------|--------|------------------|----------------------|----------------------|-------------|---------------|
| YES | banks | district_id | - | - | 100 | NO | - |
| - | - | neighborhood_id | - | 84 NULL | 20 | YES | missing neighborhoods: 0103, 0303, 0304, 0306, 0308, 0309, 0311, 0312, 0406, 0505, 0506, 0507, 0509, 0605, 0606, 0702, 0704, 0803, 0902, 0904, 0906, 0908, 0912, 0913, 0914, 0915, 1003, 1102, 1104, 1106, 1107, 1201, 1202, 1203, 1204, 1206, 1208, 1209, 1211 |
| YES | bike_lanes | district_id | RULE_VIOLATION | - | 10 | NO | - |
| - | - | neighborhood_id | - | 57273 ORPHAN | 10 | NO | - |
| - | bus_stops | district_id | - | - | NaN | NO | - |
| - | - | neighborhood_id | - | - | NaN | NO | - |
| YES | dental_offices | district_id | - | - | NaN | NO | - |
| - | - | neighborhood_id | - | 239 NULL | 20 | YES | missing neighborhoods: 0303, 0304, 0306, 0308, 0309, 0310, 0312, 0502, 0505, 0506, 0507, 0508, 0606, 0703, 0803, 0902, 0904, 0905, 0906, 0907, 0908, 0912, 0913, 0914, 0915, 1002, 1104, 1106, 1107, 1110, 1206, 1208, 1209, 1211 |
| - | districts | district_id | - | - | - | - | - |
| - | - | neighborhood_id | - | - | - | - | - |
| YES | doctors | district_id | - | - | 20 | NO | - |
| - | - | neighborhood_id | - | 1393 ORPHAN | 20 | NO | missing neighborhoods: 0306, 0308, 0312, 0915, 1104, 1106, 1107, 1203, 1207, 1208 |
| YES | exhibition_centers | district_id | - | - | 200 | NO | Missing Districts: 11001001, 11002002, 11003003, 11005005, 11006006, 11007007, 11008008, 11009009, 11011011, 11012012 |
| - | - | neighborhood_id | - | - | 20 | YES | missing neighborhoods: 0101, 0102, 0103, 0104, 0105, 0106, 0201, 0202, 0301, 0302, 0303, 0304, 0305, 0306, 0307, 0308, 0309, 0310, 0311, 0312, 0313, 0401, 0402, 0403, 0404, 0406, 0407, 0501, 0502, 0503, 0504, 0505, 0506, 0507, 0508, 0509, 0601, 0602, 0603, 0604, 0605, 0606, 0607, 0701, 0702, 0703, 0704, 0705, 0706, 0801, 0802, 0803, 0804, 0805, 0901, 0902, 0903, 0904, 0905, 0906, 0907, 0908, 0909, 0910, 0911, 0912, 0913, 0914, 0915, 1002, 1003, 1004, 1005, 1101, 1102, 1103, 1104, 1106, 1107, 1109, 1110, 1111, 1112, 1201, 1202, 1203, 1204, 1205, 1206, 1207, 1208, 1209, 1210, 1211 |
| YES | food_markets | district_id | - | - | 8 | NO | - |
| - | - | neighborhood_id | - | - | 4 | YES | missing neighborhoods: 0304, 0305, 0306, 0308, 0309, 0310, 0311, 0312, 0404, 0406, 0503, 0504, 0505, 0506, 0507, 0508, 0509, 0605, 0606, 0902, 0906, 0908, 0909, 0912, 0913, 0914, 0915, 1002, 1004, 1104, 1106, 1107, 1109, 1110, 1201, 1203, 1204, 1207, 1210, 1211 |
| YES | galleries | district_id | - | - | 200 | NO | - |
| - | - | neighborhood_id | - | - | 20 | YES | missing neighborhoods: 0303, 0304, 0305, 0306, 0308, 0309, 0310, 0312, 0313, 0403, 0404, 0405, 0406, 0407, 0502, 0503, 0505, 0506, 0507, 0508, 0509, 0603, 0604, 0606, 0703, 0704, 0705, 0706, 0803, 0804, 0805, 0902, 0903, 0904, 0905, 0906, 0910, 0911, 0912, 0913, 0914, 0915, 1001, 1002, 1003, 1004, 1101, 1102, 1103, 1104, 1106, 1107, 1109, 1111, 1202, 1203, 1204, 1207, 1208, 1209, 1210, 1211 |
| YES | government_offices | district_id | RULE_VIOLATION | - | 10 | NO | - |
| - | - | neighborhood_id | - | - | 10 | NO | Missing neighborhoods: 0303, 0305, 0308, 0310, 0312, 0313, 0505, 0508, 0607, 0705, 0803, 0804, 0805, 0908, 0909, 0912, 0913, 0914, 0915, 1004, 1104, 1106, 1107, 1111, 1203, 1205, 1206, 1207, 1208 |
| YES | gyms | district_id | - | - | 20 | NO | - |
| - | - | neighborhood_id | - | 437 NULL | 20 | YES | Missing neighborhoods: 0101, 0102, 0103, 0104, 0105, 0106, 0201, 0202, 0301, 0302, 0303, 0304, 0305, 0306, 0307, 0308, 0309, 0310, 0311, 0312, 0313, 0401, 0402, 0403, 0404, 0405, 0406, 0407, 0501, 0502, 0503, 0504, 0505, 0506, 0507, 0508, 0509, 0601, 0602, 0603, 0604, 0605, 0606, 0607, 0701, 0702, 0703, 0704, 0705, 0706, 0801, 0802, 0803, 0804, 0805, 0901, 0902, 0903, 0904, 0905, 0906, 0907, 0908, 0909, 0910, 0911, 0912, 0913, 0914, 0915, 1001, 1002, 1003, 1004, 1005, 1101, 1102, 1103, 1104, 1106, 1107, 1109, 1110, 1111, 1112, 1201, 1202, 1203, 1204, 1205, 1206, 1207, 1208, 1209, 1210, 1211 |
| YES | hospitals | district_id | - | - | 20 | NO | - |
| - | - | neighborhood_id | - | 3 NULL | 20 | YES | Missing Neighborhoods: 0103, 0303, 0304, 0306, 0308, 0310, 0312, 0313, 0406, 0502, 0503, 0504, 0702, 0705, 0802, 0805, 0902, 0903, 0906, 0909, 0913, 0914, 0915, 1104, 1106, 1107, 1203, 1204, 1205, 1207, 1208, 1209 |
| YES | kindergartens | district_id | - | - | NaN | NO | - |
| - | - | neighborhood_id | - | 1922 ORPHAN | NaN | YES | missing neighborhoods: 0306 |
| YES | libraries | district_id | - | - | 50 | NO | - |
| - | - | neighborhood_id | - | - | 100 | YES | missing neighborhoods: 0303, 0304, 0306, 0308, 0310, 0311, 0312, 0407, 0503, 0505, 0509, 0606, 0702, 0704, 0803, 0902, 0903, 0904, 0908, 0912, 0913, 0914, 0915, 1002, 1003, 1104, 1106, 1107, 1110, 1112, 1203, 1204, 1206, 1207, 1208, 1209, 1211 |
| YES | long_term_listings | district_id | - | - | NaN | NO | - |
| - | - | neighborhood_id | - | 51 NULL | 20 | YES | Missing neighborhoods: 0305, 0306, 0308, 0312, 0505, 0903, 0908, 1106, 1111, 1203, 1207, 1208 |
| YES | malls | district_id | - | - | 10 | NO | - |
| - | - | neighborhood_id | - | 61 ORPHAN | NaN | YES | Missing neighborhoods: 0103, 0303, 0304, 0305, 0306, 0308, 0309, 0310, 0311, 0312, 0313, 0402, 0403, 0404, 0405, 0406, 0407, 0505, 0507, 0508, 0509, 0603, 0605, 0606, 0607, 0704, 0706, 0803, 0804, 0902, 0903, 0904, 0906, 0909, 0911, 0912, 0913, 0914, 0915, 1003, 1004, 1102, 1104, 1106, 1107, 1203, 1204, 1205, 1206, 1208, 1209, 1211 |
| YES | milieuschutz_protection_zones | district_id | - | - | 100 | NO | Missing Districts: 11010010 |
| - | - | neighborhood_id | - | - | 20 | YES | Missing neighborhoods: 0101, 0102, 0103, 0104, 0105, 0201, 0301, 0302, 0303, 0304, 0305, 0306, 0307, 0308, 0309, 0310, 0311, 0312, 0401, 0402, 0403, 0404, 0405, 0406, 0501, 0502, 0503, 0504, 0505, 0506, 0507, 0508, 0601, 0602, 0603, 0604, 0605, 0606, 0701, 0702, 0703, 0704, 0705, 0801, 0802, 0803, 0804, 0901, 0902, 0903, 0904, 0905, 0906, 0907, 0908, 0909, 0910, 0912, 0913, 0914, 0915, 1001, 1002, 1003, 1004, 1005, 1101, 1102, 1103, 1104, 1106, 1107, 1109, 1110, 1111, 1201, 1202, 1203, 1204, 1205, 1206, 1207, 1208, 1209, 1210 |
| YES | museums | district_id | - | - | 200 | NO | - |
| - | - | neighborhood_id | - | - | 20 | YES | missing neighborhoods: 0103, 0303, 0304, 0305, 0306, 0308, 0309, 0310, 0312, 0313, 0403, 0407, 0503, 0504, 0507, 0508, 0509, 0805, 0902, 0903, 0906, 0908, 0911, 0912, 0915, 1003, 1104, 1106, 1107, 1109, 1111, 1203, 1204, 1205, 1207, 1208, 1210, 1211 |
| - | neighborhoods | district_id | - | - | - | - | - |
| - | - | neighborhood_id | - | - | - | - | - |
| YES | night_clubs | district_id | - | - | 20 | NO | Missing Districts: 11006006, 11010010 |
| - | - | neighborhood_id | - | 134 ORPHAN | 20 | NO | missing neighborhoods: 0103, 0303, 0304, 0305, 0306, 0307, 0308, 0309, 0310, 0311, 0312, 0313, 0404, 0405, 0502, 0503, 0504, 0505, 0506, 0507, 0508, 0509, 0601, 0602, 0603, 0604, 0605, 0606, 0607, 0702, 0704, 0705, 0706, 0803, 0805, 0902, 0903, 0904, 0906, 0907, 0908, 0910, 0911, 0912, 0913, 0914, 0915, 1001, 1002, 1003, 1004, 1005, 1101, 1102, 1104, 1106, 1107, 1110, 1111, 1201, 1203, 1204, 1205, 1206, 1207, 1208, 1209, 1211 |
| YES | parking_spaces | district_id | RULE_VIOLATION | - | 20 | NO | - |
| - | - | neighborhood_id | - | 98 NULL | 20 | YES | - |
| YES | parks | district_id | - | - | NaN | NO | - |
| - | - | neighborhood_id | - | - | NaN | YES | missing neighborhoods: 0312 |
| YES | petstores | district_id | - | - | 50 | YES | - |
| - | - | neighborhood_id | - | - | 50 | YES | missing neighborhoods: 0102, 0103, 0104, 0106, 0303, 0304, 0306, 0307, 0308, 0311, 0312, 0313, 0404, 0405, 0406, 0503, 0505, 0506, 0508, 0509, 0605, 0606, 0607, 0703, 0706, 0803, 0805, 0901, 0902, 0904, 0905, 0906, 0907, 0908, 0909, 0912, 0913, 0914, 0915, 1004, 1102, 1104, 1106, 1107, 1109, 1110, 1111, 1203, 1204, 1206, 1208, 1210 |
| YES | pharmacies | district_id | - | - | 20 | NO | - |
| - | - | neighborhood_id | - | - | 20 | YES | missing neighborhoods: 0306, 0308, 0505, 0915, 1104, 1106, 1107, 1208 |
| YES | playgrounds | district_id | - | - | NaN | NO | - |
| - | - | neighborhood_id | - | - | NaN | YES | - |
| YES | pools | district_id | - | - | 8 | NO | - |
| - | - | neighborhood_id | - | - | 4 | YES | missing neighborhoods: 0103, 0104, 0303, 0304, 0305, 0306, 0308, 0310, 0311, 0312, 0313, 0407, 0502, 0702, 0705, 0803, 0804, 0901, 0902, 0904, 0905, 0906, 0907, 0908, 1002, 1003, 1004, 1102, 1103, 1104, 1106, 1107, 1205, 1206, 1207, 1211 |
| YES | post_offices | district_id | - | - | 20 | NO | - |
| - | - | neighborhood_id | - | 204 ORPHAN | 20 | NO | missing neighborhoods: 0103, 0305, 0306, 0308, 0309, 0312, 0404, 0501, 0502, 0504, 0505, 0506, 0507, 0508, 0509, 0604, 0605, 0606, 0607, 0705, 0706, 0803, 0804, 0805, 0902, 0904, 0906, 0907, 0908, 0910, 0911, 0912, 0913, 0914, 0915, 1002, 1003, 1004, 1005, 1104, 1106, 1202, 1203, 1204, 1205, 1206, 1207, 1208 |
| YES | public_artworks | district_id | - | - | 200 | NO | - |
| - | - | neighborhood_id | - | - | 20 | YES | missing neighborhoods: 0304, 0306, 0505, 0705, 0706, 0804, 0914, 0915, 1104, 1106, 1203, 1206, 1207, 1208, 1211 |
| YES | recycling_points | district_id | - | - | 20 | NO | - |
| - | - | neighborhood_id | - | - | 20 | YES | missing neighborhoods: 1205 |
| YES | religious_institutions | district_id | - | - | 8 | NO | - |
| - | - | neighborhood_id | - | 627 ORPHAN | 100 | YES | missing neighborhoods: 0306, 0902, 1106, 1107 |
| YES | sbahn | district_id | - | - | NaN | NO | - |
| - | - | neighborhood_id | - | 114 NULL | 20 | YES | missing neighborhoods: 0105, 0302, 0304, 0306, 0308, 0309, 0312, 0313, 0403, 0502, 0503, 0504, 0505, 0506, 0507, 0508, 0509, 0605, 0702, 0704, 0802, 0803, 0804, 0805, 0904, 0907, 0908, 0909, 0914, 0915, 1002, 1003, 1004, 1101, 1103, 1104, 1106, 1107, 1110, 1111, 1202, 1203, 1206, 1208, 1210, 1211 |
| YES | schools | district_id | - | - | NaN | YES | - |
| - | - | neighborhood_id | - | 284 NULL | 20 | YES | Missing neighborhoods: 0104, 0303, 0306, 0309, 0505, 0907, 0908, 0913, 0914, 1107, 1208 |
| YES | short_term_listings | district_id | - | - | 20 | NO | - |
| - | - | neighborhood_id | - | 12626 NULL | 20 | YES | Missing neighborhoods: 0101, 0102, 0103, 0104, 0105, 0106, 0201, 0202, 0301, 0303, 0304, 0306, 0307, 0308, 0310, 0311, 0312, 0313, 0401, 0402, 0406, 0501, 0504, 0505, 0506, 0601, 0602, 0604, 0605, 0606, 0607, 0701, 0801, 0901, 0910, 0912, 0915, 1001, 1005, 1101, 1103, 1104, 1106, 1107, 1109, 1110, 1112, 1201, 1202, 1203, 1204, 1205, 1206, 1207, 1208, 1209, 1210, 1211 |
| YES | social_clubs_activities | district_id | - | - | 100 | NO | - |
| - | - | neighborhood_id | - | - | 100 | YES | missing neighborhoods: 0306, 0902, 1106, 1107 |
| YES | spaetis | district_id | - | - | 20 | YES | Missing Districts: 11001001, 11002002, 11003003, 11004004, 11005005, 11006006, 11007007, 11008008, 11009009, 11010010, 11011011, 11012012 |
| - | - | neighborhood_id | - | - | 20 | YES | Missing Neighborhoods: 0101, 0102, 0103, 0104, 0105, 0106, 0201, 0202, 0301, 0302, 0303, 0304, 0305, 0306, 0307, 0308, 0309, 0310, 0311, 0312, 0313, 0401, 0402, 0403, 0404, 0405, 0406, 0407, 0501, 0502, 0503, 0504, 0505, 0506, 0507, 0508, 0509, 0601, 0602, 0603, 0604, 0605, 0606, 0607, 0701, 0702, 0703, 0704, 0705, 0706, 0801, 0802, 0803, 0804, 0805, 0901, 0902, 0903, 0904, 0905, 0906, 0907, 0908, 0909, 0910, 0911, 0912, 0913, 0914, 0915, 1001, 1002, 1003, 1004, 1005, 1101, 1102, 1103, 1104, 1106, 1107, 1109, 1110, 1111, 1112, 1201, 1202, 1203, 1204, 1205, 1206, 1207, 1208, 1209, 1210, 1211 |
| YES | supermarkets | district_id | - | - | NaN | NO | - |
| - | - | neighborhood_id | - | 1080 ORPHAN | NaN | YES | missing neighborhoods: 0306, 0308, 1106, 1208 |
| YES | theaters | district_id | - | - | 10 | NO | - |
| - | - | neighborhood_id | - | - | NaN | YES | missing neighborhoods: 0303, 0304, 0305, 0306, 0308, 0309, 0310, 0312, 0313, 0403, 0406, 0503, 0504, 0505, 0506, 0507, 0508, 0509, 0607, 0704, 0705, 0706, 0804, 0902, 0905, 0908, 0912, 0913, 0914, 0915, 1003, 1004, 1102, 1104, 1106, 1107, 1110, 1201, 1203, 1204, 1206, 1207, 1208, 1210, 1211 |
| YES | tram_stops | district_id | - | - | NaN | NO | Missing Districts: 11004004, 11005005, 11006006, 11007007, 11008008, 11012012 |
| - | - | neighborhood_id | - | - | NaN | NO | Missing Neighborhoods: 0103, 0104, 0202, 0303, 0305, 0306, 0308, 0309, 0313, 0401, 0402, 0403, 0404, 0405, 0406, 0407, 0501, 0502, 0503, 0504, 0505, 0506, 0507, 0508, 0509, 0601, 0602, 0603, 0604, 0605, 0606, 0607, 0701, 0702, 0703, 0704, 0705, 0706, 0801, 0802, 0803, 0804, 0805, 0901, 0902, 0903, 0906, 0908, 0914, 1002, 1003, 1104, 1106, 1107, 1201, 1202, 1203, 1204, 1205, 1206, 1207, 1208, 1209, 1210, 1211 |
| YES | ubahn | district_id | - | - | 50 | NO | Missing Districts: 11009009 |
| - | - | neighborhood_id | - | - | 20 | YES | Missing neighborhoods: 0103, 0302, 0303, 0304, 0305, 0306, 0308, 0309, 0310, 0311, 0312, 0313, 0403, 0404, 0407, 0504, 0505, 0506, 0507, 0508, 0509, 0602, 0603, 0606, 0607, 0705, 0706, 0803, 0901, 0902, 0903, 0904, 0905, 0906, 0907, 0908, 0909, 0910, 0911, 0912, 0913, 0914, 0915, 1001, 1003, 1004, 1102, 1104, 1106, 1107, 1109, 1110, 1111, 1112, 1203, 1204, 1205, 1206, 1207, 1208, 1210, 1211 |
| YES | universities | district_id | RULE_VIOLATION | - | 10 | NO | Missing Districts: 11005005, 11012012 |
| - | - | neighborhood_id | - | - | 20 | YES | Missing Neighborhoods: 0103, 0106, 0201, 0301, 0303, 0304, 0305, 0306, 0307, 0308, 0309, 0310, 0312, 0313, 0403, 0404, 0406, 0501, 0502, 0503, 0504, 0505, 0506, 0507, 0508, 0509, 0601, 0602, 0606, 0607, 0702, 0703, 0704, 0705, 0706, 0802, 0803, 0804, 0805, 0901, 0902, 0903, 0904, 0905, 0906, 0908, 0909, 0910, 0911, 0912, 0913, 0914, 0915, 1001, 1002, 1003, 1004, 1101, 1103, 1104, 1106, 1107, 1109, 1110, 1111, 1112, 1201, 1202, 1203, 1204, 1205, 1206, 1207, 1208, 1209, 1210, 1211 |
| YES | venues | district_id | - | - | 20 | NO | - |
| - | - | neighborhood_id | - | 16 NULL | 20 | YES | - |