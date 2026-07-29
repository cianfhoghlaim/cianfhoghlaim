# Meaisínfhoghlaim Platform Capability

## Purpose

`meaisinfhoghlaim-platform` is a capability of the Cianfhoghlaim
platform. The corresponding source code lives at `cianfhoghlaim/`
(the AI/ML quadrant, 15K+ LOC, 10 sub-packages, registered as a
top-level uv workspace member with the ASCII wheel name
`meaisinfhoghlaim`). See `docs/00_index.md` for the quadrant map and
`docs/00-core/CLAUDE.md` for the project identity.

This is the first openspec spec for the meaisinfhoghlaim quadrant.

## Background

The meaisinfhoghlaim quadrant houses the AI/ML services that feed the
curriculum knowledge graph consumed by `cianfhoghlaim/` and the
dashboards in `cianfhoghlaim/apps/portal/`. The 10 sub-packages are:

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
canonical home in `cianfhoghlaim.*` or `meaisinfhoghlaim.*`. The
canonical observability logger is at
`cianfhoghlaim.observability.logging.get_logger`.

#### Scenario: A developer runs the test suite

- **GIVEN** the 13 source files have been migrated
- **WHEN** `uv run pytest cianfhoghlaim/tests/` runs
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
`cianfhoghlaim.orchestration` package (formerly `cianfhoghlaim.dagster_defs`).

#### Scenario: Lakehouse to meaisinfhoghlaim ingest

- **GIVEN** the oideachais leabharlann sources have materialised in
  DuckLake
- **WHEN** a meaisinfhoghlaim agent (e.g. `corpus_agent`) is invoked
- **THEN** the agent reads the leabharlann rows from DuckLake
- **AND** the agent returns the top-N similar chunks via the
  BGE-large-en-v1.5 embedding model

### Requirement: Celtic-language model catalog

The system SHALL maintain a Celtic-language model catalog at
`cianfhoghlaim/catalog/models.yaml` (UCCIX-Llama2-13B-Instruct,
Llama-3.2-3B-Irish, gaBERT, gaHealth, etc.).

#### Scenario: Model catalog is valid YAML

- **GIVEN** the `cianfhoghlaim/catalog/models.yaml` file
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
- **WHEN** the `cianfhoghlaim/tts/` service is invoked with
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
- **WHEN** the `cianfhoghlaim/asr/` service is invoked
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

The system SHALL use `from cianfhoghlaim...` for actual Python import examples in active OpenSpec specs. The older `from cianfhoghlaim...` examples are logical quadrant shorthand only and MUST NOT be used as real code-import examples.

#### Scenario: A consumer imports the same agent via both paths

- **GIVEN** the canonical agent lives at `cianfhoghlaim/agents/curriculum_agent.py`
- **AND** the thin-shim re-exports it at `cianfhoghlaim/agents/adk/curriculum_agent.py`
- **WHEN** a consumer imports `curriculum_agent` through a real Python import example
- **THEN** the example uses `from cianfhoghlaim.agents.adk.curriculum_agent import curriculum_agent`
- **AND** the imported object is the same object exposed by the canonical model-layer module

### Requirement: No stale `sruth.oideachas` path references

The meaisínfhoghlaim quadrant MUST NOT contain any reference to
the non-existent package path `sruth.oideachas/` (Irish nominative
"education"). The canonical package name is `cianfhoghlaim/`
(Irish genitive "of education"); `sruth/oideachas/` does not
exist. References include but are not limited to docstring
Usage-example code blocks, README examples, and tutorial-style
inline comments.

#### Scenario: A docstring Usage example references the non-existent path

- **GIVEN** a `.py` file under `cianfhoghlaim/` contains a
  docstring with `from sruth.oideachas.X import Y` in a
  Usage-example code block
- **WHEN** the file is committed
- **THEN** `grep -rn "sruth\.oideachas" cianfhoghlaim/`
  returns 0 hits
- **AND** the docstring's Usage example uses the canonical
  `cianfhoghlaim.X` path

#### Scenario: A README or AGENTS.md example references the non-existent path

- **GIVEN** a `.md` file under `cianfhoghlaim/` contains
  the substring `sruth/oideachas` or `sruth.oideachas` (other than
  in an explanatory footnote documenting the typo was fixed)
- **WHEN** the file is committed
- **THEN** `grep -rn "sruth/oideachas\|sruth\.oideachas" cianfhoghlaim/*.md cianfhoghlaim/**/*.md`
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
  `cianfhoghlaim/<sub>/<name>.py` is a tiny prototype
  (under 30 lines) that is NOT imported by any other file in
  `sruth/` (excluding `.venv/`, `__pycache__/`, installed
  3rd-party packages)
