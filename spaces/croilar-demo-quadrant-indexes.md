---
title: "Croílár Demo — Per-Quadrant Asset Index"
domain: hackathons
status: draft
description: "Per-quadrant indexes of the existing Cianfhoghlaim monorepo assets (BAML schemas, source code, datasets, agents, services) that the 4 Hackathon Spaces will reuse. Maps the demo's required features to the source-of-truth files in oideachais/, meaisínfhoghlaim/, tuatha/, croílár/, and infrastructure/."
entities:
  - OideachaisQuadrant
  - MeaisínfhoghlaimQuadrant
  - TuathaQuadrant
  - CroílárQuadrant
  - BuildSmall2026
related_skills:
  - .agents/skills/oideachas-pipeline/SKILL.md
  - .agents/skills/cognate-db/SKILL.md
  - .agents/skills/ccc/SKILL.md
ccc_query_hints:
  - "oideachais BAML leaving cert leaving certificate"
  - "meaisínfhoghlaim OCR fada gaelic-metrics"
  - "tuatha BAML mythology anam Celtic MMO"
  - "croilar 2-persona al eyum cianfhoghlaim i18n"
  - "liteLLM gateway alias irish"
last_reviewed: 2026-06-08
---

# Croílár Demo — Per-Quadrant Asset Index

> Per-quadrant indexes pointing at the existing Cianfhoghlaim monorepo assets that the 4 Hackathon Spaces will reuse. Companion to `build-small-2026-docs-catalogue.md`.

---

## Index 1: `oideachais/` quadrant — assets for **Space 1 (An Scrúdú)**

The oideachais quadrant is the **offline-first ELT engine** that ingests Irish, UK, and pan-Celtic education data — NCCA syllabi, SEC exam papers and marking schemes, Chief Examiner reports, Department of Education circulars — through a unified DuckDB/DuckLake core. Space 1 (An Scrúdú) builds on top of this.

### 1.1 BAML extraction schemas (the typed spine)

Located in `oideachais/data_platform/baml_src/`:

| BAML file | Key class | Function | Reuse by |
|:--|:--|:--|:--|
| `curriculum_extraction.baml:7-14` | `CurriculumTopic` | `ExtractCurriculumSyllabus(pdf_text) → CurriculumExtraction` | Space 1 syllabus drill-down |
| `curriculum_extraction.baml:16-22` | `CurriculumExtraction` | same | Space 1 |
| `leaving_cert_past_paper_extraction.baml:9-19` | `PastExamQuestion` | `ExtractPastPaper(pdf_text) → PastPaper` | Space 1 past paper viewer + Space 3 + Space 4 (Mac Léinn) |
| `leaving_cert_past_paper_extraction.baml:21-28` | `PastPaper` | same | all |
| `leaving_cert_marking_scheme_extraction.baml:8-14` | `MarkingPoint` | `ExtractMarkingScheme(pdf_text) → MarkingScheme` | Space 1 PCLM marking navigator + Space 4 (Fiosraigh) |
| `leaving_cert_marking_scheme_extraction.baml:15-21` | `CommonMistake` | same | Space 1 "common mistake bank" |
| `leaving_cert_marking_scheme_extraction.baml:22-28` | `MarkingAllocation` | same | Space 1 |
| `leaving_cert_marking_scheme_extraction.baml:29-37` | `MarkingScheme` | same | Space 1 |
| `leaving_cert_syllabus_extraction.baml:13-26` | `SyllabusTopic`, `LeavingCertSyllabus` | `ExtractLeavingCertSyllabus(pdf_text)` | Space 1 syllabus heatmap |
| `clients.baml:12-46` | `LitellmClient`, `DeepSeekClient`, `MiniMaxClient`, `LitellmLongContext` | (clients) | All 4 Spaces (fork to `clients_hackathon.baml` for HF Inference re-pointing) |

**To add (new BAML, ~30-40 lines each):**
- `ExtractCircularMeta` — from `docs/03-agents/baml-extraction.md:508-524`
- `GenerateExitCardQuestions` — from Space 1's "5 NEW features" in the catalogue
- `ScoreExitCardResponse` — modelled on `ResponseAnalysis` from `tuatha/baml_src/player_assessment.baml:31`
- `ComposeMarkingSchemeDiff` — takes two `MarkingScheme` objects, emits `RubricDelta`
- `ExtractPrimaryFramework` — from `docs/03-agents/baml-extraction.md:387-425` (Junior Infants → 6th Class)

### 1.2 DLT source code (the ingestion layer)

Located in `oideachais/data_platform/dlt_sources/`:

| Sub-tree | Key file | Purpose | Reuse by |
|:--|:--|:--|:--|
| `ireland/` | `examinations.py` (SEC scraper cascade with `?fp=` URL handling) | Web scraper for `examinations.ie` ASP.NET progressive-disclosure | Space 1, Space 4 (Tine) |
| `ireland/` | `pdf_downloader.py` | PDF cache | all |
| `ireland/` | `subjects/senior_cycle.py`, `junior_cycle.py` | Per-subject extraction | Space 1 |
| `ireland/` | `parallel_corpus.py` | Bilingual ga↔en corpus | Space 2 (Aer) |
| `ireland/` | `agentic_discovery.py` | Agent-driven scrape | Space 4 |
| `uk/` | `england/`, `wales/`, `scotland/`, `northern_ireland/` | 7-nation DLT sources | Space 2 (Curaclam Trasteorann) |
| `celtic/` | `duchas.py`, `canuint.py`, `tearma.py`, `gaois.py`, `universal_dependencies.py` | 6 Celtic language DLT sources | Space 2 (Foclóir) |
| `geospatial/` | `cso_small_areas.py:342-371` | HP Deprivation Index 2022 + DEIS schools | Space 2 (Scoil ar an Léarscáil), Space 4 (Talamh) |
| `geospatial/` | `geohive.py:56-58` | 18,641 Small Areas + 26 counties + 3,440 EDs | Space 2 + Space 4 |
| `geospatial/` | `met_office.py:83-102` | 18 hardcoded UK + IE weather stations | Space 2 + Space 4 |
| `crown_dependencies/` | `isle_of_man.py`, `channel_islands.py` | DESC IoM + Jersey + Guernsey | Space 2 (Scoil ar an Léarscáil) |
| `constants/` | `education_sources.py` | Master ED source URL table | all 4 Spaces |
| `constants/` | `local_sources.py` | Local dev sources | dev only |

### 1.3 Dagster assets (the orchestration layer)

Located in `oideachais/data_platform/dagster_defs/`:

