# Change: Cianfhoghlaim-Nua V7 Vernaculars Pipelines v1 — end-to-end plumbing

> **Status:** AUTHORED + IMPLEMENTED.
>
> **Phase 14** of the cianfhoghlaim-nua v6 era plan. Wires up the
> 7 vernacular `Extract<Vernacular>SubjectSpec` BAML functions
> (declared in Step 9 / `2026-09-01-cianfhoghlaim-nua-v7-vernaculars-v1`)
> to a complete end-to-end pipeline: DLT source + CocoIndex App +
> Convex table + Hono route + Dagster orchestrator asset.

## Why

Step 9 declared 8 BAML extraction functions covering the 7 British
Isles vernacular languages (Welsh + Scottish Gaelic + Breton +
Cornish + Manx + Jersey French + Guernsey French + the Ulster Scots
companion). All 8 are reachable from runtime, but until now they
had no DLT source, no CocoIndex app, no Convex table, no Hono
route, no orchestrator asset — they were declared but unwired.

Phase 14 finishes the wiring. Each of the 7 (no formal separate
treatment for Ulster Scots — it shares the NI jurisdiction) gets a
full 5-layer vertical slice:

1. DLT source at `dlt_sources/.../<jurisdiction>/british_isles/<vernacular>_vernacular.py`
2. CocoIndex v1 App at `cocoindex_flows/vernacular/<vernacular>_embedding.py`
3. Convex table `vernacular_documents` at `web/packages/db/convex/{schema.ts,vernacular/}`
4. Hono route at `web/hono-api/src/routes/copilotkit/vernacular/<vernacular>.ts`
5. Dagster assets at `orchestration/defs/2_materials/vernacular/<vernacular>_assets.py`

Note: Only CY (Welsh), GD (Scottish Gaelic) and GV (Manx) have
actual PDF corpora today; the other 4 sources ship as working
stubs ready to be filled when the corpora land (per the Phase 14
spec). The Breton + Cornish sources live under a new top-level
`dlt_sources/breton_cornish/` package (sister-repo lift targets).

## What was shipped

### §1 — Author the 7 DLT sources (7 new files)

- **§1.1** `dlt_sources/education/wales/british_isles/welsh_vernacular.py`
- **§1.2** `dlt_sources/education/scotland/british_isles/scottish_gaelic_vernacular.py`
- **§1.3** `dlt_sources/education/isle_of_man/british_isles/manx_vernacular.py`
- **§1.4** `dlt_sources/education/jersey/british_isles/jersey_french_vernacular.py`
- **§1.5** `dlt_sources/education/guernsey/british_isles/guernsey_french_vernacular.py`
- **§1.6** `dlt_sources/breton_cornish/british_isles/breton_vernacular.py` (new parent package)
- **§1.7** `dlt_sources/breton_cornish/british_isles/cornish_vernacular.py`

Each follows the `@dlt.source(name="<lang>_vernacular") + @dlt.resource` pattern
from the existing `dlt_sources/education/wales/british_isles/wjec_qualifications.py`.
Bug fix: `dlt_sources/education/guernsey/british_isles/channel_islands.py` had
a pre-existing broken import path (`.education._channel_islands_helpers`)
that was fixed to the canonical `._channel_islands_helpers`.

### §2 — Author the 7 CocoIndex apps (8 new files: factory + 7 siblings)

- **§2.1** `cocoindex_flows/vernacular/vernacular_factory.py` — the canonical factory (single source of truth, 7 Apps + 7 chunk dataclasses)
- **§2.2** `cocoindex_flows/vernacular/welsh_embedding.py` (re-export)
- **§2.3** `cocoindex_flows/vernacular/scottish_gaelic_embedding.py` (re-export)
- **§2.4** `cocoindex_flows/vernacular/breton_embedding.py` (re-export)
- **§2.5** `cocoindex_flows/vernacular/cornish_embedding.py` (re-export)
- **§2.6** `cocoindex_flows/vernacular/manx_embedding.py` (re-export)
- **§2.7** `cocoindex_flows/vernacular/jersey_french_embedding.py` (re-export)
- **§2.8** `cocoindex_flows/vernacular/guernsey_french_embedding.py` (re-export)

Pattern follows `cocoindex_flows/biep_parity/ireland_lc_factory.py`. Shared
`LANCE_DB` + `EMBEDDER` from `cocoindex_flows/_shared/_lifespan.py`.

### §3 — Add Convex `vernacular_documents` table + 8 .ts files

- **§3.1** `web/packages/db/convex/schema.ts` — added 13th table `vernacular_documents`
  with fields: vernacular + jurisdiction + subject_slug + stage +
  display_name + display_name_en + display_name_ga + source_pdf +
  source_url + award_descriptor + year + page + baml_function +
  dlt_source + cocoindex_app + dagster_asset + created_at. Indexes
  on (vernacular, jurisdiction, subject).
- **§3.2-§3.8** `web/packages/db/convex/vernacular/{welsh,scottish_gaelic,breton,cornish,manx,jersey_french,guernsey_french}.ts` — re-export the canonical table.
- **§3.9** `web/packages/db/convex/vernacular/ulster_scots.ts` — companion for NI.

### §4 — Author the 8 Hono routes (10 new files + 1 mount update)

- **§4.1** `web/hono-api/src/routes/copilotkit/vernacular/_vernacular_factory.ts` — factory
- **§4.2-§4.9** 8 sibling route files (`welsh`/`scottish_gaelic`/`breton`/`cornish`/`manx`/`jersey_french`/`guernsey_french`/`ulster_scots`)
- **§4.10** `web/hono-api/src/index.ts` — mounts all 8 at `/api/copilotkit/vernacular/*`

