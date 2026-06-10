# Specialized Pipelines

## Geospatial Linguistics & Web Automation/Archival

### `README.md` — 04-geospatial-linguistics

# Geospatial Linguistics

This directory contains research on mapping Irish language areas, schools, and demographic data using modern geospatial tools.

## Overview

Visualizing the linguistic landscape of Celtic language communities requires combining census data, administrative boundaries, and educational infrastructure. This research focuses on building a proof-of-concept map for Gaeltacht areas and Irish-medium schools using DuckDB, dlt, and MapLibre.

### Primary Use Cases

1. **Gaeltacht Mapping** - Visualize official Irish-speaking areas
2. **School Distribution** - Map Gaelscoileanna locations
3. **Census Analysis** - Analyze speaker demographics by area
4. **Cross-Border Comparison** - Compare ROI and NI data

## Documents in this Category

| Document | Focus | Key Topics |
|----------|-------|------------|
| `duckdb-spatial.md` | Geospatial analysis | DuckDB spatial extension, queries |
| `maplibre-visualization.md` | Web mapping | MapLibre GL JS, vector tiles |
| `data-sources.md` | Official datasets | Census, boundaries, schools |

## Data Sources Overview

### Republic of Ireland

| Data Type | Source | Format | Level |
|-----------|--------|--------|-------|
| **Gaeltacht Boundaries** | Tailte Éireann | GeoJSON, Shapefile | Electoral Division |
| **Language Planning Areas** | Tailte Éireann | GeoJSON, Shapefile | LPA |
| **Census Data** | CSO (PxStat) | CSV, XLSX | Small Area |
| **School Data** | gov.ie, Gaeloideachas | Excel | Individual |

### Northern Ireland

| Data Type | Source | Format | Level |
|-----------|--------|--------|-------|
| **Data Zones** | NISRA | GeoJSON, Shapefile | DZ2021 |
| **Census Data** | NISRA | CSV | Data Zone |
| **School Data** | DE NI, CnaG | Excel | Individual |

## Technical Stack

```yaml
Data Ingestion: dltHub
Storage: DuckDB with spatial extension
Processing: Ibis, Python
Visualization: MapLibre GL JS
Tile Generation: tippecanoe
```

## Key Metrics

### Irish Language Indicators

| Metric | ROI Census 2022 | NI Census 2021 |
|--------|-----------------|----------------|
| **Can Speak Irish** | 1.87M (40%) | 228,617 (12.45%) |
| **Daily Speakers** | 71,968 | 43,557 |
| **Gaeltacht Pop** | 106,220 | N/A |
| **Gaeltacht Speakers** | 65,156 (66%) | N/A |

### Schools

| Type | ROI | NI |
|------|-----|-----|
| **Primary Irish-medium** | 256 total | ~30 standalone |
| **Post-primary Irish-medium** | ~75 | 10 units |

## Architecture

```
+------------------+     +------------------+
|   Census Data    |     |   Boundary Data  |
|   (CSV/Excel)    |     |   (GeoJSON)      |
+--------+---------+     +--------+---------+
         |                        |
         v                        v
+------------------------------------------+
|              dltHub Pipeline             |
|   - Normalize encoding                   |
|   - Geocode addresses                    |
|   - Join census to boundaries            |
+------------------------------------------+
         |
         v
+------------------------------------------+
|           DuckDB + Spatial               |
|   - Spatial joins                        |
|   - Aggregations                         |
|   - Choropleth calculations              |
+------------------------------------------+
         |
         v
+------------------------------------------+
|         MapLibre GL JS                   |
|   - Vector tiles (MVT)                   |
|   - Interactive layers                   |
|   - Data-driven styling                  |
+------------------------------------------+
```

## Geographic Levels

### Republic of Ireland

| Level | Count | Use Case |
|-------|-------|----------|
| **Small Areas** | ~18,000 | Census data |
| **Electoral Divisions** | 3,409 | Gaeltacht boundaries |
| **Counties** | 31 | Regional analysis |

### Northern Ireland

| Level | Count | Use Case |
|-------|-------|----------|
| **Data Zones (DZ2021)** | 3,780 | Census data |
| **Super Data Zones** | 890 | Aggregation |
| **Council Areas** | 11 | Regional analysis |

## Cross-Border Considerations

| Challenge | Mitigation |
|-----------|------------|
| Different census years | Compare trends, not absolutes |
| Different geographies | Aggregate to comparable levels |
| Different questions | Focus on common metrics (ability, frequency) |
| No NI Gaeltacht | Define by speaker concentration |

## Key Data Downloads

### ROI Boundaries

- **Gaeltacht Areas**: https://data-osi.opendata.arcgis.com/datasets/osi::gaeltacht-areas-national-administrative-boundaries-ungeneralised-2024
- **Language Planning Areas**: https://data-osi.opendata.arcgis.com/datasets/osi::gaeltacht-language-planning-areas-national-administrative-boundaries-ungen-2024

### NI Boundaries

- **Data Zones (GeoJSON)**: https://www.nisra.gov.uk/files/nisra/publications/geography-dz2021-geojson.zip
- **Data Zones (Shapefile)**: https://www.nisra.gov.uk/files/nisra/publications/geography-dz2021-esri-shapefile.zip

## Cross-References

- **Category 02 (Data Acquisition)** - Collection pipelines
- **Category 05 (Education Policy)** - School enrollment context
- Main research Category 03 (AI-Native Data Pipelines) - dlt patterns
- Main research Category 04 (Stealth Browser Stack) - Web scraping


---

### `data-sources.md` — 04-geospatial-linguistics

# Geospatial Data Sources for Celtic Language Mapping

## Overview

This document provides detailed information on official data sources for Gaeltacht boundaries, census statistics, and school locations in the Republic of Ireland and Northern Ireland.

---

## 1. Republic of Ireland - Boundaries

### 1.1 Gaeltacht Areas

Official Gaeltacht regions defined by the Gaeltacht Area Orders (1956, 1967, 1974, 1982).

| Property | Value |
|----------|-------|
| **Source** | Tailte Éireann |
| **Dataset** | Gaeltacht Areas - National Administrative Boundaries - Ungeneralised - 2024 |
| **Portal** | data.gov.ie |
| **Formats** | GeoJSON, Shapefile, CSV, KML |
| **Level** | Electoral Division (parts of) |

**Download URL:**
https://data-osi.opendata.arcgis.com/datasets/osi::gaeltacht-areas-national-administrative-boundaries-ungeneralised-2024

**Coverage:**
- 155 Electoral Divisions (or parts)
- Counties: Cork, Donegal, Galway, Kerry, Mayo, Meath, Waterford

### 1.2 Language Planning Areas (LPAs)

Areas designated under the Gaeltacht Act 2012 for language planning.

| Property | Value |
|----------|-------|
| **Source** | Tailte Éireann |
| **Dataset** | Gaeltacht Language Planning Areas - Ungeneralised - 2024 |
| **Portal** | data.gov.ie |
| **Formats** | GeoJSON, Shapefile, CSV, KML |
| **Count** | 26 LPAs |

**Download URL:**
https://data-osi.opendata.arcgis.com/datasets/osi::gaeltacht-language-planning-areas-national-administrative-boundaries-ungen-2024

### 1.3 Small Area Boundaries

Census geography for detailed population analysis.

| Property | Value |
|----------|-------|
| **Source** | CSO / Tailte Éireann |
| **Count** | ~18,000 Small Areas |
| **Portal** | data.gov.ie / PxStat |
| **Formats** | GeoJSON, Shapefile |

---

## 2. Republic of Ireland - Census Data

### 2.1 Census 2022 - Irish Language

**Source:** Central Statistics Office (CSO)
**Portal:** https://data.cso.ie (PxStat)

**Key Statistics:**

| Metric | Value | Change from 2016 |
|--------|-------|------------------|
| Can speak Irish | 1,873,997 (40%) | +112,500 |
| Daily speakers (outside education) | 71,968 | -1,835 |
| Weekly speakers | 115,065 | - |
| Within education only | 553,965 | - |
| Never speak | ~473,000 | - |

**Proficiency Levels:**

| Level | Count | Percentage |
|-------|-------|------------|
| Very well | 195,029 | 10% |
| Well | 593,898 | 32% |
| Not well | 1,034,132 | 55% |

**Gaeltacht Specific:**

| Metric | Value |
|--------|-------|
| Total population | 106,220 |
| Irish speakers | 65,156 (66%) |
| Daily speakers | 20,000+ |

**Key Tables (PxStat):**

| Table ID | Content |
|----------|---------|
| F8014 | Irish speakers by frequency, Gaeltacht area |
| E8014 | Ability to speak Irish by area |
| F8015 | Irish speakers by proficiency |

### 2.2 Download Instructions

1. Navigate to https://data.cso.ie
2. Search for "Irish language" or table ID
3. Select geographic level (ED, SA, County)
4. Download as CSV or XLSX

---

## 3. Republic of Ireland - School Data

### 3.1 Department of Education

**Portal:** https://www.gov.ie/en/service/find-a-school/

**Data Available:**
- School Roll Number
- Address
- Eircode
- Phone/Email
- Enrollment figures

**Format:** Excel spreadsheets

### 3.2 Gaeloideachas

**Portal:** https://gaeloideachas.ie/directories/

**Lists Available (June 2023):**

| List | Content | Format |
|------|---------|--------|
| Primary Schools | Bunscoileanna 32 counties | Excel |
| Post-Primary Schools | Iar-bhunscoileanna 32 counties | Excel |
| Units (Aonaid) | Irish-medium units | Excel |

**Key Fields:**
- School name
- County
- Irish-medium status (explicit)

### 3.3 Data Combination Strategy

1. Download Gaeloideachas lists (definitive Irish-medium identification)
2. Download Department of Education lists (Eircodes, official addresses)
3. Join on School Roll Number or normalized school name
4. Geocode using Eircode

---

## 4. Northern Ireland - Boundaries

### 4.1 Data Zones (DZ2021)

Primary small-area geography for Census 2021.

| Property | Value |
|----------|-------|
| **Source** | NISRA |
| **Count** | 3,780 Data Zones |
| **Formats** | GeoJSON, Shapefile, Geodatabase |

**Download URLs:**

| Format | URL |
|--------|-----|
| **GeoJSON** | https://www.nisra.gov.uk/files/nisra/publications/geography-dz2021-geojson.zip |
| **Shapefile** | https://www.nisra.gov.uk/files/nisra/publications/geography-dz2021-esri-shapefile.zip |

### 4.2 Geographic Hierarchy

