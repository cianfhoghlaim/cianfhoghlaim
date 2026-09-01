# Change: BIEP NCCE Showcase v1 — 5 NCCE PDFs + 48 equivalencies + 12 pedagogy principles

> **Status:** AUTHORED + IMPLEMENTED.
>
> **Phase 4 of 10** in the
> [`openspec/plans/2026-09-01-cianfhoghlaim-nua-v6-era-v1.md`](../../plans/2026-09-01-cianfhoghlaim-nua-v6-era-v1.md)
> 10-phase integration of `gemini_hackathon/` learnings back into
> `cianfhoghlaim/`. The phase-by-phase authoring strategy (per
> operator direction 2026-09-01) means Phases 0-3 are already
> shipped.

## Why

The **Google "All Things Agentic" hackathon** (deadline 2026-08-31)
shipped a working NCCE learning-graph showcase into the sister
repo `~/dev/gemini_hackathon/`:
- 5 NCCE PDF artefacts → row × column learning graphs
- 6 per-subject BAML extractors (Computer Science + Mathematics +
  English + Gaeilge + Geography + Chemistry)
- 12 NCCE pedagogy principles (the overlay surface)
- 48 cell-level cross-jurisdiction equivalencies (NCCE ↔ NCCA LC +
  JC + AQA GCSE + A-Level + SQA + WJEC + CCEA + Crown Dependencies)
- The CocoIndex grid-aware PDF converter (`_docling_grid_segmenter`)
- The 11 OFFICIAL_DOC_COLUMNS response schema
- 6 per-subject annotated learning-graph JSONs

This phase lifts the canonical OSS-first version into `cianfhoghlaim/`
(OSS-first per operator direction 2026-09-01 — the GCP-first
implementation stays in the sister repo).

## What was shipped

### §1 — Author the canonical NCCE BAML file (1 file)

- **§1.1** `baml_src/british_isles/uk_ncce/learning_graph.baml` — the
  canonical BIEP lift. Defines:
    - 6 canonical enums: `UKNCCEYearLevel` (Y6-Y11) +
      `UKNCCESubjectSlug` + `LearningGraphSkillType` (KNOWLEDGE,
      SKILL, APPLICATION, REASONING, CREATIVITY, META_COGNITION) +
      `LearningGraphPedagogyPrinciple` (12 principles).
    - 7 canonical output classes: `LearningGraphCell` +
      `LearningGraphRow` + `LearningGraphColumn` +
      `LearningGraphPrerequisite` + `LearningGraph` +
      `PedagogyPrincipleDetail` + `PedagogyOverlay`.
    - 6 per-subject extractors: `ExtractComputerScienceLearningGraph` +
      `ExtractMathematicsLearningGraph` + `ExtractEnglishLearningGraph`
      + `ExtractGaeilgeLearningGraph` + `ExtractGeographyLearningGraph`.
    - 1 pedagogy overlay extractor: `ExtractNCCEPedagogyPrinciples`.
    - 4 BAML test blocks.

### §2 — Author the equivalencies BAML file (1 file)

- **§2.1** `baml_src/british_isles/uk_ncce/equivalencies.baml` — the
  48-cell cross-jurisdiction equivalencies. Defines:
    - 11 jurisdictions: `UK_NCCE` + `IE_NCCA_LC` + `IE_NCCA_JC` +
      `EN_AQA_GCSE` + `EN_AQA_AL` + `SC_SQA_NQ` + `WL_WJEC` +
      `NI_CCEA` + `JE_GSSE` + `GG_GSEG` + `IM_GSMI`.
    - 3 output classes: `EquivalencyCell` + `CrossJurisdictionEquivalency` +
      `EquivalencyGraph`.
    - 1 function: `ExtractCrossJurisdictionEquivalencies`.
    - 1 BAML test block.

### §3 — Lift the CocoIndex grid-aware converter (3 files)

- **§3.1** `cocoindex_flows/_shared/_docling_grid_segmenter.py` —
  the row × column detector (lifted from the sister repo).
