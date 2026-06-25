---
title: 'Deploy Plan 04 — Immersive Multi-Modal Content Generation'
domain: deploy-plan
status: draft
description: 'Dagster-generated flashcard packs + Marimo notebooks, derived from cross-border curriculum alignment between GCSE and Junior Cycle. BAML extractors emit granular concepts; litellm synthesises content; the assets land in DuckLake + MotherDuck.'
read_when:
  - 'designing Dagster content-generation assets'
  - 'extending Marimo notebook templates'
  - 'mapping cross-border curriculum outcomes'
supersedes: []
superseded_by: []
related_specs:
  - oideachais-pipeline
  - curriculum-ingestion
  - knowledge-graph
related_apps:
  - sruth/oideachais/dagster_defs
  - sruth/oideachais/baml_src
  - sruth/meaisinfhoghlaim/agents/content_synth
  - sruth/oideachais/notebooks
related_llm_stack:
  - 'BAML (curriculum concept extraction)'
  - 'litellm (multi-modal: text + image + code)'
  - 'mlflow (asset versioning)'
truth: sole
last_touched: 2026-06-13
---

# Deploy Plan 04 — Immersive Multi-Modal Content Generation

## 0. Why this plan

Replace the original Tangent 4 framing (which leaned on Manim for
visual flashcards and Marimo Pyodide for delivery) with a deploy plan
grounded in the existing **Dagster asset graph** and **BAML
extraction** discipline. The goal is an **active synthesis engine**
that takes the cross-border curriculum (Deploy Plan 01 + 02) and
emits:

- **Visual flashcard packs** (`.apkg` / Anki + web JSON)
- **Interactive Marimo notebooks** (`.py` with `mo.ui.*` elements)
- **Marimo Dives** published to MotherDuck

…all aligned to the specific GCSE / Junior Cycle / Leaving Cert
outcomes the learner is enrolled in.

## 1. Monorepo grounding

| Asset | Path | Use |
|:--|:--|:--|
| Quadrant | `sruth/oideachais/` | Dagster orchestration, BAML extraction, DLT sources |
| Quadrant | `sruth/meaisinfhoghlaim/` | LLM stack, OCR, content synth agents |
| Skill | `.agents/skills/dagster/SKILL.md` | SDA patterns, partitions, sensors |
| Skill | `.agents/skills/baml/SKILL.md` | Concept extraction |
| Skill | `.agents/skills/marimo/SKILL.md` | Marimo notebook assembly |
| Skill | `.agents/skills/mlflow/SKILL.md` | Asset versioning |

The 5-quadrant topology is in `docs/00-core/CLAUDE.md` §QUADRANT_MAP.

## 2. The cross-border mapping (input)

This plan **consumes** the output of Deploy Plan 01
(`CrossNationCurriculumSpec` rows) and Deploy Plan 02 (`LearningOutcome`
graph). Specifically:

```
oideachais_equivalence.equivalence_assertion  -- from Deploy Plan 01
oideachais_curriculum.learning_outcome        -- from Deploy Plan 02
oideachais_terminology.bilingual_term         -- from Deploy Plan 02
        │
        ▼
cross_border_concept_node                      -- NEW (this plan)
        │
        ▼
generated_flashcard / generated_marimo        -- NEW (this plan)
```

The `cross_border_concept_node` is the **atom** of generation. It
captures the concept + its aligned qualifications + the BAML-extracted
"bridges" between GCSE and Junior Cycle treatments.

## 3. `cross_border_concept_node` (BAML schema)

```baml
class CrossBorderConceptNode {
  concept_id string
  topic_en string
  topic_target string                         // ga|cy|gd|null
  // Three-way classification per Deploy Plan 01 §2.1:
  coverage CrossBorderCoverage
  // Per-cohort detail:
  roi_outcome LearningOutcomeRef?            // Junior Cycle / Leaving Cert
  uk_outcome LearningOutcomeRef[]            // GCSE / A-Level (one per nation)
  // The "bridge" content that needs generating:
  gap_assets GapAssetSpec[]
  // Provenance
  equivalence_anchor string                  // id of the EquivalenceAssertion
  last_extracted timestamp
}

enum CrossBorderCoverage {
  Overlap                                  // both curricula cover this identically
  DivergenceStrong                         // UK adds material ROI doesn't cover
  DivergenceSoft                           // both cover but with different emphasis
  RoiOnly
  UkOnly
}

class GapAssetSpec {
  asset_kind string                          // "flashcard" | "marimo" | "diagram" | "narrative"
  cohort_roi bool
  cohort_uk bool
  scaffold_level int                         // 1..5 (1=most scaffolded)
  bloom_target string                        // remember|understand|apply|...
}
```

The BAML extractor lives at
`sruth/oideachais/baml_src/cross_border_concept.baml` and runs as a Dagster
asset: `cross_border_concepts.extracted`.

## 4. Dagster asset lineage

```text
raw_curriculum_data                  (existing dlt source — 8 nations)
        │
        ▼
curriculum_spec_normalized           (existing)
        │
        ▼
learning_outcome_nodes               (Deploy Plan 02)
        │
        ▼
equivalence_assertion                (Deploy Plan 01)
        │
        ▼
cross_border_concept_node            (this plan — NEW asset)
        │
        ├──→ gap_asset_manifest
        │           │
        │           ├──→ generated_flashcard    (this plan — NEW)
        │           ├──→ generated_marimo       (this plan — NEW)
        │           └──→ generated_diagram      (this plan — NEW)
        │
        └──→ published_to_dive                   (MotherDuck Dive)
```

