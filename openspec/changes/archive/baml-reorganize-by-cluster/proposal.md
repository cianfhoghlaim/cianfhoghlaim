# baml-reorganize-by-cluster — Reorganise `cianfhoghlaim/baml/` into 3 cluster sub-directories (education / celtic / processing)

## Why

The `cianfhoghlaim/baml/` directory (60+ .baml files, 256 BAML functions) is
organised by **file origin** (where the data came from historically) rather than
by **purpose** (what the BAML function does). Three concrete problems result:

1. **Duplicate stage-extraction BAML files.** The 5 NCCA education stages
   (Aistear, Primary, Junior Cycle, Senior Cycle, Tertiary) each have
   **two or three** parallel .baml files that extract the same data:
   - `aistear.baml` (208 LOC) + `oideachais_other/aistear.baml` (31 LOC) + `early_childhood.baml` (82 LOC)
   - `primary.baml` (171 LOC) + `oideachais_other/primary.baml` (45 LOC)
   - `junior_cycle.baml` (229 LOC) + `oideachais_other/junior_cycle.baml` (39 LOC)
   - `tertiary.baml` (332 LOC) + `oideachais_other/tertiary.baml` (79 LOC)
   - `curriculum_extraction.baml` (1114 LOC, the mega-file) + `curriculum_extraction_0.baml` (682 LOC, the BAML 0.x syntax version)

   New contributors cannot tell which file is canonical. Verified via `ccc
   search`: only `aistear.baml`, `junior_cycle.baml`, `primary.baml`,
   `tertiary.baml`, and `curriculum_extraction.baml` have downstream callers;
   the 5 `oideachais_other/*.baml` files have zero callers; `early_childhood.baml`
   has zero callers (its function was renamed in `aistear.baml`);
   `curriculum_extraction_0.baml` is the older BAML 0.x syntax and is fully
   superseded by `curriculum_extraction.baml`.

2. **Duplicate client-registry BAML files.** `educational_clients.baml`
   (84 LOC, defining `GPT4o`, `GPT4oMini`, `Claude`, `Qwen`, `OllamaIrish`
   + `CelticContentFallback`, `FastExtraction`) has **zero callers**. The 8
   `qpack_*.baml` files reference `ExtractEn` and `ExtractEnStrong`, both
   defined in the canonical `clients.baml`.

3. **Celtic / Irish / generic file-processing BAML files scattered.** The
   ~25 BAML files in the root and `gaois/` subdir are a mix of:
   - Celtic / Irish language extraction (4 `gaois/*.baml`, `celtic_curriculum.baml`, `celtic_sources.baml`, `celtic_linguistics.baml`, `cognates.baml`, `grammar_patterns.baml`, `morphology.baml`)
   - Generic file processing (`email.baml`, `audio_extraction.baml`, `cv_extraction.baml`, `portfolio_extraction.baml`, `researchgate_extraction.baml`, `linkedin_profile_extraction.baml`, `artwork_analysis.baml`, `author_archive.baml`, `circular_extraction.baml`, `identity_verification.baml`, `upstream_monitoring.baml`)
   - Cross-cluster (`educational_clients.baml`, `oideachas.baml`, `oideachais_other/`)
   - Uncategorised (`culture_extraction.baml`, `site_analysis.baml`, `ui_components.baml`, `image_generation.baml`, `game_content.baml`, `player_assessment.baml`, `style_transfer.baml`, `named_entities.baml`, `mythology_extraction.baml`, `official_media.baml`, `ocr_extraction.baml`, `ocr_validation.baml`, `teaching_extraction.baml`, `generators.baml`)

   No grouping by purpose. A reader cannot answer "where do the Irish
   language extraction BAML files live?" without enumerating all 60+ files.

This change **moves and merges** the BAML files into 3 cluster sub-directories
(`education/`, `celtic/`, `processing/`), each with its own `_shared/`
home for cross-cluster types, plus an `_archive/` home for BAML files that
were explicitly archived in `openspec/changes/archive-celtic-baml-orphans/`.
After the change, the canonical shape is:

