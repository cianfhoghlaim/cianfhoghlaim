# Dagster — KCG Summary

## What It Is
Dagster is the orchestrator at the heart of the oideachais data platform. This directory contains the full Dagster research collection including: core Dagster concepts and CLI agent instructions, Dagster DSPy integration (Claude Code skills for building Dagster pipelines), Dagster + DuckLake + Iceberg + SQLMesh integration examples, Dagster + dlt orchestration patterns, Dagster + Evidence dashboard integration, and 30+ scraped Dagster Docs pages covering advanced configs, ML pipelines, MCP server usage, deployment, and library integrations.

## Why This Matters for Kings' College Galway
Dagster orchestrates the entire curriculum data pipeline: DLT ingestion → DuckDB/MotherDuck staging → SQLMesh transformations → Evidence dashboards. The DSPy integration skills provide agent-driven pipeline development patterns. The DuckLake/Iceberg integration examples directly inform the lakehouse architecture for curriculum data versioning. The MCP server docs show how agents monitor and manage pipelines, a core pattern for the autonomous curriculum platform.

## Key Patterns Preserved
54 .md files remain, including:
- `dagster.md` — Core Dagster expert assistant (487-line agent instruction)
- `dagster-research.md`, `dagster-research-2024-2025.md` — Comprehensive Dagster research notes
- `dagster-orchestration.md` — Orchestration patterns for CocoIndex + Graphiti
- `dagster-design-patterns-research.md` — Pipeline design patterns
- `dagster-api-quick-reference.md` — API reference
- `dagster_ducklake.md`, `dagster_iceberg.md` — DuckLake/Iceberg integration patterns
- `dagster-openapi-research.md` — OpenAPI + Dagster patterns
- `dagster-dspy/Readme.md` — DSPy integration for LLM-enhanced Dagster
- `dagster-dspy/.claude/skills/` (6 SKILL.md files) — Agent skills for Dagster development, testing, ETL patterns, automation
- `dagster-ducklake/README.md` — DuckLake integration
- `dagster-evidence/README.md` — Evidence dashboard integration
- `dagster-iceberg/` (8 .md files) — Full Iceberg integration docs: quickstart, features, reference, development
- `dagster-modal/README.md` + CHANGELOG — Modal cloud deployment
- `dagster-sqlmesh/README.md` + CHANGELOG — SQLMesh integration
- `deploy/README.md` — Deployment patterns
- 18 scraped Dagster Docs pages covering configurations, ML pipelines, MCP, concurrency, deployment, library integrations (dlt, DuckDB, MLflow, Iceberg, PostgreSQL, GitHub, DataDog)

## Source Files
Full source removed (2026-06-06). Available at:
- Dagster: https://github.com/dagster-io/dagster
- dagster-dspy: https://github.com/dagster-io/dagster-dspy

## What Was Removed
Python source (.py), TOML/YAML configs, JSON files, shell scripts, .gitignore files, CSV data, lock files, Jupyter notebooks