| Asset | Purpose | Reuse by |
|:--|:--|:--|
| `assets/ireland/curriculum_assets.py` | 4 cycle assets (Aistear, Primary, JC, SC) × 33 subjects × 2 languages | Space 1 |
| `assets/ireland/exam_materials_assets.py:56-62` | 3 cycle assets (LC, JC, LCA) — partition: subject × material_type | Space 1 |
| `assets/ireland/exam_materials_assets.py:101-107` | **DEPRECATED:** `ncca_multipartitions` + `sec_multipartitions` (use `partitions_v2`) | none — see Known Drift |
| `assets/ireland/asset_generation.py:1-80` | BAML → FIBO image gen pipeline | Space 4 (Uisce) |
| `resources.py` | `LiteLLMResource` | all 4 Spaces |

### 1.4 Samplaí (sample corpora)

Located in `oideachais/samplaí/`:

| File | Language | ISO | Scope |
|:--|:--|:--|:--|
| `gaeilge/irish_samples.yaml` (257 lines) | Irish | ga | Dictionary, verb conjugations, terminology, placenames, folklore, UD treebank |
| `cymraeg/welsh_samples.yaml` (238 lines) | Welsh | cy | Corpus, dictionary, spelling, voice commands, MT examples, terminology |
| `gaidhlig/scottish_gaelic_samples.yaml` (252 lines) | Scottish Gaelic | gd | Corpus, POS, dictionary, folklore, morphological analysis |
| `brezhoneg/breton_samples.yaml` (80 lines) | Breton | br | Dictionary (French pivot), terminology, IPA, sample sentences |
| `gaelg/manx_sample.yaml` (107 lines) | Manx | gv | Historical + modern texts, dictionary, cross-Goidelic translations, UD |
| `kernowek/cornish_samples.yaml` (71 lines) | Cornish | kw | Greetings, dictionary, example sentences |
| `cognates.yaml` (88 lines) | all 6 | (cross-Celtic) | Greetings + basic vocab + numbers 1-5 in 6 languages |

**Reuse:** Space 2 (Foclóir na Sé Náisiún) seeds the cognate table from `cognates.yaml`. Space 4 (Aer) trains on these for language coverage.

### 1.5 Document factory (the formatters)

Located in `oideachais/document_factory/`:

| File | Key class | Reuse by |
|:--|:--|:--|
| `curriculum_document.py:55-78` | `LearningOutcome` | Space 1 syllabus extraction |
| `curriculum_document.py:80-98` | `AssessmentInfo` | Space 1 + Space 4 (Mac Léinn) |
| `curriculum_document.py:143-310` | `CurriculumDocument` | Space 1 syllabus export |
| `curriculum_document.py:251-309` | completeness scoring | Space 1 |
| `curriculum_document.py:344-432` | `to_graph_nodes/edges` | Space 1 + Space 2 (knowledge graph) |
| `pdf_factory.py` | PDF emitter | Space 1 (PCLM pack) |
| `format_detectors.py` | format detection | Space 1 |
| `metrics_db.py` | quality metrics | Space 1 |

### 1.6 Quality + completeness

Located in `oideachais/quality/`:

| File | Reuse by |
|:--|:--|
| `content_quality.py` — `ContentQualityAssessor` | Space 1 (syllabus coverage scoring) |
| `completeness.py` — `CompletenessScorer` | Space 1 (LO coverage) |
| `canuint_validator.py:27-55` — `IRISH_PHONEME_INVENTORY` | Space 2 (Aer pronunciation) |

### 1.7 Documented CELT/folk sources

- `oideachais/samplaí/cognates.yaml` (cross-Celtic dictionary, 6 languages)
- `oideachais/quality/canuint_validator.py` (50+ Irish phonemes)
- `oideachais/data_platform/dlt_sources/ireland/source_adapters.py:36-69` — `NormalizedPage` dataclass

### 1.8 Training (Unsloth + Qwen2-VL)

Located in `oideachais/training/`:

| File | Reuse by |
|:--|:--|
| `unsloth_trainer.py` | Space 4 (Tine OCR fine-tuning) |
| `unsloth_config.py` | Space 4 |
| `htr_training.py` | Space 4 (Tine HTR) |
| `llm_training.py` | Space 4 (Aer language model fine-tuning) |
| `tts_dataset_generator.py` | Space 2 (Aer TTS) |
| `tts_training.py` | Space 2 |

### 1.9 Asset generation (BAML → FIBO)

Located in `oideachais/asset_generation/`:

| File | Purpose | Reuse by |
|:--|:--|:--|
| `service.py` | Asset generation service | Space 4 (Uisce) |
| `models.py` | AssetType + CelticStyle enums | Space 4 (Uisce) |
| `prompts.py` | CelticPromptGenerator | Space 4 (Uisce) |
| `exporters/babylon_exporter.py:522-542` | WGSL knotwork export | Space 3 |

### 1.10 Stedding/ (cached scrapes)

| Path | Content | Reuse by |
|:--|:--|:--|
| `stedding/site_scrape_samples/` | Cached DLT extracts | Space 1 (offline fallback) |
| `stedding/huggingface/hub/` | HF model cache | Space 4 (Tine) |
| `stedding/huggingface/gguf/` | GGUF model cache | not used (HF Inference) |
| `stedding/dev/eile/ingest_queue/` | Cached Dúchas / Téarma / Gaois extracts | Space 2 (Foclóir) |

### 1.11 Evaluation (RAGAS)

Located in `oideachais/evaluation/`:

| File | Reuse by |
|:--|:--|
| `ragas_pipeline.py` (754 lines) | Space 2 (Curaclam Trasteorann) — adapted |
| `run_evaluation.py` | Space 2 (Curaclam Trasteorann) — adapted |

---

## Index 2: `meaisínfhoghlaim/` quadrant — assets for **Space 2 (Meaisín Cliste) + Space 4 (Tine OCR)**

The meaisínfhoghlaim quadrant is the **AI brain**: 12 specialised agents, 10 OCR models, 6 Celtic languages, RAGAS evaluation (65.2% → 87.9% agentic), content quality gating. Space 2 builds on all of this.

### 2.1 12 specialised agents

Located in `meaisínfhoghlaim/agents/`:

