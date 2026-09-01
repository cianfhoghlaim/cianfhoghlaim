# Change: Cianfhoghlaim-Nua End-to-End Showcase v1 — Chemistry + Mathematics + Gaeilge + Computer Science study-plan → oral pipeline

> **Status:** AUTHORED, ready for execution.
>
> **Phase 1 of 10** in the
> [`openspec/plans/2026-09-01-cianfhoghlaim-nua-v6-era-v1.md`](../../plans/2026-09-01-cianfhoghlaim-nua-v6-era-v1.md)
> 10-phase integration of `gemini_hackathon/` learnings back into
> `cianfhoghlaim/`. The phase-by-phase authoring strategy (per
> operator direction 2026-09-01) means subsequent phases
> (web-consolidation, NCCE-showcase, A2UI catalog, BAML hardening,
> oral plans, certificate pipeline, sister-side mirrors, GCP opt-in)
> are authored as their respective phases begin.
>
> **Anchors:**
> - [`2026-08-31-sister-repo-gemini-lesson-transfer-v1/`](../2026-08-31-sister-repo-gemini-lesson-transfer-v1/)
>   — the per-sister-repo deep transfer of the gemini_hackathon
>   Gemma + Gemini + ADK 2 + AG-UI/A2UI/CopilotKit lessons
>   (background context, not a hard dependency).
> - [`2026-08-31-baml-primary-alias-and-fallback-v1/`](../2026-08-31-baml-primary-alias-and-fallback-v1/)
>   — the `Primary` BAML alias + per-function fallback chain
>   (Phase 1 of v5; Phase 1 of v6 reuses the Primary alias).
> - [`2026-08-31-cianfhoghlaim-v5-opencode-model-priority-v1/`](../2026-08-31-cianfhoghlaim-v5-opencode-model-priority-v1/)
>   — the v5 model registry (Qwen removed; MiniMax-M3 chokepoint +
>     Vertex Gemini 3.5 + Unsloth Gemma 4).
> - [`2026-08-31-meaisinfhoghlaim-unsloth-priority-v1/`](../2026-08-31-meaisinfhoghlaim-unsloth-priority-v1/)
>   — the meaisinfhoghlaim Unsloth-prioritised refactor
>   (`gemma-4-26b-a4b-vision` for OCR ensemble path 3).
> - [`openspec/specs/oideachais-pipeline/spec.md`](../../specs/oideachais-pipeline/spec.md)
>   — the canonical Celtic education curriculum pipeline spec.
>   Phase 1 extends this spec with `chat-with-syllabus` and
>   `study-plan → oral pipeline` Requirements.

## Why

The 2026-08-21 → 2026-08-31 **Google "All Things Agentic" hackathon**
(deadline 2026-08-31 @ 8:00pm EDT, $180K prize pool, 6,126
participants) shipped a working
**chat-with-syllabus → study-plan → oral-delivery** surface for the
6 NCCA Leaving Certificate subjects (Maths, Chemistry, Geography,
English, Gaeilge, Computer Science) into the sister repo
`~/dev/gemini_hackathon/`. The submission is now closed and the
operator has pivoted strategy back to `cianfhoghlaim/` as the
canonical home for the integrated capability.

A direct audit of the current cianfhoghlaim `oideachais/` web app +
`agents/adk/` + `orchestration/` + `baml_src/` surfaces
revealed **4 critical gaps** that block end-to-end operation:

1. **`agents/adk/subjects/lc/<subject>.py::get_study_plan()`**
   imports `from agents.adk.subjects.lc.<subject>.planner import
   generate_study_plan` — but **no `planner.py` exists** under any
   `agents/adk/subjects/lc/<subject>/` directory. Every per-subject
   ADK action registration is silently broken.
2. **`orchestration/defs/2_materials/lc_extraction/quest_pack_assets.py:326`**
   calls `generate_fn = getattr(b, f"Generate{prefix}QuestPack")` —
   per-subject `GenerateMathQuestPack` / `GenerateGaelQuestPack`
   were deleted by the qpack-template consolidation; the asset
   would `AttributeError` at materialisation time.
