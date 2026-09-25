## ADDED Requirements

### Requirement: ihf-1 — HuggingFace factory wholesale-copied from ciancheiltis

The `dlt_sources/common/huggingface_factory.py` file MUST be wholesale-copied from the ciancheiltis sister repo with the `SisterLift:` provenance header prepended.

#### Scenario: provenance header present

- **WHEN** an operator runs `head -10 dlt_sources/common/huggingface_factory.py`
- **THEN** the output MUST contain `SisterLift: ciancheiltis @`

### Requirement: ihf-2 — 3 Irish HuggingFace DLT sources registered

The cianfhoghlaim DLT pipeline MUST have 3 Irish-language HuggingFace sources: `irish_pretrain` (ReliableAI + roisincrtai + saillab mix), `irish_eval` (ReliableAI + BritLLM + tktung + seamusl), `irish_parallel` (c123ian + CK0607 + FrancophonIA + JerrySweeney).

#### Scenario: 3 sources importable

- **WHEN** an operator runs `uv run python -c "from dlt_sources.common.huggingface_datasets import irish_pretrain, irish_eval, irish_parallel; print('OK')"`
- **THEN** the output MUST be `OK`

### Requirement: ihf-3 — 5 BAML eval extractors

The `baml_src/celtic/_shared/eval_extract.baml` file MUST provide 5 BAML eval extractors: `ExtractGrammarEval`, `ExtractMathReasoningEval`, `ExtractExtractiveQA`, `ExtractReadingComprehension`, `ExtractHealthNLP`.

#### Scenario: 5 functions reachable

- **WHEN** an operator runs `uv run python -c "from baml_client.sync_client import b; print([n for n in dir(b) if 'Extract' in n and any(s in n for s in ['Grammar', 'Math', 'Reading', 'Health', 'ExtractiveQA'])])"`
- **THEN** the output MUST list all 5 functions

### Requirement: ihf-4 — CocoIndex pretrain mix App

The `cocoindex_flows/biep_parity/hf_irish_pretrain.py` MUST embed the UCCIX + alpaca + citizen-info + jmcinern mix into LanceDB `cianhoghlaim.celtic.irish_hf.pretrain_chunks`.

#### Scenario: CocoIndex App loads

- **WHEN** an operator runs `uv run python -c "from cocoindex_flows.biep_parity.hf_irish_pretrain import irish_hf_pretrain_embedding; print('OK')"`
- **THEN** the output MUST be `OK`

### Requirement: ihf-5 — 9 Dagster assets + 1 MotherDuck Dive + 1 marimo notebook

The cianfhoghlaim orchestration MUST add 9 new HF dataset Dagster assets (3 sources × 3 stages), 1 new MotherDuck Dive (`irish_hf_datasets_dive.py`), and 1 new marimo notebook (`37_irish_hf_datasets_dashboard.py`).

#### Scenario: surface coverage

- **WHEN** an operator runs `ls orchestration/defs/2_materials/hf_datasets/irish_hf_assets.py motherduck/dives/irish_hf_datasets_dive.py notebooks/37_irish_hf_datasets_dashboard.py`
- **THEN** all 3 files MUST exist
