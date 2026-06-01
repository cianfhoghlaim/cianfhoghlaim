---
name: motherduck
description: Master routing skill for all MotherDuck operations. Use this to determine which specialized motherduck-* skill to invoke.
---

# MotherDuck Master Router

You are operating within the `cianfhoghlaim` stack which utilizes MotherDuck for cloud data warehousing and DuckLake for local/hybrid S3 data Lakehouse capabilities.

When tasked with MotherDuck operations, use this guide to invoke the most appropriate sub-skill:

## Storage & Architecture
- **`motherduck-ducklake`**: Use when dealing with S3 object storage layouts, BYOB (Bring Your Own Bucket), fully managed DuckLake, or native MotherDuck vs DuckLake storage decisions. Critical for `oideachais` since it uses Postgres catalog + Parquet files in Garage S3 (`s3://ducklake/oideachais/`).
- **`motherduck-connect`**: Use for choosing native DuckDB vs Postgres-endpoint access paths.

## Data Integration & Modeling
- **`motherduck-load-data`**: Use for ingestion workflows and loading data into MotherDuck.
- **`motherduck-model-data`**: Use for analytical table design and dbt/SQLMesh modeling inside MotherDuck.
- **`motherduck-build-data-pipeline`**: Use when DuckLake/MotherDuck is part of a broader ingestion-to-serving workflow.

## Analytics & Application Building
- **`motherduck-duckdb-sql`**: Use when writing complex DuckDB SQL queries, macros, or leveraging DuckDB extensions.
- **`motherduck-explore`**: Use for data exploration inside MotherDuck.
- **`motherduck-build-dashboard`**: Use when building analytics dashboards over MotherDuck data (e.g., using Evidence or Marimo).
- **`motherduck-build-cfa-app`**: Use when building Customer-Facing Analytics applications.
- **`motherduck-rest-api`**: Use for interacting with the MotherDuck REST API programmatically.

## Governance & Operations
- **`motherduck-security-governance`**: Use for setting up RBAC, shares, and securing MotherDuck environments.
- **`motherduck-share-data`**: Use for sharing databases and managing access across organizations.
- **`motherduck-pricing-roi`**: Use for understanding billing, ROI, and compute costs.
- **`motherduck-migrate-to-motherduck`**: Use for migrating from other data warehouses to MotherDuck.

## Partner Delivery
- **`motherduck-partner-delivery`**: Use for managing partner integrations and consulting delivery models.

**Do not execute general MotherDuck tasks blindly.** Always try to load the relevant sub-skill for specialized reference material and best practices.
