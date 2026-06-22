# Change: sync-skills-from-docs-round-3

## Why

A third round of `docs/*` consolidation. The user listed 8
specific files (2,702 lines total) covering the data platform
(`duckdb`, `dlt`, `dagster`, `sqlmesh`), platform architecture
(`hono`, `modal`), and the tuatha product
(`babylonjs`, `TUATH_QUICKSTART`).

Four concrete patterns emerge:

1. **Generic-upstream docs duplicate the just-expanded skills.**
   `dlt.md` (1051 lines) is 100% generic dltHub material with
   zero KCG content; the `dlt` skill (just expanded in round 1)
   is the canonical KCG router. `duckdb.md` (367 lines) is
   byte-identical to the existing `duckdb` skill body.
2. **53-line stub docs add KCG blurb that should live in the
   canonical skill.** `sqlmesh.md`, `hono.md`, `modal.md`,
   `babylonjs.md`, `TUATH_QUICKSTART.md` follow a "package
   pointer with KCG paragraph" pattern. The KCG blurb (2-3
   sentences) is the only unique value; the rest is upstream
   marketing.
3. **No skills exist for `modal` or `babylonjs`.** Both are
   first-class project dependencies (Modal for burst GPU, Babylon.js
   for the `tuatha/game/` 3D client) but have no canonical doc.
4. **No `tuatha-platform` skill exists** despite the MMO being a
   full quadrant of the monorepo. `tuatha/AGENTS.md` is the
   existing entry point, but `TUATH_QUICKSTART.md` has unique
   quick-start + endpoints + Dagster-assets content that should
   be a router-style skill.

## What Changes

### Skills to create (3)

- `.agents/skills/modal/SKILL.md` — serverless GPU cloud
  (A100/H100/L40S) with per-second billing. KCG-specific:
  MacBook M4 daily baseline + Modal burst for 13B+ training +
  Garage S3 sync + llama-swap serving.
- `.agents/skills/babylonjs/SKILL.md` — 3D rendering engine
  (WebGL + WebGPU). KCG-specific: the `tuatha/game/` Babylon.js
  client, Convex real-time state, Havok physics, particle
  systems, WebGPU enablement.
- `.agents/skills/tuatha-platform/SKILL.md` — Celtic MMO + crypto
  platform quadrant router. Quick-start, endpoints, project
  structure, Dagster assets, KCG-specific env vars. Inherits the
  "Quick routing" table from `tuatha/AGENTS.md`. Cross-references
  to `baml`, `hono`, `tanstack-start`, `copilotkit`,
  `celtic-language-ai`, `dagger`.

### Skills to expand (5)

- `.agents/skills/ducklake/SKILL.md` — add a "## KCG-Specific
  Patterns" section: DuckLake `ATTACH 'ducklake:md:oideachais'`,
  MotherDuck connection string, kcg-cocoindex chunked Parquet
  writes, `stedding/ingest_queue/` reads, KCG-specific
  QUALIFY/ROW_NUMBER patterns for `ireland/curriculum/` "latest
  version" lookup, marimo + Polars round-trip
- `.agents/skills/dagster/SKILL.md` — append the KCG context
  from `docs/02-data-platform/dagster.md:79-117` (install +
  integration paragraph + 4-layer asset groups narrative form)
  + lines 763-794 (DLT/Firecrawl integration patterns)
- `.agents/skills/sqlmesh/SKILL.md` — append the KCG paragraph
  (sqlmesh.md:23-25) describing the KCG curriculum-pipeline
  use case + the `supersedes:`-style deprecation note from
  `docs/sqlmesh.md` (round 0 consolidation)
- `.agents/skills/hono/SKILL.md` — append 3-line KCG integration
  blurb (Pocket ID SSO + Langfuse headers + AG-UI SSE)
- `.agents/skills/dlt/SKILL.md` — no expansion (already
  comprehensive from round 1)

### Docs to delete (after skill updates)

- `docs/02-data-platform/duckdb.md` (367 lines, redundant with skill)
- `docs/02-data-platform/dlt.md` (1051 lines, redundant — generic
  dltHub)
- `docs/02-data-platform/dagster.md` (919 lines, KCG context
  absorbed into skill)
- `docs/02-data-platform/sqlmesh.md` (53 lines, KCG blurb absorbed)
- `docs/01-platform-architecture/hono.md` (53 lines, KCG blurb
  absorbed)
- `docs/01-platform-architecture/modal.md` (53 lines, promoted
  to a new skill)
- `docs/06-product/babylonjs.md` (51 lines, promoted to a new skill)
- `docs/06-product/TUATH_QUICKSTART.md` (155 lines, promoted to
  a new `tuatha-platform` skill with corrected paths)

### Project rules PRESERVED (not changed)

- The tuatha quadrant is the Celtic MMO + crypto platform —
  now documented in the new `tuatha-platform` skill
- The `tuatha/` workspace paths (`tuatha/game/`, `tuatha/crates/`,
  `tuatha/crypteolas/`, `tuatha/ui/`) — preserved
- The 4 sub-modules — preserved

## Impact

- **Affected specs (1)**: `tuatha-platform` adds 2 new
  requirements (Modal burst-training handoff, Babylon.js game
  client) — these map directly to the 2 new KCG integration
  sections in the new `tuatha-platform` skill
- **Affected code**: none. Skills are documentation.
- **Affected skills** (8 total): 3 new (modal, babylonjs,
  tuatha-platform) + 5 expanded (ducklake, dagster, sqlmesh,
  hono, dlt — dlt is a no-op).

## Success criteria

- `openspec validate sync-skills-from-docs-round-3 --strict`
  passes
- The 3 new skills exist at `.agents/skills/{modal, babylonjs,
  tuatha-platform}/SKILL.md`
- The 5 existing skills have new KCG context sections
- The 8 docs files are removed

## Rollback

Skills-only. Rollback = restore the 8 docs files from git
(`git checkout HEAD~1 -- docs/02-data-platform/duckdb.md ...`).
No data, code, or runtime state is affected.
