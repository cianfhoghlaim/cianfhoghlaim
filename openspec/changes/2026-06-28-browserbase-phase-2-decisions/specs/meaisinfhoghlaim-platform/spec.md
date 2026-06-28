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
