---
name: cianfhoghlaim-nua-v6-era
description: The Cianfhoghlaim-Nua v6 era (2026-09-01) — the consolidated platform target. Use when working in the consolidated `web/apps/cianfhoghlaim-nua/` app, designing A2UI v0.9 components with `@cianfhoghlaim/a2ui`, wiring the canonical Phase 1 planner at `agents/adk/subjects/lc/planner.py`, calling the Phase 4 NCCE learning-graph extractors at `baml_src/british_isles/uk_ncce/learning_graph.baml`, generating the Phase 7 7-stage certificate pipeline at `meaisinfhoghlaim/certificate/pipeline.py`, or dispatching the Phase 6 Pipecat + dialect-aware TTS router at `agents/api/_oideachais_api/services/pipecat_client.py` + `tts_router.py`. Covers the 5-pillar pattern (BAML → Convex → A2UI → Hono → React), the 11 openspec changes, the 18-test integration suite, and the OSS-first posture (vs the GCP-first `gemini_hackathon/` sister repo). Triggers: 'cianfhoghlaim-nua', 'v6 era', 'Phase 1', 'Phase 4', 'Phase 6', 'Phase 7', 'study plan', 'oral study plan', 'NCCE', 'certificate', 'A2UI catalog', 'createCatalog', 'OralStudyPlayer', 'Pipecat', 'TTS router', 'dialect', 'Chatterbox', 'mms-tts-gle'.
---

# Cianfhoghlaim-Nua V6 Era

The 2026-09-01 refactor that lifts the GCP-first `gemini_hackathon/`
sister-repo learnings into the canonical OSS-first
`cianfhoghlaim/` substrate. The 5-pillar pattern:
**BAML → Convex → A2UI → Hono → React**.

## 11 openspec changes (in `openspec/changes/`)

| # | Change | Key surface |
|--:|--|--|
| 0 | `2026-09-01-cianfhoghlaim-nua-end-to-end-showcase-v1/` | Phase 1 umbrella (38 tasks) |
| 0.1 | `2026-09-01-{bonneagar,tuatha,ciancheiltis,ciandlithe,cianchosaint,gemini-hackathon}-sister-umbrella-mirror-v1/` | 6 sister-side mirrors (Phase 0) |
| 0.5 | `2026-09-01-baml-regeneration-blocker-v1/` | BAML 0.226.2 parser fix (343+ errors) |
| 1 | `2026-09-01-cianfhoghlaim-nua-end-to-end-showcase-v1/` | Phase 1 end-to-end showcase (4 subjects) |
| 2 | `2026-09-01-cianfhoghlaim-nua-a2ui-catalog-v1/` | 11-component A2UI v0.9 catalog |
| 3 | `2026-09-01-cianfhoghlaim-nua-web-consolidation-v1/` | 5 apps → 1 consolidated app |
| 4 | `2026-09-01-cianfhoghlaim-nua-biep-ncce-showcase-v1/` | 5 NCCE PDFs + 48 equivalencies + 12 pedagogy |
| 5 | (partial) FTS index added to `cocoindex_flows/biep_parity/ireland_lc_factory.py:139-141` |
| 6 | `2026-09-01-cianfhoghlaim-nua-oral-study-plans-v1/` | Pipecat + dialect-aware TTS router |
| 7 | `2026-09-01-cianfhoghlaim-nua-certificate-pipeline-v1/` | 7-stage LC/JC certificate pipeline |
| 8 | `2026-09-01-sister-side-mirrors-v1/` | Sister-side mirrors activation |
| 9 | `2026-09-01-gcp-opt-in-completion-v1/` | 6 GCP mirror stacks enabled |
| 10 | `2026-09-01-v7-from-the-ground-up-v1/` | V7 architecture goals (DEFERRED) |

## 5-pillar pattern

```
   BAML           Convex           A2UI           Hono           React
(Phase 1/4/7)  (Phase 1/4)     (Phase 2)     (Phase 1)     (Phase 3)
   ↓               ↓               ↓              ↓              ↓
canonical       5 new tables  11 components  4+ per-subject  1 consolidated
BAML            study_plans    createCatalog  routes         app
functions       quest_packs                                    
                oral_study_plans
                formative_attempts
                audio_segments
                ncce_learning_graphs
```

## Key file paths