3. **`agents/api/routes/routes/search.py`** imports
   `HybridSearchConfig` + `SearchMode` + `get_search_engine` from
   `...knowledge_graph` — but that module path does not exist.
   `notebooks/10_biep_pipeline_lakehouse_semantic_01_search.py`
   imports `from cianfhoghlaim.storage.cognify.rules import
   semantic_search as ss` — same broken path. Hybrid search is
   half-implemented.
4. **`agents/adk/voice_agent.py::process_audio()`** is literally
   `pass # TODO: Pipecat SDK integration`. The TTS service
   (`agents/api/_oideachais_api/services/chatterbox.py`) has no UI
   consumer; the Pipecat IaC stack is provisioned but unused.

Plus 12 supporting issues: Convex schema lacks
`study_plans / quest_packs / oral_study_plans / formative_attempts /
audio_segments`; the 6 per-subject study-plan route stubs render
placeholders; the 8 per-subject CopilotKit action registries return
`{stub: true}`; the 6 per-subject Hono action routes return
`{stub: true}`; `agents/_workflow_handlers.py::dispatch_study_plan`
is explicitly a stub; the `_legacy/web/<subject>_web.baml` files
contain the only `WebStudyPlan` definitions and are flagged
`_legacy`; the `LanceDB ireland_lc_*_chunks` tables have no FTS
indexes (only HNSW vector); the 5 web apps are fragmented; the 4
PDF extraction pipelines overlap; the per-subject marimo notebooks
are 36+ duplicated templates.

Without Phase 1, the chat-with-syllabus + study-plan + oral
pipeline cannot reach a single Irish secondary-school student
through any surface in `cianfhoghlaim/`.

## What changes

### §1 — Author the canonical study-plan surface (3 tasks)

- **§1.1** Author `baml_src/british_isles/_shared/study_plan.baml`
  with `StudyPlan + ExtractStudyPlan + GenerateStudyPlanAssets`
  classes — porting the 6 legacy
  `baml_src/british_isles/ireland/education/_legacy/web/<subject>_web.baml`
  into a single canonical schema (deletes `_legacy/web/` after the
  4-subject port completes).
- **§1.2** Author `agents/adk/subjects/lc/planner.py` with the
  `generate_study_plan(parameters) -> StudyPlanResponse` callable
  that wraps `b.GenerateStudyPlanAssets(...)` and rehydrates the
  Convex `study_plans` row.
- **§1.3** Author `baml_src/british_isles/_shared/oral_study_plan.baml`
  with `GenerateOralStudyPlan(text_plan, dialect) -> OralStudyPlan`
  for Phase 6 (oral delivery); stubbed callable in Phase 1.

### §2 — Fix the broken stubs (6 tasks)

- **§2.1** Fix
  `orchestration/defs/2_materials/lc_extraction/quest_pack_assets.py:326`
  to call consolidated `b.GenerateSubjectQuestPack(...)` (the
  qpack-template consolidated entry) instead of per-subject
  `Generate{prefix}QuestPack`.
- **§2.2** Replace the broken
  `from agents.knowledge_graph import HybridSearchConfig` import in
  `agents/api/routes/routes/search.py` with
  `from agents.meaisinfhoghlaim.firecrawl_mcp.memory.router import
  MemoryRouter` (the canonical RRF hybrid).
- **§2.3** Replace the broken
  `from cianfhoghlaim.storage.cognify.rules import semantic_search as
  ss` import in
  `notebooks/10_biep_pipeline_lakehouse_semantic_01_search.py`
  with the same `MemoryRouter` re-export.
- **§2.4** Replace the `pass # TODO` body of
  `agents/adk/voice_agent.py::process_audio()` with a wired
  Pipecat client + ChatterboxTTS dispatch (Phase 1 ships a
  no-op stub that logs the round-trip; Phase 6 wires the
  real TTS).
- **§2.5** Replace the stub body of
  `agents/_workflow_handlers.py::dispatch_study_plan` with a real
  call to `agents.adk.subjects.lc.planner.generate_study_plan`.
- **§2.6** Add FTS indexes to the LanceDB `ireland_lc_*_chunks`
  tables (currently only HNSW vector indexes).

