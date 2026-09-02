# Change: Cianfhoghlaim-Nua Orchestration Integration v1 — Phase 11 wire-up

> **Status:** AUTHORED, ready for execution.
>
> **Phase 11 of 11** in the
> [`openspec/plans/2026-09-01-cianfhoghlaim-nua-v6-era-v1.md`](../../plans/2026-09-01-cianfhoghlaim-nua-v6-era-v1.md)
> plan. Wires the 4 Phase-1 LC study-plan routes + the 5 jurisdiction
> BAML extractors + the Convex persistence into a single end-to-end
> pipeline.
>
> **Anchors:**
> - [`2026-09-01-cianfhoghlaim-nua-end-to-end-showcase-v1/`](../2026-09-01-cianfhoghlaim-nua-end-to-end-showcase-v1/)
>   — the Phase 1 4-subject chat-with-syllabus + study-plan + oral pipeline.
> - [`2026-09-01-cianfhoghlaim-nua-5-jurisdiction-completion-v1/`](../2026-09-01-cianfhoghlaim-nua-5-jurisdiction-completion-v1/)
>   — the 5 jurisdiction BAML extraction surfaces
>   (`ExtractEnglandSubjectSpec` etc. + vernacular overlay classes).
> - [`2026-09-01-cianfhoghlaim-nua-ireland-lc-completion-v1/`](../2026-09-01-cianfhoghlaim-nua-ireland-lc-completion-v1/)
>   — the canonical Convex schema + the 14 NCCA LC subject tables
>   (8 priority + 6 NCCA-adjacent).
> - [`2026-09-01-cianfhoghlaim-nua-web-consolidation-v1/`](../2026-09-01-cianfhoghlaim-nua-web-consolidation-v1/)
>   — the 5→1 web app consolidation. The 4 mounted LC routes at
>   `web/hono-api/src/routes/copilotkit/lc/` belong to that
>   consolidation's Hono gateway.
> - [`openspec/specs/british-isles-education-pipeline/spec.md`](../../specs/british-isles-education-pipeline/spec.md)
>   — extended by §A below (1 new Requirement).

## Why

The 22 Phase-0..10 openspec changes shipped 18 passing tests but left
the orchestration graph in a half-wired state:

1. **Hono planner service was stubbed.** The 4 mounted LC study-plan
   routes at `/api/copilotkit/lc/{chemistry, mathematics, gaeilge,
   computer_science}/get_study_plan` returned a 12-week STUB from
   `web/hono-api/src/routes/copilotkit/lc/_study_plan_stub.ts`. The
   real Python planner at
   `agents/adk/subjects/lc/planner.py::generate_study_plan(...)`
   existed + was async + was the canonical entry point — but no
   Hono handler ever called it. The TanStack Start `useStudyPlan`
   hook therefore never received a real study plan.

2. **The 5 jurisdiction orchestrators used a `getattr` fallback.** All
   5 asset definitions at
   `orchestration/defs/2_materials/{england,wales,scotland,
   northern_ireland,isle_of_man}_education/<jur>_assets.py`
   contained the lines
   ```python
   baml_fn_name = row.baml_function.removeprefix("b.")
   fn = getattr(b, baml_fn_name, None)
   if fn is None: continue  # silently dropped
   ```
   Even though
   `baml_src/british_isles/{en,wl,sc,ni,im}/education/<jur>_extraction.baml`
   shipped real `Extract<Jurisdiction>SubjectSpec` functions + their
   `<Jurisdiction>SubjectSpec` classes, none of them were actually
   invoked from any Dagster asset. The 5 *_extractions assets
   therefore always reported `rows_extracted: 0`.

3. **Convex was schema-only.** The 5 jurisdiction subject specs had
   nowhere to land in `web/apps/cianfhoghlaim-nua/convex/schema.ts`.
   The existing 4 root tables (`users`, `study_plans`,
   `oral_study_plans`, `ncce_learning_graphs`) + the 8 per-subject
   tables (`accounting`, `business`, `french`, `history`, `art`,
   `music`, `applied_mathematics`, `physics`) covered the LC surface;
   the per-jurisdiction surface was unaddressed. No `convex.json`
   existed.

Without Phase 11, the cianfhoghlaim-nua end-to-end showcase remains a
demonstration of stubs — the four LC subjects render study plans but
no planner ever ran; the five jurisdictions ship BAML functions but
no orchestrator invokes them; the canonical Convex tables exist but
no jurisdiction row ever lands.

## What changes

### §1 — Hono planner service wire-up (4 routes × 1 builder)