| Level | Count | Notes |
|-------|-------|-------|
| Data Zones | 3,780 | Primary census unit |
| Super Data Zones | 890 | Aggregation level |
| District Electoral Areas | 80 | Electoral boundaries |
| Local Government Districts | 11 | Council areas |

---

## 5. Northern Ireland - Census Data

### 5.1 Census 2021 - Irish Language

**Source:** NISRA
**Portal:** https://build.nisra.gov.uk (Flexible Table Builder)

**Key Statistics:**

| Metric | Value | Percentage |
|--------|-------|------------|
| Some ability in Irish | 228,617 | 12.45% |
| Irish as main language | 5,969 | 0.32% |
| Daily speakers | 43,557 | 2.43% |

**Detailed Abilities:**

| Ability | Count | % of those with ability |
|---------|-------|------------------------|
| Understand only | 90,800 | 39.7% |
| Understand, speak, read, write | 71,900 | 31.4% |

### 5.2 Data Access

**Flexible Table Builder:** https://build.nisra.gov.uk

Features:
- Custom variable selection
- Cross-tabulation
- Geographic filtering to Data Zone
- CSV export

**Note:** Statistical Disclosure Control may suppress small counts.

---

## 6. Northern Ireland - School Data

### 6.1 Department of Education NI

**Portal:** https://www.education-ni.gov.uk

**Irish-Medium Schools List:**
https://www.education-ni.gov.uk/articles/irish-medium-schools

**Content:**
- 30 standalone Irish-medium schools
- 10 Irish-medium units
- 46 nurseries (via CnaG)

### 6.2 School Enrolment Data

**URL:** https://www.education-ni.gov.uk/publications/school-enrolment-school-level-data-202223

**Files Available:**
- Primary schools (Excel)
- Post-primary schools (Excel)
- Nursery schools (Excel)

**Key Fields:**
- School name
- Address
- Postcode
- School Reference Number

### 6.3 Comhairle na Gaelscolaíochta (CnaG)

**Portal:** https://www.comhairle.org

Authoritative source for Irish-medium education in NI.

**Data Strategy:**
1. Get school names from DE NI Irish-medium list
2. Get postcodes from school enrolment Excel files
3. Cross-reference with CnaG for Naíscoileanna

---

## 7. Data Quality Notes

### 7.1 Coordinate Reference Systems

| Jurisdiction | Native CRS | Web Map CRS |
|--------------|------------|-------------|
| ROI | Irish Transverse Mercator (ITM) | WGS84 (EPSG:4326) |
| NI | Irish Grid (IG) | WGS84 (EPSG:4326) |

**Transform in DuckDB:**
```sql
SELECT ST_Transform(geom, 'EPSG:4326') AS geom_wgs84 FROM boundaries;
```

### 7.2 Temporal Alignment

| Data Type | ROI Date | NI Date |
|-----------|----------|---------|
| Census | 2022 | 2021 |
| Boundaries | 2024 | 2021 |
| Schools | 2023/24 | 2022/23 |

### 7.3 Geographic Comparability

| Challenge | Solution |
|-----------|----------|
| Different census years | Compare trends, not absolutes |
| Different small areas | Aggregate to council/county level |
| No NI Gaeltacht | Define by speaker concentration |

---

## 8. Summary Table

| Data Type | ROI Source | ROI Format | NI Source | NI Format |
|-----------|------------|------------|-----------|-----------|
| **Gaeltacht Boundaries** | Tailte Éireann | GeoJSON | N/A | Define from census |
| **Census - Language** | CSO PxStat | CSV | NISRA Builder | CSV |
| **Small Area Boundaries** | Tailte Éireann | GeoJSON | NISRA | GeoJSON |
| **Schools** | gov.ie + Gaeloideachas | Excel | DE NI + CnaG | Excel |

---

## 9. Download Checklist

### ROI

- [ ] Gaeltacht Areas 2024 (GeoJSON)
- [ ] Language Planning Areas 2024 (GeoJSON)
- [ ] Small Area Boundaries 2022 (GeoJSON)
- [ ] Census F8014 - Irish speakers by frequency
- [ ] Department of Education school list
- [ ] Gaeloideachas school lists

### NI

- [ ] Data Zone Boundaries DZ2021 (GeoJSON)
- [ ] Census 2021 Irish language data (via Flexible Table Builder)
- [ ] School enrolment data (Excel)
- [ ] Irish-medium schools list

---

## References

- Tailte Éireann: https://data-osi.opendata.arcgis.com
- CSO PxStat: https://data.cso.ie
- NISRA: https://www.nisra.gov.uk
- data.gov.ie: https://data.gov.ie
- OpenDataNI: https://www.opendatani.gov.uk


---

### `duckdb-spatial.md` — 04-geospatial-linguistics

# DuckDB Spatial for Celtic Language Mapping

## Overview

DuckDB's spatial extension provides PostGIS-compatible geospatial functions for analyzing Celtic language areas, performing spatial joins between census data and boundaries, and preparing data for visualization.

---

## 1. Setup

### 1.1 Installation

```python
import duckdb

# Create connection and install spatial
conn = duckdb.connect("celtic_geo.duckdb")
conn.execute("INSTALL spatial; LOAD spatial;")
```

### 1.2 Verify Installation

```sql
-- Check spatial functions available
SELECT * FROM duckdb_functions() WHERE function_name LIKE 'ST_%' LIMIT 10;
```

---

## 2. Loading Geospatial Data

### 2.1 GeoJSON Files

```sql
-- Load Gaeltacht boundaries from GeoJSON
CREATE TABLE gaeltacht_areas AS
SELECT * FROM ST_Read('/path/to/gaeltacht_areas.geojson');

-- Load NI Data Zones
CREATE TABLE ni_data_zones AS
SELECT * FROM ST_Read('/path/to/dz2021.geojson');
```

### 2.2 Shapefiles

```sql
-- Load from Shapefile
CREATE TABLE language_planning_areas AS
SELECT * FROM ST_Read('/path/to/lpa_boundaries.shp');
```

### 2.3 CSV with Coordinates

```sql
-- Load schools with lat/lng columns
CREATE TABLE schools AS
SELECT
    school_name,
    roll_number,
    eircode,
    ST_Point(longitude, latitude) AS geom
FROM read_csv('/path/to/schools.csv');
```

---

## 3. Core Spatial Operations

### 3.1 Point in Polygon (Schools in Gaeltacht)

```sql
-- Find schools within Gaeltacht areas
SELECT
    s.school_name,
    s.roll_number,
    g.area_name AS gaeltacht_name
FROM schools s
JOIN gaeltacht_areas g
ON ST_Within(s.geom, g.geom);
```

### 3.2 Spatial Join (Census to Boundaries)

```sql
-- Join census data to Gaeltacht boundaries
SELECT
    g.area_name,
    SUM(c.irish_speakers) AS total_speakers,
    SUM(c.population) AS total_population,
    ROUND(100.0 * SUM(c.irish_speakers) / SUM(c.population), 2) AS speaker_pct
FROM gaeltacht_areas g
JOIN census_small_areas c
ON ST_Intersects(g.geom, c.geom)
GROUP BY g.area_name
ORDER BY speaker_pct DESC;
```

### 3.3 Buffer Analysis

```sql
-- Find schools within 5km of Gaeltacht boundaries
SELECT
    s.school_name,
    ST_Distance(s.geom, g.geom) / 1000 AS distance_km
FROM schools s, gaeltacht_areas g
WHERE ST_DWithin(s.geom, ST_Buffer(g.geom, 5000), 0)
ORDER BY distance_km;
```

### 3.4 Area Calculations

```sql
-- Calculate area of each Gaeltacht region
SELECT
    area_name,
    ROUND(ST_Area(geom) / 1000000, 2) AS area_km2
FROM gaeltacht_areas
ORDER BY area_km2 DESC;
```

---

## 4. Census Data Analysis

### 4.1 Speaker Concentration Mapping

```sql
-- Calculate speaker percentage by Small Area
CREATE TABLE speaker_choropleth AS
SELECT
    sa.sa_code,
    sa.geom,
    c.can_speak_irish,
    c.daily_speakers,
    c.population,
    ROUND(100.0 * c.can_speak_irish / NULLIF(c.population, 0), 2) AS ability_pct,
    ROUND(100.0 * c.daily_speakers / NULLIF(c.population, 0), 2) AS daily_pct
FROM small_area_boundaries sa
JOIN census_language c ON sa.sa_code = c.sa_code;
```

### 4.2 Gaeltacht vs Non-Gaeltacht Comparison

```sql
-- Compare speaker rates inside vs outside Gaeltacht
WITH classified AS (
    SELECT
        c.*,
        CASE WHEN g.area_name IS NOT NULL THEN 'Gaeltacht' ELSE 'Non-Gaeltacht' END AS area_type
    FROM census_small_areas c
    LEFT JOIN gaeltacht_areas g ON ST_Within(c.geom, g.geom)
)
SELECT
    area_type,
    SUM(population) AS total_pop,
    SUM(irish_speakers) AS total_speakers,
    ROUND(100.0 * SUM(irish_speakers) / SUM(population), 2) AS speaker_pct,
    SUM(daily_speakers) AS total_daily,
    ROUND(100.0 * SUM(daily_speakers) / SUM(population), 2) AS daily_pct
FROM classified
GROUP BY area_type;
```

### 4.3 County-Level Aggregation

```sql
-- Aggregate to county level
SELECT
    county,
    SUM(population) AS pop,
    SUM(irish_speakers) AS speakers,
    ROUND(100.0 * SUM(irish_speakers) / SUM(population), 2) AS pct,
    COUNT(*) AS num_areas
FROM census_small_areas
GROUP BY county
ORDER BY pct DESC;
```

---

## 5. School Analysis

### 5.1 School Density by Area

```sql
-- Count Irish-medium schools per county
SELECT
    county,
    COUNT(*) AS num_schools,
    SUM(enrollment) AS total_pupils
FROM irish_medium_schools
GROUP BY county
ORDER BY num_schools DESC;
```

### 5.2 Schools in Language Planning Areas

```sql
-- Identify schools in each LPA
SELECT
    lpa.lpa_name,
    COUNT(s.roll_number) AS num_schools,
    STRING_AGG(s.school_name, ', ') AS schools
FROM language_planning_areas lpa
LEFT JOIN irish_medium_schools s
ON ST_Within(s.geom, lpa.geom)
GROUP BY lpa.lpa_name
ORDER BY num_schools DESC;
```

### 5.3 Distance to Nearest School

