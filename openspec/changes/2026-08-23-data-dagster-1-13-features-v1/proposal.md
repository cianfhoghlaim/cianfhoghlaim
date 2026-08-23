# 2026-08-23 — Adopt Dagster 1.13+ features (3 new tasks + 1 doc update)

## Why

Dagster 1.13+ introduced several new features that the Cianfhoghlaim
5-layer KCG component architecture should adopt:

- **`dg` CLI**: the new "Dagster Generators" CLI for scaffolding assets
  + components + jobs (replaces ad-hoc Python scripts)
- **`asset_check` improvements**: native dataclass-style definitions
- **Declarative Automation**: trigger policies (e.g., "materialize when
  upstream is fresh") replace manual sensor wiring
- **Virtual Assets**: lightweight assets that don't materialize but
  signal freshness
- **State-Backed Components**: Components that persist state across runs

The current `data:dagster:up` task just launches the webserver. We
need 3 more tasks to surface the 1.13+ capabilities.

## What changes

### 3 new mise tasks in `mise.toml`

| Task | What it does |
|:--|:--|
| `data:dagster:list-assets` | `dg list assets` — emit a JSON dump of all 199+ assets + their group + kinds |
| `data:dagster:materialize` | `dg launch --assets <key>` — materialize a single asset by key (e.g., `lc5_mathematics_ingested`). Wraps the new `dg` CLI instead of the legacy `dagster asset materialize` |
| `data:dagster:cli-info` | `dg list components` — emit the 5 KCG components + their Python module paths (for CI verification) |

### 1 doc update

`.agents/skills/dagster/SKILL.md`: add a "Dagster 1.13+ new patterns"
section documenting the `dg` CLI + Declarative Automation + Virtual
Assets patterns.

## Dependencies

- **Blocked by:** none
- **Affected repos:** cianfhoghlaim only
- **Out of scope:**
  - Adopting Virtual Assets (large code change; needs separate openspec change)
  - Migrating all assets to Declarative Automation (per-asset migration)
  - Dagster Components (already adopted via the 5-layer architecture per the 2026-07-15 refactor)

## Acceptance criteria

1. All 3 new tasks exist in `mise.toml`
2. Each task exits 0 in dry-run mode
3. `data:dagster:list-assets` returns a JSON list with ≥ 199 assets (matching the current count)
4. `.agents/skills/dagster/SKILL.md` includes the new "Dagster 1.13+" section
5. `openspec validate 2026-08-23-data-dagster-1-13-features-v1 --strict` exits 0
