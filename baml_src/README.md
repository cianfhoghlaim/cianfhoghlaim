# `baml_src/` — BAML extraction schemas (v8, post-v7 layout)

> **The 320 BAML files for the Cianfhoghlaim platform — 558 functions, 838 classes, 288 enums, 33 LLM clients (all routing to `minimax-m3`).**
>
> Post-v7 flattening (2026-07-17) the canonical directory is `baml_src/` (not `baml/`). The pre-v7 layout was a 3-cluster taxonomy at `./baml/education/`, `./baml/celtic/`, `./baml/processing/`. Post-v7, the canonical layout is jurisdiction-clustered at `./baml_src/{british_isles,european_nations,european_union,commonwealth,american_nations,celtic,processing}/` with a shared `_shared/` and `shared/` home.

## Quick start

```bash
# Regenerate the baml_client/ Python module after editing any .baml file
mise run baml:generate

# Run the 11 BAML test blocks (hard CI gate)
mise run baml:test

# The canonical entry-point Python CLI (alias for mise run baml:generate)
uv run baml-cli generate --from baml_src

# Verify the embedder is wired
python -c "from baml_client import b; print(b.__class__.__module__)"
```

## Layout — 7 clusters + 1 shared home

```
baml_src/
├── __init__.py                  # Marks baml_src/ as importable
├── baml.toml                    # BAML CLI config (output_dir: ../baml_client)
├── cli.py                       # `cianfhoghlaim-baml` console_script stub
├── clients.baml                 # The 23 canonical LLM clients (all routing to minimax-m3)
├── clients_biep_v3.py           # Python-side spec for BIEPV3Extract* + BIEPV3Vision
├── clients_llama_swap.baml      # 4 llama-swap clients (vision + extraction + reasoning)
├── clients_ocr_ensemble.baml    # 2 OCR ensemble clients (Docling + Unstract)
├── british_isles/               # CLUSTER 1 — 8 BI nations (103 .baml)
│   ├── _cross/                  # Cross-BI shared types + BIEP v3 canonical
│   ├── ireland/                 # 71 .baml (5 NCCA stages + 8 NCCA LC subjects + LC extraction)
│   ├── england/                 # 9 .baml (AQA + OCR + Edexcel per-board)
│   ├── scotland/                # 3 .baml (SQA + CfE)
│   ├── wales/                   # 3 .baml (WJEC)
│   ├── northern_ireland/        # 3 .baml (CCEA)
│   ├── jersey/                  # 3 .baml (Channel Islands)
│   ├── guernsey/                # 3 .baml (Channel Islands)
│   └── isle_of_man/             # 3 .baml (Crown Dependencies)
├── european_nations/            # CLUSTER 2 — 40 EU/EEA nations (122 .baml)
│   ├── _shared/                 # NationJurisdictionMetadata + ExtractNationJurisdictionMetadata
│   ├── albania/                 # 3 .baml (education + government + statistics)
│   ├── austria/                 # 3 .baml
│   ├── belgium/                 # 3 .baml
│   └── ... (40 nations total, 3 .baml each = 120 .baml + 2 _shared .baml)
├── european_union/              # CLUSTER 3 — EU institutional (9 .baml)
│   ├── _shared/                 # EUDocument + EUDocumentBilingualEnGa + EUInstitution + EULanguage
│   ├── eur_lex_extraction.baml  # EUR-Lex (Treaty + Directive + Regulation + Decision)
│   ├── ecdc_extraction.baml     # European Centre for Disease Prevention & Control
│   ├── ema_extraction.baml      # European Medicines Agency
│   ├── eurostat_extraction.baml # Eurostat dataset metadata
│   └── eurydice_extraction.baml # Eurydice national education structures
├── commonwealth/               # CLUSTER 4 — 6 Commonwealth nations (24 .baml)
│   ├── _shared/                 # CommonwealthJurisdictionMetadata
│   ├── australia/               # 3 .baml
│   ├── canada/                  # 12 provinces + quebec/montreal education
│   ├── india/                   # 3 .baml
│   ├── new_zealand/             # 3 .baml
│   ├── nigeria/                 # federal + state + states/_states
│   └── south_africa/            # 3 .baml
├── american_nations/            # CLUSTER 5 — 4 Americas nations (15 .baml)
│   ├── _shared/                 # AmericanNationJurisdictionMetadata
│   ├── brazil/                  # 3 .baml
│   ├── mexico/                  # 3 .baml
│   ├── united_states/           # 3 .baml (currently populated with California)
│   └── venezuela/               # 3 .baml
├── celtic/                      # CLUSTER 6 — Celtic / Irish language (11 .baml)
│   ├── _shared/                 # (reserved for cross-Celtic types — empty for now)
│   ├── gaois/                   # Gaois.ie extraction (4 .baml)
│   ├── curriculum/              # Celtic-nation curriculum (2 .baml)
│   ├── grammar_patterns.baml    # Irish grammar
│   ├── morphology.baml          # Irish morphology
│   ├── sources.baml             # Source-agnostic unified record
│   └── _archive/                # 2 archived files (celtic_linguistics + cognates)
├── processing/                  # CLUSTER 7 — Generic file processing (33 .baml)
│   ├── _shared/                 # DocumentType + LanguageCodes + MusicGenre + VideoKG
│   ├── email.baml               # leabharlann email-triage pipeline
│   ├── upstream_monitoring.baml # 4 upstream packages (motherduck / dlthub / lancedb / cocoindex)
│   ├── cv_extraction.baml       # CV / achievements / teaching
│   ├── portfolio_extraction.baml
│   ├── linkedin_profile_extraction.baml
│   ├── researchgate_extraction.baml
│   ├── artwork_analysis.baml    # Artwork analysis
│   ├── author_archive.baml      # Gemini Deep Research PDF extraction
│   ├── circular_extraction.baml # Generic circular (vs BIEP-specific at british_isles/.../lc_extraction/circular_extraction.baml)
│   ├── identity_verification.baml # Identity docs + Garda vetting
│   ├── audio_extraction.baml    # Canúint audio recordings
│   ├── ocr_extraction.baml      # Hidden Heritages HTR/OCR (Celtic-nation tales)
│   ├── ocr_validation.baml      # OCR vs ground truth + Irish quality
│   ├── image_generation.baml    # Bria FIBO image generation
│   ├── style_transfer.baml      # FIBO style transfer
│   ├── game_content.baml        # MMO game content (NPCs, locations, items)
│   ├── player_assessment.baml   # MMO player assessment
│   ├── generators.baml          # MMO FIBO generators
│   ├── culture_extraction.baml  # Culture heritage claims
│   ├── named_entities.baml      # NER
│   ├── site_analysis.baml       # Site analysis (SummarizeSite + PreResearchSite + ParseGeoQuery)
│   ├── official_media.baml      # Official media classification (ClassifyOfficialMedia)
│   ├── ui_components.baml       # UI component generation (SuggestUIComponents + Render*)
│   ├── teaching_extraction.baml # Teaching CV
│   └── ... (33 files total)
├── shared/                       # Generated-client home (stale 0.222.0; not used post-v7)
└── _legacy/                     # (none — empty after v8 cleanup)
```

