## Deferred — Separate Celtic language campaign (not part of active ops cleanup)

This change is **deferred indefinitely**. The 5 done tasks are the foundation
(Celtic language registration + Gaeilge basic pipeline). The remaining 94 tasks
across the 6 Celtic language streams (Scottish Gaelic, Welsh, Cornish, Manx,
Breton, Cornish) require dedicated content sourcing + translation model wiring
+ per-language curriculum sources — a multi-week campaign separate from the
cleanup waves.

The Celtic asset generation spec at `openspec/specs/celtic-asset-generation/spec.md`
provides the framework; this change can be reopened when the Celtic language
sourcing campaign starts.
# 2026-07-17-gaois-celtic-language-pipeline-v1

## Why

The `dlt/language/` subtree ships 25 DLT source files across 7 source groups
(Gaois APIs, Dúchas, Heritage, Canuint, Universal Dependencies Celtic
treebanks, Local documents by subject, Celtic curriculum/morphology/grammar),
but the integration layer stops at the DLT ingestion stage. None of these
sources has:

- CocoIndex v1 App (R1-R4 conformance contract)
- Dagster 5-layer asset graph (1_ingestion / 2_materials / 3_model_lifecycle / 4_asset_generation / 5_agent_ops)
- BAML extraction functions for the under-served sources (Dúchas = 0 fns, Celtic curriculum = 0 fns)
- MotherDuck Dive + Flight for analytics + daily sync
- Marimo notebooks sampling each source type
- DuckLake + S3 destination writes (the existing DLT targets run in-process; no S3 staging)

By contrast, the Irish education pipeline (`british-isles-education-pipeline`)
ships all 5 layers for the 6 BIEP priority LC subjects and the 5 educational
stages (Aistear, Primary, Junior Cycle, Senior Cycle, Tertiary).

This change brings the 7 language/ source groups to the same integration
level as the Irish education pipeline, **plus** adds the bounding-box
layout alignment (page → region → sentence → word → letter with
transcripts) for the Dúchas handwritten manuscript pipeline that the
Irish education pipeline doesn't have.

## What changes

### 1. New umbrella spec `celtic-language-pipeline`

Adds `openspec/specs/celtic-language-pipeline/spec.md` as the canonical
spec for the Gaois + Celtic language pipeline. 7 Requirements (one per
source group) + 7 Scenarios.

### 2. Re-activation of 2 ARCHIVED BAML files

`baml/celtic/grammar_patterns.baml` + `baml/celtic/morphology.baml`
were archived 2026-06-24 because they had no Python consumer. This
change:

- Moves both files back from `baml/celtic/_archive/` to `baml/celtic/`
  and removes the ARCHIVED header.
- Adds the canonical consumer agents:
  - `meaisinfhoghlaim/agents/celtic_grammar.py`
  - `meaisinfhoghlaim/agents/celtic_morphology.py`
- Re-enables all 6 grammar fns + 4 morphology fns as wired.

### 3. 6 new BAML extraction functions

| Function | File | Purpose |
|:--|:--|:--|
| `ExtractDuchasManuscript(xml_record)` | `baml/celtic/gaois/duchas.baml` | Parse Dúchas XML → structured record |
| `ExtractDuchasImageBoundingBox(image_path, transcript)` | `baml/celtic/gaois/duchas.baml` | 5-level bbox alignment for handwritten manuscript |
| `ExtractDuchasTranscription(handwritten_image)` | `baml/celtic/gaois/duchas.baml` | Vision-model OCR for manuscript page |
| `ExtractCelticCurriculum(text, language)` | `baml/celtic/curriculum/celtic_curriculum.baml` | Celtic-language curriculum extraction |
| `ExtractCelticGrammar(text, language)` | `baml/celtic/grammar_patterns.baml` | Grammar pattern extraction (re-activated) |
| `ExtractCelticMorphology(text, language)` | `baml/celtic/morphology.baml` | Verb conjugation + noun declension (re-activated) |

### 4. 7 new CocoIndex v1 Apps (R1-R4 conformant)