```sql
-- Calculate distance to nearest Irish-medium school for each area
WITH nearest AS (
    SELECT
        sa.sa_code,
        MIN(ST_Distance(sa.geom, s.geom)) AS min_distance
    FROM small_area_boundaries sa
    CROSS JOIN irish_medium_schools s
    GROUP BY sa.sa_code
)
SELECT
    sa_code,
    min_distance / 1000 AS nearest_school_km
FROM nearest
ORDER BY min_distance DESC
LIMIT 20;
```

---

## 6. Cross-Border Analysis

### 6.1 Unified View

```sql
-- Create unified view of speaker data
CREATE VIEW all_ireland_speakers AS
SELECT
    'ROI' AS jurisdiction,
    sa_code AS area_code,
    geom,
    population,
    irish_speakers,
    daily_speakers
FROM roi_census_small_areas

UNION ALL

SELECT
    'NI' AS jurisdiction,
    dz_code AS area_code,
    geom,
    population,
    irish_ability AS irish_speakers,
    daily_speakers
FROM ni_census_data_zones;
```

### 6.2 Border Region Analysis

```sql
-- Define border counties
WITH border_counties AS (
    SELECT * FROM counties
    WHERE county_name IN (
        'Donegal', 'Leitrim', 'Cavan', 'Monaghan', 'Louth',  -- ROI
        'Derry', 'Tyrone', 'Fermanagh', 'Armagh', 'Down'     -- NI
    )
)
SELECT
    bc.county_name,
    bc.jurisdiction,
    SUM(c.irish_speakers) AS speakers,
    SUM(c.population) AS population,
    ROUND(100.0 * SUM(c.irish_speakers) / SUM(c.population), 2) AS pct
FROM border_counties bc
JOIN all_ireland_speakers c ON ST_Within(c.geom, bc.geom)
GROUP BY bc.county_name, bc.jurisdiction
ORDER BY pct DESC;
```

---

## 7. Export for MapLibre

### 7.1 GeoJSON Export

```sql
-- Export choropleth data as GeoJSON
COPY (
    SELECT
        sa_code,
        ability_pct,
        daily_pct,
        ST_AsGeoJSON(geom) AS geometry
    FROM speaker_choropleth
) TO '/output/speakers.geojson'
WITH (FORMAT JSON);
```

### 7.2 Prepare for Vector Tiles

```sql
-- Simplify geometries for web display
CREATE TABLE web_gaeltacht AS
SELECT
    area_name,
    speaker_pct,
    ST_Simplify(geom, 100) AS geom  -- 100m tolerance
FROM gaeltacht_areas;

-- Export for tippecanoe
COPY web_gaeltacht TO '/output/gaeltacht.geojson'
WITH (FORMAT JSON);
```

### 7.3 Centroid Export (For Labels)

```sql
-- Generate centroids for labeling
SELECT
    area_name,
    ST_X(ST_Centroid(geom)) AS lng,
    ST_Y(ST_Centroid(geom)) AS lat
FROM gaeltacht_areas;
```

---

## 8. Complete Pipeline Example

```python
#!/usr/bin/env python3
"""
DuckDB Spatial Pipeline for Celtic Language Mapping
"""

import duckdb
from pathlib import Path

class CelticGeoPipeline:
    def __init__(self, db_path: str = ":memory:"):
        self.conn = duckdb.connect(db_path)
        self.conn.execute("INSTALL spatial; LOAD spatial;")

    def load_boundaries(self, geojson_path: str, table_name: str):
        """Load GeoJSON boundaries."""
        self.conn.execute(f"""
            CREATE TABLE {table_name} AS
            SELECT * FROM ST_Read('{geojson_path}')
        """)

    def load_census_csv(self, csv_path: str, table_name: str):
        """Load census data from CSV."""
        self.conn.execute(f"""
            CREATE TABLE {table_name} AS
            SELECT * FROM read_csv('{csv_path}')
        """)

    def join_census_to_boundaries(
        self,
        census_table: str,
        boundary_table: str,
        join_key: str
    ):
        """Spatial join census data to boundaries."""
        return self.conn.execute(f"""
            SELECT
                b.*,
                c.population,
                c.irish_speakers,
                c.daily_speakers,
                ROUND(100.0 * c.irish_speakers / NULLIF(c.population, 0), 2) AS pct
            FROM {boundary_table} b
            LEFT JOIN {census_table} c ON b.{join_key} = c.{join_key}
        """).fetchdf()

    def schools_in_areas(self, schools_table: str, areas_table: str):
        """Find schools within areas."""
        return self.conn.execute(f"""
            SELECT
                a.area_name,
                COUNT(s.*) AS num_schools
            FROM {areas_table} a
            LEFT JOIN {schools_table} s ON ST_Within(s.geom, a.geom)
            GROUP BY a.area_name
        """).fetchdf()

    def export_geojson(self, query: str, output_path: str):
        """Export query result as GeoJSON."""
        self.conn.execute(f"""
            COPY ({query}) TO '{output_path}'
            WITH (FORMAT JSON)
        """)

def main():
    pipeline = CelticGeoPipeline("celtic_geo.duckdb")

    # Load data
    pipeline.load_boundaries(
        "gaeltacht_areas.geojson",
        "gaeltacht"
    )

    # Analysis
    results = pipeline.schools_in_areas("schools", "gaeltacht")
    print(results)

    # Export
    pipeline.export_geojson(
        "SELECT * FROM gaeltacht",
        "output/gaeltacht.geojson"
    )

if __name__ == "__main__":
    main()
```

---

## 9. Performance Tips

| Operation | Tip |
|-----------|-----|
| **Large datasets** | Use `ST_Simplify()` for web export |
| **Spatial joins** | Create spatial index with `CREATE INDEX` |
| **Point-in-polygon** | Use `ST_DWithin()` for approximate queries |
| **Memory** | Use disk-based DB for >1GB data |

---

## References

- DuckDB Spatial: https://duckdb.org/docs/extensions/spatial
- PostGIS (compatible functions): https://postgis.net/docs/
- Tailte Éireann Open Data: https://data-osi.opendata.arcgis.com


---

### `maplibre-visualization.md` — 04-geospatial-linguistics

# MapLibre Visualization for Celtic Language Data

## Overview

MapLibre GL JS is an open-source library for rendering interactive maps from vector tiles. This document covers implementation patterns for visualizing Irish language areas, schools, and census data.

---

## 1. Basic Setup

### 1.1 HTML Template

```html
<!DOCTYPE html>
<html>
<head>
    <title>Celtic Language Map</title>
    <link href="https://unpkg.com/maplibre-gl@3.6.2/dist/maplibre-gl.css" rel="stylesheet" />
    <script src="https://unpkg.com/maplibre-gl@3.6.2/dist/maplibre-gl.js"></script>
    <style>
        body { margin: 0; padding: 0; }
        #map { position: absolute; top: 0; bottom: 0; width: 100%; }
        .legend {
            position: absolute;
            bottom: 30px;
            left: 10px;
            background: white;
            padding: 10px;
            border-radius: 4px;
            box-shadow: 0 1px 4px rgba(0,0,0,0.3);
        }
    </style>
</head>
<body>
    <div id="map"></div>
    <div class="legend" id="legend"></div>

    <script src="app.js"></script>
</body>
</html>
```

### 1.2 Initialize Map

```javascript
// app.js
const map = new maplibregl.Map({
    container: 'map',
    style: {
        version: 8,
        sources: {
            'osm': {
                type: 'raster',
                tiles: ['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],
                tileSize: 256,
                attribution: '© OpenStreetMap'
            }
        },
        layers: [{
            id: 'osm-tiles',
            type: 'raster',
            source: 'osm'
        }]
    },
    center: [-8.0, 53.5],  // Ireland center
    zoom: 6
});
```

---

## 2. Loading Data Sources

### 2.1 GeoJSON Source

```javascript
map.on('load', () => {
    // Add Gaeltacht boundaries
    map.addSource('gaeltacht', {
        type: 'geojson',
        data: '/data/gaeltacht_areas.geojson'
    });

    // Add schools
    map.addSource('schools', {
        type: 'geojson',
        data: '/data/irish_medium_schools.geojson'
    });

    // Add census choropleth
    map.addSource('census', {
        type: 'geojson',
        data: '/data/speaker_choropleth.geojson'
    });
});
```

### 2.2 Vector Tiles Source

```javascript
// For large datasets, use vector tiles
map.addSource('census-tiles', {
    type: 'vector',
    tiles: ['https://your-server.com/tiles/census/{z}/{x}/{y}.pbf'],
    minzoom: 0,
    maxzoom: 14
});
```

---

## 3. Layer Styling

### 3.1 Choropleth Layer (Speaker Percentage)

```javascript
map.addLayer({
    id: 'census-choropleth',
    type: 'fill',
    source: 'census',
    paint: {
        'fill-color': [
            'interpolate',
            ['linear'],
            ['get', 'speaker_pct'],
            0, '#f7fbff',
            10, '#c6dbef',
            20, '#9ecae1',
            40, '#6baed6',
            60, '#3182bd',
            80, '#08519c'
        ],
        'fill-opacity': 0.7
    }
});

// Add outline
map.addLayer({
    id: 'census-outline',
    type: 'line',
    source: 'census',
    paint: {
        'line-color': '#333',
        'line-width': 0.5
    }
});
```

### 3.2 Gaeltacht Boundaries

```javascript
map.addLayer({
    id: 'gaeltacht-fill',
    type: 'fill',
    source: 'gaeltacht',
    paint: {
        'fill-color': '#228B22',
        'fill-opacity': 0.3
    }
});

map.addLayer({
    id: 'gaeltacht-outline',
    type: 'line',
    source: 'gaeltacht',
    paint: {
        'line-color': '#228B22',
        'line-width': 2,
        'line-dasharray': [2, 2]
    }
});
```

### 3.3 School Points

```javascript
map.addLayer({
    id: 'schools-points',
    type: 'circle',
    source: 'schools',
    paint: {
        'circle-radius': [
            'interpolate',
            ['linear'],
            ['get', 'enrollment'],
            50, 4,
            200, 8,
            500, 12
        ],
        'circle-color': [
            'match',
            ['get', 'school_type'],
            'primary', '#4CAF50',
            'secondary', '#2196F3',
            '#9E9E9E'
        ],
        'circle-stroke-width': 1,
        'circle-stroke-color': '#fff'
    }
});
```

### 3.4 Labels

```javascript
map.addLayer({
    id: 'gaeltacht-labels',
    type: 'symbol',
    source: 'gaeltacht',
    layout: {
        'text-field': ['get', 'area_name'],
        'text-size': 12,
        'text-anchor': 'center'
    },
    paint: {
        'text-color': '#333',
        'text-halo-color': '#fff',
        'text-halo-width': 1
    }
});
```

---

## 4. Interactivity