The full SDA definitions live in
`sruth/oideachais/dagster_defs/assets/content_generation_assets.py` (new file).

## 5. Flashcard generator (BAML + litellm)

Per `GapAssetSpec { asset_kind: "flashcard" }`:

1. **Q&A synthesis** (BAML):
   ```baml
   class FlashcardQA {
     front string
     back string
     hint string?
     example_target string?           // ga|cy|gd
     mnemonic string?
   }
   ```
2. **Diagram synthesis** (litellm → image model):
   - We delegate to `sruth/meaisinfhoghlaim/agents/diagram_synth/`
   - Default: `litellm:openai-gpt-image-1` (or `litellm:flux-pro` if available)
   - Fallback: BAML text-only description + Marimo `matplotlib` diagram
3. **Assembly**:
   - Output formats: Anki `.apkg`, JSON (for the web wallet from Deploy Plan 01)
   - Stored in `motherduck.oideachais_content.flashcard_pack`

The Marimo notebook `sruth/oideachais/notebooks/flashcard_factory.py`
provides a teacher-facing UI to review and approve packs.

## 6. Marimo notebook generator (BAML + litellm)

Per `GapAssetSpec { asset_kind: "marimo" }`:

1. **Template selection** (BAML):
   - Subject taxonomy → template registry in
     `sruth/meaisinfhoghlaim/agents/content_synth/templates/`
   - Templates: `physics_simulation`, `data_viz`, `algorithm_tracer`,
     `language_scaffolder`, `chemistry_reaction`, `stats_explorer`
2. **Code synthesis** (litellm):
   - Default: `litellm:claude-sonnet` (best code generation)
   - Fallback: `litellm:openai-gpt-4o`
   - Output: complete runnable `.py` file with `marimo` decorations
3. **Interactivity injection** (post-processing):
   - Automatically wrap numeric literals with `mo.ui.slider`
   - Add `mo.ui.text` for free-form variables
   - Insert bilingual glossary sidebars (from Deploy Plan 02)
4. **Validation**:
   - Each generated notebook is **executed** in a sandboxed subprocess
   - Failure → regenerates with the error log appended to the prompt
5. **Storage**: `motherduck.oideachais_content.marimo_notebook`

## 7. Multi-modal asset types (v1 + v2)

| Asset | v1 | v2 |
|:--|:--|:--|
| Flashcard | ✅ | ✅ |
| Marimo notebook | ✅ | ✅ |
| Static diagram (image) | ✅ (BAML → image model) | ✅ |
| Interactive diagram (Bokeh/Plotly embedded in Marimo) | — | ✅ |
| Audio (Whisper TTS) | — | ✅ |
| Spaced-repetition schedule (SM-2) | ✅ | ✅ |
| Video explainer (Synthesia) | — | ✅ (out of scope: not open) |

## 8. Front-end delivery

The web app at `sruth/oideachais/web/routes/curriculum.$conceptId.tsx`
renders:

- Flashcard deck (Anki-compatible)
- Marimo notebook (served via WebAssembly — Pyodide — for v1;
  server-side execution for v2 with caching)
- Per-cohort variant (the "GCSE version" vs the "Junior Cycle version"
  of the same concept)

The Marimo Dives are published to MotherDuck and embedded as iframes
per `docs/05-web/frontend-topology.md` §5.

## 9. Phased action plan

| Phase | Scope | Exit criteria |
|:--|:--|:--|
| 0 | `cross_border_concept_node` extractor (BAML) | 90% precision on a 50-concept gold set |
| 1 | Dagster asset lineage wiring (uses Deploy Plan 01 + 02 outputs) | `dg asset list` shows full graph |
| 2 | Flashcard generator (BAML + image) | 100 flashcard packs generated for 1 pilot subject |
| 3 | Marimo notebook generator (BAML + litellm) | 5 valid notebooks per concept (10 concepts) |
| 4 | Teacher review UI (Marimo) | 5 teachers approve 50 flashcard packs |
| 5 | Web app delivery route | 50 students use it in a 4-week pilot |

## 10. Risks and mitigations

| Risk | Mitigation |
|:--|:--|
| LLM hallucination of facts | All content is grounded in BAML-extracted outcomes; if no outcome matches, the generator emits a "no content" sentinel |
| Visual diagram bias / stereotypes | Use BAML to specify the visual style; image model is given `style_anchors: ["neutral", "geometric", "scientific"]` |
| Marimo notebook runtime errors | Sandboxed execution + auto-retry with the error in the prompt |
| Cost (image generation is expensive) | v1 only generates diagrams for `coverage = DivergenceStrong` (the high-value gap) |

## 11. Out of scope (deferred)

- Live classroom mode (multi-student notebooks) — v3
- Mobile-first delivery — v2
- Teacher co-authoring UI (drag-and-drop builder) — v2

## 12. Cross-references

- `docs/00-core/CLAUDE.md` — 5-quadrant topology
- `docs/02-data-platform/STORAGE.md` — DuckLake writes
- `docs/04-ai-ml/llm-stack-hierarchy.md` — BAML + litellm ordering
- `docs/05-web/frontend-topology.md` — Marimo Dive delivery
- `openspec/specs/oideachais-pipeline/spec.md`
- `openspec/specs/curriculum-ingestion/spec.md`
- `openspec/specs/knowledge-graph/spec.md`
- `.agents/skills/dagster/SKILL.md`
- `.agents/skills/baml/SKILL.md`
- `.agents/skills/marimo/SKILL.md`
- `.agents/skills/mlflow/SKILL.md`
