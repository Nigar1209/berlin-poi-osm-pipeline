# 🚔 Berlin Crime Atlas Manual Download Instructions

## Automatic Download Failed ⚠️

Please manually download the Crime Atlas data using the steps below:

### 📥 Primary Source (Recommended)
1. **Visit**: https://daten.berlin.de/datensaetze/kriminalitatsatlas-berlin
2. **Look for**: Download button or link to Excel/XLSX file
3. **Save as**: `kriminalitaetsatlas_2014-2023.xlsx`
4. **Place in**: `sources/crime_atlas/` directory

### 📊 Alternative Source
1. **Visit**: https://www.kriminalitaetsatlas.berlin.de/
2. **Navigate to**: Data download section
3. **Download**: Latest available XLSX file
4. **Rename and place** as described above

### 📋 What to Look For
The file should contain:
- **Columns**: Bezirk, Bezirksregion, RAUMID, Delikt, Jahr, Fallzahl, Häufigkeitszahl
- **Years**: 2014-2023 (biennial data)
- **Areas**: 12 Berlin districts, 138 district regions
- **Crime Types**: 17 different categories

### 🆘 If You Still Have Issues
1. Check if the Berlin Open Data Portal structure has changed
2. Search for "Kriminalitätsatlas" or "Crime Statistics" on the portal
3. Contact Berlin Open Data support if the dataset is no longer available
4. Consider using historical data from previous years as a fallback

### 📞 Support Resources
- **Berlin Open Data Portal**: https://daten.berlin.de
- **Police Crime Atlas**: https://www.polizei.berlin.de/service/kriminalitaetsatlas/
- **Technical Documentation**: Check the README.md for more details

---
*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