**Total**: 320 `.baml` files (post-2026-08-13 cleanup; +4 root-level clients).

## The 33 LLM clients (all routing to `minimax-m3`)

`clients.baml` defines 23 active clients + 2 retry policies. All clients route to the `MINIMAX_BASE_URL` + `MINIMAX_API_KEY` (via Infisical `dev-baile/cianfhoghlaim-llm/`).

| Client | Model | Provider | Used by |
|:--|:--|:--|:--|
| `Default` | `minimax-m3` | `openai-generic` | The canonical text client |
| `LitellmClient` | `minimax-m3` | `openai-generic` | Alias of Default (LiteLLM gateway passthrough) |
| `ExtractEn` | `minimax-m3` | `openai-generic` | **Most-used** — 200+ extraction functions |
| `ExtractEnStrong` | `minimax-m3` | `openai-generic` | Alias of ExtractEn (same model) |
| `LocalVision` | `qwen3-vl-8b` | `openai` | Local vision (litellm-served) |
| `LocalVisionGemma4` | `gemma-4-26B-A4B` | `openai` | Local vision (gemma4) |
| `LocalVisionQwen3vl` | `qwen3-vl-8b` | `openai` | Local vision (qwen3-vl) |
| `BIEPV3Extract` | `minimax-m3` | `openai-generic` | retry_policy Exponential (BIEP v3 canonical) |
| `BIEPV3ExtractStrong` | `minimax-m3` | `openai-generic` | retry_policy Exponential (BIEP v3 alias) |
| `BIEPV3Vision` | `qwen3-vl-8b` | `openai` | retry_policy Exponential (BIEP v3 vision) |
| ... (13 more aliases: ArtworkAnalyzer + CelticContentFallback + ClaudeHaiku + Extractor + ExtractorFast + FastAnalyzer + FastExtraction + Gemini2FlashAlias + LiteLLM + OideachaisDefault + VisionExtractor) | `minimax-m3` | `openai-generic` | Legacy aliases |