### 4.1 Hover Effects

```javascript
// Highlight on hover
map.on('mousemove', 'census-choropleth', (e) => {
    map.getCanvas().style.cursor = 'pointer';

    if (e.features.length > 0) {
        const feature = e.features[0];

        // Update info panel
        document.getElementById('info').innerHTML = `
            <strong>${feature.properties.area_name}</strong><br>
            Population: ${feature.properties.population.toLocaleString()}<br>
            Speakers: ${feature.properties.speaker_pct}%<br>
            Daily: ${feature.properties.daily_pct}%
        `;
    }
});

map.on('mouseleave', 'census-choropleth', () => {
    map.getCanvas().style.cursor = '';
});
```

### 4.2 Click Popups

```javascript
map.on('click', 'schools-points', (e) => {
    const feature = e.features[0];
    const coordinates = feature.geometry.coordinates.slice();

    new maplibregl.Popup()
        .setLngLat(coordinates)
        .setHTML(`
            <h3>${feature.properties.school_name}</h3>
            <p>
                <strong>Type:</strong> ${feature.properties.school_type}<br>
                <strong>Enrollment:</strong> ${feature.properties.enrollment}<br>
                <strong>Address:</strong> ${feature.properties.address}
            </p>
        `)
        .addTo(map);
});
```

### 4.3 Layer Toggle

```javascript
function toggleLayer(layerId, visible) {
    const visibility = visible ? 'visible' : 'none';
    map.setLayoutProperty(layerId, 'visibility', visibility);
}

// Usage
document.getElementById('toggle-gaeltacht').addEventListener('change', (e) => {
    toggleLayer('gaeltacht-fill', e.target.checked);
    toggleLayer('gaeltacht-outline', e.target.checked);
});
```

---

## 5. Legend

### 5.1 Choropleth Legend

```javascript
function createLegend() {
    const legend = document.getElementById('legend');

    const grades = [0, 10, 20, 40, 60, 80];
    const colors = ['#f7fbff', '#c6dbef', '#9ecae1', '#6baed6', '#3182bd', '#08519c'];

    legend.innerHTML = '<h4>Irish Speakers (%)</h4>';

    grades.forEach((grade, i) => {
        const next = grades[i + 1] || '+';
        legend.innerHTML += `
            <div>
                <span style="background:${colors[i]}; width:20px; height:20px; display:inline-block;"></span>
                ${grade}${next !== '+' ? ' - ' + next : next}
            </div>
        `;
    });
}

map.on('load', createLegend);
```

### 5.2 School Legend

```javascript
function createSchoolLegend() {
    const legend = document.getElementById('school-legend');

    legend.innerHTML = `
        <h4>Schools</h4>
        <div>
            <span style="background:#4CAF50; width:12px; height:12px; display:inline-block; border-radius:50%;"></span>
            Primary
        </div>
        <div>
            <span style="background:#2196F3; width:12px; height:12px; display:inline-block; border-radius:50%;"></span>
            Secondary
        </div>
    `;
}
```

---

## 6. Vector Tile Generation

### 6.1 Using tippecanoe

```bash
#!/bin/bash
# Generate vector tiles from GeoJSON

# Census choropleth tiles
tippecanoe \
    -o census.mbtiles \
    -z 14 \
    -l census \
    --coalesce-densest-as-needed \
    --extend-zooms-if-still-dropping \
    speaker_choropleth.geojson

# Gaeltacht boundaries
tippecanoe \
    -o gaeltacht.mbtiles \
    -z 14 \
    -l gaeltacht \
    --simplify-only-low-zooms \
    gaeltacht_areas.geojson

# Schools (preserve all features)
tippecanoe \
    -o schools.mbtiles \
    -z 14 \
    -l schools \
    --drop-smallest-as-needed \
    -r1 \
    irish_medium_schools.geojson
```

### 6.2 Serving Tiles

```bash
# Using tileserver-gl
docker run --rm -it \
    -v $(pwd)/tiles:/data \
    -p 8080:8080 \
    maptiler/tileserver-gl
```

---

## 7. Complete Application

```javascript
// Full application with all features
class CelticLanguageMap {
    constructor(containerId) {
        this.map = new maplibregl.Map({
            container: containerId,
            style: this.getBaseStyle(),
            center: [-8.0, 53.5],
            zoom: 6
        });

        this.map.on('load', () => this.initLayers());
    }

    getBaseStyle() {
        return {
            version: 8,
            sources: {
                'carto': {
                    type: 'raster',
                    tiles: ['https://basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png'],
                    tileSize: 256,
                    attribution: '© CartoDB © OSM'
                }
            },
            layers: [{
                id: 'base',
                type: 'raster',
                source: 'carto'
            }]
        };
    }

    async initLayers() {
        // Load data sources
        await this.loadSource('gaeltacht', '/data/gaeltacht.geojson');
        await this.loadSource('census', '/data/census.geojson');
        await this.loadSource('schools', '/data/schools.geojson');

        // Add layers
        this.addChoroplethLayer();
        this.addGaeltachtLayer();
        this.addSchoolsLayer();

        // Setup interactivity
        this.setupPopups();
        this.createLegend();
    }

    async loadSource(id, url) {
        const response = await fetch(url);
        const data = await response.json();

        this.map.addSource(id, {
            type: 'geojson',
            data: data
        });
    }

    addChoroplethLayer() {
        this.map.addLayer({
            id: 'census-fill',
            type: 'fill',
            source: 'census',
            paint: {
                'fill-color': [
                    'interpolate', ['linear'], ['get', 'speaker_pct'],
                    0, '#f7fbff',
                    10, '#c6dbef',
                    20, '#9ecae1',
                    40, '#6baed6',
                    60, '#3182bd',
                    80, '#08519c'
                ],
                'fill-opacity': 0.6
            }
        });
    }

    addGaeltachtLayer() {
        this.map.addLayer({
            id: 'gaeltacht-boundary',
            type: 'line',
            source: 'gaeltacht',
            paint: {
                'line-color': '#228B22',
                'line-width': 3
            }
        });
    }

    addSchoolsLayer() {
        this.map.addLayer({
            id: 'schools',
            type: 'circle',
            source: 'schools',
            paint: {
                'circle-radius': 6,
                'circle-color': '#E91E63',
                'circle-stroke-width': 2,
                'circle-stroke-color': '#fff'
            }
        });
    }

    setupPopups() {
        // School popups
        this.map.on('click', 'schools', (e) => {
            const props = e.features[0].properties;
            new maplibregl.Popup()
                .setLngLat(e.lngLat)
                .setHTML(`<h3>${props.school_name}</h3><p>Enrollment: ${props.enrollment}</p>`)
                .addTo(this.map);
        });

        // Cursor changes
        ['census-fill', 'schools'].forEach(layer => {
            this.map.on('mouseenter', layer, () => {
                this.map.getCanvas().style.cursor = 'pointer';
            });
            this.map.on('mouseleave', layer, () => {
                this.map.getCanvas().style.cursor = '';
            });
        });
    }

    createLegend() {
        // Implementation from section 5
    }
}

// Initialize
const celticMap = new CelticLanguageMap('map');
```

---

## 8. Data-Driven Styling Examples

### 8.1 Gradient by Daily Speakers

```javascript
'fill-color': [
    'case',
    ['<', ['get', 'daily_pct'], 1], '#fee5d9',
    ['<', ['get', 'daily_pct'], 5], '#fcae91',
    ['<', ['get', 'daily_pct'], 10], '#fb6a4a',
    ['<', ['get', 'daily_pct'], 20], '#de2d26',
    '#a50f15'
]
```

### 8.2 School Size by Enrollment

```javascript
'circle-radius': [
    'step',
    ['get', 'enrollment'],
    4,   // Default
    100, 6,
    200, 8,
    500, 12
]
```

---

## References

- MapLibre GL JS: https://maplibre.org/maplibre-gl-js/docs/
- tippecanoe: https://github.com/felt/tippecanoe
- CartoDB Basemaps: https://carto.com/basemaps
- OpenStreetMap: https://www.openstreetmap.org


---

### `README.md` — 04-web-automation-archival

# Web Automation & Archival Systems

This directory consolidates research on autonomous web scraping architectures, anti-bot evasion strategies, and AI-driven content extraction for building comprehensive data archives.

## Overview

The research covers the complete stack for intelligent web data acquisition:
- **Stealth Browser Infrastructure**: Patchright, Browserless, CDP architecture
- **Anti-Bot Evasion**: Cloudflare Turnstile bypass, TLS fingerprinting countermeasures
- **Agentic Scraping**: Skyvern visual agents, Stagehand operators, Crawl4AI gatherers
- **MCP Integration**: Model Context Protocol for tool interoperability
- **Irish Educational Archives**: examinations.ie, ncca.ie, curriculumonline.ie workflows

## Documents in this Category

| Document | Focus | Key Technologies |
|----------|-------|------------------|
| `stealth-browser-stack.md` | Self-hosted anti-detection infrastructure | Patchright, CDP, Docker Compose |
| `agentic-scraping-architecture.md` | Hunter-Gatherer-Operator patterns | Skyvern, Stagehand, Crawl4AI |
| `adaptive-crawling.md` | Semantic vector traversal strategies | Crawl4AI, BestFirstStrategy, BM25 |
| `irish-archives-workflow.md` | Educational data acquisition pipelines | examinations.ie, ncca.ie workflows |

## Key Architectural Decisions

### 1. The Hybrid "Swarm" Architecture

```
User Request
    ↓
┌─────────────────────────────────────────┐
│           MCP Orchestrator              │
│    (Tool Discovery & Dispatch)          │
└─────────────────────────────────────────┘
    ↓                    ↓                ↓
┌──────────┐      ┌──────────┐      ┌──────────┐
│ SKYVERN  │      │STAGEHAND │      │ CRAWL4AI │
│ (Hunter) │      │(Operator)│      │(Gatherer)│
│          │      │          │      │          │
│ Visual   │      │ Cached   │      │ Semantic │
│ Mapping  │      │ Actions  │      │ Crawling │
└──────────┘      └──────────┘      └──────────┘
    ↓                    ↓                ↓
         ┌───────────────────────────┐
         │    PATCHRIGHT GRID       │
         │  (Stealth Browser Pool)  │
         └───────────────────────────┘
```

### 2. Tool Selection Matrix

| Scenario | Tool | Rationale |
|----------|------|-----------|
| Unknown/Dynamic UI | Skyvern | Visual reasoning adapts to layout changes |
| Repetitive Forms | Stagehand | Cached selectors after first LLM call |
| Hierarchical Sites | Crawl4AI | Semantic filtering, high throughput |
| Legacy Deep Web | Stagehand | State-dependent interactions |
| CAPTCHA Challenge | Theyka Solver | Token extraction microservice |

