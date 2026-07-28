# 2026-08-13-biep-v3-filesystem-and-language-pipelines-v1

## Why

The BIEP v3 v1 + v2 + v3 changes (Phases 0-5) shipped the
jurisdiction-scoped education pipelines (Ireland + England + SCT +
WLS + NI + Jersey + Guernsey + IoM). This Phase 6 ships the 2
**jurisdiction-agnostic scanner domains**:

- **filesystem** (`dlt_sources/filesystem/`) — 16 Python files including
  the leabharlann_books source, the email_inbox pipeline, the
  google_takeout source, the zotero source, the university_of_galway
  source, the leaving_cert_source, the gemini_deep_research source,
  + 5 helpers
- **language** (`dlt_sources/language/`) — 19 Python files including the
  ainm, canuint, duchas, gaois, tearma, logainm, heritage, + 5
  helpers

These 2 domains are NOT jurisdiction-scoped — they apply across all
8 British Isles jurisdictions + cross-cutting. The BIEP v3 canonical
pattern is to wire them as **2 new domains** in the BIEP v3
cross-jurisdiction registry: `filesystem` and `language`.

## What changes

### 1. 2 new Dagster generic asset files

- `orchestration/defs/2_materials/filesystem_pipelines/generic_filesystem_assets.py` —
  3 generic filesystem assets + 3 asset checks + 11 per-source
  backfill jobs (one per filesystem source)
- `orchestration/defs/2_materials/language_pipelines/generic_language_assets.py` —
  3 generic language assets + 3 asset checks + 19 per-source
  backfill jobs (one per language source)

### 2. 2 new monthly MotherDuck Flights

- `motherduck/flights/filesystem_monthly_sync_flight.py` — runs the
  filesystem Dagster assets + writes status to
  `md:cianfhoghlaim.education.filesystem._audit.daily_sync_status`
- `motherduck/flights/language_monthly_sync_flight.py` — runs the
  language Dagster assets + writes status to
  `md:cianfhoghlaim.education.language._audit.daily_sync_status`

The monthly cadence (1st of each month, 00:00 UTC) per the BIEP v3
scheduling policy.

## Dependencies

```yaml
Blocked by (soft): 2026-08-13-biep-v3-systematic-download-ireland-england-v1
Affected repos: cianfhoghlaim (single-repo change)
```

## Acceptance gates

- `openspec validate 2026-08-13-biep-v3-filesystem-and-language-pipelines-v1 --strict` passes
- `dg list assets | grep filesystem_` lists 3 assets + 3 checks
- `dg list assets | grep language_` lists 3 assets + 3 checks
- `mise run filesystem:monthly:sync` (the new monthly flight) runs cleanly
- `mise run language:monthly:sync` (the new monthly flight) runs cleanly
- `mise run lint:skills` still passes (53/53)
- Push target: `origin/main`

## Cross-references

- [`british-isles-education-pipeline`](../../specs/british-isles-education-pipeline/spec.md) —
  the BIEP v1/v2 LC spec; extended by Phases 0-6
- `openspec/changes/2026-08-13-biep-v3-systematic-download-ireland-england-v1/` —
  the umbrella change that drove the BIEP v3 systematic download
- `orchestration/automation/biiep_scheduling.py` — the canonical
  BIEP v3 scheduling policy (yearly education + monthly filesystem + language)
- `dlt_sources/filesystem/` — the 11 canonical filesystem DLT sources
- `dlt_sources/language/` — the 19 canonical language DLT sources
- `.agents/skills/dlt/SKILL.md` — the DLT conventions