- **WHEN** the prototype is abandoned without an active consumer
- **THEN** the file is either deleted or wired into a real
  consumer within the same change that creates it
- **AND** `find cianfhoghlaim/ -name "*.py" -size -500c -not -path "*/__init__.py"`
  is reviewed each phase to ensure no new dead stubs were
  introduced

#### Scenario: An empty package directory remains after stubs are deleted

- **GIVEN** the only files in `cianfhoghlaim/<sub>/` are
  stubs that have been deleted
- **WHEN** the deletion is committed
- **THEN** the empty `<sub>/` directory is either removed (if not
  declared a Python package) or has an `__init__.py` (if it must
  remain as a package marker)
- **AND** `ls cianfhoghlaim/<sub>/` returns either empty
  output or contains only `__init__.py`

### Requirement: AGENTS.md BAML reference points to canonical path

`cianfhoghlaim/AGENTS.md` MUST reference the canonical
BAML schema home as `cianfhoghlaim/baml_src/` (the actual
on-disk path). The future rename `baml_src → scéimre` was
explicitly deferred per the `lateralise-british-isles-domains`
decision and is documented in
`openspec/specs/meaisinfhoghlaim-platform/spec.md` (Known issues
#5) and `cianfhoghlaim/README.md`. AGENTS.md MUST NOT
forward-reference a non-existent path.

#### Scenario: AGENTS.md is updated after a deferred rename

- **GIVEN** AGENTS.md line ~77 contains
  `cianfhoghlaim/scéimre/`
- **WHEN** the deferred rename has not yet been executed
- **THEN** AGENTS.md MUST instead reference
  `cianfhoghlaim/baml_src/`
- **AND** the parenthetical explanation MUST note that the
  `baml_src → scéimre` rename is deferred per
  `lateralise-british-isles-domains`
- **AND** `grep -rn "cianfhoghlaim/scéimre" cianfhoghlaim/*.md`
  returns 0 hits in the AGENTS.md file (it MAY still appear in
  `cianfhoghlaim/README.md` and the spec as a
  documentation note about the deferred decision)

### Requirement: No duplicate DLT source implementations across quadrants

The meaisínfhoghlaim quadrant MUST NOT contain a `.py` file in
`cianfhoghlaim/language/<lang>/` that re-implements a
DLT source already living at the canonical home
`cianfhoghlaim/dlt_sources/{nation}/{domain}/<entity>.py`.
Canonical homes are determined by the Round 11 audit:

- `cianfhoghlaim/data_platform/` umbrella was deleted in commit
  `8484a6353` (the predecessor `bonneagar` project package
  removal)
- `cianfhoghlaim/dlt_sources/celtic/` umbrella was deleted in
  Phase 3B (`cianfhoghlaim-audit-phase-3b-drop-domains-wrapper`)
- `cianfhoghlaim/dlt_sources/<flat>.py` flat files were migrated to
  the country-first layout in Phases 3C, 3D, 4
- The canonical layout is
  `dlt_sources/{nation}/{domain}/{entity}.py` (one file per
  `@dlt.source` function, with shared helpers in sibling
  `_<entity>_helpers.py` files)

If meaisínfhoghlaim requires a Celtic-language DLT source, it
MUST import from the canonical home via
`from cianfhoghlaim.dlt.<nation>.<domain> import <entity>_source`,
NOT re-implement the source at a meaisínfhoghlaim-local path.

#### Scenario: A meaisínfhoghlaim `language/gaeilge/` file re-implements a canonical DLT source

- **GIVEN** the canonical DLT source for Dúchas.ie lives at
  `cianfhoghlaim/dlt_sources/ie/culture/duchas.py` with
  `@dlt.source(name="duchas_folklore") def duchas_source(...)`
- **AND** the meaisínfhoghlaim quadrant contains a
  `cianfhoghlaim/language/gaeilge/duchas.py` with the
  same `@dlt.source(name="duchas_folklore") def duchas_source(...)`
  decorator (verified by `grep -n "@dlt.source"`)
- **WHEN** a contributor tries to add a new Dúchas.ie feature
- **THEN** the contributor MUST edit the canonical file at
  `cianfhoghlaim/dlt_sources/ie/culture/duchas.py`, NOT the
  meaisínfhoghlaim duplicate
- **AND** the meaisínfhoghlaim duplicate MUST be deleted (zero
  importers; the canonical home is the single source of truth)

#### Scenario: A meaisínfhoghlaim `language/gaeilge/` file has stale `cianfhoghlaim.dlt.celtic` import

- **GIVEN** a file under `cianfhoghlaim/language/gaeilge/`
  contains `from cianfhoghlaim.dlt.celtic.X import Y`
  in either an active or lazy (`try/except ImportError`) import
  block
- **AND** `cianfhoghlaim/dlt_sources/celtic/` does not exist
  (it was deleted in Phase 3B)
- **WHEN** the file is loaded
- **THEN** the import fails silently (lazy) or with
  `ModuleNotFoundError` (active)
- **AND** the file MUST be either deleted (if a true duplicate of
  a canonical home) or have its stale imports rewired to the
  canonical path (if it provides genuinely new functionality)

### Requirement: `language/gaeilge/` contains only non-duplicate files

The directory `cianfhoghlaim/language/gaeilge/` MUST
contain only the files listed in the post-Phase-2 Scenario
below.

No additional files MAY be added without first verifying they
are NOT byte-for-byte duplicates of canonical homes at
`cianfhoghlaim/dlt_sources/ie/{culture,education}/`.

- `__init__.py` (the package marker)
- Files that are NOT byte-for-byte duplicates of canonical
  homes (e.g., richer implementations where the canonical
  version is a strict subset)
- `*.yaml` data files (not Python)

#### Scenario: A future contributor adds a new DLT source to `language/gaeilge/`

- **GIVEN** the post-Phase 2 `language/gaeilge/` contains 4 files:
  `__init__.py`, `canuint.py`, `duchas_images.py`, `irish_samples.yaml`
- **WHEN** a new `@dlt.source` is needed for an Irish-language
  data source
- **THEN** the contributor MUST first verify whether a canonical
  home exists at `cianfhoghlaim/dlt_sources/ie/culture/<name>.py`
  via `ls cianfhoghlaim/dlt_sources/ie/culture/`
- **AND** if a canonical home exists, the contributor MUST add
  the new source to the canonical home (NOT the meaisínfhoghlaim
  copy) per the no-duplicates invariant
- **AND** if no canonical home exists, the contributor MUST
  create one at `cianfhoghlaim/dlt_sources/ie/culture/<name>.py`
  with the standard country-first layout, then optionally add
  a thin re-export shim to `cianfhoghlaim/language/gaeilge/`
  if a meaisínfhoghlaim-specific consumer needs it

### Requirement: No broken cross-package imports in meaisínfhoghlaim

The meaisínfhoghlaim quadrant MUST NOT contain a `.py` file
with an active (non-lazy `try/except ImportError`) import
that targets a non-existent module path. Every cross-package
import MUST be verifiable via
`PYTHONPATH=./sruth python3 -c "import <module>"` returning
exit code 0 BEFORE the importing file is committed.

The canonical homes for cross-quadrant utilities are:

| Utility | Canonical home |
|:--|:--|
| `CircuitBreaker`, `RateLimiter`, `retry` | `cianfhoghlaim/core/utils/` (importable as `from cianfhoghlaim.core.utils import ...`) |
| `get_logger` | `cianfhoghlaim/observability/logging.py` |
| `settings` | `cianfhoghlaim/settings.py` |
| DLT sources (Dúchas, Téarma, Gaois, etc.) | `cianfhoghlaim/dlt_sources/ie/culture/` |

If a meaisínfhoghlaim module needs a utility that lives in
another quadrant, it MUST import from the canonical home
(e.g. `from cianfhoghlaim.core.utils import CircuitBreaker`),
NOT a phantom meaisínfhoghlaim-local path
(e.g. `from ..core.utils import CircuitBreaker` when
`cianfhoghlaim/core/` does not exist).

#### Scenario: A meaisínfhoghlaim module imports from a phantom `meaisinfhoghlaim.core.*` path

- **GIVEN** `cianfhoghlaim/core/` does not exist
  (verified via `ls cianfhoghlaim/core/`)
- **AND** `cianfhoghlaim/pipelines/llm_router.py:23`
  contains an active import `from ..core.utils import CircuitBreaker`
- **WHEN** the module is loaded
- **THEN** Python raises `ModuleNotFoundError: No module named 'meaisinfhoghlaim.core'`
- **AND** the import MUST be rewired to the canonical home
  `from cianfhoghlaim.core.utils import CircuitBreaker`

#### Scenario: A future contributor adds a new cross-quadrant import

- **GIVEN** a meaisínfhoghlaim `.py` file needs a utility from
  another quadrant
- **WHEN** the contributor adds the import
- **THEN** the contributor MUST first verify the target module
  exists via `ls <path-to-target>/<file>.py`
- **AND** the contributor MUST first verify the target imports
  cleanly via `PYTHONPATH=./sruth python3 -c "from <canonical.path> import <symbol>"`
- **AND** the import line MUST use the canonical
  `<quadrant>.<package>.<module>` form (e.g. `cianfhoghlaim.core.utils`),
  NOT a phantom `<quadrant>.core.utils` form (unless
  `sruth/<quadrant>/core/utils/` actually exists)

### Requirement: No orphan resource modules in `pipelines/`

The meaisínfhoghlaim `pipelines/` subtree MUST NOT contain
`.py` files that define a top-level resource class or function
without any importer in `cianfhoghlaim/`. A resource
module is "orphan" if:

- It defines at least one top-level class (e.g.
  `BrowserbaseResource`) or top-level function that is not a
  private helper (prefixed with `_`), AND
- Zero importers exist for any of its top-level symbols
  anywhere in `cianfhoghlaim/`
  (verified via `grep -rn "from .* import .*<Symbol>" cianfhoghlaim/`)

The exception is `pipelines/__init__.py` itself, which is the
canonical re-export surface for the 3 main pipelines
(`dialect_classifier`, `irish_document_scanner`,
`transcript_aligner`).

#### Scenario: A pipeline resource class has zero importers

- **GIVEN** `cianfhoghlaim/pipelines/<name>.py` defines
  a class `BrowserbaseResource` or similar top-level resource
- **AND** `grep -rn "BrowserbaseResource" cianfhoghlaim/`
  returns only the definition (no importers)
- **WHEN** the file is audited
- **THEN** the file MUST be either deleted (if the resource is
  superseded by a LiteLLM or Dagster-native alternative) or
  wired into a real Dagster code-location (the canonical
  destination for `ConfigurableResource` classes)
- **AND** the resource singleton at module load time
  (e.g. `browserbase_resource = BrowserbaseResource()`) MUST
  NOT be eagerly instantiated if there are no importers
  (eager instantiation adds to import-time cost + Dagster
  startup latency)

#### Scenario: A future contributor adds a new pipeline module

- **GIVEN** a new `.py` file is added to
  `cianfhoghlaim/pipelines/`
- **WHEN** the file is committed
- **THEN** at least one of the following MUST be true:
  - The file is added to `pipelines/__init__.py` re-exports
    (becomes a public pipeline module), OR
  - The file is imported by a Dagster asset under
    `cianfhoghlaim/dagster_defs/`, OR
  - The file is imported by a test under
    `cianfhoghlaim/tests/`
- **AND** if none of the above hold for 30 days, the file
  MUST be either deleted or wired into a real consumer

### Requirement: No duplicate agent-tools package across quadrants

The meaisínfhoghlaim quadrant MUST NOT contain a `tools/` package
that duplicates `cianfhoghlaim/tools/`. The canonical home for
all Celtic-education agent tools (corpus search, curriculum search,
spatial query, statistics query, terminology, translation) is
`cianfhoghlaim/tools/`, importable as
`from cianfhoghlaim.tools.X import ...`.

Meaisínfhoghlaim agent code MUST import tools from the canonical
oideachais location (e.g.
`from cianfhoghlaim.tools.curriculum_search import compare_curricula`),
NOT from a meaisínfhoghlaim-local `tools/` package
(e.g. `from meaisinfhoghlaim.tools.curriculum_search import ...`).

#### Scenario: A meaisínfhoghlaim agent file imports from a duplicate `agents/tools/` location

- **GIVEN** `cianfhoghlaim/agents/tools/` does not exist
  (verified via `ls cianfhoghlaim/agents/tools/`)
- **AND** `cianfhoghlaim/tools/` exists as the canonical home
  (verified via `ls cianfhoghlaim/tools/`)
- **WHEN** a meaisínfhoghlaim agent file imports from
  `from meaisinfhoghlaim.agents.tools.X import ...`
- **THEN** Python raises
  `ModuleNotFoundError: No module named 'meaisinfhoghlaim.agents.tools'`
- **AND** the import MUST be rewired to the canonical home
  `from cianfhoghlaim.tools.X import ...`

#### Scenario: A future contributor adds a new tool to a meaisínfhoghlaim agent

- **GIVEN** a meaisínfhoghlaim agent file needs a new tool
- **WHEN** the contributor adds the import
- **THEN** the contributor MUST first check whether the canonical
  home `cianfhoghlaim/tools/` already provides the needed symbol
  (verified via `PYTHONPATH=. python3 -c "from cianfhoghlaim.tools.X import <symbol>"`)
- **AND** the contributor MUST import from the canonical oideachais
  location, NOT create a new `cianfhoghlaim/agents/tools/` package
- **AND** if the symbol is NOT in the canonical home, the contributor
  MUST add the new tool to `cianfhoghlaim/tools/`, NOT to a
  meaisínfhoghlaim-local duplicate

### Requirement: No broken relative tool imports in meaisínfhoghlaim agent files

The meaisínfhoghlaim `agents/` subtree MUST NOT contain any
`.py` file with a top-level (module-load-time) `from ..tools.X`
relative import. The path `cianfhoghlaim/tools/` does not
exist; any `from ..tools.X` import from a file under
`cianfhoghlaim/agents/` resolves to
`cianfhoghlaim/tools/X` and MUST raise
`ModuleNotFoundError` at module load time.

Every tool import in meaisínfhoghlaim agent code MUST be either:

1. An absolute cross-quadrant import from the canonical oideachais
   home (e.g. `from cianfhoghlaim.tools.curriculum_search import ...`),
   OR
2. A relative import that resolves correctly within the same package
   (e.g. `from .tools.X import ...` if `cianfhoghlaim/agents/tools/`
   is the canonical home — but currently no such home exists, so
   option 1 is the only valid path).

#### Scenario: A meaisínfhoghlaim agent file uses `from ..tools.X` for a tool

- **GIVEN** a `.py` file under `cianfhoghlaim/agents/`
  (e.g. `agui_curriculum_agent.py:25`,
  `curriculum_comparison_agent.py:14`,
  `geospatial_agent.py:15`,
  `statistics_agent.py:15`)
- **AND** the file contains a top-level import
  `from ..tools.X import ...`
- **AND** `cianfhoghlaim/tools/` does not exist
  (verified via `ls cianfhoghlaim/tools/`)
- **WHEN** the file is imported by any caller
- **THEN** Python raises
  `ModuleNotFoundError: No module named 'meaisinfhoghlaim.tools'`
  at module load time (NOT at function call time)
- **AND** the import MUST be rewired to the absolute canonical path
  `from cianfhoghlaim.tools.X import ...`

#### Scenario: A future contributor adds a new tool import to a meaisínfhoghlaim agent

- **GIVEN** a meaisínfhoghlaim `agents/*.py` file needs a new tool import
- **WHEN** the contributor adds the import
- **THEN** the contributor MUST first verify the target module
  exists via `ls <target-path>/X.py`
- **AND** the contributor MUST first verify the canonical symbol is
  importable via
  `PYTHONPATH=. python3 -c "from cianfhoghlaim.tools.X import <symbol>"`
- **AND** the import line MUST use the absolute canonical path
  `from cianfhoghlaim.tools.X import ...`,
  NOT the broken relative path `from ..tools.X import ...`

### Requirement: No pre-split multi-source DLT file duplicates in meaisínfhoghlaim

The meaisínfhoghlaim quadrant MUST NOT contain a single `.py` file that
bundles multiple `@dlt.source` functions together when those same
source functions already exist as separate canonical files in
`cianfhoghlaim/dlt_sources/ie/{culture,education,...}/`.

If a DLT source function exists at the canonical split location
(e.g. `cianfhoghlaim.dlt.ie.culture.canuint.canuint_source`),
meaisínfhoghlaim MUST NOT retain a duplicate copy in a pre-split
multi-source file (e.g. `meaisinfhoghlaim.language.gaeilge.canuint`).

The canonical home for each multi-source DLT pattern is one
canonical file per `@dlt.source` function. Any pre-split bundled
copy is a stale duplicate and MUST be deleted.

#### Scenario: A meaisínfhoghlaim pre-split multi-source DLT file exists

- **GIVEN** a meaisínfhoghlaim file at
  `cianfhoghlaim/language/gaeilge/canuint.py` (1,041 lines)
  bundles 5 `@dlt.source` functions
  (`canuint_source` + `canuint_search_source` + `canuint_audio_source`
  + `canuint_dialect_summary_source` + `canuint_word_alignment_source`)
- **AND** the canonical split already exists at
  `cianfhoghlaim/dlt_sources/ie/culture/{canuint,canuint_search,canuint_audio,canuint_dialect_summary,canuint_word_alignment}.py`
  (1,095 lines across 5 files)
- **AND** the canonical split files all import cleanly via
  `PYTHONPATH=. python3 -c "from cianfhoghlaim.dlt.ie.culture.canuint import canuint_source"`
- **WHEN** the audit confirms the pre-split file has 0 active
  importers across `sruth/`
- **THEN** the pre-split file MUST be deleted
  (via `git mv` into the openspec change archive)
- **AND** any future DLT source function additions MUST go to a
  NEW canonical file at
  `cianfhoghlaim/dlt_sources/ie/{culture,education,...}/<entity>.py`,
  NOT to a pre-split multi-source file in meaisínfhoghlaim

#### Scenario: A future contributor wants to add a 6th canuint source

- **GIVEN** the canonical 5 canuint split files exist at
  `cianfhoghlaim/dlt_sources/ie/culture/`
- **WHEN** a 6th canuint source function needs to be added
  (e.g. `canuint_regional_dialect_comparison_source`)
- **THEN** the contributor MUST create a new file
  `cianfhoghlaim/dlt_sources/ie/culture/canuint_regional_dialect_comparison.py`
  (the canonical split location)
- **AND** the contributor MUST NOT recreate a pre-split multi-source
  file at `cianfhoghlaim/language/gaeilge/canuint.py`
- **AND** the contributor MUST update the existing Phase 2 / Phase 5
  audit-trail rows in `cianfhoghlaim/README.md` if the new
  source introduces a fresh canonical split

### Requirement: OCR Model Registry Location (v4)

The system SHALL expose the OCR model registry at `cianfhoghlaim/ocr/models/registry.py`. The registry SHALL list **at least 20 vision models** (the 24-entry v4 registry trimmed of 4 models that don't fit on M4 48GB: qwen3-vl-235b-a22b 130GB, glm-4.6v-full 107GB, qwen3.6-35b-a3b-mtp 22GB marginal, gemma-4-31B 19GB marginal). The legacy 9×6 model registry at `cianfhoghlaim/ocr/model_registry.py` is REPLACED (gpt_4o, claude_3_5_sonnet, llama_3_2_vision, uccix_13b are removed; classical OCR stacks stay separate as Docker compose).

#### Scenario: Vision model dispatch

- **WHEN** Dagster materialises an Ireland Leaving Cert exam paper asset
- **THEN** the OCR dispatch picks a vision model from `cianfhoghlaim/ocr/models/registry.py:VISION_MODELS`
- **AND** the model runs on `litellm` (gateway), `llama-swap` (GGUF), or `mlx-omni` (MLX) backend per `cianfhoghlaim/ocr/backends/`

### Requirement: OCR Evaluation Harness (v4 NEW)

The system SHALL expose an OCR evaluation harness at `cianfhoghlaim/ocr/evaluation/compare.py` that compares vision models (Gemma-4 + Qwen3.6 + GLM-4.6V) against classical OCR Docker stacks (dots-ocr + docling-serve + olmocr + paddleocr) on the same documents.

#### Scenario: CER/WER comparison

- **WHEN** a developer runs `python -m cianfhoghlaim.ocr.evaluation.compare --corpus ireland_syllabus --backends vision,classical`
- **THEN** the harness reports CER, WER, fada-consistency, tironian-detection, and punctum-delens metrics per model/backend pair
- **AND** writes the report to `motherduck://cianfhoghlaim.ocr.evaluation.results`

### Requirement: 12 Agents × 5 Dagster Assets per Agent (L5 Agent Operations)

The `meaisinfhoghlaim-platform` capability SHALL emit every agent
in the 12-agent fleet through `CelticAgentOpsComponent`, which
registers exactly 5 Dagster assets per agent:

1. `agent_health_{name}` — `compute_kind="adk"|"agno"|"custom"` —
   pings the agent's HTTP endpoint and reports `latency_ms` +
   `last_observed_at` as MaterializeResult metadata. Schedule:
   `AutomationCondition.cron("*/5 * * * *")`.
2. `agent_routing_{name}` — verifies the agent's `routing_keywords`
   are registered in `meaisinfhoghlaim/agents/root_agent.py:ROUTING_KEYWORDS`
   and the keyword classification returns the expected bucket.
3. `agent_memory_{name}` — reads + writes a sentinel record to
   the agent's Letta memory namespace (`letta.cianfhoghlaim.ie:8283`)
   to verify the memory backend is reachable.
4. `agent_event_{name}` — publishes a `agent.{name}.ready` event
   to the RisingWave stream at `risingwave.cianfhoghlaim.ie:4566`
   to verify the event bus is reachable.
5. `agent_trace_{name}` — emits a Langfuse trace (v3 OTLP/HTTP)
   tagged with `agent.{name}` and a synthetic `agent_smoke_test`
   span. **Per user direction, the synthetic smoke-test span is
   dropped** (`MaterializeResult(metadata={"langfuse_span_dropped":
   True, "trace_tag": ...})`) so the trace history is not polluted.

The 12 agents map to the L5 sub-folders as follows:

| Framework | Agents | L5 sub-folder |
|:--|:--|:--|
| Custom | `root_agent` (1) | `5_agent_ops/custom/` |
| ADK | 8 agents (`curriculum_agent`, `translation_agent`, `corpus_agent`, `research_agent`, `geospatial_agent`, `statistics_agent`, `curriculum_comparison_agent`, `mcp_curriculum_agent`) | `5_agent_ops/adk/` |
| Agno | 3 agents (`education_research_agent`, `bunchloch_research_agent`, `agui_curriculum_agent`) | `5_agent_ops/agno/` |
| Pipecat | `voice_agent` (1) | **DEFERRED to a follow-on change** per user direction |

Total emitted in this change: 12 agents × 5 assets = **60 new L5
assets** added to the Dagster graph in the
`5_agent_ops/{custom|adk|agno}/` group.

The `routing_keywords` list is APPENDED to
`meaisinfhoghlaim/agents/root_agent.py:ROUTING_KEYWORDS` at
Component scaffold time, so a new agent's keywords are routable
in the root_agent without a manual code edit.

#### Scenario: A developer scaffolds a new agent via the Component

- **WHEN** `dg scaffold defs CelticAgentOpsComponent hybrid_curriculum_agent --agent-name hybrid_curriculum_agent --framework agno --memory-backend letta --event-stream risingwave --langfuse-trace-tag agent.hybrid_curriculum --routing-keywords hybrid 4-framework all-frameworks` runs
- **THEN** a YAML defs file is created at `defs/5_agent_ops/agno/hybrid_curriculum_agent/defs.yaml`
- **AND** 5 new assets are emitted: `5_agent_ops/agno/hybrid_curriculum_agent/agent_health_hybrid_curriculum_agent`, `agent_routing_*`, `agent_memory_*`, `agent_event_*`, `agent_trace_*`
- **AND** the 3 keywords `["hybrid", "4-framework", "all-frameworks"]` are appended to `root_agent.py:ROUTING_KEYWORDS["hybrid_curriculum_agent"]`
- **AND** `dg check yaml` reports the new assets pass
- **AND** `dg list defs` shows 5 new assets in the `5_agent_ops/agno/` group

#### Scenario: All 5 emitted assets materialise for a healthy agent

- **GIVEN** `5_agent_ops/adk/curriculum_agent/{health,routing,memory,event,trace}` are emitted
- **WHEN** `dg launch --select "5_agent_ops/adk/curriculum_agent/*"` runs
- **THEN** all 5 assets materialise successfully
- **AND** `agent_health_curriculum_agent` returns `MaterializeResult(metadata={"latency_ms": <ms>, "last_observed_at": <iso>})`
- **AND** `agent_routing_curriculum_agent` verifies the keyword `curriculum` is in the `ROUTING_KEYWORDS["curriculum_agent"]` bucket
- **AND** `agent_memory_curriculum_agent` confirms Letta memory read+write succeeded
- **AND** `agent_event_curriculum_agent` publishes the `agent.curriculum_agent.ready` event to RisingWave at `risingwave.cianfhoghlaim.ie:4566`
- **AND** `agent_trace_curriculum_agent` returns `MaterializeResult(metadata={"langfuse_span_dropped": True, "trace_tag": "agent.curriculum"})` (per user direction, no trace is persisted)

#### Scenario: A missing agent endpoint fails the health asset and blocks downstream L2 assets

- **GIVEN** the `curriculum_agent` HTTP endpoint at `adk.cianfhoghlaim.ie:7777/curriculum/health` returns 503
- **WHEN** `dg launch --select 5_agent_ops/adk/curriculum_agent/agent_health_curriculum_agent` runs
- **THEN** the asset materialises with `MaterializeResult(metadata={"healthy": false, "status_code": 503})`
- **AND** a Sensor is fired (`5_agent_ops/adk/curriculum_agent_down`) that pages the operator via n8n
- **AND** the downstream `2_materials/baml_extraction/leaving_cert_math` asset is BLOCKED via `AutomationCondition.all_deps_blocked()` until the health asset recovers

#### Scenario: The pipecat voice agent is deferred

- **WHEN** `dg list defs --json | jq '.[] | .group_name' | grep pipecat` runs
- **THEN** 0 hits SHALL appear (the `5_agent_ops/pipecat/` sub-folder is intentionally absent in this change)
- **AND** a follow-on change `2026-07-add-pipecat-voice-agent-to-l5` (tracked but out of scope here) will add the 13th L5 sub-folder + 5 emitted assets

### Requirement: 12 Python OCR/VLM/memory packages in the dagster-local image

The system SHALL keep the `12 Python OCR/VLM/memory packages in the dagster-local image` requirement inside the main `## Requirements` section of `openspec/specs/meaisinfhoghlaim-platform/spec.md`. This requirement SHALL begin with a normative SHALL/MUST statement so OpenSpec strict validation parses it correctly.

The `dagster-local` Docker image SHALL install the Python packages required for the v4 OCR/VLM/memory stack: OCR packages, VLM packages, document-to-markdown packages, in-process GGUF runtime support, memory packages, and the Hugging Face CLI package.

#### Scenario: Requirement is parsed by strict validation

- **GIVEN** `openspec/specs/meaisinfhoghlaim-platform/spec.md`
- **WHEN** `openspec validate meaisinfhoghlaim-platform --strict` runs
- **THEN** the spec is valid
- **AND** this requirement is visible under the main `## Requirements` section

#### Scenario: The dagster image imports all required packages

- **WHEN** the `dagster-local` image runs a Python import smoke test for the declared OCR/VLM/memory packages
- **THEN** the command SHALL exit 0 with no `ImportError`

### Requirement: pyproject.toml extra `ocr-vision-full`

The system SHALL keep the `pyproject.toml extra ocr-vision-full` requirement inside the main `## Requirements` section of `openspec/specs/meaisinfhoghlaim-platform/spec.md` so it is visible to strict validation.

The `cianfhoghlaim/pyproject.toml` SHALL provide an `ocr-vision-full` optional-dependency group and a `dev-with-vision` composite extra for the dev notebooks that require the OCR/VLM stack.

#### Scenario: dev-with-vision installs all required dependencies

- **WHEN** `uv pip install -e '.[dev-with-vision]'` runs
- **THEN** the environment SHALL contain the OCR, VLM, doc-to-markdown, memory, notebook, and quality-tool dependencies required by the v4 dev notebook set

### Requirement: 25 dev marimo notebooks for LC5 + Gemini

The system SHALL keep the `25 dev marimo notebooks for LC5 + Gemini` requirement inside the main `## Requirements` section of `openspec/specs/meaisinfhoghlaim-platform/spec.md` so it is visible to strict validation.

The system SHALL provide working dev notebooks for the LC5 and Gemini pipelines, with parseable `@app.cell` cells, SQL-backed exploration, and visualisations.

#### Scenario: All dev notebooks parse

- **WHEN** the notebook parse smoke test runs across the LC5 and Gemini notebook directories
- **THEN** all notebooks SHALL parse without syntax errors

### Requirement: PlanetScale Postgres Centralisation (meaisinfhoghlaim-platform)

The system SHALL migrate the 10 meaisínfhoghlaim sub-packages (Cognee + Logfire + per-package event log state) to PlanetScale PostgreSQL per `openspec/specs/planetscale-postgres-data-strategy/spec.md` R7.

#### Scenario: A consumer reads the platform spec

- **GIVEN** the platform spec is opened alongside the planetscale-postgres-data-strategy umbrella
- **WHEN** they look up `cognee` / `logfire` / per-package event logs
- **THEN** they see the PlanetScale PG row in the matrix
- **AND** each sub-package SHALL read from the canonical Locket-injected secret

#### Scenario: Migration is per-package, not big-bang

- **GIVEN** the Phase B change has archived
- **WHEN** the operator inspects a sub-package
- **THEN** only the sub-package's compose.yaml + secrets.env SHALL be touched
- **AND** the platform-level commands SHALL remain unchanged

## Known issues (from `cianfhoghlaim/README.md`)
| # | Issue | Tracked in | Severity |
|--:|:--|:--|:--|
| 1 | Most sub-packages are stubs; the 4 heartbeats are the first real assets | the 10 sub-packages | high |
| 2 | No `[tool.uv.sources]` block; sibling workspace members are not declared as local-path dependencies | `cianfhoghlaim/pyproject.toml` | high — blocks cross-quadrant imports |
| 3 | The 6 Celtic-language subdirs are stubs | the 6 subdirs | medium |
| 4 | No production dagster code-location (only the 4 heartbeats) | `cianfhoghlaim/dagster_defs/assets/healthchecks.py` | medium |
| 5 | The `baml_src → scéimre` rename was deferred per `lateralise-british-isles-domains` | the AGENTS.md | low — deferred |

## Cross-references

- [`cianfhoghlaim/`](../../cianfhoghlaim/) (the AI/ML quadrant)
- [`cianfhoghlaim/README.md`](../../cianfhoghlaim/README.md) (the status table + known issues)
- [`cianfhoghlaim/AGENTS.md`](../../cianfhoghlaim/AGENTS.md) (the developer-quick-reference)
- [`cianfhoghlaim/pyproject.toml`](../../cianfhoghlaim/pyproject.toml) (the uv workspace member)
- [`dg.toml`](../../dg.toml) (the root Dagster code-location config)
- [`openspec/specs/meaisinfhoghlaim-agent-frameworks/spec.md`](meaisinfhoghlaim-agent-frameworks/spec.md) (the 12 agents)
- [`openspec/specs/meaisinfhoghlaim-ocr-htr/spec.md`](meaisinfhoghlaim-ocr-htr/spec.md) (the 10 OCR models)
