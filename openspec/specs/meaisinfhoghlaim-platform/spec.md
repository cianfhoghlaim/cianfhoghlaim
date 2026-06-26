# Meaisínfhoghlaim Platform Capability

## Purpose

`meaisinfhoghlaim-platform` is a capability of the Cianfhoghlaim
platform. The corresponding source code lives at `sruth/meaisinfhoghlaim/`
(the AI/ML quadrant, 15K+ LOC, 10 sub-packages, registered as a
top-level uv workspace member with the ASCII wheel name
`meaisinfhoghlaim`). See `docs/00_index.md` for the quadrant map and
`docs/00-core/CLAUDE.md` for the project identity.

This is the first openspec spec for the meaisinfhoghlaim quadrant.

## Background

The meaisinfhoghlaim quadrant houses the AI/ML services that feed the
curriculum knowledge graph consumed by `sruth/oideachais/` and the
dashboards in `sruth/croilar/apps/portal/`. The 10 sub-packages are:

- `agents/` — 12 specialised agents (Root, Curriculum, Translation,
  Corpus, Geospatial, Statistics, Research, Curriculum Comparison,
  Bunchloch Research, AG-UI Curriculum, Site Analysis, etc.)
- `ocr/` — 10 OCR models across 6 backends (Pylaia, VLM, TrOCR,
  PaddleOCR, Tesseract, dots.ocr)
- `language/` — 6 Celtic-language subdirs (`brezhoneg/`, `cymraeg/`,
  `gaeilge/`, `gaelg/`, `gaidhlig/`, `kernowek/`) + a `cognates.yaml`
  cross-Celtic cognate database
- `pipelines/` — 7 ML pipelines (Canuint audio slicer, dialect
  classifier, Irish document scanner, LLM router, transcript aligner,
  VLM bridge)
- `alignment/` — 7 alignment modules (aligner, canuint exporter,
  character interpolator, colpali aligner, dataset generator, export,
  Irish G2P, quality)
- `evaluation/` — RAGAS evaluation pipeline + run_evaluation driver
- `quality/` — 3 content quality modules (canuint validator,
  completeness, content quality)
- `catalog/` — `models.yaml` (ML model registry) + `sources.yaml` (Celtic
  data sources registry)
- `services/` — 3 FastAPI services (agent_fastapi, celery_worker,
  pipeline_fastapi)
- `scripts/` — utility scripts (e.g. dataset generation)

The meaisinfhoghlaim quadrant is registered in the root `dg.toml` as
a Dagster code-location with 4 heartbeat assets in the
`meaisin_heartbeat` group (added in commit `6afe63dac`, Phase 0.2 of
`lateralise-british-isles-domains`).
## Requirements
### Requirement: 10 sub-packages

The system SHALL NOT import from the `sruth.*` namespace. The
`sruth` package is the predecessor `bonneagar` project's Python
package and has been deleted from the filesystem. The 13
remaining `sruth.*` imports in the meaisinfhoghlaim source tree
unblock the following:

- The 5 `language/gaeilge/{duchas,tearma,gaois,duchas_images,canuint}.py`
  DLT sources
- The 4 `alignment/*.py` G2P / character-interpolation modules
- The `pipelines/llm_router.py` (the entire LLM routing layer)
- The `pipelines/canuint_audio_slicer.py` audio pipeline
- The `quality/canuint_validator.py` audio quality scorer
- The `evaluation/run_evaluation.py` RAGAS runner
- The `agents/bunchloch_research_agent.py` research agent
- The `agents/api/main_simple.py` FastAPI alternate entry-point
- The `ocr/config/base.py` (entire file is a sruth copy)

Every affected file SHALL be migrated to import from the
canonical home in `oideachais.*` or `meaisinfhoghlaim.*`. The
canonical observability logger is at
`oideachais.observability.logging.get_logger`.

#### Scenario: A developer runs the test suite

- **GIVEN** the 13 source files have been migrated
- **WHEN** `uv run pytest sruth/meaisinfhoghlaim/tests/` runs
- **THEN** no `ModuleNotFoundError: No module named 'sruth'`
  exception is raised
- **AND** all 22 tests pass (the 3 test files: test_ensemble_gradio,
  test_hf_hub_push, test_marimo_notebooks)

### Requirement: 4 heartbeat assets

The system SHALL register 4 heartbeat assets in the
`meaisin_heartbeat` Dagster group that import-test each meaisín
sub-package.

#### Scenario: Heartbeat assets pass

- **GIVEN** the meaisinfhoghlaim code-location is loaded
- **WHEN** the 4 heartbeat assets materialise
- **THEN** all 4 succeed (smoke test that `agents/curriculum_agent`,
  `pipelines/dialect_classifier`, `pipelines/transcript_aligner`,
  `pipelines/irish_document_scanner` import cleanly)

