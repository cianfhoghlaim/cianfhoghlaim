# 2026-08-23 — Fill in 10 TBD Purpose fields (data specs batch) + add lint:spec:purpose

## Why

Per the user's "Domain-driven batches" choice (for the 30 specs with TBD Purpose fields), this change addresses the **data-specs batch** — 10 specs that cover the data plane (DLT + BAML + DuckDB + DuckLake + MotherDuck + CocoIndex + marimo).

The TBD Purpose is the standard openspec archive stamp (`## Purpose: TBD - created by archiving change X. Update Purpose after archive.`). It signals "the spec exists, but the Purpose hasn't been authored yet." Leaving it as TBD makes the spec less discoverable from `openspec list` and harder for new agents to grok.

This change:
1. **Replaces the TBD Purpose** in 10 data specs with 2-3 sentence Purpose sections (per the user's locked-in template choice).
2. **Adds a `lint:spec:purpose` task** that fails CI if any spec has a TBD Purpose (so future archive-then-forget cycles are caught at lint time).

Per the locked-in template (from the plan refinement):
```
The {topic} {noun-phrase: capability surface / workflow / sub-system / pattern}
across the {scope: Cianfhoghlaim monorepo / domain / pipeline / surface}.
It defines {N} invariants: {comma-separated list from the existing requirements}.
{Cross-references: openspec/specs/<adjacent-spec>/spec.md + .agents/skills/<relevant-skill>/SKILL.md}
```

## The 10 data specs to update

| Spec | TBD→Purpose | Source change |
|:--|:--|:--|
| `americas-california-pipeline` | TBD → Americas pipeline path contract | 2026-07-11-americas-california-pipeline-v1 |
| `celtic-language-pipeline` | TBD → Gaois + Celtic language path contract | 2026-07-17-gaois-celtic-language-pipeline-v1 |
| `commonwealth-pipeline` | TBD → Commonwealth of Nations path contract | 2026-07-11-commonwealth-pipeline-v1 |
| `european-nations-ukraine-pipeline` | TBD → Ukraine per-subject depth parity with BI | 2026-07-15-eu-pilot-upgrade-v1 |
| `european-union-official-language-pipeline` | TBD → 24 EU official languages path contract | 2026-07-11-european-union-official-language-pipeline-v1 |
| `firecrawl-corpus-and-portals` | TBD → Firecrawl call observability contract | 2026-08-14-firecrawl-corpus-and-examinations-ie-v1 |
| `duckdb-ducklake-lakehouse-hydration` | TBD → DuckDB/DuckLake hydration pipeline contract | 2026-08-08-lakehouse-extensive-hydration-v1 |
| `motherduck-connections` | TBD → MotherDuck connection registration contract | 2026-08-15-cascading-registry-integration-v1 |
| `dlt-sync-loop` | TBD → DLT sync loop Layer 1-5 contract | 2026-08-15-dlt-sync-loop-v1 |
| `baml-schemas` | TBD → BAML ClientRegistry OCR ensemble fallback contract | 2026-08-17-hygiene-drift-cleanup-v1 |

The remaining 20 specs with TBD Purpose fields are split across the **agent specs** (Phase 5.1.2) + **infra specs** (Phase 5.1.3) + the **dev-tooling-spec itself** (already has a non-TBD Purpose in the latest draft).

## The new `lint:spec:purpose` task

Per the `sync:*` task pattern (`sync:dlt`, `sync:baml`, `sync:stacks`), add a new `lint:spec:purpose` task that:

```bash
# Find all spec files with ## Purpose: TBD - ...
TBD_COUNT=$(grep -rl "^## Purpose" openspec/specs/*/spec.md | xargs grep -l "TBD" 2>/dev/null | wc -l)
if [ "$TBD_COUNT" -gt 0 ]; then
  echo "FAIL: $TBD_COUNT specs still have TBD Purpose fields"
  exit 1
else
  echo "OK: all $(grep -rl "^## Purpose" openspec/specs/*/spec.md | wc -l) specs have non-TBD Purpose"
  exit 0
fi
```

Wired into `core:lint` aggregate gate as the 6th sub-gate (after `lint:skills`, `lint:registry`, `core:typecheck`, `core:uv:audit:strict`, `core:uv:check`).

## Dependencies

- **Blocked by:** none
- **Soft-blocked by:** the 10 archived changes listed above (their specs exist)
- **Affected repos:** cianfhoghlaim only

## Acceptance criteria

1. All 10 data specs have a non-TBD Purpose section (verified via `grep -rl "TBD" openspec/specs/<X>/spec.md | wc -l` returning 0 for each)
2. The `lint:spec:purpose` task exists in `mise.toml` and exits 0 when all specs have non-TBD Purpose
3. `core:lint` now depends on `lint:spec:purpose`
4. `openspec validate 2026-08-23-dev-tooling-tbd-purpose-refresh-batch-data-specs-v1 --strict` exits 0
5. The 20 remaining TBD Purpose fields (in agent + infra specs) are documented as Phase 5.1.2/5.1.3 follow-up

## Out of scope

- Filling in TBD Purpose fields for agent specs (Phase 5.1.2)
- Filling in TBD Purpose fields for infra specs (Phase 5.1.3)
- Re-architecting any spec content (only Purpose fields are touched)

## Rollback plan

- Revert the 10 spec.md files to their pre-change state (TBD Purpose) via `git checkout`
- Remove the `lint:spec:purpose` task from `mise.toml`
- Remove the `core:lint` depends entry
