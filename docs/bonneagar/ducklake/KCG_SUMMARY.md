# DuckLake — KCG Summary

## What It Is
DuckLake is a collection of DuckDB-based analytical tools and infrastructure components: Duck-UI (browser-based DuckDB interface via WebAssembly), duckdb-api (Hono.js REST API wrapper for DuckDB in Docker), frozen-ducklake (scripts for creating and publishing immutable DuckDB data archives), and sql-workbench-embedded (lightweight JavaScript library that converts static SQL code blocks into interactive browser-based DuckDB execution environments).

## Why This Matters for Kings' College Galway
DuckLake forms the analytical backbone of our education data platform. Duck-UI provides the browser-based query interface used by curriculum researchers to explore Irish/UK education datasets directly in DuckDB without infrastructure overhead. The frozen-ducklake pattern is critical for how we archive immutable snapshots of curriculum examination data — each academic year's Leaving Cert results are versioned as a frozen DuckLake that can be queried with time-travel semantics. The sql-workbench-embedded library powers interactive SQL tutorials in our student-facing documentation portal, enabling learners to execute real SQL against educational datasets entirely in-browser with zero backend. The Hono.js DuckDB API pattern is the basis for our MotherDuck integration layer in the `oideachais` data platform.

## Key Patterns Preserved
- `duck-ui/README.md` — Duck-UI overview, Docker setup, environment variables
- `duck-ui/docs/` — Complete Duck-UI documentation (getting-started, charts, troubleshooting, environment-variables, index, acknowledgments, license)
- `duckdb-api/README.md` — DuckDB REST API usage and configuration
- `frozen-ducklake/README.md` — Frozen DuckLake workflow and examples
- `sql-workbench-embedded/README.md` — Library overview, API, integration patterns
- `sql-workbench-embedded/CLAUDE.md` — Architecture and implementation guidance
- `sql-workbench-embedded/requirements/sql-workbench-embedded-requirements.md` — Full requirements spec

## Source Files
Full source removed (2026-06-06), available at their respective GitHub repositories:
- Duck-UI: https://github.com/ibero-data/duck-ui
- DuckDB API: (duckdb-api subproject)
- Frozen DuckLake: https://github.com/marhar/duckdb_tools (frozen-ducklake)
- SQL Workbench Embedded: https://github.com/tobilg/sql-workbench-embedded

## What Was Removed
Source code (TypeScript, JavaScript, Python, SQL, Shell scripts), build artifacts, Dockerfiles, npm/package configuration files, test fixtures, sample data files (Parquet, CSV), binary assets (images, fonts, logos), CI/CD workflow definitions, Next.js/React app source, WASM binaries, node_modules remnants, and all non-documentation files.
