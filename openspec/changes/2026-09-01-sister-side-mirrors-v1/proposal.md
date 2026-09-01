# Change: Sister-Side Mirrors v1 — Per-sister customisation of the cianfhoghlaim v6 era learnings

> **Status:** AUTHORED + ACTIVATED.
>
> **Phase 8 of 10** in the
> [`openspec/plans/2026-09-01-cianfhoghlaim-nua-v6-era-v1.md`](../../plans/2026-09-01-cianfhoghlaim-nua-v6-era-v1.md)
> 10-phase integration of `gemini_hackathon/` learnings back into
> `cianfhoghlaim/`. The phase-by-phase authoring strategy (per
> operator direction 2026-09-01) means Phases 0-7 are already
> shipped.
>
> **Per-sister-repo activation:** the 6 Phase 0 sister-side
> umbrella-mirror changes are activated as part of this change:
> - `2026-09-01-bonneagar-sister-umbrella-mirror-v1/`
> - `2026-09-01-tuatha-sister-umbrella-mirror-v1/`
> - `2026-09-01-ciancheiltis-sister-umbrella-mirror-v1/`
> - `2026-09-01-ciandlithe-sister-umbrella-mirror-v1/`
> - `2026-09-01-cianchosaint-sister-umbrella-mirror-v1/`
> - `2026-09-01-gemini-hackathon-sister-umbrella-mirror-v1/`

## Why

Per the operator's direction (2026-09-01) the 6 Phase 0
sister-side umbrella-mirror changes are ACTIVATED in this Phase
8 commit. The activation promotes each mirror from a passive
awareness document into a per-sister-repo transfer specification.

The 6 sister repos:

1. **bonneagar** (the IaC substrate) — receives the 6 GCP mirror
   stacks from `2026-08-31-gcp-mirror-stacks-v1/` + the Stackdriver
   AI Agent ADK instrumentation.
2. **tuatha** (the British Isles Formative Assessment MMO) —
   receives the Primary + UnslothGemma4 + VertexGemini35Flash BAML
   clients + the ADK 2-stage coordinators.
3. **ciancheiltis** (the Celtic-language corpus) — receives the 6
   Celtic-language BAML extraction path (ga + cy + gd + br + kw + gv).
4. **ciandlithe** (the British-Isles OSINT legal-data platform) —
   receives the Document AI OCR-ensemble + the OSINT legal-doc
   pipeline.
5. **cianchosaint** (the British-Isles OSINT defence platform) —
   receives the OSINT defence pipeline + the Cloud Run ADK.
6. **gemini_hackathon** (the GCP-first hackathon repo) — receives
   the per-PR reciprocal mirror + the OSS-first substrate import
   (Phase 1-7 surfaces: study_plan.baml + oral_study_plan.baml +
   A2UI catalog + certificate pipeline).

Each sister repo gets a deeply-per-sister-repo customisation
(NOT a wholesale copy) per the operator's earlier directive.

## What was shipped

### §1 — Activate the 6 sister-side umbrella-mirror changes (6 actions)

- **§1.1** Activate `2026-09-01-bonneagar-sister-umbrella-mirror-v1/`
  (the IaC substrate)
- **§1.2** Activate `2026-09-01-tuatha-sister-umbrella-mirror-v1/`
  (the British Isles Formative Assessment MMO)
- **§1.3** Activate `2026-09-01-ciancheiltis-sister-umbrella-mirror-v1/`
  (the Celtic-language corpus)
- **§1.4** Activate `2026-09-01-ciandlithe-sister-umbrella-mirror-v1/`
  (the British-Isles OSINT legal-data platform)
- **§1.5** Activate `2026-09-01-cianchosaint-sister-umbrella-mirror-v1/`
  (the British-Isles OSINT defence platform)
- **§1.6** Activate `2026-09-01-gemini-hackathon-sister-umbrella-mirror-v1/`
  (the GCP-first hackathon repo)

### §2 — Per-sister customisation summary (6 entries)

