# DuckLake — KCG Summary

## What It Is
DuckLake is a DuckDB extension providing lakehouse capabilities: zero-copy file registration, ACID snapshots, time-travel queries, change data capture, and file compaction — all without external manifest files. This directory contains the DuckLake TPCH demo (10-script end-to-end lakehouse workflow), a DuckLake + SQLMesh tutorial for building a modern data lakehouse on a laptop, and an MLflow + Kafka + DuckLake pipeline for streaming ML telemetry to a lakehouse.

## Why This Matters for Kings' College Galway
DuckLake is the lakehouse layer for the oideachais platform, providing ACID guarantees over curriculum data stored on Garage S3. The zero-copy file registration pattern directly maps to DLT's filesystem pipeline output — curriculum Parquet files are registered into DuckLake without data duplication. The time-travel and CDC features enable curriculum version auditing across academic years. The DuckLake → MotherDuck pattern provides the local-to-cloud workflow for development on bunchloch and production on MotherDuck.

## Key Patterns Preserved
6 .md files remain:
- `README.md` — Full DuckLake TPCH demo documentation: catalog bootstrap, partitioning, snapshots, compaction, time travel, CDC, expiration
- `ducklake.md` — DuckLake concept reference
- `DuckLake + SQLMesh Tutorial_ Build a Modern Data Lakehouse On Your Laptop.md` — DuckLake + SQLMesh integration walkthrough
- `DuckLake to MotherDuck_ Validate locally, deploy to cloud in minutes.md` — Local-to-cloud deployment pattern
- `mlflow_kafka_ducklake/README.md` + CHANGELOG — MLflow + Kafka streaming to DuckLake

## Source Files
Full source removed (2026-06-06). Available at https://github.com/ducklake/ducklake

## What Was Removed
Python scripts (.py), SQL scripts (.sql), Makefile, YAML configs, lock files, .gitignore, README without .md extension
