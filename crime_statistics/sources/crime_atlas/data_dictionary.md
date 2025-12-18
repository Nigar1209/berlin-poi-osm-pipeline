# 🚔 Berlin Crime Atlas Data Dictionary

## 📊 Overview
This document describes the structure and content of the Berlin Crime Atlas data file.

## 📁 File Information
- **Filename**: `kriminalitaetsatlas_2014-2023.xlsx`
- **Source**: Berlin Police Department (Polizei Berlin)
- **Format**: Microsoft Excel (XLSX)
- **License**: Creative Commons Attribution Share-Alike (CC-BY-SA)

## 📋 Expected Columns

| **German Name** | **English Translation** | **Data Type** | **Description** |
|-----------------|------------------------|---------------|-----------------|
| `Bezirk` | District | Text | Berlin district name (e.g., "Mitte") |
| `Bezirksregion` | District Region | Text | Sub-district area name |
| `RAUMID` | Area ID | Text | Unique LOR area identifier (7-digit code) |
| `Delikt` | Crime Type | Text | German crime category name |
| `Jahr` | Year | Integer | Year of data (2014, 2016, 2018, 2020, 2022, 2023) |
| `Fallzahl` | Case Count | Integer | Absolute number of reported cases |
| `Häufigkeitszahl` | Frequency Number | Float | Cases per 100,000 inhabitants |
| `EinwohnerInnen` | Residents | Integer | Population base for calculation |

## 🚨 Crime Types (German → English)

| **German** | **English** | **Category** |
|------------|-------------|--------------|
| Diebstahl | Theft | Property Crime |
| Straßenraub | Street Robbery | Violent Crime |
| Wohnungseinbruch | Residential Burglary | Property Crime |
| Fahrraddiebstahl | Bicycle Theft | Property Crime |
| Rauschgiftdelikte | Drug Crimes | Drug Offense |
| Sachbeschädigung | Property Damage | Property Crime |
| Körperverletzung | Assault | Violent Crime |
| Betrug | Fraud | Financial Crime |
| Taschendiebstahl | Pickpocketing | Property Crime |
| Autodiebstahl | Vehicle Theft | Property Crime |
| Einbruch in Keller/Boden | Cellar/Attic Burglary | Property Crime |
| Vandalismus | Vandalism | Property Crime |
| Gewalt in öffentlichen Räumen | Public Space Violence | Violent Crime |
| Sexualdelikte | Sexual Offenses | Violent Crime |
| Häusliche Gewalt | Domestic Violence | Violent Crime |
| Jugendkriminalität | Youth Crime | Various |
| Internetkriminalität | Cybercrime | Financial Crime |

## 🗺️ Geographic Structure

### 📍 LOR Area ID Format (RAUMID)
- **Format**: 7-digit number (e.g., "1011303")
- **Structure**: BPGBNPR
  - **B**: Bezirk (District) - 1 digit
  - **PG**: Prognoseraum (Forecast Area) - 2 digits  
  - **BN**: Bezirksregion (District Region) - 2 digits
  - **PR**: Planungsraum (Planning Area) - 2 digits

### 🏛️ Administrative Levels
1. **Bezirk** (District): 12 total districts
2. **Bezirksregion** (District Region): 138 total regions
3. **Planungsraum** (Planning Area): 542 total areas

## 📊 Data Quality Notes

### ✅ Expected Data Quality
- **Completeness**: All districts and regions should be present
- **Consistency**: RAUMID codes should be valid LOR identifiers
- **Accuracy**: Case counts should be non-negative integers
- **Timeliness**: Data reflects biennial reporting cycle

### ⚠️ Known Issues
1. **Temporal Gaps**: Data published every 2 years (2014, 2016, 2018, 2020, 2022, 2023)
2. **Language Dependency**: All original data in German
3. **Geographic Changes**: LOR boundaries may change over time
4. **Reporting Variations**: Different crime types may have different detection rates

### 🔍 Validation Checks
- [ ] File opens correctly in Excel/LibreOffice
- [ ] All expected columns are present
- [ ] RAUMID codes follow 7-digit format
- [ ] Years match expected biennial pattern
- [ ] Case counts are realistic (not negative, not impossibly high)
- [ ] Population figures are reasonable for Berlin areas

## 🔄 Processing Notes

### 🛠️ Transformation Requirements
1. **Translation**: Convert German crime types to English
2. **Standardization**: Normalize area names and IDs
3. **Interpolation**: Handle missing years between biennial reports
4. **Validation**: Check data consistency and outliers
5. **Geographic Mapping**: Convert RAUMID to coordinates

### 📈 Derived Metrics
- **Safety Scores**: Composite metric based on multiple crime types
- **Risk Levels**: Categorical classification (very_low to very_high)  
- **Trends**: Year-over-year changes in crime patterns
- **Density**: Crime rate per square kilometer

---

## 📞 Support Information

**Data Issues**: Contact Berlin Open Data Portal support  
**Technical Questions**: Refer to project documentation  
**Last Updated**: {datetime.now().strftime('%Y-%m-%d')}  
