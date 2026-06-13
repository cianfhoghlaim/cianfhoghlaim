---
title: docs-v2 — Consolidated Documentation
status: living-document
generated: 2026-06-13
description: Per-topic merged, sections-per-source mirror of docs/ for easier navigation
---

# docs-v2 — Consolidated Documentation Index

**Regenerated from `docs/` via ccc + Cognee. No files in `docs/` are deleted.**

This index is rebuilt by `scripts/migrate-docs-v2.py`. See `MIGRATION.md`
for the per-source section structure.

## Domain routing

| Domain | Topic | Path |
|:--|:--|:--|
| 01 | Platform Architecture | `01-platform-architecture/` |
| 02 | Data Platform | `02-data-platform/` |
| 03 | Agents & Orchestration | `03-agents/` |
| 04 | AI / ML | `04-ai-ml/` |
| 05 | Web Stack | `05-web/` |
| 06 | Infrastructure | `06-infrastructure/` |
| 07 | Standards & Skills | `07-standards/` |
| 08 | Misc & Examples | `08-misc/` |
| 09 | Cognee / Knowledge Graph | `09-cognee/` |
| 10 | Loose top-level files | `10-loose-files/` |
| 11 | Scripts | `11-scripts/` |
| 12 | Configs | `12-configs/` |
| 13 | Images | `13-images/` |

## Source mapping

- Original canonical 7-domain tree: `docs/00-meta/`, `docs/01-*/`, `docs/02-*/`, ..., `docs/08-*`
- Leftover consolidation dirs: `docs/dlt/`, `docs/dagster/`, `docs/cocoindex/`, `docs/baml/`, `docs/lance/`, `docs/marimo/`, `docs/hackathons/`, `docs/docs_examples_consolidated/`, `docs/hmgcc/`
- Archive: `docs/archive/2026-06-06-data-engineering/`, `docs/archive/2026-06-06-meaisinfhoghlaim/`
- Loose: 9 files at `docs/` root (4 PDFs, `INDEX.md`, `00_index.md`, `auto-deploy-stacks.toml`, etc.)
- Non-md: 38,459 source files include `.md`, `.py`, `.yaml`, `.toml`, `.json`, `.png`, `.jpg`, `.svg`, `.pdf`

## See also

- `MIGRATION.md` — how merged files are structured
- `changelog.md` — per-commit coverage statistics
- `.migration/manifest.md` — full source-to-target file map
