# croilar-aleyum-to-streams-cleanup-v1

## Why

The Croílár data-engineering layer was originally authored
under the `aleyum` persona (the pre-rebrand name of the
project). Round 11 of the multi-quadrant refactor plan
collapses the 5 remaining `aleyum` aliases to `croilar` so
the entire data engineering layer is consistent with the
4 quadrant names (`oideachais` / `meaisinfhoghlaim` /
`tuatha` / `croilar`).

The 5 aleyum aliases are scattered across 3 files:

- `croilar/_shared/config/settings.py` — the `ALEYUM_` env
  prefix (already partially retired) + the deprecated
  `AleyumSettings` alias
- `croilar/pipelines/shared/destinations.py` — 8 aleyum
  references (database path, R2 bucket, catalog path,
  4 pipeline names, env var)
- `croilar/pipelines/shared/ducklake.py` — 3 aleyum
  references (default catalog path, default R2 bucket,
  `initialize_catalog` defaults)
- `croilar/pipelines/shared/r2_client.py` — 1 aleyum
  reference (`ALEYUM_R2_BUCKET = "aleyum-assets"` constant)

The change delivers 4 sub-tasks:

1. **5 alias collapses** — `ALEYUM_` env prefix → `STREAMS_`,
   `aleyum.duckdb` → `croilar.duckdb`, `aleyum-data` →
   `croilar-data`, `aleyum_local` → `croilar_local` (and 3
   other pipeline names), `aleyum_catalog.duckdb` →
   `croilar_catalog.duckdb`
2. **Deprecated `AleyumSettings` alias removal** — the
   `AleyumSettings = StreamSettings` line in
   `croilar/_shared/config/settings.py` is removed
3. **1 new skill** — `.agents/skills/croilar-stream-registry/SKILL.md`
   to document the 5 collapses + the `StreamSettings` Pydantic
   BaseSettings + the 12 stream-driven Dagster assets + the
   `Stream` model + the `croilar/config/sources.yaml` registry
4. **OpenSpec spec delta** — 2 ADDED Requirements on
   `croilar-data-engineering` (Aleyum-to-croilar cleanup
   mandate, Stream-registry canonical config surface)

The change is the 11th round of the multi-quadrant refactor
plan (rounds 7-13). Rounds 7-10 have already landed
(infrastructure, meaisinfhoghlaim, oideachais, tuatha).

## What changes

- `croilar/pipelines/shared/destinations.py` (8 aleyum renames)
- `croilar/pipelines/shared/ducklake.py` (3 aleyum renames)
- `croilar/pipelines/shared/r2_client.py` (1 aleyum constant
  removal)
- `croilar/_shared/config/settings.py` (deprecated
  `AleyumSettings` alias removed)
- `.agents/skills/croilar-stream-registry/SKILL.md` (new)
- `croilar/AGENTS.md` (priority skills 8 of 108 → 9 of 120
  + 1 new skill row in the related skills section)
- `openspec/specs/croilar-data-engineering/spec.md` (2 ADDED
  requirements)

## Impact

- **Naming consistency** — the croilar data engineering
  layer is fully aligned with the 4-quadrant naming
  convention. No more `aleyum` in code, env vars, or
  config defaults.
- **Stream-registry as canonical config** — the
  `StreamSettings` Pydantic BaseSettings is the only API
  surface; no deprecated aliases.
- **Documentation** — the 1 new skill documents the 5
  collapses + the 12 streams + the 3 schedules + the 9
  BAML functions + the 4 R2 destinations.
- **Spec consistency** — the `croilar-data-engineering`
  spec gains 2 new requirements documenting the
  aleyum→croilar cleanup mandate + the Stream-registry
  canonical config surface.
