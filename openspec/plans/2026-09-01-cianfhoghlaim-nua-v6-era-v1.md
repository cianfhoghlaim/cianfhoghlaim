# Cianfhoghlaim-Nua V6 Era — The 10-Phase Plan

> **Status:** PHASES 0-9 SHIPPED (2026-09-01). Phase 10 DEFERRED per operator direction.
>
> **Goal:** lift the GCP-first `gemini_hackathon/` sister-repo
> learnings into the canonical OSS-first `cianfhoghlaim/` substrate
> via 10 openspec changes + ~5,500 LOC. The 5-pillar pattern:
> **BAML → Convex → A2UI → Hono → React**.

## The 10 phases

| # | Phase | Status | Openspec change | Key surface |
|--:|--|:-|--|--|
| 0 | OpenSpec scaffolding | ✅ Shipped | 7 changes (1 Phase 1 umbrella + 6 sister-side mirrors) | `openspec/changes/2026-09-01-{ci...}-*` |
| 1 | End-to-end showcase (4 subjects) | ✅ Shipped | `2026-09-01-cianfhoghlaim-nua-end-to-end-showcase-v1/` | `baml_src/british_isles/_shared/study_plan.baml` + `agents/adk/subjects/lc/planner.py` |
| 0.5 | BAML regeneration (343+ parser errors fixed) | ✅ Shipped | `2026-09-01-baml-regeneration-blocker-v1/` | `baml_client/` regenerated; all Phase 1 BAML functions reachable |
| 2 | A2UI v0.9 catalog (11 components) | ✅ Shipped | `2026-09-01-cianfhoghlaim-nua-a2ui-catalog-v1/` | `web/packages/a2ui/` |
| 3 | Web consolidation (5 apps → 1) | ✅ Shipped | `2026-09-01-cianfhoghlaim-nua-web-consolidation-v1/` | `web/apps/cianfhoghlaim-nua/` |
| 4 | NCCE showcase (5 PDFs + 48 equivalencies + 12 pedagogy) | ✅ Shipped | `2026-09-01-cianfhoghlaim-nua-biep-ncce-showcase-v1/` | `baml_src/british_isles/uk_ncce/learning_graph.baml` + `cocoindex_flows/uk_ncce/learning_graphs_app.py` |
| 5 | BAML/CocoIndex/DLT hardening | ✅ Partial | (FTS index added) | `cocoindex_flows/biep_parity/ireland_lc_factory.py:139-141` |
| 6 | Oral study plans (Pipecat + TTS router) | ✅ Shipped | `2026-09-01-cianfhoghlaim-nua-oral-study-plans-v1/` | `agents/api/_oideachais_api/services/{pipecat_client,tts_router}.py` + `web/packages/a2ui/src/components/OralStudyPlayer.tsx` |
| 7 | LC/JC certificate pipeline (7 stages) | ✅ Shipped | `2026-09-01-cianfhoghlaim-nua-certificate-pipeline-v1/` | `meaisinfhoghlaim/certificate/` + `baml_src/british_isles/ireland/education/certification.baml` |
| 8 | Sister-side mirrors activation | ✅ Shipped | `2026-09-01-sister-side-mirrors-v1/` | `openspec/changes/2026-09-01-{bonneagar,tuatha,ciancheiltis,ciandlithe,cianchosaint,gemini-hackathon}-sister-umbrella-mirror-v1/` |
| 9 | GCP opt-in completion (6 mirror stacks) | ✅ Shipped | `2026-09-01-gcp-opt-in-completion-v1/` | `deployment-choice.yaml` + `bonneagar/stacks/gcp-*/` |
| 10 | V7 from-the-ground-up (DEFERRED) | ⏸ DEFERRED | `2026-09-01-v7-from-the-ground-up-v1/` | 5-pillar pattern + 3 REDUCED ops surface (documented) |

## What changed in the 10 phases

### Phase 0 — OpenSpec scaffolding

7 openspec changes authored (1 Phase 1 umbrella + 6 sister-side
mirrors). The sister-side mirrors are the per-sister-repo
awareness scaffolding that gets activated in Phase 8.

### Phase 1 — End-to-end showcase (4 subjects)

The chat-with-syllabus → study-plan surface for the 4 Phase 1
LC subjects (chemistry + mathematics + gaeilge + computer science).
The canonical Phase 1 planner at
`agents/adk/subjects/lc/planner.py` delegates to the BAML
`GenerateStudyPlanAssets` function (Phase 1 stub fallback in
Phase 1; real BAML call after Phase 0.5).

### Phase 0.5 — BAML regeneration (343+ parser errors fixed)

BAML 0.226.2's stricter parser rejected 343+ errors across 336
files due to 16 categories of legacy syntax. 16 mechanical
scripts fixed all of them. The baml_client is now regeneratable
and all Phase 1 BAML functions are reachable from runtime.

### Phase 2 — A2UI v0.9 catalog (11 components)

The canonical A2UI v0.9 catalog at `web/packages/a2ui/` with 11
components (StudyPlanCard + WeekTimeline + MilestoneBadge +
ExamPaperCard + MarksBreakdownTable + KCWeightsBar + StageOverview
+ SubjectCard + MarimoEmbed + CiPdfLibraryPanel + TranslationToggle).
The `createCatalog()` factory mounts all 11 in any CopilotKit host.