### 3. Cloudflare Turnstile Detection Layers

| Layer | Detection Method | Countermeasure |
|-------|-----------------|----------------|
| Network (TLS) | JA3/JA4 fingerprinting | Patchright binary patching |
| Runtime | `navigator.webdriver` | Patchright C++ patches |
| Behavioral | Mouse/keystroke entropy | Human-like delays |
| Canvas/WebGL | GPU fingerprinting | Xvfb headful mode |

## Quick Reference

### Docker Compose Stack

```yaml
services:
  browser-grid:
    build: ./browser-grid  # Patchright stealth
    shm_size: '2gb'
    cap_add: [SYS_ADMIN]

  solver-service:
    image: theyka/turnstile-solver:latest
    environment:
      - BROWSER_TYPE=chromium

  mcp-server:
    build: ./mcp-server
    environment:
      - CDP_URL=ws://browser-grid:9222
      - SOLVER_API_URL=http://solver-service:5000/turnstile
```

### Crawl4AI Adaptive Configuration

```python
from crawl4ai import AsyncWebCrawler, AdaptiveConfig
from crawl4ai.deep_crawling import BestFirstCrawlingStrategy

strategy = BestFirstCrawlingStrategy(
    max_depth=5,
    max_pages=5000,
    scorer_config={
        "keywords": ["curriculum", "specification", "syllabus"],
        "weight": 0.85
    }
)

config = CrawlerRunConfig(
    deep_crawl_strategy=strategy,
    fit_markdown=True,
    adaptive_config=AdaptiveConfig(
        confidence_threshold=0.8,
        min_gain_threshold=0.05
    )
)
```

### Stagehand Form Automation

```typescript
import { Stagehand } from "@browserbasehq/stagehand";

const stagehand = new Stagehand({ llmClient: myClient });
await stagehand.init();

// First call: LLM finds selector
// Subsequent calls: Uses cached selector (no LLM cost)
await page.act("Select '2024' from the Year dropdown");
await page.act("Click the Search button");

// Extract with schema
const data = await page.extract({
    instruction: "Extract all exam paper download links",
    schema: z.object({
        papers: z.array(z.object({
            subject: z.string(),
            level: z.string(),
            downloadUrl: z.string()
        }))
    })
});
```

## Source Files Consolidated

This category merges content from:
- `Open-Source Crawl4ai Anti-Bot Stack.md`
- `Integrating Skyvern with Crawl4AI_Stagehand.md`
- `Open-Source Web Scraping Architecture Analysis.md`
- `Celtic Data Scraping and Integration Plan.md`
- `Unified Scraping Swarm Stack Optimization.md`

## Performance Benchmarks

| Tool | Pages/Minute | Cost/1000 Pages | Best For |
|------|-------------|-----------------|----------|
| Crawl4AI | 100-500 | ~$0 (local) | Discovery |
| Stagehand (cached) | 50-100 | ~$0.50 | Forms |
| Stagehand (cold) | 5-10 | ~$5.00 | New layouts |
| Skyvern | 3-5 | ~$50.00 | Complex UI |

## Licensing Considerations

| Tool | License | Commercial Use |
|------|---------|----------------|
| Crawl4AI | Apache 2.0 | Permissive |
| Stagehand | MIT | Permissive |
| Skyvern | AGPL-3.0 | Restrictive (copyleft) |
| Patchright | MIT | Permissive |
| Browserless | Mix (OSS/Commercial) | Check edition |

## Implementation Priorities

### Phase 1: Stealth Infrastructure
1. Build Patchright Docker image with Xvfb
2. Deploy browser grid with CDP exposure
3. Configure Theyka solver service

### Phase 2: Crawler Integration
1. Implement Crawl4AI adaptive strategy
2. Configure semantic keyword scoring
3. Set up fit_markdown processing

### Phase 3: Agent Orchestration
1. Deploy Stagehand for form automation
2. Implement selector caching persistence
3. Add self-healing error recovery

### Phase 4: MCP Unification
1. Wrap scrapers as MCP tools
2. Configure tool discovery
3. Integrate with AI orchestrator


---

### `agentic-scraping-architecture.md` — 04-web-automation-archival

# Agentic Scraping Architecture: Hunter-Gatherer-Operator Pattern

## Executive Summary

This document details the "Unified Scraping Swarm" architecture that orchestrates Skyvern, Crawl4AI, and Stagehand into a cohesive system. By leveraging the Model Context Protocol (MCP) as a control plane, organizations can dynamically compose workflows using the optimal tool for each task.

---

## 1. The Fragmentation Problem

Traditional scraping architectures deploy tools in silos:

| Silo Type | Tool | Problem |
|-----------|------|---------|
| **Visual Navigation** | Skyvern | Authenticated state trapped in isolated container |
| **High-Volume Extraction** | Crawl4AI | Cannot access Skyvern's authenticated session |
| **Tactical Interaction** | Stagehand | Requires manual session management |

The **Unified Swarm** resolves this by treating browser state as a shared resource while automation libraries act as transient clients.

---

## 2. Tool Philosophies and Architectural Roles

### 2.1 Skyvern: The Visual Reasoning Engine (Hunter)

Skyvern operates on a "Vision-First" paradigm, using Vision LLMs to interpret visual renderings rather than DOM parsing.

**Mechanism:**
1. Captures viewport screenshots
2. Overlays coordinate system
3. Feeds visual data to LLM with high-level goal
4. LLM returns coordinate-based actions

**Resilience Profile:**
- Immune to DOM thrashing (randomized class names)
- Resistant to layout changes
- Handles dynamic SPAs effectively

**Architectural Role:** The **Navigator** - traverses initial barriers, solves visual puzzles, reaches target state.

```python
# Skyvern Task Configuration
task_config = {
    "url": "https://examinations.ie",
    "goal": "Navigate to the exam archive and select Mathematics 2024",
    "browser_session_id": "pbs_shared_session_123",
    "max_steps": 10
}
```

### 2.2 Crawl4AI: The High-Velocity Extractor (Gatherer)

Crawl4AI focuses on efficient transformation of unstructured content into LLM-friendly formats.

**Mechanism:**
1. Loads pages via Playwright
2. Applies heuristic intelligence (BM25, content pruning)
3. Strips boilerplate (nav, footer, ads)
4. Converts to clean Markdown

**Performance Features:**
- Aggressive caching strategies
- Parallel execution via `arun_many()`
- Image loading disabled for bandwidth

**Architectural Role:** The **Extractor** - once navigation complete, pulls content efficiently.

```python
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

browser_config = BrowserConfig(
    browser_type="chromium",
    cdp_url="http://browser-hub:9222",  # Shared browser
    verbose=True
)

run_config = CrawlerRunConfig(
    cache_mode="BYPASS",  # Real-time state after Skyvern navigation
    word_count_threshold=10,
    fit_markdown=True
)

async with AsyncWebCrawler(config=browser_config) as crawler:
    result = await crawler.arun(url="current_page", config=run_config)
```

### 2.3 Stagehand: The Hybrid Tactician (Operator)

Stagehand bridges rigid code and fluid AI intent with primitives: `act`, `extract`, `observe`.

**Mechanism:**
1. Interleaves deterministic Playwright code with AI instructions
2. Implements "Self-Healing" - caches successful selectors
3. Falls back to LLM only if cached selector fails

**Architectural Role:** The **Operator** - handles precise, multi-step interactions.

```typescript
import { Stagehand } from "@browserbasehq/stagehand";

const stagehand = new Stagehand({
  localBrowserLaunchOptions: {
    cdpUrl: "http://browser-hub:9222"
  }
});

await stagehand.init();

// First call: LLM finds selector
// Subsequent calls: Uses cached selector (no LLM cost)
await page.act("Select '2024' from the Year dropdown");
await page.act("Click the Search button");

// Extract with schema validation
const data = await page.extract({
    instruction: "Extract all exam paper download links",
    schema: z.object({
        papers: z.array(z.object({
            subject: z.string(),
            level: z.string(),
            downloadUrl: z.string()
        }))
    })
});
```

---

## 3. Tool Selection Matrix

| Scenario | Tool | Rationale |
|----------|------|-----------|
| Unknown/Dynamic UI | **Skyvern** | Visual reasoning adapts to layout changes |
| Repetitive Forms | **Stagehand** | Cached selectors after first LLM call |
| Hierarchical Sites | **Crawl4AI** | Semantic filtering, high throughput |
| Legacy Deep Web | **Stagehand** | State-dependent interactions |
| CAPTCHA Challenge | **Solver Sidecar** | Token extraction microservice |

---

## 4. MCP Integration: The Nervous System

The Model Context Protocol provides a standardized interface for AI agents to discover and invoke tools.

### 4.1 Gateway Configuration

```json
{
  "mcpServers": {
    "skyvern": {
      "command": "docker",
      "args": ["exec", "-i", "skyvern_container", "skyvern", "mcp"]
    },
    "crawl4ai": {
      "command": "docker",
      "args": ["exec", "-i", "crawl4ai_container", "python", "-m", "crawl4ai_mcp"]
    },
    "stagehand": {
      "command": "docker",
      "args": ["exec", "-i", "stagehand_container", "npm", "start"]
    },
    "turnstile_solver": {
      "command": "docker",
      "args": ["exec", "-i", "solver_container", "python", "-m", "solver_mcp"]
    }
  }
}
```

### 4.2 Tool Schema Definitions

**Skyvern Tools:**
```yaml
- name: navigate_visual
  description: Use visual AI to navigate to a goal state
  parameters:
    url: string
    goal: string
    browser_session_id: string

- name: solve_auth
  description: Complete authentication workflow
  parameters:
    credentials_id: string
```

**Crawl4AI Tools:**
```yaml
- name: extract_markdown
  description: Extract page content as clean Markdown
  parameters:
    url: string | "current_page"

- name: crawl_site
  description: Recursive crawl from starting point
  parameters:
    url: string
    max_depth: integer
    keywords: array[string]
```

**Stagehand Tools:**
```yaml
- name: act
  description: Execute specific UI action
  parameters:
    instruction: string

- name: extract_data
  description: Extract data with schema validation
  parameters:
    instruction: string
    schema: object
```

### 4.3 Dynamic Routing Example

**User Request:** "Download the invoice for the last order from Amazon."

**Orchestrator Plan:**
1. Call `skyvern.navigate_visual("amazon.com", "Go to recent orders")`
2. *Wait for completion*
3. Call `stagehand.act("Click the 'Invoice' link for the top order")`
4. *Wait for navigation*
5. Call `crawl4ai.extract_markdown("current_page")`