| App | LanceDB table | LlamaSwap routing |
|:--|:--|:--|
| `gaois_embedding.py` | `cianfhoghlaim.language.gaois_chunks` | `uccix-mistral-24b` (Irish) / `gemma-4-26B-A4B` (English) |
| `duchas_embedding.py` | `cianfhoghlaim.language.duchas_chunks` (with `duchas_bboxes` child table) | `molmo2-8b` + `dots-ocr` |
| `heritage_embedding.py` | `cianfhoghlaim.language.heritage_chunks` | `gemma-4-26B-A4B` |
| `canuint_embedding.py` | `cianfhoghlaim.language.canuint_chunks` | `qwen3-vl-8b` (audio + text) |
| `ud_celtic_embedding.py` | `cianfhoghlaim.language.ud_celtic_chunks` | `uccix-mistral-24b` (Irish) / `gemma-4-26B-A4B` (Celtic) |
| `local_documents_embedding.py` | `cianfhoghlaim.language.local_documents_chunks` | `qwen3-vl-8b` |
| `celtic_curriculum_embedding.py` | `cianfhoghlaim.celtic.curriculum_chunks` | `uccix-mistral-24b` (Irish) / `gemma-4-26B-A4B` (Welsh/Scottish/Breton) |

Each App uses `BAAI/bge-m3` (1024-d) for embeddings, dispatches through
the canonical OCR/VLM registry (`meaisinfhoghlaim.models.registry`), and
follows the R1-R4 conformance contract.

### 5. 21 new Dagster defs (7 groups × 3 layers)

```
orchestration/defs/
├── 1_ingestion/language/<source>/defs.yaml             # 7 files
├── 2_materials/baml_extraction/language/<source>/_assets.py  # 7 files
└── 3_model_lifecycle/cocoindex_v1/<source>_embedding/defs.yaml  # 7 files
```

### 6. 7 new MotherDuck Dives (page-level summaries for Dúchas)

```
motherduck/dives/
├── gaois_terminology_dive.py
├── duchas_folklore_dive.py              # page-level summaries only (NOT 74M row word-level)
├── heritage_sites_dive.py
├── canuint_dialect_dive.py
├── ud_celtic_dive.py
├── local_documents_dive.py
└── celtic_curriculum_dive.py
```

### 7. 7 new marimo notebooks

```
notebooks/16_celtic_language/
├── 01_gaois_terminology_explorer.py
├── 02_duchas_folklore_with_bboxes.py    # Altair bbox visualization
├── 03_heritage_sites_map.py
├── 04_canuint_dialect_player.py
├── 05_ud_celtic_treebank_viewer.py
├── 06_local_documents_subject_viewer.py
└── 07_celtic_curriculum_browser.py
```

### 8. 1 new shared routing module

`meaisinfhoghlaim/models/routing.py` — the shared LlamaSwap routing table
for the 7 CocoIndex Apps (per-language + per-source routing).

### 9. 1 MODIFIED + 2 MODIFIED spec deltas

- ADDED Requirements on `celtic-language-pipeline/spec.md` (new umbrella)
- MODIFIED delta on `cianfhoghlaim-pipeline/spec.md` (cross-reference)
- MODIFIED delta on `british-isles-education-pipeline/spec.md` (cross-reference)

## Dependencies

```yaml
Affected repos: cianfhoghlaim (single-repo change)
Push target:    origin/pick-4-biep-v1
```

## Acceptance gates

- `openspec validate 2026-07-17-gaois-celtic-language-pipeline-v1 --strict` passes
- All 7 CocoIndex Apps conform to R1-R4 (verified via `cocoindex_v1_conformance`)
- `dg check yaml` passes on all 21 new `defs.yaml` files
- `mise run lint:skills` still passes
- `mise run baml:generate` shows 0 errors (no new BAML parse errors)

## Cross-references

- [`british-isles-education-pipeline`](../../specs/british-isles-education-pipeline/spec.md) — the seed instance of the 5-layer Dagster + CocoIndex + MotherDuck pattern
- [`cianfhoghlaim-cocoindex-v1-migration`](../../specs/cianfhoghlaim-cocoindex-v1-migration/spec.md) — the R1-R4 conformance contract
- [`cianfhoghlaim-baml-schemas`](../../specs/cianfhoghlaim-baml-schemas/spec.md) — the BAML cluster taxonomy
- [`cianfhoghlaim-pipeline`](../../specs/cianfhoghlaim-pipeline/spec.md) — the parent pipeline
- `.agents/skills/dlt/SKILL.md` — DLT conventions
- `.agents/skills/baml/SKILL.md` — BAML schema patterns
- `.agents/skills/cocoindex/SKILL.md` — R1-R4 conformance contract
- `.agents/skills/dagster/SKILL.md` — 5-layer asset architecture
- `.agents/skills/motherduck/SKILL.md` — Dives + Flights + Lakehouse
- `.agents/skills/marimo/SKILL.md` — dual-mode notebook patterns