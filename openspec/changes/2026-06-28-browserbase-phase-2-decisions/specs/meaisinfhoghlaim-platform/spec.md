# meaisinfhoghlaim-platform (delta: Phase 2 research findings)

> Filled by Phase 2 research agent (23/23 prompts complete).
> See `openspec/research/2026-06-28-browserbase-credit-program/phase-2/`.

## ADDED Requirements

### Requirement: LiteLLM is the canonical LLM gateway with minimax alias

The system SHALL use LiteLLM as the canonical LLM gateway, with the
`minimax` alias as the default model (7-tier fallback chain per
`openspec/changes/litellm-minimax-vendor-derisking`).

#### Scenario: LiteLLM default_model = minimax

- **GIVEN** the LiteLLM stack is running with the canonical config
- **WHEN** a request without an explicit model is sent to LiteLLM
- **THEN** LiteLLM routes it through the `minimax` alias
- **AND** the alias tries the 7 fallback entries in order
- **AND** the response is attributed to whichever entry answered

### Requirement: MotherDuck + LiteLLM is the canonical analytics + LLM stack

The system SHALL use MotherDuck (managed DuckDB) + LiteLLM (LLM
gateway) as the canonical analytics + LLM stack, with MotherDuck
Dives for cross-team dashboards and LiteLLM `minimax` for LLM calls.

#### Scenario: Dive + LLM combo

- **GIVEN** a MotherDuck Dive that summarizes a dataset
- **WHEN** the summary is generated
- **THEN** the Dive calls LiteLLM `minimax` for the summary text
- **AND** Langfuse traces both the DuckDB query and the LLM call

### Requirement: Unsloth + Modal is the canonical fine-tuning stack

The system SHALL use Unsloth (local M4 Max, MLX + GGUF, QLoRA 4-bit) as
the primary fine-tuning framework, with Modal (serverless GPU cloud)
as the burst-capacity overflow for models >48 GB.

#### Scenario: Fine-tune local on M4 Max

- **GIVEN** an OCR model fine-tuning task for Gemma 4 26B on Irish data
- **WHEN** the user runs `unsloth_finetune.py` on the MacBook M4 Max
- **THEN** Unsloth loads the model in 4-bit QLoRA
- **AND** training runs at ~2x vanilla HF Transformers speed
- **AND** the resulting GGUF Q4_K_M checkpoint is exported for llama-swap

#### Scenario: Burst to Modal A100

- **GIVEN** a fine-tuning task for a 70B model that exceeds M4 Max 48 GB RAM
- **WHEN** the user runs `modal_unsloth.py` with `--gpu A100`
- **THEN** Modal provisions an A100 (40 GB) container
- **AND** the training runs on cloud GPU
- **AND** the trained model is persisted to the `cianfhoghlaim-models` Modal Volume

### Requirement: RisingWave + olake is the canonical CDC stack

The system SHALL use RisingWave (streaming SQL) + olake (batch CDC) as
the canonical CDC stack, both writing to the same Iceberg catalog.

#### Scenario: RisingWave CDC stream

- **GIVEN** a PlanetScale Postgres OLTP database
- **WHEN** a CDC event arrives
- **THEN** RisingWave captures it via logical replication
- **AND** writes to the Iceberg catalog with sub-second latency

#### Scenario: olake batch CDC

- **GIVEN** a PlanetScale Postgres OLTP database
- **WHEN** the olake batch job runs (every 15 minutes)
- **THEN** olake captures changed rows since the last run
- **AND** writes to the same Iceberg catalog as RisingWave

### Requirement: mlflow + langfuse is the canonical model + observability stack

The system SHALL use mlflow (model registry) + langfuse (LLM
observability) as the canonical model + observability stack.

#### Scenario: MLflow model registration

- **GIVEN** a trained OCR model checkpoint
- **WHEN** `mlflow.register_model(...)` is called
- **THEN** the model is registered in the mlflow registry
- **AND** the artifact is stored in `s3://mlflow-artifacts/`

#### Scenario: Langfuse auto-trace

- **GIVEN** a LiteLLM call
- **WHEN** the call completes
- **THEN** Langfuse auto-captures the trace
- **AND** the trace includes tokens used, latency, and any
  fallback-triggered events

### Requirement: PlanetScale Postgres is the canonical managed DB

The system SHALL use PlanetScale (managed MySQL-compatible Postgres) as
the canonical managed database for the 7 stateful services (lakehouse,
cognee, motherduck, litellm, langfuse, mlflow, pangolin-ee).

#### Scenario: PlanetScale per-service database

- **GIVEN** a service needing persistent state
- **WHEN** the service deploys
- **THEN** it gets its own database in PlanetScale (e.g., `lakehouse_catalog`)
- **AND** its own user with least-privilege grants on that database

### Requirement: OpenChamber is the canonical agent IDE

The system SHALL use OpenChamber as the canonical agent IDE for
human operators building, testing, and deploying AI agents.

#### Scenario: OpenChamber in TanStack Start

- **GIVEN** an operator opens the agent IDE
- **WHEN** they navigate to `oideachais-web/agents`
- **THEN** the OpenChamber UI loads (iframe-embedded)
- **AND** they can run agents using the configured LLM

### Requirement: HuggingFace + invokeai is the canonical model hub + image gen stack

The system SHALL use HuggingFace Hub as the canonical model hub (for
downloading GGUF + MLX models) and InvokeAI as the canonical image
generation server (SDXL + Z-Image-Turbo).

#### Scenario: HF model download

- **GIVEN** a model registry entry (e.g., `unsloth/gemma-4-26B-A4B-it-GGUF`)
- **WHEN** `huggingface-cli download` runs
- **THEN** the GGUF files are downloaded to `~/.cache/huggingface`
- **AND** llama-swap can serve the model