```
cianfhoghlaim/baml/
├── clients.baml                              # KEEP at root (canonical LLM clients)
├── clients_llama_swap.baml                   # KEEP at root (specialty VL clients)
├── education/                                # CLUSTER 1 — NCCA education (all 5 stages + PDFs + subjects + cross-nation + stats + university)
│   ├── _shared/                              # stage_models, education_level, strand_outcome, pdf_extraction, curriculum_relationships
│   ├── stages/                               # aistear, primary, junior_cycle, senior_cycle, tertiary (one merged file per stage)
│   ├── pdfs/                                 # leaving_cert_syllabus, leaving_cert_past_paper, leaving_cert_marking_scheme
│   ├── subjects/                             # qpack_{mathematics, applied_mathematics, chemistry, geography, history, english, gaeilge, computer_science}
│   ├── cross_nation/                         # isles_education, multi_nation_curriculum
│   ├── statistics/                           # education_statistics
│   └── university/                           # university_extraction
├── celtic/                                   # CLUSTER 2 — Celtic / Irish language
│   ├── _shared/                              # celtic_languages, folklore_source, geography
│   ├── gaois/                                # KEEP — duchas, logainm, tearma, folklore_extraction (the gaois.ie API extraction layer)
│   ├── curriculum/                           # celtic_curriculum
│   ├── sources.baml                          # KEEP (celtic_sources.baml renamed)
│   └── _archive/                             # celtic_linguistics, cognates (per the 2026-06-24 ARCHIVED headers)
├── processing/                               # CLUSTER 3 — Generic file processing
│   ├── _shared/                              # person_organization
│   ├── email.baml                            # leabharlann email-triage pipeline
│   ├── upstream_monitoring.baml              # 4 upstream packages
│   ├── cv_extraction.baml                    # CV / achievements / teaching
│   ├── portfolio_extraction.baml             # portfolio
│   ├── linkedin_profile_extraction.baml      # LinkedIn (per croilar personas)
│   ├── researchgate_extraction.baml          # ResearchGate (per croilar)
│   ├── artwork_analysis.baml                 # artwork
│   ├── author_archive.baml                   # Gemini Deep Research PDF extraction
│   ├── circular_extraction.baml              # circular letters / gov docs
│   ├── identity_verification.baml            # identity docs + Garda vetting
│   ├── audio_extraction.baml                 # Canúint audio recordings
│   ├── ocr_extraction.baml                   # OCR validation (per meaisinfhoghlaim-ocr-htr)
│   ├── ocr_validation.baml                   # OCR vs ground truth
│   ├── image_generation.baml                 # FIBO image generation
│   ├── style_transfer.baml                   # FIBO style transfer
│   ├── game_content.baml                     # MMO game content (NPC, locations, items)
│   ├── player_assessment.baml                # MMO player assessment
│   ├── generators.baml                       # MMO FIBO generators
│   ├── culture_extraction.baml               # culture heritage claims
│   ├── named_entities.baml                   # NER
│   ├── site_analysis.baml                    # site analysis
│   ├── official_media.baml                   # official media classification
│   ├── ui_components.baml                    # UI component generation
│   └── teaching_extraction.baml              # teaching CV
└── shared/                                   # KEEP — the generated-client home (baml_client/, baml_client_ts/, baml_src/)
```

## What

A single openspec change with **8 numbered phases**. Each phase has its own
validation gate and must pass before the next begins. NO consumer rewrites in
this change — those happen in the follow-on `wire-baml-to-consolidated-pipelines`.

### Phase 1 — Create the new directory structure (no file moves)
```
mkdir -p cianfhoghlaim/baml/education/{_shared,stages,pdfs,subjects,cross_nation,statistics,university}
mkdir -p cianfhoghlaim/baml/celtic/{_shared,curriculum,gaois,_archive}
mkdir -p cianfhoghlaim/baml/processing/{_shared}
```