| Agent | File | Framework | Reuse by |
|:--|:--|:--|:--|
| `root_agent.py` (212-369) | QueryRouter with `KEYWORD_MAP` (5 domains: curriculum, translation, corpus, research, geospatial) | Custom + LiteLLM | Space 2 (Curaclam Trasteorann) |
| `root_agent.py:253-254` | `ROUTING_MODEL = "gemini-2.0-flash"` | LiteLLM | Space 2 |
| `root_agent.py:573-592` | `RootAgent.stream()` | Custom | Space 2 |
| `curriculum_agent.py` | LanceDB vector search + DuckDB LO queries | Custom | Space 2 (Foclóir) |
| `translation_agent.py:60-84` | 6 Celtic languages, 3 model backends (opus-mt, m2m100, NLLB) | Custom | Space 2 (Foclóir) |
| `corpus_agent.py` | Dúchas folklore search, dictionary lookup | Custom | Space 2 (Foclóir) |
| `research_agent.py` | Iterative search → evaluate → compose with citations | Google ADK | Space 2 (Curaclam Trasteorann) |
| `education_research_agent.py` | Cross-nation (IE/UK) education policy research | Google ADK LoopAgent | Space 4 (Talamh) |
| `bunchloch_research_agent.py` | Local academic document research | Google ADK SequentialAgent | Space 4 (Talamh) |
| `geospatial_agent.py` | LSOA/Data Zone spatial analysis | Google ADK | Space 2 (Scoil ar an Léarscáil) |
| `statistics_agent.py` | Education metrics, trend analysis | Google ADK | Space 2 (Curaclam Trasteorann) |
| `curriculum_comparison_agent.py` | Cross-nation curriculum mapping | Google ADK | Space 2 (Curaclam Trasteorann) |
| `mcp_curriculum_agent.py` | chunkhound + zai-mcp + Cognee + Firecrawl + LanceDB | Custom MCP | Space 2 (all 3 themes) |
| `agui_curriculum_agent.py` | AG-UI protocol curriculum agent | Custom | Space 4 (Mac Léinn) |
| `voice_agent.py:18-30` | Real-time ASR → LLM → TTS (Whisper/wav2vec2 → LLM → ABAIR/Chatterbox) | Pipecat (replace with Web Speech API for Spaces) | Space 2 (Aer TTS demo) |
| `api/main.py` | FastAPI entry point | FastAPI | (replace with Gradio app.py) |
| `api/routes/`, `api/services/`, `api/storage/` | FastAPI sub-paths | — | (replace with Gradio) |
| `enhanced_orchestrator.py` | AG-UI protocol events | Custom | Space 4 (Mac Léinn) |
| `op_sync.py` | Agent ops sync | — | — |
| `tools/` | corpus_search, corpus_tools, curriculum_search, curriculum_tools, geospatial_tools, spatial_query, statistics_query, terminology, translation_tools | — | Space 2 |

### 2.2 OCR / HTR (the 10-model race)

Located in `meaisínfhoghlaim/ocr/`:

| File | Reuse by |
|:--|:--|
| `model_registry.py:330-543` — 10 OCR models × 6 backends | Space 2 + Space 4 (Tine) |
| `comparison_runner.py:95-165` — `ComparisonRunner.compare_single()` runs models in parallel | Space 4 (Tine) |
| `gaelic_metrics.py:195-242` — `GaelicMetrics.evaluate()` returns fada/tironian/punctum | Space 2 + Space 4 (Tine) |
| `gaelic_metrics.py:28-61` — Unicode NFC normalization | Space 2 + Space 4 |
| `gaelic_metrics.py:175-176`, `:322-357` — Fada accuracy metric | Space 4 (Tine) |
| `gaelic_metrics.py:178`, `:244-273` — Tironian et metric | Space 4 (Tine) |
| `gaelic_metrics.py:172`, `:275-320` — Punctum delens F1 | Space 4 (Tine) |
| `gaelic_metrics.py:140-163` — `GaelicEvaluationResult` | Space 4 (Tine) |
| `gaelic_metrics.py:359-391` — Batch evaluation | Space 4 (Tine) |
| `irish_processing.py:251-367` — `IrishOCRProcessor.process_with_fallback()` (auto-switches to UCCIX) | Space 4 (Tine) |
| `irish_processing.py:138-157` — `DIALECT_VOCABULARY` | Space 2 (Aer) |
| `irish_processing.py:494-537` — `_detect_dialect()` (Connacht/Munster/Ulster) | Space 2 (Aer) |
| `irish_htr_dataset.py` | Space 4 (Tine HTR) |
| `line_segmentation.py` | Space 4 (Tine) |
| `vision_comparison.py` | Space 4 (Tine) |
| `vlm_finetune_comparison.py:51-120` — VLM_MODELS dict | Space 4 (Tine) |
| `adapters.py` | Space 4 (Tine) |
| `pylaia_comparison.py` | Space 4 (Tine HTR) |
| `observability.py` | all |

**OCR models from `model_registry.py:330-439`:**
1. `olmOCR-2-7B` (Transformers)
2. `Qwen/Qwen2.5-VL-7B-Instruct` (Transformers)
3. `Qwen/Qwen2.5-VL-7B-Instruct` (MLX)
4. `deepseek-ai/deepseek-ocr` (Transformers)
5. `ibm-granite/granite-docling-base` (Transformers)
6. `gpt-4o` (OpenAI) — fallback only
7. `claude-3-5-sonnet-20241022` (Anthropic) — fallback only
8. `llama3.2-vision:11b` (Ollama)
9. `ReliableAI/UCCIX-Llama2-13B-Instruct` (LiteLLM)
10. (Plus VLM fine-tune variants from `vlm_finetune_comparison.py:51-120`: `glm-4.6v-flash`, `qwen3-vl-7b`, `qwen3-vl-30b`, `gemma-3`)

### 2.3 Evaluation (RAGAS, the 22.7pp headline)

Located in `meaisínfhoghlaim/evaluation/`:

| File | Reuse by |
|:--|:--|
| `ragas_pipeline.py:135-411` — `AgenticRagEvaluator` (4-step: generate_search_queries → retrieve_contexts → synthesize_answer → self_correct) | Space 2 (Curaclam Trasteorann Q&A) — adapted to 12 agents |
| `ragas_pipeline.py:418-534` — 10 template questions (Junior + Senior Cycle) | Space 2 |
| `ragas_pipeline.py:537-702` — `run_baseline_evaluation()` + `run_agentic_evaluation()` | Space 2 |
| `ragas_pipeline.py:705-754` — `compare_evaluation_runs()` (the 22.7pp delta) | Space 2 |
| `run_evaluation.py:304` | Space 2 |

**DEPRECATED:** `datetime.utcnow()` at `ragas_pipeline.py:65` → use `datetime.now(datetime.UTC)`.

### 2.4 Quality (the content gating pipeline)

Located in `meaisínfhoghlaim/quality/`:

| File | Reuse by |
|:--|:--|
| `content_quality.py` — `ContentQualityAssessor` | Space 2 |
| `completeness.py` — `CompletenessScorer` | Space 2 + Space 4 (Mac Léinn) |
| `canuint_validator.py:27-55` — `IRISH_PHONEME_INVENTORY` | Space 2 (Aer pronunciation) |
| `canuint_validator.py:57-62` — `MIN_PHONEME_COVERAGE` | Space 2 |

### 2.5 ML pipelines (4 end-to-end)

Located in `meaisínfhoghlaim/pipelines/`:

| File | LOC | Reuse by |
|:--|--:|:--|
| `irish_document_scanner.py` | 734 | Space 4 (Tine) |
| `dialect_classifier.py:67-210` — `AcousticDialectClassifier` (3 methods: acoustic+Wav2Vec2+Whisper) | Space 2 (Aer) |
| `transcript_aligner.py` (350+) | 350 | Space 2 (Aer) |
| `llm_router.py` | 325 | Space 2 (all) |

### 2.6 Alignment