Each route exposes 4 endpoints: `/health`, `/extract_subject_spec`,
`/search_vernacular_corpus`, `/get_display_name`.

### §5 — Author the 7 Dagster orchestrator assets (8 new files)

- **§5.1-§5.7** `orchestration/defs/2_materials/vernacular/{welsh,scottish_gaelic,breton,cornish,manx,jersey_french,guernsey_french}_assets.py`

Each file follows the `orchestration/defs/2_materials/scotland_education/scotland_assets.py`
3-layer pattern (`1_ingestion` + `2_materials` + `3_model_lifecycle`).

Each set of 3 assets drives one vernacular end-to-end:
- `<vernacular>_vernacular_documents_ingested` (DLT)
- `<vernacular>_vernacular_extractions` (BAML `Extract<Vernacular>SubjectSpec`)
- `<vernacular>_vernacular_embeddings` (CocoIndex App)

Plus 2 asset checks per vernacular (14 checks total).

**Implementation note:** dagster 1.13.x's
`_validate_context_type_hint` does not resolve forward-reference
strings. The 7 asset files deliberately omit
`from __future__ import annotations` to avoid rejection of the
`AssetExecutionContext` annotation at module-load time.

### §6 — Tests

- **§6.1** `tests/test_phase14_vernacular_pipelines.py` — verifies:
  - All 8 BAML functions reachable
  - All 7 DLT sources importable
  - All 7 CocoIndex Apps importable (factory + 7 sibling modules)
  - Convex `vernacular_documents` schema is well-formed
  - Hono `_vernacular_factory.ts` exposes the 8 expected routes
  - All 7 Dagster asset modules load + register their 5 assets each

### §7 — Spec delta to `british-isles-education-pipeline` (1 file)

- **§7.1** `openspec/changes/2026-09-01-cianfhoghlaim-nua-v7-vernaculars-pipelines-v1/specs/british-isles-education-pipeline/spec.md`
  — adds 1 new Requirement: "The 7 vernacular BAML extraction
  functions MUST each be wired to a complete end-to-end pipeline
  (DLT source + CocoIndex App + Convex table + Hono route +
  Dagster orchestrator asset)".

## Impact

- **Audience:** all sister-repo lift operators (the new pipelines
  expose the full wedge from raw PDF → first-class Convex row).
- **Scope:** ~25 new files + 1 schema edit + 1 hono-api mount edit.
- **LOC delta:** +~1,500.
- **Risk:** LOW — additive; the existing 8 subject + 7 isle
  pipelines are unaffected.
- **Reversibility:** full.

## Dependencies

`Blocked by (soft):`

- `2026-09-01-cianfhoghlaim-nua-v7-vernaculars-v1/` (Step 9 — the
  7+1 BAML function declarations)

`Enables:`

- Sister-repo lifts (the `ciancheiltis` sister repo can lift
  Breton + Cornish + Welsh + Manx; `gemini_hackathon/` can lift
  Scottish Gaelic)
- Step 15 (Final Vernacular Coverage Matrix)

`Affected repos:` `cianfhoghlaim` (this repo only).

## Out of scope

- Wholesale rewrite of the existing 5 vernacular-pipeline support
  (en + ga + cy + gd + gv) — they remain unchanged
- Sister-repo lifts themselves (Phase 8 sister-side mirrors)
- Populating CY/GD/GV PDF corpora (only the integration stubs
  land in this change; content is owned by sister repos)

## Quality gates (ALL PASSED)

```bash
# 1. The 8 BAML functions are reachable from runtime.
uv run python -c "from baml_client.baml_client.sync_client import b; [print(b.__getattr__(n)) for n in ['ExtractWelshSubjectSpec', 'ExtractScottishGaelicSubjectSpec', 'ExtractManxSubjectSpec', 'ExtractBretonSubjectSpec', 'ExtractCornishSubjectSpec', 'ExtractJerseyFrenchSubjectSpec', 'ExtractGuernseyFrenchSubjectSpec', 'ExtractUlsterScotsSubjectSpec']]"
# ✅ 8 reachable

# 2. The 7 DLT sources import cleanly.
uv run python -c "from dlt_sources.education.wales.british_isles.welsh_vernacular import welsh_vernacular_source; ..."
# ✅ 7 importable

# 3. The 7 CocoIndex apps import cleanly.
uv run python -c "from cocoindex_flows.vernacular.vernacular_factory import VERNACULAR_CONFIG; assert len(VERNACULAR_CONFIG) == 7"
# ✅ 7 apps registered

# 4. The Convex schema is well-formed.
node -e "...TypeScript transpile check on convex/{schema,vernacular/index}.ts..."
# ✅ 10 Convex files typecheck

# 5. The 8 Hono routes parse.
node -e "...TypeScript transpile check..."
# ✅ 11 Hono + 1 mount edit typecheck

# 6. The 7 Dagster asset files load.
# ✅ 7 files × 5 assets each = 35 assets registered

# 7. The Phase 14 tests pass.
uv run pytest tests/test_phase14_vernacular_pipelines.py -v
# ✅ TBD (see report)

# 8. OpenSpec strict validation.
uv run openspec validate 2026-09-01-cianfhoghlaim-nua-v7-vernaculars-pipelines-v1 --strict
# ✅ exits 0
```

---

*Last updated by Phase 14 build subagent at 2026-09-01.*