### Phase 2 — Move the 8 qpack_*.baml files into `education/subjects/`
Pure `git mv` — no content changes:
- `baml/qpack_mathematics.baml` → `baml/education/subjects/qpack_mathematics.baml`
- `baml/qpack_applied_mathematics.baml` → `baml/education/subjects/qpack_applied_mathematics.baml`
- `baml/qpack_chemistry.baml` → `baml/education/subjects/qpack_chemistry.baml`
- `baml/qpack_geography.baml` → `baml/education/subjects/qpack_geography.baml`
- `baml/qpack_history.baml` → `baml/education/subjects/qpack_history.baml`
- `baml/qpack_english.baml` → `baml/education/subjects/qpack_english.baml`
- `baml/qpack_gaeilge.baml` → `baml/education/subjects/qpack_gaeilge.baml`
- `baml/qpack_computer_science.baml` → `baml/education/subjects/qpack_computer_science.baml`

### Phase 3 — Move the 3 leaving_cert_*_extraction.baml files into `education/pdfs/`
Pure `git mv`:
- `baml/leaving_cert_syllabus_extraction.baml` → `baml/education/pdfs/leaving_cert_syllabus.baml`
- `baml/leaving_cert_past_paper_extraction.baml` → `baml/education/pdfs/leaving_cert_past_paper.baml`
- `baml/leaving_cert_marking_scheme_extraction.baml` → `baml/education/pdfs/leaving_cert_marking_scheme.baml`

### Phase 4 — Move the cross_nation / statistics / university BAML files
- `baml/isles_education.baml` → `baml/education/cross_nation/isles_education.baml`
- `baml/multi_nation_curriculum.baml` → `baml/education/cross_nation/multi_nation_curriculum.baml`
- `baml/education_statistics.baml` → `baml/education/statistics/education_statistics.baml`
- `baml/university_extraction.baml` → `baml/education/university/university_extraction.baml`

### Phase 5 — Merge the 5 NCCA stage duplicates
Each merge preserves ALL features from all source files. The output file
goes into `education/stages/`.

#### 5a — `education/stages/aistear.baml` (MERGED from 3 sources)
- `baml/aistear.baml` (208 LOC): enums `AistearTheme`, `AistearAgeBand`,
  `AistearLanguageMedium`; classes `AistearPrinciple` (with
  `name_en`/`name_ga`), `AistearLearningGoal` (with `linked_primary_outcome`),
  `GeoPoint`, `Naionra`, `AistearDocument`, `BridgeEdge`; functions
  `ExtractAistearFramework(text, language)`,
  `ExtractNaionraListing(page_markdown)`,
  `BridgeAistearToPrimary(aistear_doc, primary_doc)`.
- `baml/oideachais_other/aistear.baml` (31 LOC): function
  `ExtractAistearFrameworkFromUrl(source_url)` (from URL).
- `baml/early_childhood.baml` (82 LOC): simplified `AistearPrinciple`,
  `AistearLearningGoal`, `AistearFramework`, `AistearDocument`; function
  `ExtractAistearFramework(pdf_text)` (uses `LitellmClient`).

The merged file keeps:
- All 4 enums + `AistearDialect` (new — for the 3 Munster/Connacht/Ulster dialects already used in `gaois/duchas.baml`)
- All 4 classes from `aistear.baml` (the richest schema) + the simplified versions from `early_childhood.baml` (aliased for backward compat)
- All 4 functions, each renamed to disambiguate:
  - `ExtractAistearFrameworkFromText(text, language)` (from `aistear.baml`)
  - `ExtractAistearFrameworkFromUrl(source_url)` (from `oideachais_other/aistear.baml`)
  - `ExtractAistearFrameworkFromPdf(pdf_text)` (from `early_childhood.baml`)
  - `ExtractNaionraListing(page_markdown)` (from `aistear.baml`)
  - `BridgeAistearToPrimary(aistear_doc, primary_doc)` (from `aistear.baml`)