Located in `meaisínfhoghlaim/alignment/`:

| File | Reuse by |
|:--|:--|
| `aligner.py` — `IrishEnglishAligner` (sentence-transformers + DP) | Space 2 (Aer) |
| `colpali_aligner.py` | Space 2 (Aer) |
| `irish_g2p.py:33-38` — IPA / X-SAMPA / SAMPA formats | Space 2 (Aer) |
| `irish_g2p.py:40-46` — `IrishDialect` enum (CONNACHT, MUNSTER, ULSTER, STANDARD) | Space 2 (Aer) |
| `irish_g2p.py:76-150` — `IRISH_PHONEME_RULES` (grapheme→IPA) | Space 2 (Aer) |
| `dataset_generator.py` | Space 2 (Aer) |
| `canuint_exporter.py` | Space 2 (Aer) |
| `export.py` | Space 2 (Aer) |
| `quality.py` | Space 2 (Aer) |
| `character_interpolator.py` | Space 4 (Tine HTR) |

### 2.7 Celtic language data (6 languages)

Located in `meaisínfhoghlaim/language/`:

| File | Reuse by |
|:--|:--|
| `gaeilge/duchas.py` — DLT source for Dúchas Schools' Collection (~750K records) | Space 2 (Foclóir) |
| `gaeilge/duchas_images.py` | Space 4 (Tine OCR) |
| `gaeilge/canuint.py` — DLT source for Canúint (~5K dialect audio) | Space 2 (Aer) |
| `gaeilge/tearma.py` | Space 2 (Foclóir) |
| `gaeilge/gaois.py` | Space 2 (Foclóir) |
| `gaeilge/universal_dependencies.py:24-45` — 11 treebanks across 7 langs | Space 2 (Foclóir) |
| `gaeilge/universal_dependencies.py:173-215` — `dependency_relations_resource` (per-language aggregation) | Space 2 (Foclóir) |
| `gaeilge/` (more files) | Space 2 |
| `gaidhlig/` (Scottish Gaelic samples) | Space 2 (Foclóir) |
| `cymraeg/` (Welsh samples) | Space 2 (Foclóir) |
| `brezhoneg/` (Breton samples) | Space 2 (Foclóir) |
| `gaelg/` (Manx samples) | Space 2 (Foclóir) |
| `kernowek/` (Cornish samples) | Space 2 (Foclóir) |
| `cognates.yaml` | Space 2 (Foclóir) |

### 2.8 Model + data catalog

Located in `meaisínfhoghlaim/catalog/`:

| File | Reuse by |
|:--|:--|
| `models.yaml` (126 lines, 13 models) | Space 2 + Space 4 |
| `sources.yaml` (153 lines, 16 sources + 3 training mixes) | Space 2 |

### 2.9 Services (FastAPI wrappers)

Located in `meaisínfhoghlaim/services/`:

| File | Reuse by |
|:--|:--|
| `agent_fastapi.py:16-20` — `FastAPI(title="meaisínfhoghlaim agents")` | (replaced by Gradio) |
| `pipeline_fastapi.py:9-13` | (replaced by Gradio) |
| `celery_worker.py` | (not needed for HF Spaces) |

### 2.10 Compose + config

Located in `meaisínfhoghlaim/`:

| File | Reuse by |
|:--|:--|
| `compose.yaml` — llama-swap on 0.0.0.0:8080 | (replaced by HF Inference for chat) |
| `llama-swap-config.yaml` — 11 models, 3 profiles (text / vision / image) | (replaced by HF Inference aliases) |
| `pangolin.yaml` | (infrastructure archived for this hackathon) |
| `secrets.env` | (secrets via Infisical) |

### 2.11 Scripts

Located in `meaisínfhoghlaim/scripts/`:

| File | Reuse by |
|:--|:--|
| `download_hf_models.sh` | (not needed — HF Inference) |
| `convert_hf_to_gguf.sh` | (not needed — HF Inference) |

### 2.12 Staleness notes (from ccc audit)

- `meaisínfhoghlaim/AGENTS.md:30-32` references `agents/orchestrator.py` and `agents/registry.py` which do not exist. Real entry is `agents/root_agent.py`.
- `meaisínfhoghlaim/pyproject.toml` does not exist (logical quadrant, not a workspace member).
- `pipelines/irish_document_scanner.py:19` references Confluent Kafka; real path is RisingWave.
- `root_agent.py:16` references Datadog LLMObs; real observability is Langfuse.
- `evaluation/ragas_pipeline.py:65` uses `datetime.utcnow()` (deprecated in Python 3.12).

---

## Index 3: `tuatha/` quadrant — assets for **Space 3 (Cianfhoghlaim) + Space 4 (Anam)**

The tuatha quadrant is the **Celtic Educational MMO** — SpacetimeDB real-time game state, Babylon.js/wgpu/WebGPU client, Bria FIBO image gen, 5 mythology cycles, Anam soulbound credentials, 4 Bardic ranks, pent-elemental magic system, x402 micropayments.

### 3.1 BAML schemas (the game content)

Located in `tuatha/baml_src/`:

