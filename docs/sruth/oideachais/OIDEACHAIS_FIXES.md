# OIDEACHAIS Pipeline Fixes - Lakekeeper/DuckLake Integration

## Summary

Fixed critical issues where scraped curriculum data was not being saved to the Lakekeeper/DuckLake storage layer.

## Root Causes Identified

### 1. DLT Resource vs Table Name Mismatch
**File**: `sruth/oideachais/dagster_defs/assets/ireland/curriculum_dlt_assets.py`

**Problem**: The Dagster asset was using `parallel_scrape_subject()` which returned raw Firecrawl data, then passing it to `pipeline.run()` with a `table_name` parameter. This bypassed the DLT resource schema definition, causing data to not match expected columns.

**Fix**: Changed to use the `curriculum_source()` DLT source directly, which properly defines the `curriculum_pages` resource with all columns. Now uses `pipeline.extract()` + `safe_dlt_normalize()` + `safe_dlt_load()` pattern.

### 2. Incomplete Schema Definition
**File**: `sruth/oideachais/.dlt/curriculum_unified/schemas/curriculum_unified.schema.json`

**Problem**: The schema only defined `url` column as primary key, missing all other columns (title, content, content_hash, cycle, subject, language, source, crawled_at, metadata).

**Fix**: Added full column definitions matching the DLT resource decorator in `curriculum_source.py`.

### 3. Missing Connectivity Verification
**File**: `sruth/oideachais/dlt_utils/destinations.py`

**Problem**: DuckLake destination was returned without verifying if Garage S3 or PostgreSQL services were actually running. This caused silent failures.

**Fix**: Added `_verify_ducklake_connectivity()` function that checks socket connectivity before returning DuckLake destination. Falls back to DuckDB with warning if services are unavailable.

### 4. Insufficient Error Logging
**File**: `sruth/oideachais/dlt_utils/safety.py`

**Problem**: When DLT pipeline failed, minimal logging made debugging difficult.

**Fix**: Added detailed error logging with pipeline name, destination, dataset name, and full exception traceback.

## Changes Made

### curriculum_dlt_assets.py
- Replaced `parallel_scrape_subject()` with `curriculum_source()` DLT source
- Changed from `pipeline.run(data, table_name=...)` to `pipeline.extract(source)` pattern
- Added separate normalize and load phases using `safe_dlt_normalize()` and `safe_dlt_load()`
- Updated metadata to use page_count from extraction phase

### curriculum_unified.schema.json
- Added columns: url, title, content, content_hash, cycle, subject, language, source, crawled_at, metadata
- Set proper data types: text, timestamp, complex
- Configured nullable constraints appropriately

### destinations.py
- Added `_verify_ducklake_connectivity()` function
- Checks Garage S3 (localhost:3900) and PostgreSQL (localhost:5433) connectivity
- Falls back to DuckDB if services unavailable
- Logs warning when fallback occurs

### safety.py
- Enhanced `safe_dlt_run()` with try/except and detailed logging
- Logs success metrics including load IDs
- Logs errors with pipeline context for debugging

## Environment Variables

```bash
# Enable/disable DuckLake (default: true)
export USE_DUCKLAKE=true

# Environment: local or production (default: local)
export DLT_ENVIRONMENT=local

# Local DuckLake configuration
export DUCKLAKE_POSTGRES_HOST=localhost
export DUCKLAKE_POSTGRES_PORT=5433
export DUCKLAKE_POSTGRES_DB=ducklake_oideachais
export DUCKLAKE_POSTGRES_USER=lakekeeper
export DUCKLAKE_POSTGRES_PASSWORD=devpassword

# S3/Garage configuration
export AWS_ENDPOINT_URL=http://localhost:3900
export AWS_ACCESS_KEY_ID=<your-key>
export AWS_SECRET_ACCESS_KEY=<your-secret>
```

## Testing

1. **Without DuckLake infrastructure** (quick test):
   ```bash
   export USE_DUCKLAKE=false
   dagster dev -m sruth.oideachais
   ```

2. **With DuckLake infrastructure** (full integration):
   ```bash
   # Start Garage S3 and PostgreSQL first
   export USE_DUCKLAKE=true
   dagster dev -m sruth.oideachais
   ```

## Verification

After materializing an asset, verify data was saved:

```python
import duckdb

# For DuckDB fallback
con = duckdb.connect(".dlt/curriculum_unified/curriculum.duckdb")
result = con.execute("SELECT COUNT(*) FROM curriculum_pages").fetchone()
print(f"Rows saved: {result[0]}")
```

## Related Files

- `sruth/oideachais/dlt_sources/ireland/curriculum_source.py` - DLT source with resource definitions
- `sruth/oideachais/dlt_sources/ireland/source_adapters.py` - Normalization adapters
- `sruth/oideachais/core/storage/serial_executor.py` - SerialDatabaseExecutor for DuckDB safety
- `sruth/shared/dagster/components/dlt_component.py` - Shared DLT component patterns