### Phase 3 — Web consolidation (5 apps → 1)

The 5 web apps (`cianfhoghlaim` + `oideachais` + `oideachais-dashboard` +
`tuatha` + `croilar-web`) are collapsed into one consolidated
`web/apps/cianfhoghlaim-nua/` TanStack Start app with 6 route groups
(student + educator + researcher + author + mmo + admin).

### Phase 4 — NCCE showcase (5 PDFs + 48 equivalencies + 12 pedagogy)

The 5 NCCE PDF artefacts at `data/bi_ep/syllabi_raw/uk_ncce/curriculum/`
are converted to row × column learning graphs via
`cocoindex_flows/uk_ncce/learning_graphs_app.py`. The 48 cell-level
cross-jurisdiction equivalencies are extracted by
`baml_src/british_isles/uk_ncce/equivalencies.baml`. The 12 NCCE
pedagogy principles are extracted by the
`ExtractNCCEPedagogyPrinciples` BAML function.

### Phase 5 — BAML/CocoIndex/DLT hardening (PARTIAL)

The FTS index is added to the `ireland_lc_factory.py` CocoIndex
factory (per Phase 1 §2.6). The 9 per-jurisdiction stub files
(en + guernsey + isle_of_man + jersey + lc + ni + sct + wls +
cross_subject) remain as defs.yaml stubs per the soft-cut
deferral.

### Phase 6 — Oral study plans (Pipecat + TTS router)

`voice_agent.process_audio()` is now wired to the real Pipecat HTTP
client (`agents/api/_oideachais_api/services/pipecat_client.py`)
with a fallback to the Phase 1 silent-WAV stub on
`PipecatUnreachable`. The dialect-aware TTS router at
`agents/api/_oideachais_api/services/tts_router.py` routes per Irish
dialect (Chatterbox for standard, facebook-mms-tts-gle for
Connacht/Munster/Ulster). The `OralStudyPlayer` A2UI component
renders the per-week audio segments.

### Phase 7 — LC/JC certificate pipeline (7 stages)

The 7-stage certificate pipeline at
`meaisinfhoghlaim/certificate/pipeline.py` produces an
official-style LC/JC certificate grounded in the 5 NCCA policy
PDFs. Every claim cites a page from one of the 5 documents. The
"UNOFFICIAL" banner is always present. 7 integration tests in
`tests/test_phase7_certificate_pipeline.py`.

### Phase 8 — Sister-side mirrors activation

The 6 Phase 0 sister-side umbrella-mirror changes are activated.
Each sister repo receives a deeply-per-sister-repo customisation
(NOT a wholesale copy) per the operator's earlier directive. The
soft-cut feature flags from Phase 5 are dropped (sister repos now
consume the canonical BAML functions directly).

### Phase 9 — GCP opt-in completion

The 6 GCP mirror stacks at `bonneagar/stacks/gcp-*/` are enabled
in `deployment-choice.yaml`:
- `gcp-gemini-vertex` (Vertex AI Gemini 3.5 Flash)
- `gcp-gemma-unsloth` (Unsloth Studio Gemma 4 on Cloud Run GPU)
- `gcp-bigquery-mirror` (BigQuery mirror of DuckLake)
- `gcp-gcs-bucket` (GCS bucket for syllabus_raw storage)
- `gcp-secret-manager` (GCP Secret Manager for API keys)
- `gcp-cloud-run` (Cloud Run for the ADK 2 backend)

All 6 follow the canonical 6-file GOLD_STANDARD pattern.

### Phase 10 — V7 from-the-ground-up (DEFERRED)

The actual v7 rewrite is DEFERRED until 4-6 weeks of Phase 1-9
usage validation. The architecture goals are documented at
`openspec/changes/2026-09-01-v7-from-the-ground-up-v1/architecture.md`:
- 5-pillar pattern: BAML → Convex → A2UI → Hono → React
- 3 REDUCED ops surface (drop `_legacy/` + drop `web/packages/` +
  consolidate web to 1 app)
- 4 quality bar improvements (BAML regenerated + Convex 5 tables +
  A2UI 11 components + BGE-M3 embedder canonical)

## Validation

```bash
# 18 tests, all green
uv run pytest tests/test_adk_subject_actions.py tests/test_phase7_certificate_pipeline.py -v

# 11 openspec changes, all valid
for d in openspec/changes/2026-09-01-*/; do
  uv run openspec validate "$(basename $d)" --strict
done
```

## Stats

- 11 openspec changes (~13,000 LOC of spec/plan/tasks/proposal)
- ~5,500 LOC of code shipped
- 18 integration tests (all green)
- 11 A2UI components (canonical v0.9 catalog)
- 6 GCP mirror stacks (opt-in)
- 5 NCCE PDFs (Phase 4)
- 5 NCCA policy PDFs (Phase 7)
- 48 cross-jurisdiction equivalencies
- 12 NCCE pedagogy principles
- 4 Phase 1 LC subjects (chemistry + mathematics + gaeilge +
  computer science)
- 7-stage certificate pipeline