- Adds 2 alias functions for backward compat:
  - `ExtractAistearFramework(pdf_text, language)` → calls `ExtractAistearFrameworkFromText` then sets the language field
  - `ExtractAistearFramework(pdf_text)` (from `early_childhood.baml`) → calls `ExtractAistearFrameworkFromPdf`

#### 5b — `education/stages/primary.baml` (MERGED from 2 sources)
- `baml/primary.baml` (171 LOC): enums `PrimaryStage`, `PrimaryAreaCode`;
  classes `CompetencyLink`, `PrimaryLearningOutcome`,
  `PrimaryStrand`, `PrimaryCurriculumArea`; functions
  `ExtractPrimaryFramework(text, stage, area)`,
  `ExtractPrimaryLearningOutcomes(text, stage, area)`.
- `baml/oideachais_other/primary.baml` (45 LOC): function
  `ExtractPrimaryFrameworkFromUrl(source_url, stage, area)`.

The merged file keeps all 4 functions:
- `ExtractPrimaryFramework(text, stage, area)` (from `primary.baml`)
- `ExtractPrimaryLearningOutcomes(text, stage, area)` (from `primary.baml`)
- `ExtractPrimaryFrameworkFromUrl(source_url, stage, area)` (from `oideachais_other/primary.baml`)
- `ExtractPrimaryFrameworkFromText(text, stage, area)` (new alias — same as `ExtractPrimaryFramework` but with explicit name)

#### 5c — `education/stages/junior_cycle.baml` (MERGED from 2 sources)
- `baml/junior_cycle.baml` (229 LOC): enums `JuniorCycleSubject`,
  `JuniorCycleShortCourse`, `AchievementLevel`; classes `RubricDescriptor`,
  `CBATask`, `JCWellbeingStatement`, `JCSubjectSpec`, `L2LPOutcome`;
  functions `ExtractJCSpec`, `ExtractCBADescriptor`, `ExtractShortCourse`.
- `baml/oideachais_other/junior_cycle.baml` (39 LOC): function
  `ExtractJCSpecFromUrl(source_url, subject)`.

#### 5d — `education/stages/senior_cycle.baml` (MOVED from 1 source)
- `baml/oideachais_other/senior_cycle.baml` (76 LOC): function
  `ExtractSeniorCycleSpecFromUrl`, `ScoreEssayAgainstRubricStdLib`.
  No merge needed.

#### 5e — `education/stages/tertiary.baml` (MERGED from 2 sources)
- `baml/tertiary.baml` (332 LOC): enums `NFQLevel`, `EQFLevel`, `HEIType`,
  `EntryPathway`; classes `MatriculationRequirement`, `CAOCourse`,
  `QqiFetAward`, `Apprenticeship`, `Programme`, `ApplicationTimeline`,
  `CAOGradeProfile`, `CoursePointsPrediction`, `MatriculationAudit`;
  7 functions.
- `baml/oideachais_other/tertiary.baml` (79 LOC): functions
  `ExtractCAOCourseListFromUrl`, `ExtractMatriculationRulesFromUrl`,
  `AuditMatriculationStdLib`.

### Phase 6 — Split the mega-file `curriculum_extraction.baml` (1114 LOC)
Split into 4 files in `education/_shared/`:
- `education/_shared/education_level.baml` — the 10 enums
  (`RelationshipType`, `DifficultyLevel`, `EducationLevel`, `ExamLevel`,
  `QuestionType`, `LeavingCertSubject`, `Specialism`,
  `AssessmentComponentType`, `RubricStyle`, `DocumentCategory`).
- `education/_shared/strand_outcome.baml` — the 17 classes
  (`LearningOutcome`, `Skill`, `CurriculumSpecification`, `ExamPaper`,
  `MarkingScheme`, `ExaminerReport`, …).