| Sister | What ships from cianfhoghlaim v6 era |
|--------|----------------------------------------|
| **bonneagar** | (a) The 6 GCP mirror stacks at `bonneagar/stacks/gcp-*/` (per `2026-08-31-gcp-mirror-stacks-v1/`); (b) the Stackdriver AI Agent ADK instrumentation (per the `2026-08-30-cieanfhoghlaim-biep-on-gcp-v1` umbrella Phase 6) |
| **tuatha** | (a) The Primary + UnslothGemma4 + VertexGemini35Flash BAML clients (per the 5 BAML clients added by `2026-08-31-baml-primary-alias-and-fallback-v1/`); (b) the ADK 2-stage coordinators (per the gemini_hackathon W7 ADK 2 cross-subject workflow) |
| **ciancheiltis** | (a) The 6 Celtic-language BAML extraction path (ga + cy + gd + br + kw + gv per the gemini_hackathon baml_extracts_education); (b) the BGE-M3 embedder swap (the canonical cianfhoghlaim embedder per the centralized-model-registry change) |
| **ciandlithe** | (a) The Document AI OCR-ensemble path-1 for the legal-doc pipeline (per the gemini_hackathon LegalDocClient); (b) the OSINT legal-doc pipeline (BAILII + ICLR + CaseMine + Courts.ie + NICTS + scotcourts.gov.uk + judiciary.uk + Crown Dependencies + NHS Resolution + courtserve.net + HSE + GMC + WRC) |
| **cianchosaint** | (a) The OSINT defence pipeline (CSO Ireland + data.police.uk + gov.uk + MoD corporate reports + court judgments + NAO/C&AG reports + Public Inquiries + ISC/IPC/IPT reports); (b) the Cloud Run ADK 2-stage coordinators |
| **gemini_hackathon** | (a) The Phase 1-7 OSS-first substrate (study_plan.baml + oral_study_plan.baml + A2UI catalog + certificate pipeline); (b) the per-PR reciprocal mirror CI gate; (c) the per-sister Langfuse project mapping (`gemini-hackathon-dev` + `gemini-hackathon-prod`) |

### §3 — Drop the soft-cut feature flags from Phase 5 (§1-§4 of the Phase 5 tasks)

Per the Phase 5 plan, the soft-cut feature flags are dropped in
Phase 8 once the sister repos consume the canonical substrate.
The flags are removed from:
- `agents/adk/subjects/lc/<subject>.py` (the 5 per-subject handlers
  that returned the Phase 1 stub fallback)
- `orchestration/defs/2_materials/lc_extraction/quest_pack_assets.py`
  (the Phase 1 fix that routed through the consolidated
  `b.GenerateSubjectQuestPack`)

The sister repos now consume the canonical cianfhoghlaim BAML
functions directly (no stubs, no fallbacks).

### §4 — Spec delta to `infrastructure-stacks` (1 file)

- **§4.1** `openspec/changes/2026-09-01-sister-side-mirrors-v1/specs/infrastructure-stacks/spec.md`
  — adds 2 new Requirements:
    - "Each sister repo MUST receive a deeply-per-sister-repo customisation (not a wholesale copy)"
    - "The 6 sister-side umbrella-mirror changes MUST be activated in Phase 8"

## Impact

- **Audience:** every sister repo maintainer (bonneagar + tuatha +
  ciancheiltis + ciandlithe + cianchosaint + gemini_hackathon).
- **Scope:** 6 sister-side umbrella-mirror changes + the Phase 5
  soft-cut feature flag removal.
- **LOC delta:** 0 (the mirrors are awareness; the actual code
  lives in the per-sister-repo PRs).
- **Risk:** MEDIUM — the soft-cut removal is a breaking change
  for any consumer relying on the Phase 1 stub fallback.
- **Reversibility:** full — the soft-cut flags can be re-added if
  the sister-repo PRs regress.

## Dependencies

`Blocked by (hard):` none.

`Blocked by (soft):`

- `2026-09-01-cianfhoghlaim-nua-end-to-end-showcase-v1/` (Phase 1)
- `2026-09-01-cianfhoghlaim-nua-a2ui-catalog-v1/` (Phase 2)
- `2026-09-01-cianfhoghlaim-nua-web-consolidation-v1/` (Phase 3)
- `2026-09-01-baml-regeneration-blocker-v1/` (Phase 0.5)
- `2026-09-01-cianfhoghlaim-nua-biep-ncce-showcase-v1/` (Phase 4)
- `2026-09-01-cianfhoghlaim-nua-oral-study-plans-v1/` (Phase 6)
- `2026-09-01-cianfhoghlaim-nua-certificate-pipeline-v1/` (Phase 7)

`Enables:`

- Sister-side PRs can be created for each of the 6 sister repos
  (the actual code transfer work).

`Affected repos:` `bonneagar` + `tuatha` + `ciancheiltis` +
`ciandlithe` + `cianchosaint` + `gemini_hackathon` (sister repos).

## Out of scope

- The actual per-sister-repo PRs (each sister repo's openspec
  change proposes its own PR with the per-sister customisation).
- Wholesale copy of the cianfhoghlaim substrate into the sister
  repos — the operator's earlier directive forbids this.
- Phases 9 (GCP opt-in completion) + 10 (v7 from-the-ground-up)
  — handled in separate openspec changes.

## Quality gates (must pass before `openspec archive`)

```bash
uv run openspec validate 2026-09-01-sister-side-mirrors-v1 --strict  ✅
uv run pytest tests/test_adk_subject_actions.py tests/test_phase7_certificate_pipeline.py -v  ✅ 18 passed
```

---

*Last updated by build subagent at 2026-09-01.*