### §3 — Convex schema + per-subject wire-ups (5 tasks)

- **§3.1** Extend `web/packages/db/convex/schema.ts` with
  `study_plans + quest_packs + oral_study_plans +
  formative_attempts + audio_segments + learning_graph_nodes`
  tables (Phase 1 adds the first 3; Phase 4/6 add the rest).
- **§3.2** Wire `web/hono-api/src/routes/copilotkit/lc/{chemistry,
  mathematics, gaeilge, computer_science}.ts` `POST
  /get_study_plan` to `agents.adk.subjects.lc.planner` instead
  of returning `{stub: true}`.
- **§3.3** Wire
  `web/apps/oideachais/src/lib/copilotkit/lc/{chemistry,
  mathematics, gaeilge, computer_science}.ts`
  `useCopilotAction({name: "get_study_plan", ...})` handler to
  the same planner (return shape unchanged).
- **§3.4** Replace placeholder content of
  `web/apps/oideachais/routes/lc/{chemistry, mathematics, gaeilge,
  computer_science}/study-plan.tsx` with a real
  `<StudyPlanCard>` A2UI surface (Phase 1 ships a basic
  `<StudyPlanCard>` placeholder; Phase 2 fills in the full
  11-component catalog).
- **§3.5** Wire `agents/_workflow_handlers.py::dispatch_study_plan`
  to the planner (the §2.5 stub) and verify end-to-end via
  the `tests/test_adk_subject_actions.py` test suite.

### §4 — Subject end-to-end showcases (4 subjects × 4 tasks = 16 tasks)

For each of **Chemistry** (§4.1-§4.4), **Mathematics** (§4.5-§4.8),
**Gaeilge** (§4.9-§4.12), and **Computer Science** (§4.13-§4.16):

- [ ] **§4.{N}.1** `baml_src/british_isles/ireland/education/marking/{subject}_marking.baml`
  reuses the canonical `StudyPlan` schema (no per-subject
  duplicate schema).
- [ ] **§4.{N}.2** `agents/adk/subjects/lc/{subject}.py` registers
  `get_study_plan` + `get_syllabus_topics` + `get_exam_papers` +
  `get_marking_schemes` + `get_cross_jurisdictional_equivalences` +
  `extract_syllabus_from_pdf` + 5 more actions (13 total per the
  Subject spec).
- [ ] **§4.{N}.3** `web/apps/oideachais/routes/lc/{subject}/index.tsx`
  mounts the per-subject `SubjectChat` + `MarimoEmbed` +
  `CiPdfLibraryPanel` + `BIEPSubjectPage` (existing oideachais
  components — no new components in Phase 1).
- [ ] **§4.{N}.4** `notebooks/lc/{subject}.py` extends the BIEP
  pipeline with a "study-plan demo" cell that calls the new
  `planner.generate_study_plan(...)` and renders the
  `StudyPlanResponse` inline.

The 4 subjects are demonstrated end-to-end via the existing
**`web/apps/oideachais/`** app (Phase 3 collapses the 5 web apps
into `web/apps/cianfhoghlaim-nua/`; Phase 1 ships the showcase in
the existing app as the bridge to that consolidation).

### §5 — Validation + quality gates (3 tasks)

- **§5.1** `uv run openspec validate
  2026-09-01-cianfhoghlaim-nua-end-to-end-showcase-v1 --strict`
  exits 0.
- **§5.2** `mise run lint:registry` reports 0 drift (no
  hardcoded model strings).
- **§5.3** `mise run lint:skills` reports 167 skills pass.
- **§5.4** `pytest tests/test_adk_subject_actions.py` runs the
  4 per-subject integration tests green (one per subject).
- **§5.5** `dg list assets | grep lc_extraction` shows the
  fixed `quest_pack_assets.py` + `study_plan_assets.py`
  materialisations succeed in the local DuckDB.

### §6 — BAML Primary alias confirmation (1 task)

