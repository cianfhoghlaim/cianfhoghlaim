# `cianfhoghlaim/baml/` — BAML cluster taxonomy (v4)

This directory contains the BAML (Basically a Made-up Language) extraction
schemas for the Cianfhoghlaim platform. Per `openspec/changes/baml-reorganize-by-cluster/`,
the files are organised into **3 purpose-driven clusters** with `_shared/`
homes for cross-cluster types.

## Layout

```
baml/
├── clients.baml                  # Canonical LLM clients (LitellmClient, DeepSeekClient,
│                                 # MiniMaxClient, LitellmLongContext, Extractor,
│                                 # vision clients, 2 fallback chains)
├── clients_llama_swap.baml       # Specialty VL clients (LlamaSwapClient + 3 aliases)
│
├── education/                    # CLUSTER 1 — NCCA education
│   ├── _shared/                  # Cross-stage types + functions
│   │   ├── education_level.baml  # 10 enums (RelationshipType, ExamLevel, etc.)
│   │   ├── strand_outcome.baml   # 17 classes (LearningOutcome, ExamPaper, etc.)
│   │   ├── curriculum_relationships.baml  # 4 relationship functions
│   │   ├── subject_rubric.baml   # 4 rubric functions + 5 classes
│   │   └── document_metadata.baml  # 2 document metadata functions
│   ├── stages/                   # 5 NCCA stages — one file per stage
│   │   ├── aistear.baml          # MERGED from 3 sources (aistear + oideachais_other + early_childhood)
│   │   ├── primary.baml          # MERGED from 2 sources
│   │   ├── junior_cycle.baml     # MERGED from 2 sources
│   │   ├── senior_cycle.baml     # MOVED from oideachais_other/
│   │   └── tertiary.baml         # MERGED from 2 sources
│   ├── pdfs/                     # 3 leaving_cert_*_extraction files (renamed)
│   │   ├── leaving_cert_syllabus.baml
│   │   ├── leaving_cert_past_paper.baml
│   │   └── leaving_cert_marking_scheme.baml
│   ├── subjects/                 # 8 qpack_*.baml (per-NCCA-subject quest pack generators)
│   │   ├── qpack_mathematics.baml
│   │   ├── qpack_applied_mathematics.baml
│   │   ├── qpack_chemistry.baml
│   │   ├── qpack_geography.baml
│   │   ├── qpack_history.baml
│   │   ├── qpack_english.baml
│   │   ├── qpack_gaeilge.baml
│   │   └── qpack_computer_science.baml
│   ├── cross_nation/             # 2 British Isles cross-nation files
│   │   ├── isles_education.baml
│   │   └── multi_nation_curriculum.baml
│   ├── statistics/               # 1 file
│   │   └── education_statistics.baml
│   └── university/               # 1 file (per the oideachais-university-deep-extraction spec)
│       └── university_extraction.baml
│
├── celtic/                       # CLUSTER 2 — Celtic / Irish language
│   ├── _shared/                  # (reserved for cross-Celtic types — empty for now)
│   ├── gaois/                    # 4 gaois.ie API extraction layer
│   │   ├── duchas.baml           # Schools Collection + Manuscripts + Photographs + Persons
│   │   ├── logainm.baml          # Placenames database of Ireland
│   │   ├── tearma.baml           # National Terminology Database
│   │   └── folklore_extraction.baml
│   ├── curriculum/                # Celtic-nation curriculum
│   │   ├── celtic_curriculum.baml
│   │   └── mythology_extraction.baml
│   ├── grammar_patterns.baml      # Irish grammar
│   ├── morphology.baml           # Irish morphology
│   ├── sources.baml              # Source-agnostic unified record (renamed from celtic_sources.baml)
│   └── _archive/                 # The 2 archived 2026-06-24 files (per archive-celtic-baml-orphans)
│       ├── celtic_linguistics.baml  # (re-activation procedure documented in the file header)
│       └── cognates.baml            # (re-activation procedure documented in the file header)
│
├── processing/                   # CLUSTER 3 — Generic file processing
│   ├── _shared/                  # (reserved for cross-processing types — empty for now)
│   ├── email.baml                # leabharlann email-triage pipeline
│   ├── upstream_monitoring.baml  # 4 upstream packages (motherduck / dlthub / lancedb / cocoindex)
│   ├── cv_extraction.baml        # CV / achievements / teaching
│   ├── portfolio_extraction.baml # Portfolio
│   ├── linkedin_profile_extraction.baml  # LinkedIn (per croilar personas)
│   ├── researchgate_extraction.baml  # ResearchGate (per croilar) — syntax-fixed
│   ├── artwork_analysis.baml     # Artwork
│   ├── author_archive.baml       # Gemini Deep Research PDF extraction
│   ├── circular_extraction.baml  # Department of Education circulars
│   ├── identity_verification.baml  # Identity docs + Garda vetting
│   ├── audio_extraction.baml     # Canúint audio recordings
│   ├── ocr_extraction.baml       # OCR validation (per meaisinfhoghlaim-ocr-htr)
│   ├── ocr_validation.baml       # OCR vs ground truth
│   ├── image_generation.baml     # FIBO image generation
│   ├── style_transfer.baml       # FIBO style transfer
│   ├── game_content.baml         # MMO game content (NPC, locations, items)
│   ├── player_assessment.baml    # MMO player assessment
│   ├── generators.baml           # MMO FIBO generators
│   ├── culture_extraction.baml   # Culture heritage claims
│   ├── named_entities.baml       # NER
│   ├── site_analysis.baml        # Site analysis
│   ├── official_media.baml       # Official media classification
│   ├── ui_components.baml        # UI component generation
│   └── teaching_extraction.baml  # Teaching CV
│
└── shared/                       # The generated-client home (baml_client/, baml_client_ts/, baml_src/)
```