#### Scenario: InvokeAI image generation

- **GIVEN** a request to generate a tuatha MMO asset (e.g., a Crypteolas badge)
- **WHEN** the request hits LiteLLM's `image` alias
- **THEN** LiteLLM forwards to InvokeAI at `http://invokeai:9090/api/v1`
- **AND** InvokeAI generates the image via SDXL or Z-Image-Turbo

### Requirement: Unsloth 3.0 FastModel + `train_on_responses_only` is the canonical fine-tuning loader (Wave 2)

The system SHALL use **Unsloth 3.0+ `FastModel`** (the unified loader
that supersedes `FastVisionModel` for Gemma 4) and SHALL apply the
four Wave-2 patch categories: (1) `use_cache=False` for Gemma-4 E2B/E4B
(fixes garbage logits), (2) `num_kv_shared_layers=0` for Gemma-4
31B/26B (fixes IndexError), (3) `train_on_responses_only` in
`UnslothTrainer.train()` (the +1% accuracy booster per the QLoRA
paper), and (4) Dynamic 2.0 GGUFs for the export.

#### Scenario: Fine-tune Gemma-4 26B-A4B with FastModel

- **GIVEN** an Irish OCR fine-tuning task for
  `unsloth/gemma-4-26B-A4B-it`
- **WHEN** the user runs `unsloth_finetune.py --base-model
  gemma-4-26B-A4B`
- **THEN** Unsloth loads the model via
  `FastModel.from_pretrained(model_name=..., max_seq_length=8192,
  load_in_4bit=True)`
- **AND** the LoRA is applied via `FastModel.get_peft_model(...)` with
  `finetune_vision_layers=False, finetune_language_layers=True,
  finetune_attention_modules=True, finetune_mlp_modules=True, r=16`
- **AND** `train_on_responses_only=True` is set in `SFTConfig`
- **AND** the resulting Dynamic 2.0 GGUF Q4_K_M checkpoint is exported

### Requirement: Google ADK agents SHALL route through LiteLLM via `LiteLlm` 1-line swap (bypass fix)

The system SHALL replace every `LlmAgent(model="gemini-2.0-flash")`
hardcode in the 5 specialised meaisínfhoghlaim agents (32 `LlmAgent`
sites total across `research_agent`, `education_research_agent`,
`bunchloch_research_agent`, `curriculum_comparison_agent`,
`statistics_agent`, `geospatial_agent`, `agui_curriculum_agent`) with
`LlmAgent(model=LiteLlm(model="minimax",
api_base="http://litellm:4000"))` (ADK 1.5+ ships
`from google.adk.models.lite_llm import LiteLlm`), gated on the
`minimax_alias_health` Dagster asset check.

#### Scenario: ADK agent routes through minimax fallback chain

- **GIVEN** an ADK agent constructed with
  `LlmAgent(model=LiteLlm(model="minimax",
  api_base="http://litellm:4000"))`
- **WHEN** the agent receives a prompt and the underlying provider
  returns 503
- **THEN** the LiteLlm wrapper transparently retries through the
  `minimax` 7-tier fallback chain
- **AND** the response is attributed to whichever fallback entry
  answered (e.g. `opencode-go/kimi-k2.6`)
- **AND** Langfuse auto-traces the call with
  `metadata.fallback_triggered=true`

### Requirement: Pydantic Logfire is the canonical Python tracing layer (Wave 2 confirmed)

The system SHALL use **Pydantic Logfire** as the canonical Python-side
tracing layer for every FastAPI service, every Celery worker, and every
BAML extraction call (Langfuse is reserved for the LLM-call-side
telemetry), and SHALL install `logfire[fastapi,celery,baml]` in
`pyproject.toml` and configure it via `LOGFIRE_TOKEN` (Locket-injected).

#### Scenario: Logfire traces a BAML extraction

- **GIVEN** a FastAPI service calls
  `await baml.ExtractExaminationPDF(input)`
- **WHEN** the call returns the structured `ExaminationForm` model
- **THEN** Logfire auto-captures the span tree (HTTP request → BAML
  function → LiteLLM `minimax` call → JSON parser)
- **AND** the Logfire dashboard at `logfire.pydantic.dev` shows p50 /
  p95 latency, token usage, and exception rate
- **AND** the matching Langfuse trace (captured by the BAML `@observe`
  decorator) cross-links via the `trace_id`

### Requirement: BAML 0.13+ is the canonical LLM-structured-output layer

The system SHALL use **BAML 0.13+** as the canonical
LLM-structured-output layer for every extraction (`Examination`,
`CurriculumOutcome`, `IrishOCRDocument`, `WelshOCRDocument`,
`OfficialMediaPost`), defining schemas in `.baml` files under
`cianfhoghlaim/core/baml/_oideachais_src/` and using the
`ExtractEn` (cheap, fast) and `ExtractEnStrong` (expensive, accurate)
clients that both route through LiteLLM `minimax` alias.

#### Scenario: BAML extraction of Leaving Cert Maths 2024 PDF

- **GIVEN** an examinations.ie PDF for Leaving Cert Maths 2024
- **WHEN** `b.ExtractExaminationPDF(input={"pdf": "lc_maths_2024.pdf"},
  client="ExtractEnStrong")` runs
- **THEN** BAML returns a Pydantic `Examination` object with
  `subject="Mathematics", year=2024, component="Paper 2",
  question_count=8, max_marks=150`
- **AND** the underlying LiteLLM call traces to Langfuse + Logfire
  with the prompt + response + parsed-JSON
