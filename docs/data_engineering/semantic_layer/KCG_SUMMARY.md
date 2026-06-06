# Semantic Layer — KCG Summary

## What It Is
This directory aggregates three major semantic layer projects: **Boring Semantic Layer** (BSL) — a lightweight Ibis-based semantic layer with MCP and LangChain integration for LLM-to-SQL querying; **Cube.js** (Cube.dev) — a full-featured semantic layer framework with 40+ database drivers, REST/GraphQL APIs, and a Rust-based SQL compiler; and **Rill** — example dashboards demonstrating Rill Developer patterns for ClickHouse, openRTB, and embedding use cases.

## Why This Matters for Kings' College Galway
BSL's Ibis-based approach aligns directly with the oideachais platform's Ibis analytics layer, providing MCP-friendly query patterns for connecting LLMs (like OpenCode agents) to structured education data. Cube.js's multi-driver architecture and semantic table patterns inform how to expose curriculum datasets across DuckDB, MotherDuck, and PostgreSQL. The BSL query agent (LangChain + MCP + Claude Code skills) provides a working reference for building AI-assisted educational data exploration tools.

## Key Patterns Preserved
200+ .md files remain, including:
- `boring-semantic-layer/README.md` — BSL overview and quick start
- `boring-semantic-layer/docs/md/doc/*.md` (22 files) — Full BSL documentation: query agents, semantic tables, MCP integration, charting, bucketing, sessionized data
- `boring-semantic-layer/docs/md/prompts/query/mcp/*.md` (17 files) — MCP tool parameter docs and system prompts
- `boring-semantic-layer/docs/md/prompts/query/langchain/*.md` (12 files) — LangChain agent prompt engineering patterns
- `boring-semantic-layer/docs/md/skills/claude-code/` — SKILL.md files for BSL model builder and query expert
- `cube/README.md`, `cube/CLAUDE.md`, `cube/CONTRIBUTING.md` — Cube.js architecture and agent instructions
- `cube/packages/*/` (60+ README/CHANGELOG.md) — Per-driver docs for DuckDB, Postgres, BigQuery, Snowflake, ClickHouse, Druid, etc.
- `cube/rust/cubesql/*.md` — Rust SQL compiler and CubeStore internals
- `cube-ui-kit/README.md`, `CONTRIBUTING.md`, `CHANGELOG.md` — React UI kit for semantic layers
- `rill-examples/*/README.md` (14 files) — Rill dashboard examples

## Source Files
Full source removed (2026-06-06). Available at:
- BSL: https://github.com/boringdata/boring-semantic-layer
- Cube.js: https://github.com/cube-js/cube
- Cube UI Kit: https://github.com/cube-js/cube-ui-kit

## What Was Removed
TypeScript/JavaScript source, Rust source, Python packages, Docker files, JSON/YAML configs, Cargo/Rust build files, CSS/HTML, test fixtures, images, nix/CI configs