- **§6.1** Confirm `baml_src/clients.baml` + `baml_src/clients_biep_v3.py`
  use the `Primary` BAML alias (per
  `2026-08-31-baml-primary-alias-and-fallback-v1/`); the new
  `study_plan.baml` + `oral_study_plan.baml` reuse the alias
  with `unavailable-to-provide` retry policy per the
  fallback chain.

## Impact

- **Audience:** every Irish secondary-school student using
  `oideachais/` for LC Chemistry + LC Mathematics + LC Gaeilge +
  LC Computer Science.
- **Scope:** 4 LC subjects (the remaining 4 subjects — geography +
  english + applied mathematics + biology — are out of Phase 1
  scope; Phase 5 broadens to all 8 NCCA subjects).
- **LOC delta:** ~600 new (study_plan.baml + planner.py +
  Convex schema additions + 4×4 wire-ups + oral_study_plan.baml
  stub) + ~100 modified (broken-stub fixes).
- **Risk:** LOW for §1-§3 (refactors into existing structure);
  MEDIUM for §4 (4 subjects end-to-end requires per-subject
  integration testing).
- **Reversibility:** full — `git revert` of the Phase 1 commit
  restores the stubbed state without schema migration (Convex
  schema additions are additive).

## Dependencies

`Blocked by (soft):`

- `2026-08-31-cianfhoghlaim-v5-opencode-model-priority-v1/` — the
  model registry refactor (Qwen removed; Gemma 4 + MiniMax-M3
  + Vertex Gemini 3.5 stack live).
- `2026-08-31-baml-primary-alias-and-fallback-v1/` — the BAML
  `Primary` alias (reused by §6.1).
- `2026-08-31-meaisinfhoghlaim-unsloth-priority-v1/` — the
  OCR ensemble path 3 swap to `gemma-4-26b-a4b-vision` (used by
  the per-subject `extract_syllabus_from_pdf` action).

`Blocked by (hard):` none.

`Extends:`

- [`openspec/specs/oideachais-pipeline/spec.md`](../../specs/oideachais-pipeline/spec.md)
  — adds §A-D Requirements to the canonical pipeline spec.

`Affected repos:` `cianfhoghlaim` (this repo only; no sister-side
or bonneagar changes in Phase 1).

## Out of scope

- Wholesale copy of `gemini_hackathon/` — lifted selectively per
  the operator's earlier directive (deeply-per-sister-repo
  customisation, NOT wholesale copies).
- A2UI catalog v1 (the 11-component catalog) — Phase 2.
- Web consolidation (5 apps → 1) — Phase 3.
- NCCE learning-graph showcase — Phase 4.
- BAML + CocoIndex + DLT hardening (soft cut) — Phase 5.
- Voice/TTS oral delivery — Phase 6 (Phase 1 ships the stub).
- LC/JC certificate pipeline — Phase 7.
- Sister-side mirrors — Phase 8 (the 5 sister-side umbrella
  mirrors are *promoted to dated* in Phase 0 but their per-PR
  work lives in Phase 8).
- GCP opt-in completion — Phase 9.
- The 4 deferred subjects (geography, english, applied
  mathematics, biology) — Phase 5 broadens to 8 NCCA subjects.

## Quality gates (must pass before `openspec archive`)

```bash
mise run openspec:validate 2026-09-01-cianfhoghlaim-nua-end-to-end-showcase-v1 --strict
mise run lint:registry
mise run lint:skills
mise run lint:baml-fallbacks
mise run lint:drift-docs
pytest tests/test_adk_subject_actions.py -v
dg list assets 2>&1 | grep -E "lc_extraction|study_plan" | head -10
```

The change CANNOT archive until ALL gates exit 0.

## Cross-cutting quality gates

1. **`openspec validate --strict`** exits 0.
2. **No new TODO / pass stubs** added by §2.{1-5} (the broken
   stubs become real implementations, not new ones).
3. **Convex schema additions are additive** — no
   `study_plans/quest_packs/oral_study_plans` table is removed
   or renamed by this change.
4. **`_legacy/web/<subject>_web.baml`** is deleted only after
   `baml_src/british_isles/_shared/study_plan.baml` passes
   `baml-cli test` for all 4 subjects.

---

*Last updated by build subagent at 2026-09-01.*