- `education/_shared/curriculum_relationships.baml` — the 4 relationship
  functions (`ExtractLearningOutcomeRelationships`,
  `ExtractSkillsFromOutcome`, `ExtractCurriculumFromDocument`,
  `IdentifyPrerequisiteChain`).
- `education/_shared/subject_rubric.baml` — the 4 rubric functions
  (`ExtractSubjectRubric`, `ScoreEssayAgainstRubric`,
  `CompareMarkingSchemes`, `LazyExtractExamPaper`).
- `education/_shared/document_metadata.baml` — the 2 document metadata
  functions (`ExtractAllPdfMetadata`, `ExtractCurriculumSyllabus`).

### Phase 7 — Move the Celtic / Irish language BAML files into `celtic/`
- `baml/gaois/*.baml` (4 files: `duchas`, `logainm`, `tearma`,
  `folklore_extraction`) → `baml/celtic/gaois/*.baml`
- `baml/celtic_sources.baml` → `baml/celtic/sources.baml`
- `baml/celtic_curriculum.baml` → `baml/celtic/curriculum/celtic_curriculum.baml`
- `baml/morphology.baml` + `baml/grammar_patterns.baml` → `baml/celtic/`
  (the Celtic/Irish cluster; both files are about Irish grammar)
- `baml/mythology_extraction.baml` → `baml/celtic/curriculum/mythology_extraction.baml`

### Phase 8 — Move the generic file-processing BAML files into `processing/`
- `baml/email.baml` → `baml/processing/email.baml`
- `baml/upstream_monitoring.baml` → `baml/processing/upstream_monitoring.baml`
- `baml/cv_extraction.baml` → `baml/processing/cv_extraction.baml`
- `baml/portfolio_extraction.baml` → `baml/processing/portfolio_extraction.baml`
- `baml/linkedin_profile_extraction.baml` → `baml/processing/linkedin_profile_extraction.baml`
- `baml/researchgate_extraction.baml` → `baml/processing/researchgate_extraction.baml` (AND fix the `| null` syntax bug to `?`)
- `baml/artwork_analysis.baml` → `baml/processing/artwork_analysis.baml`
- `baml/author_archive.baml` → `baml/processing/author_archive.baml`
- `baml/circular_extraction.baml` → `baml/processing/circular_extraction.baml`
- `baml/identity_verification.baml` → `baml/processing/identity_verification.baml`
- `baml/audio_extraction.baml` → `baml/processing/audio_extraction.baml`
- `baml/ocr_extraction.baml` → `baml/processing/ocr_extraction.baml`
- `baml/ocr_validation.baml` → `baml/processing/ocr_validation.baml`
- `baml/image_generation.baml` → `baml/processing/image_generation.baml`
- `baml/style_transfer.baml` → `baml/processing/style_transfer.baml`
- `baml/game_content.baml` → `baml/processing/game_content.baml`
- `baml/player_assessment.baml` → `baml/processing/player_assessment.baml`
- `baml/generators.baml` → `baml/processing/generators.baml`
- `baml/culture_extraction.baml` → `baml/processing/culture_extraction.baml`
- `baml/named_entities.baml` → `baml/processing/named_entities.baml`
- `baml/site_analysis.baml` → `baml/processing/site_analysis.baml`
- `baml/official_media.baml` → `baml/processing/official_media.baml`
- `baml/ui_components.baml` → `baml/processing/ui_components.baml`
- `baml/teaching_extraction.baml` → `baml/processing/teaching_extraction.baml`

### Phase 9 — Delete dead files and directories
- `baml/educational_clients.baml` — **DELETE** (0 callers; verified via `ccc search`)
- `baml/curriculum_extraction_0.baml` — **DELETE** (BAML 0.x syntax superseded by `curriculum_extraction.baml` which is now split into 4 files in `education/_shared/`)
- `baml/oideachais_other/` — **DELETE ENTIRE DIRECTORY** (all 5 files were duplicates of top-level files; verified via `ccc search` for each file showing 0 callers)
- `baml/_croilar_src/` — **DELETE ENTIRE DIRECTORY** if it still exists (already removed per earlier consolidation)