| File | Key classes | Reuse by |
|:--|:--|:--|
| `player_assessment.baml:4-11` | `ProficiencyLevel` (A1-C2 CEFR), `AssessmentType`, `SkillDomain` | Space 3 + Space 4 (Mac Léinn) |
| `player_assessment.baml:20-35` | `PlayerLanguageProfile` | Space 3 |
| `player_assessment.baml:55-70` | `ResponseAnalysis` | Space 3 + Space 4 |
| `player_assessment.baml:94-122` | `AnalyzePlayerResponse()` function | Space 3 |
| `player_assessment.baml:124-137` | `AdaptiveAssessment` | Space 3 + Space 4 |
| `player_assessment.baml:139-157` | `AdaptiveQuestion` | Space 3 + Space 4 |
| `player_assessment.baml:159-187` | `GenerateAdaptiveAssessment()` | Space 3 + Space 4 |
| `player_assessment.baml:190-204` | `PlacementResult` | Space 3 |
| `player_assessment.baml:206-237` | `EvaluatePlacementTest()` | Space 3 |
| `player_assessment.baml:248-265` | `ProgressReport` | Space 4 (dashboard) |
| `player_assessment.baml:285-314` | `GenerateProgressReport()` | Space 4 |
| `celtic_curriculum.baml:4-11` | `CelticLanguage` enum (IRISH, SCOTTISH_GAELIC, WELSH, MANX, CORNISH, BRETON) | Space 2 (Foclóir) + Space 3 |
| `celtic_curriculum.baml:29-35` | `LearningOutcome` | Space 3 + Space 4 |
| `celtic_curriculum.baml:37-44` | `GrammarTopic` | Space 3 |
| `celtic_curriculum.baml:53-57` | `VocabularySet` | Space 2 (Foclóir) |
| `celtic_curriculum.baml:59-68` | `CelticWord` | Space 2 (Foclóir) |
| `celtic_curriculum.baml:70-84` | `CurriculumUnit` | Space 3 + Space 4 |
| `celtic_curriculum.baml:87-103` | `ExtractCurriculumUnit()` | Space 3 + Space 4 |
| `celtic_curriculum.baml:106-120` | `ExtractGrammarTopic()` | Space 3 |
| `celtic_curriculum.baml:122-138` | `ExtractVocabulary()` | Space 2 (Foclóir) |
| `celtic_curriculum.baml:141-146` | `OutcomeAssessment` | Space 3 + Space 4 |
| `celtic_curriculum.baml:148-156` | `AssessmentQuestion` (with `distractors`) | Space 4 (Mac Léinn) |
| `celtic_curriculum.baml:158-176` | `GenerateAssessment()` | Space 3 + Space 4 |
| `celtic_curriculum.baml:179-186` | `CurriculumComparison` | Space 2 (Curaclam Trasteorann) |
| `celtic_curriculum.baml:188-214` | `CompareCurricula()` | Space 2 (Curaclam Trasteorann) |
| `mythology_extraction.baml:4-12` | `CelticTradition` enum (7 traditions) | Space 3 |
| `mythology_extraction.baml:14-22` | `MythologicalCycle` enum (TUATHA_DE_DANANN, FIANNA, ULSTER, KINGS, MABINOGION, ARTHURIAN, FOLK) | Space 3 |
| `mythology_extraction.baml:24-36` | `CharacterType` enum (DEITY, HERO, DRUID, BARD, KING, WARRIOR, FAIRY, etc.) | Space 3 |
| `mythology_extraction.baml:38-58` | `MythologicalCharacter` | Space 3 (all 6 NPCs) |
| `mythology_extraction.baml:67-71` | `CharacterRelationship` | Space 3 (Rhiannon's Justice) |
| `mythology_extraction.baml:73-86` | `MythologicalLocation` | Space 3 (map zones) |
| `mythology_extraction.baml:88-104` | `MythologicalStory` | Space 3 (Déisi Living Epic) |
| `mythology_extraction.baml:122-137` | `ExtractMythologicalCharacter()` | Space 3 |
| `mythology_extraction.baml:140-154` | `ExtractMythologicalStory()` | Space 3 |
| `mythology_extraction.baml:156-171` | `ExtractMythologicalLocation()` | Space 3 |
| `mythology_extraction.baml:174-187` | `NPCDialogue`, `DialogueLine` | Space 3 |
| `mythology_extraction.baml:189-219` | `GenerateNPCDialogue()` | Space 3 (all 6 NPCs) |
| `mythology_extraction.baml:222-243` | `FolkloreElement` | Space 3 |
| `game_content.baml:8-16` | `AssetType` enum (CHARACTER_PORTRAIT, ITEM_ICON, CLAN_HERALDRY, TERRITORY_TILE, SPELL_EFFECT, CREATURE) | Space 4 (Uisce) |
| `game_content.baml:18-25` | `CelticStyle` enum (LA_TENE, OGHAM, KNOTWORK, ZOOMORPHIC, SPIRAL, ILLUMINATED) | Space 4 (Uisce) |
| `game_content.baml:21-28` | `GameZoneType` enum (TUTORIAL, GAELTACHT, GAIDHEALTACHD, WELSH_SPEAKING, MYTHOLOGICAL, OTHERWORLD) | Space 3 (map zones) |
| `game_content.baml:30-50` | `Quest` | Space 3 |
| `game_content.baml:52-61` | `QuestObjective` | Space 3 |
| `game_content.baml:63-69` | `CelticContent` | Space 3 |
| `game_content.baml:71-76` | `QuestHint` | Space 3 |
| `game_content.baml:78-83` | `QuestReward` | Space 3 |
| `game_content.baml:86-115` | `GenerateLanguageQuest()` | Space 3 |
| `game_content.baml:118-147` | `GenerateMythologyQuest()` | Space 3 |
| `game_content.baml:150-172` | `NPC` | Space 3 |
| `game_content.baml:181-209` | `GenerateNPC()` | Space 3 |
| `game_content.baml:212-233` | `GameLocation` | Space 3 |
| `game_content.baml:244-272` | `GenerateGameLocation()` | Space 3 |
| `game_content.baml:275-293` | `GameItem` | Space 3 |
| `game_content.baml:295-317` | `GenerateGameItem()` | Space 3 |
| `tuatha_clients.baml:5-79` | Client definitions | (re-point to `clients_hackathon.baml`) |

**To add (new BAML, ~60 lines each):**
- `ExtractWikipediaArticle` — extended `MythologicalCharacter` for Wikipedia ingestion (Space 3)
- `EvaluateRiddleResponse` — modelled on `MarkingPoint` (Space 3 Manannán's Trial)

### 3.2 NPC roster (the 6 Wikipedia-informed NPCs)

| # | NPC | Location | Wikipedia source | File:line ref |
|--:|:--|:--|:--|:--|
| 1 | **Uí Liatháin lord** | Loughcrew, Co. Meath | `ga:Uí_Liatháin` | cached at `doc/hackathons/wikipedia-sources/ga-ui-liathain.md` |
| 2 | **Brec / Óengus** | Rathmore, Co. Wicklow | `en:The_Expulsion_of_the_Déisi` | cached at `doc/hackathons/wikipedia-sources/expulsion-desii.md` |
| 3 | **Manannán mac Lir** | Isle of Man | `en:Manannán_mac_Lir` | cached at `doc/hackathons/wikipedia-sources/manannan-mac-lir.md` |
| 4 | **Rhiannon** | Prysgwyddion, Dyfed | `en:Rhiannon` | cached at `doc/hackathons/wikipedia-sources/rhiannon.md` |
| 5 | **Dian Cécht** | the Leinster Healing Well | `en:Dian_Cecht` | cached at `doc/hackathons/wikipedia-sources/dian-cecht.md` |
| 6 | **Cian** | Loughcrew, Co. Meath (same cairn as Uí Liatháin) | `en:Cian` | cached at `doc/hackathons/wikipedia-sources/cian.md` |

### 3.3 The 4 mythology cycles (diegetic zones)

| Cycle | Centrepiece | Key characters | Reuse by |
|:--|:--|:--|:--|
| **Tuatha Dé Danann** (Mythological) | Brú na Bóinne, Tara, Moytura | the Dagda, Lugh, Nuada, the Morrígan, Brigid, Manannán, Aengus, Ogma, Dian Cécht, Balor | Space 3 (centred) + Space 4 |
| **Ulster** | Emain Macha, Cooley | Cú Chulainn, Medb, Conchobar, Deirdre, Fergus | Space 3 |
| **Fenian** | Cnoc Alúine, Tara, Leinster | Fionn, Oisín, Diarmuid, Gráinne, Caílte | Space 3 (deprioritised per user) |
| **Mabinogion** (Welsh) | Dyfed, Gwynedd, Harlech | Pwyll, Pryderi, Rhiannon, Brân, Manawydan, Math, Gwydion | Space 3 |

### 3.4 Asset generation (Bria FIBO + Celtic art)

Located in `tuatha/asset_generation/`:

| File | Reuse by |
|:--|:--|
| `service.py` — `AssetGenerationService` + `LiteLLMConfig` | Space 4 (Uisce) |
| `models.py:8-16` — `AssetType` enum | Space 4 |
| `models.py:18-25` — `CelticStyle` enum | Space 4 |
| `models.py:28-34` — Image gen model registry (`FLUX_DEV`, `FLUX_SCHNELL`, `SDXL_TURBO`, `QWEN_VL`) | Space 4 |
| `prompts.py:7-209` — `CelticPromptGenerator` (6 styles × 4 clans × 5 rarities) | Space 4 (Uisce) |
| `prompts.py:39-56` — Clan aesthetics (TUATHA_DE_DANANN, FIR_BOLG, FOMORIANS, MILESIANS) | Space 3 |
| `prompts.py:59-68` — Rarity modifiers (COMMON → LEGENDARY) | Space 3 + Space 4 |
| `prompts.py:81-124` — `generate_prompt()` | Space 3 + Space 4 |
| `prompts.py:224-239` — Pre-cached weapon/armor prompts | Space 3 |
| `exporters/babylon_exporter.py:522-542` — WGSL knotwork export | Space 3 |

### 3.5 FIBO generation

Located in `tuatha/fibo_generation/`:

| File | Reuse by |
|:--|:--|
| `schemas.py:136-172` — `FiboConfig` (title, description, style, medium, color_palette, composition, lighting, aspect_ratio, complexity_level) | Space 4 (Uisce) |
| `resources.py` | Space 4 |
| `assets.py` | Space 4 |

### 3.6 Agents (4 ADK agents + orchestrator)

Located in `tuatha/agents/`:

| File | Reuse by |
|:--|:--|
| `orchestrator.py:96-116` — 4 ADK agents (Celtic Tutor, Mythology Narrator, Quest Guide, Research Assistant) | Space 3 + Space 4 |
| `orchestrator.py:306-570` — `TuathAgentOrchestrator.process_request()` | Space 4 (Mac Léinn) |
| `orchestrator.py:670-676` — AG-UI protocol events (RUN_STARTED, STEP_STARTED, TEXT_MESSAGE_CONTENT, STATE_SNAPSHOT, RUN_FINISHED, RUN_ERROR) | Space 3 + Space 4 |
| `adk/` | Space 3 + Space 4 |
| `tools/` | Space 3 + Space 4 |

### 3.7 API + game server

Located in `tuatha/api/`:

| File | Reuse by |
|:--|:--|
| `main.py:98-116` — `PAYMENT_CONFIG` (chat_message $0.01, premium_quest $0.05) | (not used — local Anvil for hackathon) |
| `main.py:60` — CopilotKit integration | Space 4 (Mac Léinn) |
| `ag_ui_protocol.py` | Space 3 + Space 4 |
| `services/`, `routes/`, `storage/` | (replaced by Gradio app) |

Located in `tuatha/api-rs/`:

| File | Reuse by |
|:--|:--|
| (Rust SpacetimeDB game server) | (not used — game server stays as design reference) |

### 3.8 Game data (the SpacetimeDB schema + ECS)

Located in `tuatha/crates/stdb-modules/tuath-game/src/lib.rs:224-244` — `Npc` table struct (the canonical NPC data model). Space 3's 6 NPCs should conform to this schema even if running locally without SpacetimeDB.

### 3.9 Graphics (WGSL Celtic shaders + Babylon.js + wgpu)

Located in `tuatha/crates/wgpu/`:

| File | Reuse by |
|:--|:--|
| `celtic-shaders/src/lib.rs:1-19` — `KNOTWORK_SHADER` WGSL with `knot_cell()` SDF | Space 3 (Cian's Sun-Gem Quest) |
| `celtic-shaders/src/lib.rs:19-99` — full procedural WGSL knotwork shader | Space 3 |
| `particle-system/src/lib.rs:38-100` — `ParticlePreset` (Fire, Magic, Smoke, Nature, Celebration) | Space 3 + Space 4 (Uisce) |
| `particle-system/src/lib.rs:38-100` — `EmitterConfig` (color_start/end, wind, gravity) | Space 3 + Space 4 |
| `std-modules/` (SpacetimeDB Rust modules) | (design reference) |

### 3.10 Knowledge graph

Located in `tuatha/knowledge_graph/`:

| File | Reuse by |
|:--|:--|
| (KG client + Cognee config) | Space 3 + Space 4 |

### 3.11 DLT + CocoIndex flows

Located in `tuatha/dlt_sources/`, `tuatha/cocoindex_flows/`, `tuatha/dagster_assets/`, `tuatha/storage/`:

| File | Reuse by |
|:--|:--|
| (Dagster definitions for the 13 Celtic MMO assets) | Space 3 + Space 4 (Mac Léinn) |
| (CocoIndex flows for embedding) | Space 3 + Space 4 |
| (DLT sources for game telemetry) | Space 3 (player progress) |

### 3.12 Anam contracts (Solidity)

Located in `tuatha/apps/crypteolas_demo/anam-contracts/`:

| File | Reuse by |
|:--|:--|
| `src/CuchulainnNFT.sol:1-80` — ERC721 with on-chain SVG, 3 stages (Sétanta / Cúchulainn / Ríastrad), 5 elements | Space 3 + Space 4 (Anam mounter on local Anvil) |
| `CuchulainnNFT.sol:74-94` — `mintForLearning()` | Space 4 |
| `CuchulainnNFT.sol:99-124` — XP grant function | Space 4 |
| `CuchulainnNFT.sol:142-146` — Evolutionary stages (Sétanta → Cúchulainn → Ríastrad) | Space 4 |
| `CuchulainnNFT.sol:162-168` — `_getElementColor()` (5 elements) | Space 4 (Anam) |
| `CuchulainnNFT.sol:173-203` — `_generateSVG()` (on-chain SVG gen) | Space 4 (Anam) |
| `CuchulainnNFT.sol:179` — `knotComplexity: simple → medium → complex` | Space 4 (Anam) |
| `CuchulainnNFT.sol:208-231` — `tokenURI` with base64 metadata | Space 4 (Anam) |
| `src/AnamCaraDAO.sol:17-26` — `SoulBond` (bidirectional mentorship) | Space 4 (Anam Anamchara) |
| `src/AnamCaraDAO.sol:19-26` — `soulTitheRate`, `bondTime` | Space 4 (Anam) |
| `src/TuathToken.sol` — ERC20 + EIP-2612 + EIP-3009 (Tuath utility token) | Space 4 (Anam) |
| `src/TuathToken.sol:62-72` — `mintForLearning()` (validator-gated) | Space 4 (Anam) |
| `foundry.toml` | Space 4 (Anam Anvil deploy) |

### 3.13 Crypteolas crypto data platform

Located in `tuatha/crypteolas/`:

| File | Reuse by |
|:--|:--|
| `dlt_sources/` (CoinGecko, DeFiLlama, Binance, Aave, Pendle subgraphs) | (not used for hackathon) |
| `agent_os/` (Agno AgentOS) | (not used) |
| `mcp_server/` (TOOL_REGISTRY + 8 tools) | (not used) |
| `knowledge_graph/cognee/static_knowledge.py` | (not used) |
| `knowledge_graph/graphiti/temporal_graph.py` | (not used) |
| `cocoindex_flows/` (unified_search, code_search) | Space 3 + Space 4 (search) |

### 3.14 Codeolas (code analysis)

Located in `tuatha/codeolas/`:

| File | Reuse by |
|:--|:--|
| `chunking/` (Tree-sitter AST-aware chunking) | (not used for hackathon) |
| `core/CodebaseAnalyzer.py` | (not used) |
| `storage/lance_catalog.py` | Space 4 (Talamh map data) |
| `search/` (multi-hop semantic + reranking) | (not used) |
| `graph/GraphBuilder.py` + `GraphQueries.py` | (not used) |
| `mcp_server/` (JSON-RPC MCP server) | (not used) |
| `generators/arch.py` (`.arch.md` generation) | (not used) |

### 3.15 Crypteolas demo app

Located in `tuatha/apps/crypteolas_demo/`:

| File | Reuse by |
|:--|:--|
| `defs/curriculum/` (NCCA/SQA/WJEC curriculum pipeline) | Space 4 (Aer) — partially |
| `defs/fibo_generation/` (FIBO JSON → image gen) | Space 4 (Uisce) |
| `defs/blockchain/` (Web3/XP/NFT event streaming) | Space 4 (Anam) |
| `pipelines/defs/` (full crypteolas data pipeline) | (not used) |
| `ui/` (Gradio FIBO curriculum-to-image gen) | (design reference for Spaces 1-4 Gradio apps) |
| `scéimre/` (BAML schemas: curriculum, fibo, validation, agent_outputs, anam_schema, crypto_document, generators) | Space 4 (Anam) — particularly `anam_schema.baml` |
| `anam-contracts/` (see §3.12) | Space 4 (Anam) |
| `foinse/` (LiteLLM configs + 1Password template) | Space 4 |

### 3.16 UI (Babylon.js + Godot 4)

Located in `tuatha/ui/`:

| File | Reuse by |
|:--|:--|
| (Babylon.js + Vinxi + React 18 + Babylon.js + Wagmi + Viem + CopilotKit) | Space 3 (replaced by Gradio wrapper around Babylon.js) |
| `game/` | (not used) |
| `Godot 4/`, `Hades II/`, `wow/` | (design reference for Hades-style diegetic UI) |
| `crates/` (wgpu shaders) | Space 3 (WGSL knotwork) |

### 3.17 Design docs (background)

- `tuatha/anam.md` — the Anam vision (soul, breath, mentorship)
- `tuatha/summary.txt` — Anam particle simulation (weather-driven wind for Unreal/Unity/Godot)
- `tuatha/gaeilge.md` — Irish data sources
- `tuatha/DEVELOPMENT.md` — dev environment setup
- `tuatha/knowledge_graph/` — KG client code
- `tuatha/storage/` — storage clients (LanceCatalog, Garage, DuckLake, Lakekeeper)

---

## Index 4: `croílár/` quadrant — assets for **Space 4 (Anam: Tuatha na nGaelscoil)**

The croílár quadrant is the **multi-persona portfolio platform** — the first adopter of the monorepo's self-hosted infrastructure. Space 4 (the integrated demo) borrows heavily from croílár's pattern of "one codebase, multiple personas."

### 4.1 Apps

Located in `croilar/apps/`:

| App | Stack | Reuse by |
|:--|:--|:--|
| `apps/web/` | TanStack Start + React 19 + SSR | Space 4 (replaced by Gradio for HF Space, but pattern reference) |
| `apps/portal/` | 5-module self-hosted portal (stacks, pipelines, monitoring, MCP, image registry) | Space 4 (dashboard inspiration) |
| `apps/storybook/` | (not used) | — |

### 4.2 Packages (shared libraries)

Located in `croilar/packages/`:

| Package | Reuse by |
|:--|:--|
| `packages/ui/` (46 shadcn/ui components) | Space 4 (Gradio theme tokens) |
| `packages/i18n/` (EN + GA in 3 namespaces) | Space 4 (bilingual EN/GA throughout) |
| `packages/config/` (Tailwind 4 theme tokens) | Space 4 (design tokens) |
| `packages/db/` | (not used) |
| `packages/auth/` | (not used for Space 4) |
| `packages/analytics/` | (not used) |

### 4.3 Convex (real-time backend)

Located in `croilar/convex/`:

| File | Reuse by |
|:--|:--|
| `schema.ts:1-103` — 9 tables (personas, orgs, memberships, portfolioPages, CV entries, music entries, GitHub repos, contact submissions, invites) | (design reference) |
| `auth.config.ts` — BetterAuth OIDC trust | (not used) |
| `helpers.ts` | (not used) |
| `personas.ts`, `portfolio.ts`, `cv.ts`, `contact.ts`, `invites.ts`, `stacks.ts`, `pipelines.ts`, `mcp.ts`, `registry.ts` | (design reference) |
| `crons.ts` — 4 periodic syncs | (not used) |

### 4.4 Hono API (auth-gated REST)

Located in `croilar/hono-api/`:

| File | Reuse by |
|:--|:--|
| `src/auth.ts` — BetterAuth OIDC config | (not used) |
| `src/middleware.ts` | (not used) |
| `src/index.ts` — main Hono app | (not used) |
| `src/db/client.ts` | (not used) |
| `src/db/schema.ts` | (not used) |
| `src/data/spotify.ts`, `github.ts`, `cv.ts` | (not used) |

### 4.5 BAML extraction schemas (for croílár CV extraction)

Located in `croilar/baml/`:

| File | Reuse by |
|:--|:--|
| `cv_extraction.baml` | (not used for hackathon) |
| `teaching_extraction.baml` | Space 1 (could repurpose for teacher-facing features) |
| `identity_verification.baml` | Space 4 (Anam) — could repurpose |
| `artwork_analysis.baml` | Space 4 (Uisce) — could repurpose |
| `style_transfer.baml` | (not used) |
| `linkedin.baml` | (not used) |
| `clients.baml` | (fork to `clients_hackathon.baml`) |
| `generators.baml` | (re-point generator paths) |

### 4.6 DLT pipelines (for croílár)

Located in `croilar/pipelines/`:

| File | Reuse by |
|:--|:--|
| `spotify/`, `soundcloud/`, `github/`, `labels/`, `artwork/`, `cv/`, `teaching/` | (not used for hackathon) |
| `shared/` | (not used) |

### 4.7 Dagster assets

Located in `croilar/dagster_assets/`:

| File | Reuse by |
|:--|:--|
| `dlt_assets.py:169-195` — `motherduck_sync_asset` (syncs DuckDB tables to MotherDuck cloud) | Space 3 (MotherDuck Dive for player progress) + Space 4 (Talamh) |
| `cv_assets.py`, `cocoindex_assets.py` | (not used) |
| `schedules.py` — 4 cron schedules + 2 sensors | (not used) |
| `definitions.py` | (not used) |

### 4.8 CocoIndex flows (embeddings)

Located in `croilar/cocoindex_flows/`:

| File | Reuse by |
|:--|:--|
| `cv_embedding.py` | (not used) |
| `artwork_embedding.py` | (not used) |

### 4.9 Notebooks (Marimo reactive)

Located in `croilar/notebooks/`:

| File | Reuse by |
|:--|:--|
| `music_analytics.py` | (not used) |
| `github_insights.py` | (not used) |
| `cv_dashboard.py` | Space 4 (Mac Léinn dashboard — teacher heatmap pattern) |
| `aleyum/music_analytics.py` | (not used) |
| `cianfhoghlaim/teaching_analytics.py` | Space 1 (An Scrúdú) — pattern |

### 4.10 Services (LiteLLM-backed)

Located in `croilar/services/`:

| File | Reuse by |
|:--|:--|
| `vision.py` | Space 4 (Uisce) |
| `image_generation.py` | Space 4 (Uisce) |

### 4.11 AgentOS (Agno research agent)

Located in `croilar/agent_os/`:

| File | Reuse by |
|:--|:--|
| `main.py` — Agno research agent | (not used for hackathon) |
| `config.yaml` | (not used) |

### 4.12 Shared utilities

Located in `croilar/_shared/`:

| File | Reuse by |
|:--|:--|
| `config/paths.py` — `get_repo_root`, `get_author_dir` | all 4 Spaces |
| `config/settings.py` — Pydantic ALEYUM_ env config | (not used) |
| `database/` | Space 4 (Marimo dashboard) |
| `agents/router.py` | (not used) |
| `observability/` | all 4 Spaces (Langfuse + MLflow + Logfire) |
| `embeddings/` | Space 4 (Talamh map data) |
| `mcp/gateway.py` | (not used) |

### 4.13 Tests (31 pytest)

Located in `croilar/tests/`:

| File | Reuse by |
|:--|:--|
| `conftest.py` | (not used) |
| `test_smoke.py` (24 tests) | (not used) |
| `test_database.py` (7 tests) | (not used) |

### 4.14 Game showcase (game development prototype)

Located in `croilar/game_showcase/`:

| File | Reuse by |
|:--|:--|
| `project_data/babylon_webclient.yaml` | Space 3 (Babylon.js scene) |
| `project_data/spacetimedb_mmo.yaml` | Space 3 (SpacetimeDB) |
| `project_data/godot_shaders.yaml` | Space 3 (Celtic knotwork WGSL) |

### 4.15 Image pipeline (Node 20)

Located in `croilar/image-pipeline/`:

| File | Reuse by |
|:--|:--|
| (image generation pipeline) | Space 4 (Uisce) |

### 4.16 Marimo + Honua

Located in `croilar/marimo/`, `croilar/hono-api/`:

(design references only)

### 4.17 Demo + portal (design references)

Located in `croilar/portal/`, `croilar/demo/`:

(design references for Space 4's Gradio wrapper)

---

## Index 5: `infrastructure/` — assets for **the Anam Bonneagar footer (archived for this hackathon)**

Per the locked decision (2026-06-08), **infrastructure is archived** for this hackathon. The Pangolin topology, 6-file GOLD STANDARD linter, and 3-way secret contract are referenced in the demo narration but not deployed. Future hackathons will revive them.

| Asset | Status for this hackathon |
|:--|:--|
| `infrastructure/stacks/` (89 Docker Compose stacks) | archived |
| `infrastructure/pangolin/` (Traefik + WireGuard + Pocket ID) | archived |
| `infrastructure/komodo/` (Core/Periphery, 65 procedures) | archived |
| `infrastructure/infisical/` (vault, 3-way contract) | archived |
| `infrastructure/dagger/` (8 functions, 4 pipelines) | archived |
| `infrastructure/pulumi/` (OCI, Hetzner, Cloudflare) | archived |
| `infrastructure/observability/` (Prometheus, Grafana) | archived |
| `infrastructure/ansible/` (server bootstrap) | archived |
| `infrastructure/scripts/` | archived |
| `infrastructure/templates/` | archived |
| `infrastructure/legacy/` | archived |
| `infrastructure/hmgcc/` | archived |
| `infrastructure/pangolin/` (Newt/Gerbil/Olm mascots) | referenced in demo narration only |

**The "Anam Bonneagar" footer** (per Space 4's Anam element) is a small per-Space line that displays:
- The Pobal HP Deprivation Index for the Space's primary region (e.g. "Galway City, decile 4 of 10, 2016")
- The 32B model alias being used (e.g. "Qwen2.5-32B-Instruct via HF Inference")
- A short note that the 6-file GOLD STANDARD linter would score this Space's underlying stack if it were deployed (e.g. "linter: 6/6 — virtual")

This footer is the architectural homage to the infrastructure quadrant without requiring its deployment.

---

## 5. Cross-Quadrant Integration Map

| Space | Primary Quadrant | Supporting Quadrant(s) | Files reused (rough count) |
|:--|:--|:--|:--|
| **Space 1 "An Scrúdú"** | `oideachais` (Talamh) | `meaisínfhoghlaim` (Tine OCR) | ~50 files (1.1, 1.2, 1.3, 1.4, 1.5, 1.6) |
| **Space 2 "Meaisín Cliste"** | `meaisínfhoghlaim` (Uisce + Aer) | `oideachais` (Talamh geospatial) + `tuatha` (Aer NPC) | ~70 files (2.1, 2.2, 2.3, 2.5, 2.6, 2.7, 2.8 + 1.2, 1.4) |
| **Space 3 "Cianfhoghlaim"** | `tuatha` (Aer + Anam) | `oideachais` (Talamh geographic) | ~50 files (3.1, 3.2, 3.3, 3.4, 3.6, 3.9) |
| **Space 4 "Anam: Tuatha na nGaelscoil"** | `croílár` (5 elements) | All 5 quadrants | ~80 files (4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.10, 4.12, 4.14) |

**The connective tissue is the 5-element framework** (Talamh / Uisce / Tine / Aer / Anam). Each Space maps to one or more elements; Space 4 ties them all together.

---

*End of per-quadrant index. The catalogue and the index together cover the 4-Space build. Approve and exit plan mode when ready; 3 file writes pending (model fallback, OpenSpec change bundle, plan patch).*