### Requirement: Dagster code-location registration

The system SHALL register meaisinfhoghlaim as a Dagster code-location in
the root `dg.toml`.

#### Scenario: Code-location loads

- **GIVEN** the root `dg.toml` is configured with the meaisinfhoghlaim
  code-location
- **WHEN** `dg dev` starts the Dagster UI
- **THEN** the meaisinfhoghlaim code-location appears in the UI
  with the 4 heartbeat assets

### Requirement: Cross-quadrant ingestion from oideachais DuckLake

The system SHALL ingest from the oideachais DuckLake catalog via the
`oideachais.dagster_defs` package.

#### Scenario: Lakehouse to meaisinfhoghlaim ingest

- **GIVEN** the oideachais leabharlann sources have materialised in
  DuckLake
- **WHEN** a meaisinfhoghlaim agent (e.g. `corpus_agent`) is invoked
- **THEN** the agent reads the leabharlann rows from DuckLake
- **AND** the agent returns the top-N similar chunks via the
  BGE-large-en-v1.5 embedding model

### Requirement: Celtic-language model catalog

The system SHALL maintain a Celtic-language model catalog at
`sruth/meaisinfhoghlaim/catalog/models.yaml` (UCCIX-Llama2-13B-Instruct,
Llama-3.2-3B-Irish, gaBERT, gaHealth, etc.).

#### Scenario: Model catalog is valid YAML

- **GIVEN** the `sruth/meaisinfhoghlaim/catalog/models.yaml` file
- **WHEN** the file is loaded via `yaml.safe_load()`
- **THEN** the file parses without errors
- **AND** each model entry has `id`, `name`, `type`, `base`,
  `languages`, `status`, and `huggingface` fields

### Requirement: TTS pipeline (text-to-speech)

The system SHALL support Irish-language TTS via Chatterbox
(9.7 GB Resemble AI model) for pronunciation guides, audio
study notes, and AI tutor speech, with a BAML→TTS pipeline
that converts BAML-extracted curriculum text to audio files
stored in Garage S3.

#### Scenario: BAML→TTS audio generation

- **GIVEN** a BAML-extracted curriculum passage (e.g. a
  NCCA Irish Leaving Cert grammar explanation)
- **WHEN** the `sruth/meaisinfhoghlaim/tts/` service is invoked with
  the passage + voice ID
- **THEN** Chatterbox SHALL render the passage to a 16-bit
  PCM WAV file
- **AND** the WAV SHALL be uploaded to `garage://kcg-tts/`
  with a deterministic key (sha256 of the text + voice)
- **AND** the FastAPI route `POST /api/tts/synthesize` SHALL
  return the signed URL

### Requirement: ASR routing (speech recognition)

The system SHALL use the canonical ASR routing rule:
`wav2vec2-XLSR-Irish` for accuracy-critical Irish (séimhiú,
urú, dialectal variation, oral exam recordings), Whisper
large-v3 (via faster-whisper) for general multilingual
transcription, MMS-1B-fl102 as a fallback for low-resource
languages.

#### Scenario: Irish oral exam transcription

- **GIVEN** an audio recording of an Irish Leaving Cert oral
  exam (Irish + English mixed)
- **WHEN** the `sruth/meaisinfhoghlaim/asr/` service is invoked
- **THEN** the service SHALL route to
  `cpierse/wav2vec2-large-xlsr-53-irish` for the Irish
  segments (auto-detected by language ID)
- **AND** to `openai/whisper-large-v3` (faster-whisper) for
  the English segments
- **AND** return a single transcript with per-segment
  language tags

### Requirement: TRL training (preference optimization)

The system SHALL support HuggingFace TRL SFTTrainer, DPOTrainer,
GRPOTrainer, and RewardTrainer for alignment training, with
the RAGAS-as-DPO-preference-signal pattern wired in via a
Dagster asset.

#### Scenario: RAGAS-driven DPO training run

- **GIVEN** a BAML extraction with 1000 examples, each
  scored by RAGAS (faithfulness, answer-relevancy, etc.)
- **WHEN** the `trl_dpo_training` Dagster asset runs
- **THEN** examples with RAGAS faithfulness ≥ 0.8 SHALL be
  used as the "chosen" examples
- **AND** examples with RAGAS faithfulness < 0.5 SHALL be
  used as the "rejected" examples
- **AND** the DPOTrainer SHALL produce a LoRA adapter
  (via PEFT) on the base model
- **AND** the adapter SHALL be logged to MLflow + Langfuse
- **AND** the trained adapter SHALL be served via llama-swap