---

## 5. Performance Benchmarks

| Tool | Pages/Minute | Cost/1000 Pages | Best For |
|------|-------------|-----------------|----------|
| **Crawl4AI** | 100-500 | ~$0 (local) | Discovery, bulk extraction |
| **Stagehand (cached)** | 50-100 | ~$0.50 | Repetitive forms |
| **Stagehand (cold)** | 5-10 | ~$5.00 | New layouts |
| **Skyvern** | 3-5 | ~$50.00 | Complex visual UI |

---

## 6. Interoperability and State Management

### 6.1 Session Handoff Protocol

```python
# Unified session management
class SwarmSession:
    def __init__(self, cdp_url: str, session_id: str):
        self.cdp_url = cdp_url
        self.session_id = session_id
        self._lock = asyncio.Lock()

    async def with_skyvern(self):
        async with self._lock:
            return SkyvernClient(
                browser_session_id=self.session_id,
                cdp_url=self.cdp_url
            )

    async def with_crawl4ai(self):
        async with self._lock:
            browser_config = BrowserConfig(cdp_url=self.cdp_url)
            return AsyncWebCrawler(config=browser_config)

    async def with_stagehand(self):
        async with self._lock:
            return Stagehand(localBrowserLaunchOptions={
                "cdpUrl": self.cdp_url
            })
```

### 6.2 Cookie and State Persistence

```python
# Export session state for backup/restore
async def export_session_state(session: SwarmSession) -> dict:
    browser, context, _ = await attach_to_shared_browser(session.cdp_url)

    return {
        "cookies": await context.cookies(),
        "local_storage": await context.storage_state(),
        "session_id": session.session_id,
        "timestamp": datetime.utcnow().isoformat()
    }

async def restore_session_state(session: SwarmSession, state: dict):
    browser, context, _ = await attach_to_shared_browser(session.cdp_url)

    await context.add_cookies(state["cookies"])
    await context.add_init_script(f"""
        Object.keys({state['local_storage']}).forEach(key => {{
            localStorage.setItem(key, {state['local_storage']}[key]);
        }});
    """)
```

---

## 7. Licensing Considerations

| Tool | License | Commercial Use |
|------|---------|----------------|
| **Crawl4AI** | Apache 2.0 | Permissive |
| **Stagehand** | MIT | Permissive |
| **Skyvern** | AGPL-3.0 | Restrictive (copyleft) |
| **Patchright** | MIT | Permissive |
| **Browserless** | Mix (OSS/Commercial) | Check edition |

---

## 8. Implementation Priorities

### Phase 1: Foundation
1. Deploy shared Patchright browser grid
2. Configure CDP exposure and session persistence
3. Test basic tool connectivity

### Phase 2: Tool Integration
1. Deploy Skyvern with remote browser config
2. Configure Crawl4AI with CDP connection
3. Set up Stagehand with LOCAL_CDP_URL

### Phase 3: MCP Orchestration
1. Build MCP Gateway with tool registry
2. Implement browser locking mechanism
3. Create unified session management

### Phase 4: Production Workflows
1. Design domain-specific workflow templates
2. Implement error recovery and retry logic
3. Add monitoring and alerting

---

## References

- Skyvern Documentation: https://skyvern.com/docs
- Crawl4AI Documentation: https://docs.crawl4ai.com/
- Stagehand: https://github.com/browserbase/stagehand
- MCP Protocol: https://modelcontextprotocol.io/


---

### `irish-archives-workflow.md` — 04-web-automation-archival

# Irish Educational Archives Workflow

## Executive Summary

This document details specific workflows for archiving Irish educational and linguistic resources, including examinations.ie, ncca.ie, curriculumonline.ie, canuint.ie, and duchas.ie. The approach uses the Hunter-Gatherer-Operator pattern with domain-specific configurations.

---

## 1. Target Site Analysis

### 1.1 Site Classification

| Site | Type | Challenge | Tool Strategy |
|------|------|-----------|---------------|
| **examinations.ie** | Legacy Form | Session state, ViewState | Stagehand (Operator) |
| **ncca.ie** | Hierarchical Docs | Nested menus | Crawl4AI (Gatherer) |
| **curriculumonline.ie** | PDF Archive | Deep navigation | Navigation V2 Block |
| **canuint.ie** | Audio + Map | Spatial UI, audio assets | Hybrid (avoid canvas) |
| **duchas.ie** | Paginated Archive | Sequential traversal | Crawl4AI (Gatherer) |

### 1.2 Interaction Type Framework

| Type | Description | Example Sites |
|------|-------------|---------------|
| **Type A** | Hierarchical Drill-Down | ncca.ie, curriculumonline.ie |
| **Type B** | Complex Form Logic | examinations.ie |
| **Type C** | Spatial/Map Traversal | canuint.ie |
| **Type D** | Sequential/Paginated | duchas.ie |

---

## 2. examinations.ie: The Legacy Archive

### 2.1 Interface Analysis

The State Examinations Commission website represents a classic "Deep Web" legacy portal:
- ASP.NET framework with POST requests
- Session cookies and `__VIEWSTATE` parameters
- Multi-step form with dependent dropdowns

### 2.2 Workflow Design

```yaml
# examinations.ie workflow
name: irish_exam_harvester
tool: stagehand
type: Type_B_Form

steps:
  - action: navigate
    url: "https://www.examinations.ie/exammaterialarchive/"

  - action: wait
    selector: "#year-dropdown"

  - action: select
    target: "#year-dropdown"
    value: "{{ year }}"

  - action: wait
    description: "Wait for subject list to populate"
    timeout: 5000

  - action: select
    target: "#subject-dropdown"
    value: "{{ subject }}"

  - action: select
    target: "#level-dropdown"
    value: "{{ level }}"  # Higher, Ordinary, Foundation

  - action: click
    target: "#search-button"

  - action: extract
    instruction: "Extract all PDF download links from results"
    schema:
      papers:
        - filename: string
          url: string
          type: string  # Question Paper, Marking Scheme
```

### 2.3 Stagehand Implementation

```typescript
// examinations.ie scraper
const examArchive = async (year: number, subject: string, level: string) => {
  const stagehand = new Stagehand({
    localBrowserLaunchOptions: { cdpUrl: CDP_URL }
  });

  await stagehand.init();
  await page.goto("https://www.examinations.ie/exammaterialarchive/");

  // Form interaction with wait for dependent dropdowns
  await page.act(`Select '${year}' from the Year dropdown`);
  await page.waitForSelector("#subject-dropdown option:not([disabled])", { timeout: 5000 });

  await page.act(`Select '${subject}' from the Subject dropdown`);
  await page.act(`Select '${level}' from the Level dropdown`);
  await page.act("Click the Search button");

  // Extract results
  const papers = await page.extract({
    instruction: "Extract all exam paper download links with type and filename",
    schema: z.object({
      papers: z.array(z.object({
        filename: z.string(),
        url: z.string(),
        paperType: z.enum(["Question Paper", "Marking Scheme", "Audio"])
      }))
    })
  });

  return papers;
};

// Iterate through all subjects
const subjects = ["Mathematics", "English", "Irish", "Physics", "Chemistry"];
const years = [2024, 2023, 2022, 2021, 2020];
const levels = ["Higher", "Ordinary"];

for (const subject of subjects) {
  for (const year of years) {
    for (const level of levels) {
      const papers = await examArchive(year, subject, level);
      await downloadPapers(papers);
    }
  }
}
```

---

## 3. canuint.ie: Irish Dialect Audio Archive

### 3.1 Interface Analysis

Taisce Chanúintí na Gaeilge presents a hybrid interface:
- Interactive map (canvas-based - avoid)
- Text-based hierarchical lists (target)
- Audio assets linked to geographic locations

**Hierarchy:**
```
Province (Cúige)
└── Area (Limistéar)
    └── Locality/Townland
        └── Speaker → Audio Files
```

### 3.2 Navigation Strategy

**Critical:** Avoid the map canvas. Use the text list "TAIFEADTAÍ DE RÉIR LIMISTÉIR" (Recordings by Area).

```python
# canuint.ie crawler
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
from crawl4ai.deep_crawling import BestFirstCrawlingStrategy

# Province pages
provinces = [
    ("ulster", "/en/province/ulster"),
    ("connacht", "/en/province/connacht"),
    ("munster", "/en/province/munster"),
    ("leinster", "/en/province/leinster")
]

strategy = BestFirstCrawlingStrategy(
    max_depth=3,
    max_pages=1000,
    scorer_config={
        "keywords": ["taifeadtaí", "recordings", "audio"],
        "weight": 0.85
    },
    # Filter to stay within recordings sections
    url_filter=lambda url: "/recordings/" in url or "/area/" in url
)

config = CrawlerRunConfig(
    deep_crawl_strategy=strategy,
    fit_markdown=True,
    excluded_tags=["nav", "footer", "aside"],  # Strip navigation
    css_selector="main.content"  # Focus on main content
)

async def crawl_dialect_archive():
    async with AsyncWebCrawler(config=BrowserConfig(cdp_url=CDP_URL)) as crawler:
        for province_name, province_url in provinces:
            result = await crawler.arun(
                url=f"https://www.canuint.ie{province_url}",
                config=config
            )

            # Parse audio links from markdown
            audio_links = extract_audio_urls(result.markdown)

            for audio in audio_links:
                await download_audio(
                    url=audio["url"],
                    metadata={
                        "province": province_name,
                        "area": audio["area"],
                        "speaker": audio["speaker"],
                        "word": audio["lemma"]
                    }
                )
```

### 3.3 Audio Extraction Schema

```python
from pydantic import BaseModel
from typing import Optional

class DialectRecording(BaseModel):
    """Schema for canuint.ie audio entries."""
    lemma: str  # Irish word
    audio_url: str
    speaker_name: str
    area: str  # Townland/locality
    county: str
    province: str
    year_recorded: Optional[int]

class DialectCorpus(BaseModel):
    """Collection of dialect recordings."""
    recordings: list[DialectRecording]
    province: str
    extraction_date: str
```

---

## 4. duchas.ie: Folklore Collection

### 4.1 Interface Analysis

The Schools' Collection (Bailiúchán na Scol) features:
- Volume-based organization (CBÉS 0001, CBÉS 0002...)
- Explicit pagination ("Page 1 / 225")
- Rich metadata (School, County, Transcription status)

### 4.2 Sequential Crawl Strategy

