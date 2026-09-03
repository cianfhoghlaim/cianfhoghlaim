## Why

`.agents/skills/` currently has **19 MotherDuck-related skills** (1
routing + 18 specialised sub-skills). This is the worst skill-bloat
problem in the directory and pollutes the agent's discovery surface.

The 18 sub-skills are the upstream MotherDuck skill tree (sourced from
the official `motherduck` skill at `https://github.com/motherduckdb`).
KCG only ever needs 4 of them in practice (verified against
`sruth/oideachais/`, `sruth/croilar/`, `sruth/tuatha/`, and `infrastructure/`):

- `motherduck-connect` (MCP wiring, Postgres endpoint)
- `motherduck-load-data` (CTAS, INSERT...SELECT)
- `motherduck-duckdb-sql` (DuckDB SQL dialect reference)
- `motherduck-ducklake` (the storage layer we actually use)

The other 14 are tangential: sales/strategy (pricing-roi,
partner-delivery, migrate-to-motherduck, enable-self-serve-analytics,
build-cfa-app), specialised Dives/embed content (create-dive,
build-dashboard, share-data, rest-api), or duplicates (query vs
duckdb-sql, model-data vs load-data, build-data-pipeline vs the
DuckLake skill, security-governance vs the MCP `--saas-mode` flag).

The 4 skills KCG actually needs can be reorganised into 4
**task-oriented** skills that match the agent's mental model:

- `motherduck-architecture` — pick the storage pattern
  (managed MD vs BYOB vs DuckLake vs own-compute); absorb the
  pricing/migration/partner-delivery/migrate material into a "when
  NOT to use MotherDuck" appendix.
- `motherduck-data-modeling` — schema + ingestion (table design,
  CTAS/INSERT, dbt/SQLMesh patterns).
- `motherduck-analytics` — SQL + Dives + dashboards + sharing +
  explore (one skill for everything you do inside a query).
- `motherduck-connections` — wiring (Postgres endpoint, pg_duckdb,
  native DuckDB API, JDBC, REST API, MCP, RBAC).

The router `motherduck` stays; the KCG-specific MCP section in it
(175 lines) is kept verbatim and is the most-used section.

## What changes

- 4 new skills created:
  - `.agents/skills/motherduck-architecture/SKILL.md` (merges
    `motherduck-build-data-pipeline` + `motherduck-ducklake` +
    `motherduck-migrate-to-motherduck` + `motherduck-pricing-roi`
    + `motherduck-partner-delivery`)
  - `.agents/skills/motherduck-data-modeling/SKILL.md` (merges
    `motherduck-model-data` + `motherduck-load-data`)
  - `.agents/skills/motherduck-analytics/SKILL.md` (merges
    `motherduck-query` + `motherduck-duckdb-sql` +
    `motherduck-create-dive` + `motherduck-build-dashboard` +
    `motherduck-explore` + `motherduck-share-data`)
  - `.agents/skills/motherduck-connections/SKILL.md` (merges
    `motherduck-connect` + `motherduck-rest-api` +
    `motherduck-build-cfa-app` +
    `motherduck-enable-self-serve-analytics` +
    `motherduck-security-governance`)
- 18 sub-skill directories deleted
- `.agents/skills/motherduck/SKILL.md` updated to delegate to the
  4 new skills + keep the MCP section verbatim

## Out of scope

- Browser tools 8 → 3 consolidation (B2) — separate change.
- Code search 2 → 1 (B3) — separate change.
- Shared-spec router skills (B4) — separate change.
- Skill content refresh to 2026-06 package state (C) — separate change.
- `docs-skills-canonical-reference` governance (D1) — separate change.
- `skills-as-project-docs` feedback loop (D2) — separate change.