| Layer | Path |
|---|---|
| **Phase 1: BAML** | `baml_src/british_isles/_shared/study_plan.baml` (study-plan) + `oral_study_plan.baml` (oral-plan) + `baml_src/british_isles/ireland/education/marking/{chemistry,mathematics,gaeilge,english,geography,computer_science}_marking.baml` |
| **Phase 1: planner** | `agents/adk/subjects/lc/planner.py` (the canonical Phase 1 planner; `generate_study_plan` + the oral stub) |
| **Phase 1: per-subject handlers** | `agents/adk/subjects/lc/{chemistry,mathematics,gaeilge,computer_science}.py::get_study_plan` |
| **Phase 1: Hono routes** | `web/hono-api/src/routes/copilotkit/lc/{chemistry,mathematics,gaeilge,computer_science}.ts::POST /get_study_plan` + `_study_plan_stub.ts` (shared stub helper) |
| **Phase 1: A2UI surface** | `web/apps/oideachais/src/components/study-plan/StudyPlanCard.tsx` (Phase 1) + `web/packages/a2ui/src/components/{WeekTimeline,MilestoneBadge,KCWeightsBar,ExamPaperCard}.tsx` (Phase 2) |
| **Phase 1: Convex schema** | `web/packages/db/convex/schema.ts` (5 new tables) |
| **Phase 1: tests** | `tests/test_adk_subject_actions.py` (11 tests, all green) |
| **Phase 4: NCCE BAML** | `baml_src/british_isles/uk_ncce/learning_graph.baml` (6 per-subject extractors) + `equivalencies.baml` (48 cell-level cross-walks) |
| **Phase 4: CocoIndex** | `cocoindex_flows/uk_ncce/learning_graphs_app.py` + `cocoindex_flows/_shared/_docling_grid_segmenter.py` (grid-aware PDF converter) |
| **Phase 4: Convex schema** | `web/packages/db/convex/schema.ts::ncce_learning_graphs` (Phase 4 addition) |
| **Phase 6: Pipecat** | `agents/api/_oideachais_api/services/pipecat_client.py` (HTTP client) + `agents/api/_oideachais_api/services/tts_router.py` (dialect-aware TTS) |
| **Phase 6: voice agent** | `agents/adk/voice_agent.py` (wired to Pipecat; falls back to silent WAV on PipecatUnreachable) |
| **Phase 6: OralStudyPlayer** | `web/packages/a2ui/src/components/OralStudyPlayer.tsx` |
| **Phase 7: certificate** | `meaisinfhoghlaim/certificate/{types,rubric,pipeline,__init__}.py` + `baml_src/british_isles/ireland/education/certification.baml` |
| **Phase 7: tests** | `tests/test_phase7_certificate_pipeline.py` (7 tests, all green) |
| **Phase 9: GCP opt-in** | `deployment-choice.yaml` (6 GCP stacks enabled) |

## Common workflows

### 1. Check the BAML client is regeneratable + reachable

```bash
# Regenerate the baml_client
uv run baml-cli generate --from baml_src

# Verify the Phase 1 + Phase 4 + Phase 7 functions are reachable
uv run python -c "
from baml_client.baml_client.sync_client import b
# Phase 1
print('GenerateStudyPlanAssets:', hasattr(b, 'GenerateStudyPlanAssets'))
print('GenerateOralStudyPlan:', hasattr(b, 'GenerateOralStudyPlan'))
# Phase 4
print('ExtractComputerScienceLearningGraph:', hasattr(b, 'ExtractComputerScienceLearningGraph'))
# Phase 7
print('ExtractNCCAPolicyCriteria:', hasattr(b, 'ExtractNCCAPolicyCriteria'))
"
```

### 2. Run the integration test suite (18 tests)

```bash
uv run pytest tests/test_adk_subject_actions.py tests/test_phase7_certificate_pipeline.py -v
# 18 passed in ~10s
```

### 3. Run the 7-stage certificate pipeline

```bash
uv run python -c "
import asyncio
from meaisinfhoghlaim.certificate import run_certificate_pipeline
result = asyncio.run(run_certificate_pipeline(
    learner_id='learner-1',
    learner_name='Test',
    subject_slug='chemistry',
    stage='scoil_sinsearach',
    lo_codes=['LC-CHEM-LO-3.1'],
    ncca_policy_pdfs=[('SC-L1-L2-Programme-Statement.pdf', 'Sample NCCA text...')],
))
print(f'PNG: {result.png_bytes[:8]!r}')
print(f'Citations: {len(result.policy_citations)}')
"
```