Plus `clients_ocr_ensemble.baml` (Docling + Unstract) and
`clients_llama_swap.baml` (4 LlamaSwap clients for local vision +
extraction + reasoning).

**Plus 2 retry policies:** `Simple` (max_retries 2, exp backoff 500ms × 2) and `Exponential` (max_retries 3, exp backoff 200ms × 1.5). Only `BIEPV3*` clients use Exponential.

> **Historical note**: The README of the pre-v7 era claimed `clients.baml` has `LitellmClient, DeepSeekClient, MiniMaxClient, LitellmLongContext, Extractor, vision clients, 2 fallback chains`. Post-v7, only `minimax-m3` (the coding-plan API) is wired. `DeepSeekClient` and `MiniMaxClient` no longer exist; `LitellmLongContext` no longer exists; "2 fallback chains" was misleading — only `2 retry_policy` blocks exist (not chains).

## The canonical LC extraction functions

`british_isles/ireland/education/lc_extraction/` houses the 6 BIEP v1 extractors:

| File | Function | Returns | Client |
|:--|:--|:--|:--|
| `curriculum_syllabus.baml:87` | `ExtractCurriculumSyllabus(pdf_text, subject?, language?)` | `SyllabusDocument` | `ExtractEn` |
| `exam_paper_layout.baml:75` | `ExtractExamPaperLayout(pdf_text, subject?, paper_code?, year?)` | `ExamPaper` | `ExtractEn` |
| `marking_scheme.baml:64` | `ExtractMarkingSchemeGuideline(pdf_text, subject?, year?, paper?)` | `MarkingScheme` | `ExtractEn` |
| `cross_linguistic.baml:51` | `ExtractCrossLinguisticConcept(pdf_text_en, pdf_text_ga?, subject?, concept_id?)` | `CrossLinguisticConcept[]` | `BIEPV3Extract` |
| `syllabus_diagram.baml:80` | `ExtractSyllabusDiagram(pdf_text, page_text?, page_number?, subject?, subject_language?)` | `SyllabusDiagram[]` | `BIEPV3Vision` |
| `lc_topic_extraction.baml:87` | `ExtractCrossSubjectTopics(subject, level, language, pdf_text, source_pdf)` | `CrossSubjectTopicSet` | `ExtractEn` |

Plus 2 link helpers:
- `LinkTopicToCompetency(topic, competency)` → `CrossSubjectTopic`
- `LinkCircularToSyllabus(circular, candidate_syllabi)` → `CircularToSyllabusLink[]`

Plus 1 classifier:
- `ClassifyCircular(pdf_text, url)` → `CircularDepartment` (DES / NCCA / SEC / DOE_NI)

**Historical note**: The legacy function names `ExtractLeavingCertSyllabus`, `ExtractLeavingCertPastPaper`, `ExtractLeavingCertMarkingScheme`, `ClassifyOfficialMedia` have been retired. Use the canonical `ExtractCurriculumSyllabus` + `ExtractExamPaperLayout` + `ExtractMarkingSchemeGuideline` + the per-stage functions.

## The 11 BAML test blocks

11 test blocks exist (per the `baml-cli test --from baml_src` discovery):

