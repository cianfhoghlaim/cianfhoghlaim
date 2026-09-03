# Ireland LC BIEP — the official document pipeline

This document tracks the per-subject ingestion of the 148 official
PDFs into the BIEP pipeline. It's the canonical artifact that
the BAML extraction consumes (per the 2026-08-10-baml-extraction-completion-v1
change + the 2026-08-13-web-monorepo-consolidation-and-agent-integration-v1
change Phase 3).

## The 14 LC subjects × NCCA LOs

| Subject | NCCA LO prefix | PDFs on disk | Status |
|:--|:--|--:|:--|
| mathematics | `LC-MATH-LO` | 16 | ✅ Ready |
| applied_mathematics | `LC-APM-LO` | 7 | ✅ Ready |
| chemistry | `LC-CHEM-LO` | 16 | ✅ Ready |
| physics | `LC-PHYS-LO` | 1 | ✅ Ready (newly downloaded) |
| biology | `LC-BIO-LO` | 12 | ✅ Ready |
| geography | `LC-GEOG-LO` | 18 | ✅ Ready |
| gaeilge | `LC-GAEL-LO` | 11 | ✅ Ready |
| english | `LC-ENGL-LO` | 8 | ✅ Ready |
| french | `LC-FREN-LO` | 7 | ✅ Ready |
| history | `LC-HIST-LO` | 12 | ✅ Ready |
| business | `LC-BUS-LO` | 12 | ✅ Ready |
| accounting | `LC-ACCT-LO` | 1 | ✅ Ready (newly downloaded) |
| art | `LC-ART-LO` | 1 | ✅ Ready (newly downloaded) |
| music | `LC-MUS-LO` | 1 | ✅ Ready (newly downloaded) |
| computer_science | `LC-COMP-LO` | 11 | ✅ Ready |
| **TOTAL** | | **134** | **All 14 subjects covered** |

## The 4-path OCR/VLM ensemble (per PDF)

Each PDF flows through the ensemble:

```
                          ┌──────────────┐
   PDF input ───────────► │  Path 1      │ ──► BAML function
                          │  Docling→BAML│     (typed Pydantic row)
                          └──────┬───────┘
                                 │
                          ┌──────▼───────┐
                          │  Path 2      │ ──► JSON
                          │  Unstract    │
                          └──────┬───────┘
                                 │
                          ┌──────▼───────┐
                          │  Path 3      │ ──► JSON
                          │  qwen3-vl-8b │
                          └──────┬───────┘
                                 │
                          ┌──────▼───────┐
                          │  Path 4      │ ──► JSON
                          │  gemma4-26B  │
                          └──────┬───────┘
                                 │
                          ┌──────▼───────┐
                          │  RAGAS       │ ──► 1 canonical row
                          │  consensus   │     → BIEP DuckLake table
                          └──────────────┘
```

## The 8 BAML extraction functions (per subject)

Each PDF's canonical row is produced by calling 8 BAML functions:

1. `ExtractCurriculumSyllabus(text, subject)` → `CurriculumSyllabus`
2. `ExtractExamPaperLayout(text, subject)` → `ExamPaperLayout`
3. `ExtractMarkingSchemeGuideline(text, subject)` → `MarkingSchemeGuideline`
4. `ExtractSyllabusDiagram(text, subject)` → `SyllabusDiagram`
5. `ExtractCrossLinguisticConcept(en_text, ga_text)` → `CrossLinguisticConcept`
6. `ExtractBilingualLearningOutcome(en_text, ga_text)` → `BilingualLearningOutcome`
7. `ExtractCrossLinguisticGA(ga_text)` → `CrossLinguisticConcept`
8. `ExtractCrossSubjectTopics(subject, level, language, pdf_text, source_pdf)` → `CrossSubjectTopicSet`

## The 4 dependent openspec specs

Per the 2026-08-13-web-monorepo-consolidation-and-agent-integration-v1 mega-change:

