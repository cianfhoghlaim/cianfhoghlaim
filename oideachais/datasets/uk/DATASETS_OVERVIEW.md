# Data Sets Overview

This document describes the main datasets available in the `datasets` folder, their sources, and the keys used for linking data across different domains (census, education, achievements, etc.).

## 1. dfe/
- **Source:** Department for Education (DfE), England
- **Contents:**
  - School information, census, subject entries, pupil destinations, KS4/KS5 results, and more
  - Subfolders by year and topic
  - Formats: CSV, XLSX
- **Key files for linking:**
  - `england_school_information.csv`: School-level data, often with local authority codes
  - `england_census.csv`: Demographic and census data, likely with LSOA or authority codes
  - `england_ks4-subject-entries.xlsx`, `england_ks5-subject-entries.csv`: Achievement data, including computer science

## 2. gis/
- **Source:** Geographic Information System datasets (Edubase, government sources)
- **Contents:**
  - School, academy, and group membership data
  - Files like `edubaseallacademiesandfree20250426.csv`, `allgroupsdata20250426.csv`
- **Key for linking:**
  - LSOA codes, local authority codes, and school identifiers for spatial joins

## 3. ons/
- **Source:** Office for National Statistics (ONS), England
- **Contents:**
  - Socioeconomic and demographic data: `economic_activity_status.csv`, `ethnic_group.csv`, `highest_qualification.csv`
- **Key for linking:**
  - LSOA codes and authority codes for census-level joins

## 4. raw/
- **Source:** Raw, unprocessed data from DfE, ONS, IMD, etc.
- **Contents:**
  - Yearly folders and files for direct access to original datasets
  - IMD scores, ONS data, DfE data

## 5. ucas/
- **Source:** UCAS (Universities and Colleges Admissions Service)
- **Contents:**
  - Equality and admissions data by year and provider
  - Useful for linking higher education outcomes

---

## Linking Key: LSOA/Authority Codes
- **LSOA (Lower Layer Super Output Area):**
  - Geographic area code used in census and ONS datasets
  - Present in ONS and IMD datasets, and often in DfE school data
- **Local Authority Codes:**
  - Used in DfE and GIS datasets to identify schools and regions
  - Enables joining school achievement data (e.g., computer science results) with census and socioeconomic data

## Example Linkage
To analyze computer science achievement across England:
- Use DfE subject entries/results (KS4/KS5) for computer science
- Join with ONS census data using LSOA or local authority codes
- Optionally, enrich with IMD scores and GIS school location data

## Summary Table
| Folder      | Source         | Key Data Types                | Linking Key(s)         |
|-------------|---------------|-------------------------------|------------------------|
| dfe/        | DfE            | School info, results, census  | LSOA, Authority Code   |
| gis/        | Edubase/GIS    | School/academy locations      | LSOA, Authority Code   |
| ons/        | ONS            | Census, demographics          | LSOA, Authority Code   |
| raw/        | Various        | Unprocessed originals         | LSOA, Authority Code   |
| ucas/       | UCAS           | Admissions, equality          | LSOA, Authority Code   |