### 4. Validate the 11 openspec changes

```bash
for d in openspec/changes/2026-09-01-*/; do
  uv run openspec validate "$(basename $d)" --strict
done
```

## OSS-first posture (vs the GCP-first `gemini_hackathon/` sister repo)

- **OSS substrate** (canonical): self-hosted via `mise run stack:up`
  - BGE-M3 embedder (the canonical 1024-d embedder)
  - Convex for persistence
  - TanStack + React for the web layer
  - flux_schnell / fibo for image generation (when available)
- **GCP substrate** (opt-in): the 6 GCP mirror stacks at `bonneagar/stacks/gcp-*/`
  - Vertex AI + Unsloth Studio + BigQuery + GCS + Secret Manager + Cloud Run
  - Enabled via `deployment-choice.yaml` (the canonical deployment-control-panel surface)

The OSS substrate remains canonical per operator direction 2026-09-01.
The GCP substrate is for users who specifically want the managed-cloud
substrate.

## v7 from-the-ground-up (DEFERRED per operator direction)

Per `2026-09-01-v7-from-the-ground-up-v1/`:
- 5-pillar pattern: BAML → Convex → A2UI → Hono → React
- 3 REDUCED ops surface:
  1. Drop `_legacy/`
  2. Drop `web/packages/` (consolidate into `cianfhoghlaim-nua/`)
  3. Consolidate web to 1 app
- 4 quality bar improvements:
  1. BAML client regenerated (Phase 0.5)
  2. Convex schema with 5 new tables (Phase 1 §3.1)
  3. A2UI 11-component catalog (Phase 2)
  4. BGE-M3 embedder canonical

The actual v7 rewrite is DEFERRED until 4-6 weeks of Phase 1-9
usage validation per operator direction.

## Anti-patterns

- Do NOT copy wholesale from `gemini_hackathon/` — the operator's
  earlier directive forbids this. Each sister-repo transfer must be
  a deeply-per-sister-repo customisation.
- Do NOT add GCP-only dependencies to the OSS substrate — the
  canonical substrate must work in lightweight container builds.
- Do NOT use the old `pass # TODO: Pipecat SDK integration` body
  in `voice_agent.py::process_audio` — Phase 6 wires the real
  Pipecat HTTP client. Use the canonical `call_pipecat_roundtrip`.
- Do NOT use `{{ input }}` in BAML prompt bodies — the renamed
  `{{ text }}` (per the Phase 0.5 BAML regeneration) is canonical
  (input is a reserved keyword in BAML 0.226.2+).
- Do NOT use `catch_all` blocks — BAML 0.226.2 removed this directive
  (per the Phase 0.5 fix; 223 files stripped).

## See also

- `openspec/plans/2026-09-01-cianfhoghlaim-nua-v6-era-v1.md` (the
  10-phase plan)
- `openspec/specs/oicelais-pipeline/spec.md` (Phase 4 NCCE specs)
- `openspec/specs/agentic-frontend-frameworks/spec.md` (Phase 2/3/6/7 specs)
- `openspec/specs/agent-memory-systems/spec.md` (Phase 7 spec)
- `openspec/specs/infrastructure-stacks/spec.md` (Phase 8 spec)
- `openspec/specs/deployment-control-panel/spec.md` (Phase 9 spec)
- `openspec/specs/centralized-schema-registry/spec.md` (Phase 0.5 spec)
- `openspec/specs/dev-tooling-surfaces/spec.md` (Phase 10 spec)
- `.agents/skills/agentic-frontend-frameworks/SKILL.md` (the canonical
  A2UI skill)
- `.agents/skills/agent-fleet-orchestration/SKILL.md` (the canonical
  agent fleet skill)
- `.agents/skills/agent-memory-systems/SKILL.md` (the canonical
  memory skill)
- `.agents/skills/agent-observability/SKILL.md` (the canonical
  observability skill)
- `.agents/skills/agentic-frontend-frameworks/SKILL.md` (the canonical
  A2UI skill)
- `.agents/skills/baml/SKILL.md` (the canonical BAML skill)
- `.agents/skills/cocoindex/SKILL.md` (the canonical CocoIndex skill)
- `.agents/skills/openspec/SKILL.md` (the canonical OpenSpec skill)