### Requirement: PEFT parameter-efficient fine-tuning

The system SHALL use HuggingFace PEFT (LoRA, QLoRA,
IA³) for parameter-efficient fine-tuning on MacBook M4
48 GB unified memory, with bitsandbytes 4-bit quantisation
for the base model.

#### Scenario: QLoRA fine-tune on M4 Mac

- **GIVEN** a 7B parameter base model (e.g.
  `ReliableAI/UCCIX-Llama3.1-8B-Instruct`) + a 1k-example
  Irish curriculum dataset
- **WHEN** the `peft_qlora_finetune` Dagster asset runs
  via Unsloth
- **THEN** the base model SHALL be quantised to 4-bit via
  bitsandbytes
- **AND** a 64-rank LoRA adapter SHALL be trained on the
  quantised base
- **AND** the adapter SHALL be < 100 MB on disk
- **AND** the adapter SHALL be saved to
  `stedding/huggingface/hub/ReliableAI-UCCIX-Llama3.1-8B-Instruct/`

### Requirement: Agent + OCR thin-shim canonicalisation

The system SHALL canonicalise the `sruth/oideachais/agents/{adk,agno}/`
and `sruth/oideachais/ocr/` directories as **thin re-exports** of the
model-layer agents + OCR modules in `sruth/meaisinfhoghlaim/agents/` +
`sruth/meaisinfhoghlaim/ocr/`. The 12 ADK agents (root_agent,
curriculum_agent, translation_agent, corpus_agent,
research_agent, education_research_agent,
bunchloch_research_agent, geospatial_agent,
statistics_agent, curriculum_comparison_agent,
agui_curriculum_agent, mcp_curriculum_agent) and the 12 OCR
modules (adapters, comparison_runner, gaelic_metrics,
irish_htr_dataset, irish_processing, line_segmentation,
model_registry, observability, pylaia_comparison,
vision_comparison, vlm_finetune_comparison, gaelscribhneoir)
SHALL be re-exported, not duplicated.

The system SHALL keep the 5 tuatha-specific agents
(celtic_tutor_agent, mythology_narrator_agent,
quest_guide_agent, research_assistant_agent, tuatha_root_agent)
and the 1 leabharlann-specific OCR file
(`sruth/oideachais/ocr/author_archive_ocr.py`) as real code (they
are domain-specific, not duplicates).

#### Scenario: A consumer imports the same agent via both paths

- **GIVEN** the canonical agent lives at
  `sruth/meaisinfhoghlaim/agents/curriculum_agent.py`
- **AND** the thin-shim re-exports it at
  `sruth/oideachais/agents/adk/curriculum_agent.py`
- **WHEN** a consumer does
  `from oideachais.agents.adk.curriculum_agent import curriculum_agent`
- **THEN** the imported `curriculum_agent` is the **same object**
  as `meaisinfhoghlaim.agents.curriculum_agent.curriculum_agent`
  (verified via `is` comparison)

### Requirement: No stale `sruth.oideachas` path references

The meaisínfhoghlaim quadrant MUST NOT contain any reference to
the non-existent package path `sruth.oideachas/` (Irish nominative
"education"). The canonical package name is `sruth/oideachais/`
(Irish genitive "of education"); `sruth/oideachas/` does not
exist. References include but are not limited to docstring
Usage-example code blocks, README examples, and tutorial-style
inline comments.

#### Scenario: A docstring Usage example references the non-existent path

- **GIVEN** a `.py` file under `sruth/meaisinfhoghlaim/` contains a
  docstring with `from sruth.oideachas.X import Y` in a
  Usage-example code block
- **WHEN** the file is committed
- **THEN** `grep -rn "sruth\.oideachas" sruth/meaisinfhoghlaim/`
  returns 0 hits
- **AND** the docstring's Usage example uses the canonical
  `sruth.oideachais.X` path

#### Scenario: A README or AGENTS.md example references the non-existent path

- **GIVEN** a `.md` file under `sruth/meaisinfhoghlaim/` contains
  the substring `sruth/oideachas` or `sruth.oideachas` (other than
  in an explanatory footnote documenting the typo was fixed)
- **WHEN** the file is committed
- **THEN** `grep -rn "sruth/oideachas\|sruth\.oideachas" sruth/meaisinfhoghlaim/*.md sruth/meaisinfhoghlaim/**/*.md`
  returns 0 hits outside an explicit typo-fix footnote

### Requirement: No dead stub modules in `meaisínfhoghlaim`