| File | Test function |
|:--|:--|
| `processing/ocr_registry_test.baml` | `test GetOptimalForM4`, `test SelectOCRBackend` (2 tests) |
| `processing/ocr_extraction.baml` | `test ExtractHiddenHeritagesTale` |
| `processing/ocr_validation.baml` | `test ValidateOCRResult`, `test CompareOCRModels` (2 tests) |
| `british_isles/wales/education/subject_taxonomy.baml` | `test ExtractWalesSyllabus` |
| `british_isles/jersey/education/subject_taxonomy.baml` | `test ExtractJerseySyllabus` |
| `british_isles/guernsey/education/subject_taxonomy.baml` | `test ExtractGuernseySyllabus` |
| `british_isles/northern_ireland/education/subject_taxonomy.baml` | `test ExtractNIExamPaper` |
| `british_isles/scotland/education/subject_taxonomy.baml` | `test ExtractScotlandSyllabus` |
| `british_isles/isle_of_man/education/subject_taxonomy.baml` | `test ExtractIsleOfManSyllabus` |

## The Celtic cluster

`celtic/` houses the Irish-language + Celtic-nation extraction:

- `gaois/duchas.baml` — Schools Collection + Manuscripts + Photographs + Persons
  (the canonical Duchas collection enum + 9 occupations + 16+ topic codes from the Handbook of Irish Folklore)