## What's NOT here (and where it went)

The following dead files have been deleted:

- `baml/educational_clients.baml` (0 callers; clients moved to `clients.baml`)
- `baml/curriculum_extraction_0.baml` (BAML 0.x syntax superseded)
- `baml/oideachas.baml` (typo; 0 callers)
- `baml/oideachais_other/` directory and all 5 files inside (all duplicates of top-level files)
- `baml/_croilar_src` (dead circular symlink to `baml/`)

The following files have been merged:

- `aistear.baml` + `oideachais_other/aistear.baml` + `early_childhood.baml`
  → `education/stages/aistear.baml`
- `primary.baml` + `oideachais_other/primary.baml`
  → `education/stages/primary.baml`
- `junior_cycle.baml` + `oideachais_other/junior_cycle.baml`
  → `education/stages/junior_cycle.baml`
- `tertiary.baml` + `oideachais_other/tertiary.baml`
  → `education/stages/tertiary.baml`
- `curriculum_extraction.baml` (1114 LOC mega-file) split into:
  - `education/_shared/education_level.baml` (10 enums)
  - `education/_shared/strand_outcome.baml` (17 classes)
  - `education/_shared/curriculum_relationships.baml` (4 functions)
  - `education/_shared/subject_rubric.baml` (4 functions + 5 classes)
  - `education/_shared/document_metadata.baml` (2 functions + 2 classes)

The following files have been moved to `_archive/` (per
`openspec/changes/archive-celtic-baml-orphans/`):

- `celtic_linguistics.baml` → `celtic/_archive/celtic_linguistics.baml`
- `cognates.baml` → `celtic/_archive/cognates.baml`

## Re-activation procedure for `_archive/` files

Per the archived-header procedure in each file:

1. Implement the consumer (e.g. `meaisinfhoghlaim/agents/celtic_linguistics.py`)
2. `git mv baml/celtic/_archive/<file>.baml baml/celtic/`
3. Remove the `ARCHIVED` header from the top
4. Update `openspec/specs/oideachais-baml-schemas/spec.md` to mark the
   functions as wired
5. Run `baml-cli generate` to regenerate the BAML client

## Cluster rationale

- **`education/`** is the 5 NCCA stages (Aistear → Tertiary) + the
  8 NCCA LC subjects (per the `cianfhoghlaim-educational-mmo` spec) +
  the per-stage leaving-cert PDF processing pipeline + cross-nation
  comparison + statistics + university.
- **`celtic/`** is the Celtic / Irish language extraction layer —
  Duchas (folklore), Logainm (placenames), Tearma (terminology) +
  Celtic-nation curriculum + Irish grammar + the 2 archived files.
- **`processing/`** is generic file processing that doesn't fit into
  the education or celtic clusters — email triage, CV/portfolio/LinkedIn
  /ResearchGate extraction, OCR, MMO game content, etc.

## Related specs

- `openspec/specs/oideachais-baml-schemas/spec.md` — the canonical spec
- `openspec/changes/baml-reorganize-by-cluster/` — the change that
  produced this structure
- `openspec/changes/wire-baml-to-consolidated-pipelines/` — the
  follow-on change that updates consumer imports (dlt, dagster, agents,
  cocoindex) to point at the new BAML paths