```python
# duchas.ie paginated crawler
async def crawl_duchas_collection(start_volume: int = 1, end_volume: int = 1000):
    """Crawl Dúchas Schools' Collection volumes."""

    results = []

    for volume_num in range(start_volume, end_volume + 1):
        volume_id = f"CBÉS{str(volume_num).zfill(4)}"
        volume_url = f"https://www.duchas.ie/en/cbes/{volume_id}"

        # Get volume metadata
        async with AsyncWebCrawler(config=BrowserConfig(cdp_url=CDP_URL)) as crawler:
            result = await crawler.arun(url=volume_url)

            metadata = await extract_volume_metadata(result.markdown)

            # Paginate through items
            page = 1
            while True:
                page_url = f"{volume_url}?page={page}"
                page_result = await crawler.arun(url=page_url)

                items = await extract_items(page_result.markdown)
                if not items:
                    break

                for item in items:
                    results.append({
                        "volume_id": volume_id,
                        "page": page,
                        "school": metadata["school"],
                        "county": metadata["county"],
                        "transcription_pct": metadata.get("transcription_pct"),
                        **item
                    })

                page += 1

    return results
```

### 4.3 Hidden Heritages Integration

The hiddenheritages.ai project links Irish and Scottish folklore with Aarne-Thompson classification:

```python
# Cross-reference with Hidden Heritages
async def enrich_with_folklore_types(duchas_items: list[dict]):
    """Add AT folktale type classification from Hidden Heritages."""

    # Hidden Heritages provides AT type metadata
    async with AsyncWebCrawler() as crawler:
        hh_result = await crawler.arun(
            url="https://www.hiddenheritages.ai/ga/s",
            config=CrawlerRunConfig(
                fit_markdown=True,
                extraction_strategy=JsonCssExtractionStrategy(
                    schema={
                        "stories": [{
                            "title": "h3.story-title",
                            "at_type": "span.at-classification",
                            "country": "span.country-tag"
                        }]
                    }
                )
            )
        )

        # Build lookup table
        at_lookup = {s["title"]: s["at_type"] for s in hh_result.extracted}

        # Enrich duchas items
        for item in duchas_items:
            if item["title"] in at_lookup:
                item["at_type"] = at_lookup[item["title"]]

        return duchas_items
```

---

## 5. Teanglann.ie: Pronunciation Database

### 5.1 URL Pattern Analysis

Teanglann uses predictable URL structures for audio:

| Dialect | Directory | Example |
|---------|-----------|---------|
| Ulster | `/CanU/` | `/CanU/abhainn.mp3` |
| Connacht | `/CanC/` | `/CanC/abhainn.mp3` |
| Munster | `/CanM/` | `/CanM/abhainn.mp3` |

### 5.2 Speculative Download Strategy

```python
import aiohttp
import urllib.parse

async def harvest_teanglann_audio(words: list[str]):
    """
    Download Teanglann audio using predictable URL patterns.
    """
    dialects = ["CanU", "CanC", "CanM"]
    base_url = "https://www.teanglann.ie"

    async with aiohttp.ClientSession() as session:
        for word in words:
            # URL encode for fada characters (á, é, í, ó, ú)
            encoded_word = urllib.parse.quote(word)

            for dialect in dialects:
                url = f"{base_url}/{dialect}/{encoded_word}.mp3"

                # HEAD request first to check existence
                async with session.head(url) as response:
                    if response.status == 200:
                        # Download the file
                        async with session.get(url) as audio_response:
                            content = await audio_response.read()

                            # Save with metadata
                            save_audio(
                                content=content,
                                word=word,
                                dialect=dialect,
                                checksum=hashlib.md5(content).hexdigest()
                            )
                    elif response.status == 404:
                        # Audio not available for this dialect
                        log.info(f"No {dialect} audio for: {word}")
```

### 5.3 Index Traversal

```python
# Crawl alphabetical index to build word list
async def build_word_index():
    """Build comprehensive word list from Teanglann index."""
    words = []

    async with AsyncWebCrawler() as crawler:
        for letter in "abcdefghilmnoprstu":  # Irish alphabet
            index_url = f"https://www.teanglann.ie/en/fuaim/_{letter}"

            result = await crawler.arun(url=index_url)

            # Extract word links
            soup = BeautifulSoup(result.html, "html.parser")
            word_links = soup.select("a[href*='/en/fuaim/']")

            for link in word_links:
                word = link.get_text().strip()
                if word and word != letter.upper():
                    words.append(word)

            # Check for sub-indices (e.g., ACH, ACU for 'a')
            sub_indices = soup.select(".sub-index a")
            for sub in sub_indices:
                sub_url = f"https://www.teanglann.ie{sub['href']}"
                sub_result = await crawler.arun(url=sub_url)
                # ... extract words from sub-index

    return words
```

---

## 6. sources.yaml Configuration

```yaml
# Comprehensive Celtic Educational Sources Configuration
groups:
  - id: irish_educational_framework
    description: "Primary and Post-Primary Curriculum Specifications"
    targets:
      - url: "https://www.curriculumonline.ie/Primary/Curriculum-Areas/"
        name: "Irish Primary Curriculum"
        type: "Type_A_Hierarchical"
        depth: 2
        content_types: ["pdf", "html_toolkit"]
        priority: high

      - url: "https://ncca.ie/en/junior-cycle/subjects/"
        name: "NCCA Junior Cycle Subjects"
        type: "Type_A_Hierarchical"
        priority: high

  - id: examination_archives
    description: "State Examination Papers and Marking Schemes"
    targets:
      - url: "https://www.examinations.ie/exammaterialarchive/"
        name: "SEC Exam Archive"
        type: "Type_B_Form"
        inputs:
          years: [2024, 2023, 2022, 2021, 2020]
          subjects: ["Mathematics", "English", "Irish", "Physics", "Chemistry"]
          levels: ["Higher", "Ordinary", "Foundation"]
        priority: critical

  - id: celtic_audio_archives
    description: "Dialect and Pronunciation Archives"
    targets:
      - url: "https://www.canuint.ie/ga/"
        name: "Taisce Chanúintí na Gaeilge"
        type: "Type_C_Spatial"
        instruction: "Navigate via Text List only. Do not use Map Canvas."
        priority: high

      - url: "https://www.teanglann.ie/en/fuaim/"
        name: "Teanglann Pronunciation Database"
        type: "Type_A_Hierarchical"
        note: "Use speculative URL construction for audio files"
        priority: medium

  - id: folklore_manuscripts
    description: "Historical Folklore Collections"
    targets:
      - url: "https://www.duchas.ie/en/cbes"
        name: "Schools' Collection"
        type: "Type_D_Sequential"
        pagination_indicator: "Page number / "
        priority: medium

      - url: "https://www.hiddenheritages.ai/ga/s"
        name: "Hidden Heritages (Irish)"
        type: "Type_D_Sequential"
        filters: ["Éire"]
        priority: medium
```

---

## 7. Data Organization Schema

### 7.1 Directory Structure

```
/Irish_Educational_Archive/
├── /Examinations/
│   ├── /Mathematics/
│   │   ├── /2024/
│   │   │   ├── Higher_Question_Paper.pdf
│   │   │   ├── Higher_Marking_Scheme.pdf
│   │   │   └── metadata.json
│   │   └── /2023/
│   └── /Irish/
├── /Curriculum/
│   ├── /Primary/
│   │   ├── Mathematics_Specification.pdf
│   │   └── Language_Specification.pdf
│   └── /Junior_Cycle/
├── /Audio_Corpora/
│   ├── /Teanglann/
│   │   ├── /Ulster/
│   │   ├── /Connacht/
│   │   └── /Munster/
│   └── /Canuint/
│       ├── /Ulster/
│       │   └── /Donegal/
│       └── /Munster/
│           └── /Kerry/
└── /Folklore/
    ├── /Schools_Collection/
    │   └── /CBES_0001/
    └── /Hidden_Heritages/
```

### 7.2 Metadata Schema

```python
from pydantic import BaseModel
from datetime import date
from typing import Optional

class ExamPaper(BaseModel):
    subject: str
    year: int
    level: str  # Higher, Ordinary, Foundation
    paper_type: str  # Question Paper, Marking Scheme
    language: str  # English, Irish
    file_path: str
    source_url: str
    download_date: date
    checksum: str

class CurriculumDocument(BaseModel):
    name: str
    level: str  # Primary, Junior Cycle, Senior Cycle
    subject_area: str
    version: str  # Draft, Final
    effective_year: int
    file_path: str
    source_url: str

class AudioRecording(BaseModel):
    word: str
    dialect: str
    speaker: Optional[str]
    location: Optional[str]
    year_recorded: Optional[int]
    file_path: str
    source_url: str
    duration_ms: Optional[int]
    sample_rate: Optional[int]
```

---

## 8. Implementation Priorities

### Phase 1: Core Archives
1. Set up examinations.ie Stagehand workflow
2. Implement subject/year iteration logic
3. Configure download and metadata storage

### Phase 2: Curriculum Documents
1. Deploy Crawl4AI for ncca.ie/curriculumonline.ie
2. Implement hierarchical traversal
3. Extract PDF links and download

### Phase 3: Audio Corpora
1. Build Teanglann word index
2. Implement speculative audio download
3. Configure canuint.ie text-based navigation

### Phase 4: Folklore Integration
1. Set up duchas.ie paginated crawler
2. Implement Hidden Heritages cross-reference
3. Add AT type classification

---

## References

- examinations.ie: https://www.examinations.ie
- NCCA: https://ncca.ie
- Curriculum Online: https://www.curriculumonline.ie
- Canuint.ie: https://www.canuint.ie
- Teanglann.ie: https://www.teanglann.ie
- Dúchas.ie: https://www.duchas.ie
- Hidden Heritages: https://www.hiddenheritages.ai


---

### `stealth-browser-stack.md` — 04-web-automation-archival

# Stealth Browser Infrastructure

## Executive Summary

Modern anti-bot systems like Cloudflare Turnstile, DataDome, and Akamai employ sophisticated fingerprinting techniques that easily identify standard automation tools. This document details the construction of a hardened browser infrastructure using Patchright, CDP architecture, and containerized deployment for reliable web automation.

---

## 1. The Detection Arms Race

### 1.1 Standard Automation Tool Leaks

Standard browser automation tools leak their identity through multiple vectors:

| Detection Vector | Method | Standard Tool Behavior |
|-----------------|--------|----------------------|
| **navigator.webdriver** | JavaScript property check | Returns `true` in automated browsers |
| **Runtime.enable Leak** | CDP command monitoring | Explicit call triggers detection |
| **Stack Traces** | Error analysis | Reveals automation library presence |
| **CDP Flags** | Command-line inspection | `--enable-automation` flag present |
| **Canvas/WebGL** | GPU fingerprinting | Inconsistent with claimed user agent |