- **§1.1** Replace
  `web/hono-api/src/routes/copilotkit/lc/_study_plan_stub.ts` with a
  thin subprocess bridge to
  `agents/adk/subjects/lc/planner.py::generate_study_plan(...)`. Use
  `node:child_process::execFile` with the Python module path + function
  name as fixed strings (no shell interpolation), and serialise
  inputs/outputs as JSON over stdin/stdout — the same pattern
  already used by
  `web/hono-api/src/routes/copilotkit/registry.ts::invokePythonRuntime(...)`.

- **§1.2** Update the 4 route handlers
  (`chemistry.ts`, `mathematics.ts`, `gaeilge.ts`,
  `computer_science.ts`) to call the new `buildStudyPlanHandler(...)`
  instead of inlining the stub response. The route mounts in
  `web/hono-api/src/index.ts` stay unchanged.

- **§1.3** Fall back to the in-process `studyPlanStubResponse(...)`
  helper on subprocess failure (Python missing, planner raises,
  baml_client unavailable) so the route never 5xxs in dev / CI.

### §2 — Per-jurisdiction BAML extractor wire-up (5 orchestrators × 1 helper)

- **§2.1** Author the shared helper at
  `orchestration/defs/2_materials/_base/jurisdiction_baml_extractor.py`
  with:
  - `read_pdf_text(path)` (pypdf-based; matches
    `quest_pack_assets.py`'s style)
  - `get_jurisdiction_baml_fn(jurisdiction)` returning
    `b.Extract<Jurisdiction>SubjectSpec` (or `None` — same fallback
    semantics as before, but with explicit per-jurisdiction
    `JURISDICTION_BAML_FUNCTIONS` mapping)
  - `serialise_spec(spec)` (Pydantic v1/v2 + dict tolerant)
  - `materialise_subject_spec_to_convex(jurisdiction, subject_slug,
    spec, ...)` — uses `convex.ConvexClient.mutation(...)`, degrades
    gracefully when the Convex client isn't available (mirrors
    `_write_quest_pack_to_convex` in `quest_pack_assets.py`)
  - `invoke_jurisdiction_extractor(jurisdiction, pdf_path,
    subject_slug, ...)` — the orchestrator hot-path that reads
    PDF → invokes BAML → writes to Convex.

- **§2.2** Update the 5 jurisdiction orchestrators to use the
  helper. Each one's `<jur>_extractions` asset replaces the
  `getattr(b, fn_name, None)` block with:
  ```python
  result = invoke_jurisdiction_extractor(
      jurisdiction="<jur>",
      pdf_path=row.source_url or "",
      subject_slug=row.subject_slug,
      source_url=row.source_url,
      stage="LEAVING_CERT",
  )
  ```
  Result dict captures `extracted` / `spec` / `convex_written`
  / `reason` and is added to the asset's return value.

### §3 — Convex deployment prep (5 new tables + 1 config)

- **§3.1** Author `web/apps/cianfhoghlaim-nua/convex.json` with the
  canonical Convex codegen + functions paths.

- **§3.2** Add the 5 jurisdiction subject_spec tables to
  `web/apps/cianfhoghlaim-nua/convex/schema.ts`:
  - `england_subject_specs`
  - `wales_subject_specs`
  - `scotland_subject_specs`
  - `northern_ireland_subject_specs`
  - `isle_of_man_subject_specs`

  Each table stores the canonical fields
  (`subject_slug`, `source_pdf`, `source_url`, `stage`,
  `display_name`, `display_name_ga`, `display_name_local`,
  `award_descriptor`, `descriptor_vocabulary[]`,
  `key_competencies[]`, `language`, `year`, `page`,
  `payload_json`, `created_at`) with `by_jurisdiction`,
  `by_subject`, `by_stage` indexes.

- **§3.3** Author
  `web/apps/cianfhoghlaim-nua/convex/jurisdictions/{england,wales,
  scotland,northern_ireland,isle_of_man}.ts` — one table definition
  + one `create` mutation per jurisdiction, called from
  `materialise_subject_spec_to_convex`.

### §4 — Test coverage (1 new test file)

- **§4.1** Author `tests/test_phase11_orchestration_integration.py`
  covering all four sub-deliverables:
  - The Hono `buildStudyPlanHandler` falls back to the in-process
    stub on subprocess failure.
  - The 5 jurisdiction orchestrators reference the canonical
    `invoke_jurisdiction_extractor` (NOT the `getattr` fallback).
  - The 5 jurisdiction Convex tables are wired into `convex/schema.ts`.
  - The canonical 18-table schema is preserved (the 4 root + 8
    per-subject tables stay; 5 new tables added; no renames).
  - The 5 jurisdiction BAML extraction functions are present in the
    generated `baml_client` (`b.ExtractEnglandSubjectSpec` +
    `ExtractWalesSubjectSpec` + `ExtractScotlandSubjectSpec` +
    `ExtractNorthernIrelandSubjectSpec` +
    `ExtractIsleOfManSubjectSpec`).