### Phase 10 — Move ARCHIVED Celtic BAML files to `_archive/`
Per `openspec/changes/archive-celtic-baml-orphans/` (the 2026-06-24 archived
headers in the files themselves):
- `baml/celtic_linguistics.baml` → `baml/celtic/_archive/celtic_linguistics.baml`
  (preserves `ExtractMorphology`, `AnalyzeSentence`, `IdentifyDialect` per the archive header's re-activation procedure)
- `baml/cognates.baml` → `baml/celtic/_archive/cognates.baml`
  (preserves `IdentifyCognates`, `CompareCelticVocabulary`,
  `IdentifyFalseFriends`, `ExplainSoundChanges`, `GenerateCognateVocabulary`)

### Phase 11 — Delete `baml/oideachas.baml`
The file `baml/oideachas.baml` appears to be a typo of `baml/oideachais.baml`
(no such file exists; `oideachas.baml` is unrelated). Verify via `ccc search`
that it has 0 callers; if so, **DELETE**.

### Phase 12 — Validate
- `baml-cli generate` succeeds against the new structure
- `ccc search "oideachais_other"` returns 0 hits in `baml/`
- `ccc search "ExtractAistearFrameworkFromUrl"` returns 1 hit in `education/stages/aistear.baml`
- `ccc search "GenerateMathQuestPack"` returns 1 hit in `education/subjects/qpack_mathematics.baml`
- `ccc search "celtic_linguistics.baml"` returns 1 hit in `celtic/_archive/celtic_linguistics.baml`
- The BAML-generated client exposes all functions (the file count goes from 60+ at root to 3 at root + N per cluster sub-directory)

## Impact

| Metric | Before | After |
|--|--|--|
| BAML files at `baml/` root | 60+ | 2 (`clients.baml` + `clients_llama_swap.baml`) |
| `baml/oideachais_other/` directory | 5 duplicate files | DELETED |
| `baml/_croilar_src/` directory | dead leftover | DELETED |
| Duplicate stage BAML files | 5 (aistear ×3, primary ×2, junior_cycle ×2, tertiary ×2, curriculum_extraction ×2) | 0 (merged into 1 file per stage) |
| `baml/educational_clients.baml` (0 callers) | exists | DELETED |
| `baml/curriculum_extraction_0.baml` (BAML 0.x) | exists | DELETED |
| `baml/oideachas.baml` (typo, 0 callers) | exists | DELETED |
| `baml/celtic_linguistics.baml` (archived 2026-06-24) | at root | at `celtic/_archive/` |
| `baml/cognates.baml` (archived 2026-06-24) | at root | at `celtic/_archive/` |
| `baml/researchgate_extraction.baml` syntax bug | `string \| null` (invalid BAML) | `string?` |
| Cluster sub-directories | 1 (`gaois/`) | 3 (`education/`, `celtic/`, `processing/`) |
| `_shared/` homes | 0 | 4 (one per cluster + cluster-agnostic) |
| `_archive/` home | 0 | 1 (`celtic/_archive/`) |

### Affected specs
- **MODIFIED `oideachais-baml-schemas`** — the rule that BAML files live
  in one of the 3 cluster sub-directories (`education/`, `celtic/`,
  `processing/`), plus their respective `_shared/` homes. The 2-client
  shape (`clients.baml` + `clients_llama_swap.baml`) is canonical at
  the root. The dead `educational_clients.baml` + `curriculum_extraction_0.baml`
  + `oideachas.baml` + `oideachais_other/` are explicitly forbidden.

### Backward compatibility
This change moves files but does NOT update consumer imports. The consumer
rewrites happen in the follow-on change
`openspec/changes/wire-baml-to-consolidated-pipelines/`. In the interim,
existing consumer files (`dlt/`, `dagster/`, `agents/`, `cocoindex/`)
continue to work IF AND ONLY IF the BAML compiler is configured to
discover the new paths. The `baml_src/` configuration in the
`pyproject.toml` (under `[tool.baml]`) must be updated to include the
new cluster sub-directories. The BAML compiler then regenerates the
Python + TypeScript clients at `baml/shared/baml_client{,_ts}/` (which
is the canonical generated-output home).

### Non-Goals
- No new BAML functions added
- No consumer imports updated (that is the follow-on change)
- No BAML client configuration rewrites (the 4 existing clients in
  `clients.baml` + `clients_llama_swap.baml` are kept verbatim)
- No deletions of the generated clients (`baml/shared/baml_client/`)
- No DAG / dlt / cocoindex pipeline restructuring (that is the
  parallel `consolidate-cianfhoghlaim-subdirs` change)

### Risk Assessment

| Risk | Mitigation |
|:--|:--|
| **Merging 3 aistear.baml files loses subtle prompt differences** | Use a per-section reconciliation table (in tasks.md); each `ExtractAistearFramework*` keeps its distinct prompt verbatim; only the duplicate types merge with the richest schema winning. The 3 source files are read fully before any merge. |
| **The BAML-generated types break** | Run `baml-cli generate` after every move; the generated clients live at `baml/shared/baml_client{,_ts}/` and get overwritten. Validate via `baml-cli generate && python -c "from cianfhoghlaim.baml_client import b; print(len([f for f in dir(b) if not f.startswith('_')]))"` should print >= 250 (the current function count). |
| **The 8 qpack files break when moved to `education/subjects/`** | Each qpack file references `ExtractEn` and `ExtractEnStrong` clients from `clients.baml` (NOT relative imports). Pure `git mv` does not change the cross-file client references. Validate by running the MMO tests (`agents/tuatha/subject_agents/*_agent.py`). |
| **The 256 BAML functions take too long to move atomically** | Each Phase 2-11 is a series of `git mv` operations that are atomic per file. The BAML compiler doesn't care about the path; only the `baml_src/` config does (handled in Phase 12). |
| **The `curriculum_extraction.baml` split introduces merge conflicts** | The mega-file is the only consumer of its own internal types. Splitting into 4 `_shared/` files preserves all types; the only "consumer" is `curriculum_extraction.baml` itself. No external conflicts. |

## Validation

1. `baml-cli generate` succeeds against the new structure
2. `ccc search "oideachais_other"` returns 0 hits in `baml/`
3. `ccc search "ExtractAistearFrameworkFromUrl"` returns 1 hit (in `education/stages/aistear.baml`)
4. `ccc search "ExtractAistearFrameworkFromText"` returns 1 hit
5. `ccc search "ExtractAistearFrameworkFromPdf"` returns 1 hit
6. `ccc search "ExtractPrimaryFrameworkFromUrl"` returns 0 hits (the old name); the new name returns 1 hit
7. `ccc search "ExtractLeavingCertSyllabus"` returns 1 hit (in `education/pdfs/`)
8. `ccc search "GenerateMathQuestPack"` returns 1 hit (in `education/subjects/`)
9. `ccc search "celtic_linguistics.baml"` returns 1 hit (in `celtic/_archive/`)
10. `ccc search "ParseSchoolsVolume"` returns 1 hit (in `celtic/gaois/duchas.baml`)
11. `python -c "from cianfhoghlaim.baml_client import b; print(len([f for f in dir(b) if not f.startswith('_')]))"` prints >= 250
12. `ls baml/` shows exactly 2 client files at root + 3 cluster sub-directories + `shared/` + `cli.py`
13. `ls baml/educational_clients.baml` returns "No such file or directory"
14. `ls baml/curriculum_extraction_0.baml` returns "No such file or directory"
15. `ls baml/oideachas.baml` returns "No such file or directory"
16. `openspec validate baml-reorganize-by-cluster --strict` passes