### 1.2 Cloudflare Turnstile Detection Layers

| Layer | Detection Method | Difficulty |
|-------|-----------------|------------|
| **Network (TLS)** | JA3/JA4 fingerprinting | High |
| **Runtime** | `navigator.webdriver` | Medium |
| **Behavioral** | Mouse/keystroke entropy | High |
| **Canvas/WebGL** | GPU fingerprinting | Medium |

---

## 2. Patchright: The Hardened Browser Kernel

**Patchright** is a modified Playwright distribution that patches detection leaks at the binary and protocol level. Unlike stealth plugins that inject JavaScript to hide properties, Patchright modifies the browser's internal behavior.

### 2.1 Key Patches

1. **Runtime.enable Patch**: Re-architects script injection to avoid triggering detection
2. **Flag Sanitization**: Strips automation flags, adds user-like flags
3. **Console API Disabled**: Prevents debug output detection
4. **CDP Isolation**: Executes JavaScript in invisible isolated contexts

### 2.2 Docker Container Build

```dockerfile
# Base image: Playwright with Python (includes dependencies)
FROM mcr.microsoft.com/playwright/python:v1.49.0-jammy

# Install utilities and Xvfb for virtual display
RUN apt-get update && apt-get install -y \
    xvfb \
    socat \
    net-tools \
    && rm -rf /var/lib/apt/lists/*

# Install Patchright Python package
RUN pip install patchright && patchright install chromium

# Create automation user
RUN useradd -m automation
USER automation
WORKDIR /home/automation

# Expose CDP port
EXPOSE 9222

# Entrypoint script
COPY start_browser.sh /start_browser.sh
ENTRYPOINT ["/bin/bash", "/start_browser.sh"]
```

### 2.3 Browser Launch Script

```bash
#!/bin/bash
# Start Xvfb for "headed" mode in headless container
# "Headed" mode is significantly stealthier than "Headless" mode
Xvfb :99 -screen 0 1920x1080x24 &
export DISPLAY=:99

# Locate Patchright Chromium Binary
BROWSER_BIN=$(python3 -c "import patchright; print(patchright.executable_path('chromium'))")

echo "Launching Patchright Chromium Listener on 0.0.0.0:9222..."

"$BROWSER_BIN" \
  --remote-debugging-port=9222 \
  --remote-debugging-address=0.0.0.0 \
  --user-data-dir=/home/automation/chrome_data \
  --no-first-run \
  --no-default-browser-check \
  --disable-blink-features=AutomationControlled \
  --disable-infobars \
  --start-maximized \
  --window-size=1920,1080
```

---

## 3. Shared CDP Gateway Architecture

The core innovation is centralizing the stateful browser while keeping automation tools stateless.

### 3.1 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    MCP ORCHESTRATOR                          │
│              (Tool Discovery & Dispatch)                     │
└─────────────────────────────────────────────────────────────┘
    ↓                    ↓                    ↓
┌──────────┐      ┌──────────┐      ┌──────────┐
│ SKYVERN  │      │STAGEHAND │      │ CRAWL4AI │
│ (Hunter) │      │(Operator)│      │(Gatherer)│
└──────────┘      └──────────┘      └──────────┘
    ↓                    ↓                    ↓
         ┌───────────────────────────┐
         │    PATCHRIGHT GRID       │
         │  (Stealth Browser Pool)  │
         │      CDP Port 9222       │
         └───────────────────────────┘
```

### 3.2 Docker Compose Stack

```yaml
version: "3.8"

services:
  # Stealth Browser Hub
  browser-grid:
    build: ./browser-grid
    container_name: browser-hub
    shm_size: '2gb'  # Required for Chromium
    cap_add:
      - SYS_ADMIN
    networks:
      - scraping-mesh
    volumes:
      - browser_data:/home/automation/chrome_data
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9222/json"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Turnstile Solver Sidecar
  solver-service:
    image: theyka/turnstile-solver:latest
    container_name: turnstile-solver
    environment:
      - BROWSER_TYPE=chromium
      - CDP_URL=ws://browser-hub:9222
    networks:
      - scraping-mesh
    depends_on:
      - browser-grid

  # MCP Gateway
  mcp-gateway:
    build: ./mcp-server
    container_name: mcp-gateway
    ports:
      - "3000:3000"
    environment:
      - CDP_URL=ws://browser-hub:9222
      - SOLVER_API_URL=http://solver-service:5000/turnstile
    volumes:
      - ./config/mcp_config.json:/etc/mcp/config.json
    networks:
      - scraping-mesh

networks:
  scraping-mesh:
    driver: bridge

volumes:
  browser_data:
```

### 3.3 Memory and Resource Management

| Resource | Requirement | Rationale |
|----------|-------------|-----------|
| **shm_size** | 2GB minimum | Chromium shared memory requirement |
| **SYS_ADMIN** | Capability | Required for sandbox operations |
| **User Data Volume** | Persistent | Session/cookie persistence across restarts |

---

## 4. Cloudflare Turnstile Mitigation

### 4.1 Theyka Solver Integration

The solver operates as an MCP tool, invoked when Turnstile is detected:

```python
from patchright.sync_api import sync_playwright

class TurnstileSolver:
    def __init__(self, cdp_url: str):
        self.cdp_url = cdp_url

    async def solve(self, page_context: str) -> str:
        """
        Connect to shared browser and solve Turnstile challenge.
        Returns clearance token on success.
        """
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp(self.cdp_url)
            context = browser.contexts[0]
            page = context.pages[0]

            # Locate Turnstile iframe
            turnstile = page.frame_locator("iframe[src*='challenges.cloudflare.com']")

            # Execute human-like interaction
            checkbox = turnstile.locator("input[type='checkbox']")
            await self._human_click(checkbox)

            # Wait for clearance
            await page.wait_for_selector("[data-turnstile-response]", timeout=30000)

            return page.get_attribute("[data-turnstile-response]", "value")

    async def _human_click(self, element):
        """Simulate human-like mouse movement and click."""
        box = await element.bounding_box()
        # Add entropy to click position
        import random
        x = box['x'] + box['width'] * random.uniform(0.3, 0.7)
        y = box['y'] + box['height'] * random.uniform(0.3, 0.7)
        await element.page.mouse.move(x, y, steps=random.randint(10, 25))
        await asyncio.sleep(random.uniform(0.1, 0.3))
        await element.page.mouse.click(x, y)
```

### 4.2 CapSolver API Alternative

For high-volume scenarios where local solving is inconsistent:

```python
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig

async def solve_with_capsolver(crawler: AsyncWebCrawler, page):
    """
    Hook into Crawl4AI to inject CapSolver token.
    """
    script = """
    (async () => {
        const response = await fetch('https://api.capsolver.com/createTask', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                clientKey: '%s',
                task: {
                    type: 'TurnstileTaskProxyLess',
                    websiteURL: window.location.href,
                    websiteKey: document.querySelector('[data-sitekey]').dataset.sitekey
                }
            })
        });
        const result = await response.json();
        // Force turnstile callback with token
        window.turnstile.execute(result.solution.token);
    })();
    """ % CAPSOLVER_API_KEY

    await page.evaluate(script)
```

---

## 5. Session Persistence and State Management

### 5.1 The "Active Tab" Strategy

When multiple tools share a browser, they must attach to the same context:

```python
from playwright.async_api import async_playwright

async def attach_to_shared_browser(cdp_url: str):
    """
    Connect to shared CDP gateway and attach to active context.
    """
    playwright = await async_playwright().start()
    browser = await playwright.chromium.connect_over_cdp(cdp_url)

    # Critical: Reuse existing context, don't create new one
    if not browser.contexts:
        context = await browser.new_context()
    else:
        context = browser.contexts[0]

    # Attach to active page
    if not context.pages:
        page = await context.new_page()
    else:
        page = context.pages[0]

    return browser, context, page
```

### 5.2 Concurrency Control

The MCP Gateway implements locking to prevent race conditions:

```python
import asyncio
from contextlib import asynccontextmanager

class BrowserLock:
    def __init__(self):
        self._lock = asyncio.Lock()
        self._owner = None

    @asynccontextmanager
    async def acquire(self, tool_name: str):
        await self._lock.acquire()
        self._owner = tool_name
        try:
            yield
        finally:
            self._owner = None
            self._lock.release()

    @property
    def is_locked(self) -> bool:
        return self._lock.locked()

    @property
    def owner(self) -> str | None:
        return self._owner
```

---

## 6. Operational Resilience

### 6.1 VNC Debugging

Add VNC server for visual debugging:

```dockerfile
# Add to browser-grid Dockerfile
RUN apt-get install -y x11vnc

# In start_browser.sh
x11vnc -display :99 -forever -shared -rfbport 5900 &
```

### 6.2 Health Checks and Recovery

```yaml
# docker-compose health monitoring
healthcheck:
  test: |
    curl -sf http://localhost:9222/json/version || exit 1
    # Check for zombie processes
    pgrep -x chromium > /dev/null || exit 1
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 10s
```

### 6.3 Logging and Observability

```python
# MCP Gateway logging configuration
import structlog

logger = structlog.get_logger()

# Log all tool invocations
@app.middleware("http")
async def log_requests(request, call_next):
    logger.info(
        "mcp_tool_invoked",
        tool=request.headers.get("X-MCP-Tool"),
        target_url=request.json().get("url"),
        timestamp=datetime.utcnow().isoformat()
    )
    response = await call_next(request)
    return response
```

---

## 7. Implementation Priorities

### Phase 1: Core Infrastructure
1. Build Patchright Docker image with Xvfb
2. Configure CDP exposure on 0.0.0.0:9222
3. Test basic browser connectivity

### Phase 2: Solver Integration
1. Deploy Theyka solver as sidecar
2. Implement MCP tool wrapper
3. Test against Cloudflare-protected sites

### Phase 3: Production Hardening
1. Add VNC debugging capability
2. Implement browser lock mechanism
3. Configure health checks and auto-restart
4. Set up logging and alerting

---

## References

- Patchright GitHub: https://github.com/Kaliiiiiiiiii-Vinyzu/patchright
- Theyka Turnstile Solver: https://github.com/Theyka/Turnstile-Solver
- Playwright Docker: https://playwright.dev/python/docs/docker
- CDP Protocol: https://chromedevtools.github.io/devtools-protocol/


---

## Original Sources

- `04-geospatial-linguistics/` (README.md, data-sources.md, duckdb-spatial.md, maplibre-visualization.md)
- `04-web-automation-archival/` (README.md, agentic-scraping-architecture.md, irish-archives-workflow.md, stealth-browser-stack.md)
