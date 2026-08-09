## ADDED Requirements

### Requirement: 5 DLT Sources for Authoritative Geospatial Feeds

The system SHALL provide 5 DLT sources under `dlt/infrastructure/`:
`os_mastermap.py`, `tailte_eireann_lidar.py`, `met_office_datapoint.py`,
`met_eireann_mera.py`, `crown_dependencies.py`.

#### Scenario: 5 DLT sources ingest
- **WHEN** the user invokes `mise run dlt:infrastructure`
- **THEN** all 5 sources SHALL ingest their respective data

### Requirement: ITM / OSGB36 → WGS84 Reprojection Utility

The system SHALL provide `notebooks/_shared/geo.py` implementing the
Helmert transform from ITM and OSGB36 to WGS84.

#### Scenario: Reproject Dublin from ITM to WGS84
- **WHEN** the user invokes `geo.itm_to_wgs84(easting=315949, northing=234567)`
- **THEN** the function returns `(lat=53.3498, lon=-6.2603)` (Dublin)

### Requirement: OGC API Features Client

The system SHALL provide an OGC API Features client in `notebooks/_shared/geo.py`.

#### Scenario: Query Coflein OGC API
- **WHEN** the user invokes `geo.ogc_query("https://coflein.gov.uk/api/features", bbox=(51.0,-6.0,53.0,-2.0))`
- **THEN** the function returns a list of heritage sites in the bbox

### Requirement: Interactive Geospatial Explorer

The system SHALL provide `notebooks/37_geospatial_explorer.py` as a
marimo + Altair visualisation with 5 tabs.

#### Scenario: Explorer renders all 5 layers
- **WHEN** the user invokes `mise run notebook:geospatial`
- **THEN** the explorer SHALL render with 5 tabs and 5 toggleable layers

### Requirement: 0.01° Uniform Spatial Grid Utility

The system SHALL provide `notebooks/_shared/spatial_grid.py` implementing
a 0.01° uniform grid.

#### Scenario: Bucket key for Dublin
- **WHEN** the user invokes `spatial_grid.bucket_key(lat=53.3498, lon=-6.2603)`
- **THEN** the function returns a unique integer key for the Dublin cell