- `gaois/logainm.baml` — Placenames Database of Ireland (34 Irish county codes + 7 administrative unit categories)
- `gaois/tearma.baml` — National Terminology Database extraction
- `gaois/folklore_extraction.baml` — Folklore extraction (separate from `duchas.baml`'s source parsing)
- `curriculum/celtic_curriculum.baml` — Celtic-nation curriculum
- `curriculum/mythology_extraction.baml` — Mythology
- `grammar_patterns.baml` — Irish grammar (VSO, copula, mutation, genitive, etc. + 8 IrishCopulaType values)
- `morphology.baml` — Irish morphology (verb conjugation + noun declension)
- `sources.baml` — Source-agnostic unified record (CelticLanguage + FolkloreSource + MediaType + IrishDialect enums)
- `_archive/celtic_linguistics.baml` — ARCHIVED 2026-06-24 (3 functions: `ExtractMorphology` + `AnalyzeSentence` + `IdentifyDialect`)
- `_archive/cognates.baml` — ARCHIVED 2026-06-24 (5 functions: `IdentifyCognates` + `CompareCelticVocabulary` + `IdentifyFalseFriends` + `ExplainSoundChanges` + `GenerateCognateVocabulary`)

### Re-activation procedure for `_archive/` files

Per the archived-header procedure in each file:

1. Implement the consumer (e.g. `agents/meaisinfhoghlaim/agents/celtic_linguistics.py`)
2. `git mv baml_src/celtic/_archive/<file>.baml baml_src/celtic/`
3. Remove the `ARCHIVED` header from the top
4. Update `openspec/specs/oideachais-baml-schemas/spec.md` to mark the functions as wired
5. Run `baml-cli generate` to regenerate the BAML client

## The Processing cluster (33 files)

| File | Purpose |
|:--|:--|
| `email.baml` | leabharlann email-inbox pipeline (`ClassifyEmail` + `ExtractEmailThread` + `LinkEmailToResearch`) |
| `ocr_extraction.baml` | Hidden Heritages HTR/OCR (the Celtic-nation Hidden Heritages tale corpus) |
| `ocr_validation.baml` | OCR vs ground truth + Irish-specific quality (`IrishContentQuality` + `FadaError` + `DialectIndicator` + `CommonIrishError` + `IrishOCRErrorType`) |
| `ocr_registry_test.baml` | The 2 BAML test blocks (`GetOptimalForM4` + `SelectOCRBackend`) |
| `upstream_monitoring.baml` | 4 upstream packages (motherduck / dlthub / lancedb / cocoindex) |
| `image_generation.baml` | Bria FIBO image generation |
| `style_transfer.baml` | FIBO style transfer |
| `game_content.baml` | MMO game content (NPCs + locations + items) |
| `player_assessment.baml` | MMO player assessment |
| `generators.baml` | MMO FIBO generators |
| `official_media.baml` | Official media classification |
| `cv_extraction.baml` | CV / achievements / teaching |
| `portfolio_extraction.baml` | Portfolio |
| `linkedin_profile_extraction.baml` | LinkedIn per croilar personas |
| `researchgate_extraction.baml` | ResearchGate per croilar |
| `artwork_analysis.baml` | Artwork analysis |
| `author_archive.baml` | Gemini Deep Research PDF extraction |
| `circular_extraction.baml` | Generic circular (vs BIEP-specific at `british_isles/.../lc_extraction/circular_extraction.baml`) |
| `identity_verification.baml` | Identity docs + Garda vetting |
| `audio_extraction.baml` | Canúint audio recordings |
| `named_entities.baml` | NER |
| `site_analysis.baml` | Site analysis |
| `ui_components.baml` | UI component generation |
| `teaching_extraction.baml` | Teaching CV |
| `culture_extraction.baml` | Cultural heritage claims |

Plus 5 in `_shared/`: `document_type.baml` + `language_codes.baml` + `music_genre.baml` + `video_kg.baml` + the canonical type enums.

## Cluster rationale

- **`british_isles/`** is the **flagship** — 8 BI nations × {education, law, medicine, statistics} + the BIEP canonical LC extraction functions. This is what the BIEP v1 / v2 / v3 specs all target.
- **`european_nations/`** is the **40-nation template** — every EU/EEA nation gets the same `education + law + medicine + statistics` shape.
- **`european_union/`** is the **EU institutional layer** — EUR-Lex + CEDEFOP + ECDC + EMA + Eurostat + Eurydice.
- **`commonwealth/`** is the **6-nation Commonwealth layer** — Australia + Canada (12 provinces + Quebec/Montreal) + India + New Zealand + Nigeria (federal + 36 states) + South Africa.
- **`american_nations/`** is the **4-nation Americas layer** — Brazil + Mexico + US (California) + Venezuela.
- **`celtic/`** is the **Celtic / Irish-language extraction layer** — Duchas + Logainm + Tearma + Celtic-nation curriculum + Irish grammar + the 2 archived files.
- **`processing/`** is **generic file processing** that doesn't fit into the jurisdictional clusters — email triage + CV/portfolio/LinkedIn/ResearchGate extraction + OCR + MMO game content + etc.

## Multi-nation jurisdictions

### `european_nations/` — 40 nations (122 .baml)

`european_nations/{nation}/{education,law,medicine}.baml` is the universal template (germany/education.baml shown below):

```baml
class DEUEducationDocument {
  kmk_id string @description("...")
  country_code string @description("ISO 3166-1 alpha-3 (lowercase)")
  language string @description("...")
  title string
  summary string?
  publication_date string?
  source_url string
  content_hash string?
}

function ExtractDEUEducationDocument(
  country_code: string, language: string, text: string
) -> DEUEducationDocument {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}
```

40 nations: albania, austria, belgium, bosnia_and_herzegovina, bulgaria, croatia, cyprus, czechia (was `cze`), denmark, estonia, finland, france, georgia, germany, greece, hungary, iceland, italy, **kosovo** (was `xkx`), latvia, liechtenstein, lithuania, luxembourg, malta, moldova, montenegro, netherlands, **north_macedonia** (was `mkd`), norway, poland, portugal, romania, serbia, slovakia, slovenia, spain, sweden, switzerland (was `che`), turkey, ukraine.

Plus `european_nations/_shared/`:
- `jurisdiction.baml` — the shared `NationJurisdictionMetadata` class + `ExtractNationJurisdictionMetadata` function

### `european_union/` — 9 .baml (already listed above)

### `british_isles/` — 103 .baml

### `commonwealth/` — 24 .baml

6 nations (australia + canada (12 provinces + quebec/montreal) + india + new_zealand + nigeria (federal + state + states/_states) + south_africa) + `_shared/` (2 .baml).

### `american_nations/` — 15 .baml

4 nations (brazil + mexico + united_states + venezuela) + `_shared/` (2 .baml).

## Cross-references

- [`../openspec/specs/oideachais-baml-schemas/spec.md`](../openspec/specs/oideachais-baml-schemas/spec.md) — the canonical spec
- [`../.agents/skills/baml/SKILL.md`](../.agents/skills/baml/SKILL.md) — BAML extraction patterns
- [`../agents/AGENTS.md`](../agents/AGENTS.md) — the agents quadrant overview (the primary consumer of `baml_client`)
- [`../orchestration/README.md`](../orchestration/README.md) — the Dagster orchestration layer (consumes BAML via `BAMLGenerationResource`)
- [`../dlt_sources/AGENTS.md`](../dlt_sources/AGENTS.md) — the DLT ingestion layer (consumes BAML via the BAML-driven `BIEPDLTResource`)