The meaisínfhoghlaim quadrant MUST NOT contain stand-alone module
files (`.py`) at any depth that have no Python importer anywhere
in the actual codebase (excluding `.venv/`, `__pycache__/`, and
3rd-party `.py` files inside installed packages). A "stub" is a
`.py` file that defines no production behaviour and is not
imported by any production code.

#### Scenario: A dead stub file is left behind after a prototype is abandoned

- **GIVEN** a `.py` file at e.g.
  `sruth/meaisinfhoghlaim/<sub>/<name>.py` is a tiny prototype
  (under 30 lines) that is NOT imported by any other file in
  `sruth/` (excluding `.venv/`, `__pycache__/`, installed
  3rd-party packages)
- **WHEN** the prototype is abandoned without an active consumer
- **THEN** the file is either deleted or wired into a real
  consumer within the same change that creates it
- **AND** `find sruth/meaisinfhoghlaim/ -name "*.py" -size -500c -not -path "*/__init__.py"`
  is reviewed each phase to ensure no new dead stubs were
  introduced

#### Scenario: An empty package directory remains after stubs are deleted

- **GIVEN** the only files in `sruth/meaisinfhoghlaim/<sub>/` are
  stubs that have been deleted
- **WHEN** the deletion is committed
- **THEN** the empty `<sub>/` directory is either removed (if not
  declared a Python package) or has an `__init__.py` (if it must
  remain as a package marker)
- **AND** `ls sruth/meaisinfhoghlaim/<sub>/` returns either empty
  output or contains only `__init__.py`

### Requirement: AGENTS.md BAML reference points to canonical path

`sruth/meaisinfhoghlaim/AGENTS.md` MUST reference the canonical
BAML schema home as `sruth/oideachais/baml_src/` (the actual
on-disk path). The future rename `baml_src → scéimre` was
explicitly deferred per the `lateralise-british-isles-domains`
decision and is documented in
`openspec/specs/meaisinfhoghlaim-platform/spec.md` (Known issues
#5) and `sruth/meaisinfhoghlaim/README.md`. AGENTS.md MUST NOT
forward-reference a non-existent path.

#### Scenario: AGENTS.md is updated after a deferred rename

- **GIVEN** AGENTS.md line ~77 contains
  `sruth/oideachais/scéimre/`
- **WHEN** the deferred rename has not yet been executed
- **THEN** AGENTS.md MUST instead reference
  `sruth/oideachais/baml_src/`
- **AND** the parenthetical explanation MUST note that the
  `baml_src → scéimre` rename is deferred per
  `lateralise-british-isles-domains`
- **AND** `grep -rn "sruth/oideachais/scéimre" sruth/meaisinfhoghlaim/*.md`
  returns 0 hits in the AGENTS.md file (it MAY still appear in
  `sruth/meaisinfhoghlaim/README.md` and the spec as a
  documentation note about the deferred decision)

## Known issues (from `sruth/meaisinfhoghlaim/README.md`)

| # | Issue | Tracked in | Severity |
|--:|:--|:--|:--|
| 1 | Most sub-packages are stubs; the 4 heartbeats are the first real assets | the 10 sub-packages | high |
| 2 | No `[tool.uv.sources]` block; sibling workspace members are not declared as local-path dependencies | `sruth/meaisinfhoghlaim/pyproject.toml` | high — blocks cross-quadrant imports |
| 3 | The 6 Celtic-language subdirs are stubs | the 6 subdirs | medium |
| 4 | No production dagster code-location (only the 4 heartbeats) | `sruth/meaisinfhoghlaim/dagster_defs/assets/healthchecks.py` | medium |
| 5 | The `baml_src → scéimre` rename was deferred per `lateralise-british-isles-domains` | the AGENTS.md | low — deferred |

## Cross-references

- [`sruth/meaisinfhoghlaim/`](../../sruth/meaisinfhoghlaim/) (the AI/ML quadrant)
- [`sruth/meaisinfhoghlaim/README.md`](../../sruth/meaisinfhoghlaim/README.md) (the status table + known issues)
- [`sruth/meaisinfhoghlaim/AGENTS.md`](../../sruth/meaisinfhoghlaim/AGENTS.md) (the developer-quick-reference)
- [`sruth/meaisinfhoghlaim/pyproject.toml`](../../sruth/meaisinfhoghlaim/pyproject.toml) (the uv workspace member)
- [`dg.toml`](../../dg.toml) (the root Dagster code-location config)
- [`openspec/specs/meaisinfhoghlaim-agent-frameworks/spec.md`](meaisinfhoghlaim-agent-frameworks/spec.md) (the 12 agents)
- [`openspec/specs/meaisinfhoghlaim-ocr-htr/spec.md`](meaisinfhoghlaim-ocr-htr/spec.md) (the 10 OCR models)