- **§3.2** `cocoindex_flows/uk_ncce/learning_graphs_app.py` — the
  canonical grid-aware PDF converter.
- **§3.3** `cocoindex_flows/uk_ncce/__init__.py` + `README.md` —
  package metadata + docs.

### §4 — Lift the 11 NCCE learning-graph JSONs (11 files)

- **§4.1** Copied `data/bi_ep/learning_graphs/uk_ncce_*.json` (11 files)
  from `gemini_hackathon/data/bi_ep/learning_graphs/`.

### §5 — Extend the Convex schema with NCCE tables (1 file)

- **§5.1** `web/packages/db/convex/schema.ts` — adds the
  `ncce_learning_graphs` table with subject + year_level + rows_json
  + columns_json + cells_json + pedagogy_overlay_json +
  equivalencies_json fields. Additive; existing 12 tables untouched.

### §6 — Regenerate baml_client (1 action)

- **§6.1** `uv run baml-cli generate --from baml_src` —
  regenerated `baml_client/` (14 files written). All 7 NCCE
  functions are reachable from runtime.

### §7 — Spec delta (1 file)

- **§7.1** `openspec/changes/2026-09-01-cianfhoghlaim-nua-biep-ncce-showcase-v1/specs/oicelais-pipeline/spec.md`
  — adds 3 new Requirements:
    - "BAML MUST support 6 per-subject NCCE learning-graph extractors"
    - "Convex schema MUST persist NCCE learning-graph rows + equivalencies + pedagogy overlay"
    - "CocoIndex pipeline MUST preserve row × column grid structure"

## Impact

- **Audience:**:** every Cianfhoghlaim user (educators + students +
  researchers + admins).
- **Scope:** 17 new files (~1500 LOC).
- **LOC delta:** +~1500.
- **Risk:** LOW — additive; existing surfaces unchanged.
- **Reversibility:** full — every change can be reverted.

## Dependencies

`Blocked by (soft):`

- `2026-09-01-baml-regeneration-blocker-v1/` — Phase 0.5 (BAML
  regeneration) shipped earlier today. Required for Phase 4's
  BAML files to compile.

`Blocked by (hard):` none.

`Extends:`

- [`openspec/specs/oicelais-pipeline/spec.md`](../../specs/oicelais-pipeline/spec.md)
  — the British Isles Education Pipeline spec — adds 3
  Requirements to the canonical pipeline.

`Affected repos:` `cianfhoghlaim` (this repo only).

## Out of scope

- Wholesale copy of `gemini_hackathon/baml_extracts/` — lifted
  selectively per the operator's earlier directive (deeply-per-
  sister-repo customisation, NOT wholesale copies).
- Wholesale copy of `gemini_hackathon/cocoindex_flows/uk_ncce/` —
  simplified (OSS-first; no GCP dependency).
- Wholesale copy of `gemini_hackathon/data/bi_ep/learning_graphs/`
  — only the canonical 11 JSONs are lifted; the per-subject
  annotated JSONs are lifted in Phase 5 (BAML/CocoIndex hardening).
- Wholesale copy of `gemini_hackathon/orchestration/` — Phase 5
  widens the Dagster asset set.
- Phase 5 (BAML/CocoIndex/DLT hardening) — soft cut + sister-
  mirror first per operator direction.
- Phase 6 (oral study plans) — Phase 4 doesn't depend on it.

## Quality gates (must pass before `openspec archive`)

```bash
uv run openspec validate 2026-09-01-cianfhoghlaim-nua-biep-ncce-showcase-v1 --strict
uv run baml-cli generate --from baml_src                       # 14 files written
uv run baml-cli check                                          # 0 errors
uv run python -c "from baml_client.baml_client.sync_client import b; print(b.ExtractComputerScienceLearningGraph)"  ✅
uv run pytest tests/test_adk_subject_actions.py -v              # 11 passed
```

---

*Last updated by build subagent at 2026-09-01.*