1. **`web-monorepo-consolidation`** — the 4 web apps (consolidation of `web/`)
2. **`schema-driven-codegen`** — the 6 sub-generators in `scripts/schema-codegen/`
3. **`per-subject-coverage`** — the 60-subject × 4-stage matrix
4. **`per-subject-agents`** — the 60 per-subject agents in `agents/adk/subjects/`

## Cross-nation research via Firecrawl

Use Firecrawl MCP to fetch cross-jurisdictional comparisons:

- **Ireland LC** (current focus) — 14 subjects × 2 languages
- **England A-Level** — 49 subjects × 3 boards (AQA / OCR / Edexcel)
- **England GCSE** — 43 subjects × 3 boards
- **Wales WJEC** — 14 subjects
- **Scotland SQA** — 8 subjects
- **NI CCEA** — 8 subjects
- **Crown Dependencies** (Jersey / Guernsey / IoM) — 3 jurisdictions

The Firecrawl MCP tools (per `agents/meaisinfhoghlaim/firecrawl_mcp/`) handle the external research.

## The 4 newly downloaded PDFs (Phase 2)

| Subject | PDF | Source URL | Size |
|:--|:--|:--|--:|
| Physics | `LC_Physics_Syllabus_EN.pdf` | https://curriculumonline.ie/getmedia/fe400d39-9ea0-46ee-927b-ce570bddad76/SCSEC27_Physics_syllabus_eng.pdf | 431 KB |
| Accounting | `LC_Accounting_Syllabus_EN.pdf` | https://www.curriculumonline.ie/getmedia/1cc50fb4-90da-428c-83d4-df53c8f49dd9/SCSEC01_Accounting_syllabus_English.pdf | 73 KB |
| Art | `Leaving-Certificate-Art-Specification_EN.pdf` | https://curriculumonline.ie/getmedia/d809df63-51e4-43dc-b091-3c5f18a8312d/Leaving-Certificate-Art-Specification_EN.pdf | 857 KB |
| Music | `LC_Music_Syllabus_EN.pdf` | https://www.curriculumonline.ie/getmedia/85bfed8e-207e-4fbc-b8ed-3120cd979a4b/SCSEC26_Music_syllabus_eng.pdf | 147 KB |

## The 4 NCCA official sources (Firecrawl-verified)

The curl downloads above were cross-verified against the official NCCA
curriculumonline.ie pages via Firecrawl MCP. The canonical source URLs are:

- **Physics**: https://curriculumonline.ie/senior-cycle/senior-cycle-subjects/physics/
- **Accounting**: https://www.curriculumonline.ie/senior-cycle/senior-cycle-subjects/accounting/
- **Art**: https://curriculumonline.ie/senior-cycle/senior-cycle-subjects/art/
- **Music**: https://www.curriculumonline.ie/senior-cycle/senior-cycle-subjects/music/

## Next steps (Phase 4-10)

Per the 2026-08-13-web-monorepo-consolidation-and-agent-integration-v1 change:

1. **Phase 4 - Add 8 JC + 9 GCSE + 15 A-Level BAML files** (per the existing Ireland LC pattern)
2. **Phase 5 - Extend DLT sources** to all 60 subjects
3. **Phase 6 - Extend CocoIndex factories** to all 60 subjects
4. **Phase 7 - Run the codegen** (Phase O of the mega-change)
5. **Phase 8 - Generate 60 per-subject agents**
6. **Phase 9 - Generate 60 per-subject notebooks**
7. **Phase 10 - Build the central Cianfhoghlaim homepage**

## File inventory (this folder)

- `ireland_lc_ingestion_manifest.json` — the canonical artefact (134 PDFs × 14 subjects)
- `build_ingestion_manifest.py` — the manifest builder
- `process_4_paths.py` — the 4-path OCR/VLM ensemble runner
- `physics_extraction_results.json` — the extraction results for physics (sample)
- `INGESTION.md` — this file