### §5 — Spec delta (1 new Requirement + 4 Scenarios)

- **§5.1** Add 1 new Requirement +
  `### Requirement: 5 jurisdiction orchestrators invoke canonical Extract<Jurisdiction>SubjectSpec + materialise to Convex`
  under `openspec/changes/.../specs/british-isles-education-pipeline/spec.md`,
  with 4 Scenarios covering: Hono route returns live planner
  response; each jurisdiction orchestrator invokes the canonical
  BAML function; Convex materialisation happens per row; graceful
  degradation when BAML/Convex are unavailable.

## Impact

- **Audience:** every British Isles secondary-school student using
  `cianfhoghlaim-nua/` (LC + the 5 jurisdiction routes), plus the 5
  jurisdiction Dagster asset operators.
- **Scope:** 1 Hono file replaced + 4 Hono files lightly updated + 1
  shared Python helper added + 5 jurisdiction orchestrators updated +
  5 Convex tables added + 1 Convex config + 1 test file + 1 openspec
  change.
- **LOC delta:** ~900 new (helper + 5 Convex tables + 1 test
  suite + 1 openspec) + ~250 modified (Hono stub + 5 orchestrators +
  Convex schema).
- **Risk:** LOW for §1 (subprocess bridge is a recognised pattern
  already used by `registry.ts`); MEDIUM for §2 (5 orchestrators
  move from `getattr` fallback to canonical BAML call + Convex write
  — each of the 5 must materialise correctly); LOW for §3 (Convex
  is additive, no renames).
- **Reversibility:** full — `git revert` of the Phase 11 commit
  restores the previous stubbed state (Hono stays stubbed, the 5
  orchestrators revert to the `getattr` fallback, the 5 Convex tables
  can be dropped via `npx convex schema drop england_subject_specs`
  if the schema ever blocks a deployment).

## Dependencies

`Blocked by (soft):`
- `2026-09-01-cianfhoghlaim-nua-end-to-end-showcase-v1/` — Phase 1
  shipped the canonical Python planner at
  `agents/adk/subjects/lc/planner.py`; Phase 11 wires the Hono
  bridge to it.
- `2026-09-01-cianfhoghlaim-nua-5-jurisdiction-completion-v1/` —
  Steps 4-8 shipped the 5 jurisdiction BAML extraction functions;
  Phase 11 wires the 5 orchestrators to them.
- `2026-09-01-cianfhoghlaim-nua-ireland-lc-completion-v1/` —
  Step 2 shipped the canonical Convex schema; Phase 11 adds the 5
  jurisdiction tables to it.

`Blocked by (hard):` none.

`Extends:`
- [`openspec/specs/british-isles-education-pipeline/spec.md`](../../specs/british-isles-education-pipeline/spec.md)
  — adds 1 Requirement "5 jurisdiction orchestrators invoke canonical
  Extract<Jurisdiction>SubjectSpec + materialise to Convex".

`Affected repos:` `cianfhoghlaim` (this repo only).

## Out of scope

- BAML hard hardening of the 5 jurisdiction extractors (Phase 5
  territory — RAGAS scores + quality gates).
- The Jersey + Guernsey jurisdiction completions (Steps 9 + 10
  deferred per the 5-jurisdiction completion change).
- Replacing the subprocess-bridge pattern with a real
  HTTP-bridge service (Phase 12+ if infra allows).
- Convex deployment to production (`npx convex deploy` + the
  Wrangler / Cloudflare Pages front-end) — Phase 12+
  infra-deliverable.
- The 8 deferred LC subjects (geography, english, applied
  mathematics, biology) — Phase 5 broadens to 8 NCCA subjects.

## Quality gates (must pass before `openspec archive`)

```bash
uv run openspec validate 2026-09-XX-orchestration-integration-v1 --strict
pytest tests/test_phase11_orchestration_integration.py -v
pytest tests/test_adk_subject_actions.py -v
dg list assets 2>&1 | grep -E "england|wales|scotland|northern_ireland|isle_of_man" | head -20
```

The change CANNOT archive until ALL gates exit 0.

## Cross-cutting quality gates

1. **`openspec validate --strict`** exits 0.
2. **No `getattr(b, fn_name, None)` fallback remains** in any of the
   5 jurisdiction orchestrators. Phase 11 explicitly replaces each
   one with `invoke_jurisdiction_extractor(...)`.
3. **All 5 Convex tables are additive** — no
   `study_plans / oral_study_plans / quest_packs` table is removed
   or renamed by this change.
4. **All 5 Convex mutations** (`<jur>_subject_specs:create`) succeed
   in the local dev deployment (manually verified at
   `/Users/cianmacandeisigh/dev/cianfhoghlaim/web/apps/cianfhoghlaim-nua/convex/jurisdictions/`).

---

*Last updated by build subagent at 2026-09-01.*
