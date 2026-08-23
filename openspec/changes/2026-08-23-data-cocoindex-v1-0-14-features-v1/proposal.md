# 2026-08-23 — Adopt CocoIndex v1.0.14 features (2 new tasks + skill refresh)

## Why

CocoIndex v1.0.14+ added:

- **`memo=True` execution primitive**: cache function outputs across
  re-runs (massive perf win for BAML-driven flows)
- **`deps=` parameter on `@coco.fn`**: explicit dependency declaration
- **17 source/target connectors** (S3, Doris, FalkorDB, Google Drive,
  Iggy, Kafka, LanceDB, LocalFS, Neo4j, OCI, Postgres, Qdrant, SQLite,
  SurrealDB, Turbopuffer, Valkey, zvec) — the 7 BIEP v1 Apps use a
  subset

The current `sync:ccc` task only refreshes the CCC code-search index.
This change adds 2 new tasks to surface the broader CocoIndex surface.

## What changes

### 2 new mise tasks in `mise.toml`

| Task | What it does |
|:--|:--|
| `data:cocoindex:apps:list` | `uv run cocoindex list-apps` — enumerate all 7 BIEP v1 Apps (6 LC subjects + government_circulars) |
| `data:cocoindex:flows:status` | `uv run cocoindex status <app>` — check the freshness + last-run timestamp of a named v1 App |

### 1 skill update

`.agents/skills/cocoindex/SKILL.md`: add a "CocoIndex v1.0.14+ new
patterns" section documenting `memo=True` + `deps=` + the 17
connectors.

## Dependencies

- **Blocked by:** none
- **Affected repos:** cianfhoghlaim only

## Acceptance criteria

1. Both new tasks exist in `mise.toml`
2. `data:cocoindex:apps:list` returns ≥ 7 entries (matching the BIEP v1 App count)
3. `data:cocoindex:flows:status` exits 0 when given a valid app name
4. `.agents/skills/cocoindex/SKILL.md` includes the new section
5. `openspec validate 2026-08-23-data-cocoindex-v1-0-14-features-v1 --strict` exits 0