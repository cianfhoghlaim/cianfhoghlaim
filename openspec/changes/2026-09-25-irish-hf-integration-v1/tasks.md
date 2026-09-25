# Tasks: Irish HuggingFace Dataset Integration (Phase 2)

> **Sequential execution — 10 stages = ~10 working days.**
> Per-stage verify: ruff + baml-cli generate + unit tests. Per-phase verify: scripts/verify.sh + sync:all + lint:registry + openspec validate --strict.

## Stage 2.1 — LC datasets (ReliableAI Irish pretrain mix)

- [ ] 2.1.1. Wholesale-copy ciancheiltis `dlt_sources/common/huggingface_factory.py` → cianfhoghlaim `dlt_sources/common/huggingface_factory.py` (via `scripts/sister_lifts.py add ciancheiltis --src dlt_sources/common/huggingface_factory.py --dst dlt_sources/common/huggingface_factory.py --openspec-change 2026-09-25-irish-hf-integration-v1 --shared-rule Shared-3-cocoindex_flows_shared`)
- [ ] 2.1.2. Create `dlt_sources/common/huggingface_datasets/__init__.py` (new sibling tree)
- [ ] 2.1.3. Create `dlt_sources/common/huggingface_datasets/irish_pretrain.py` wrapping `ReliableAI/Irish-Text-Collection` + `ReliableAI/irish_fineweb_edu` + `roisincrtai/llm-pretrain-gaelic-uccix-irish-textual-corpus` → `celtic.irish_pretrain`
- [ ] 2.1.4. Verify: `uv run python -c "from dlt_sources.common.huggingface_datasets.irish_pretrain import irish_pretrain_source; print(irish_pretrain_source())"` produces `[]` (no network) or actual rows

## Stage 2.2 — JC datasets (ReliableAI eval + BritLLM)

- [ ] 2.2.1. Create `dlt_sources/common/huggingface_datasets/irish_eval.py` wrapping `ReliableAI/irish_belebele` + `IrishQA` + `irish_retrieval_data` + `irish_blimp` + `irish_aime2024` + `britllm/truthfulqa_irish` + `britllm/arc_irish` + `britllm/piqa_irish` → `celtic.irish_eval`
- [ ] 2.2.2. Verify: smoke import

## Stage 2.3 — Speech (ymoslem Living-Audio)

- [ ] 2.3.1. Create `dlt_sources/language/irish_speech/__init__.py` + `_irish_speech_helpers.py`
- [ ] 2.3.2. Create `dlt_sources/language/irish_speech/__init__.py` wrapping `ymoslem/Living-Audio-Irish` + `Living-Audio-Irish-GA-EN-Mted` + `Wikimedia-Speech-Irish` + `Tatoeba-Speech-Irish` + `EUbookshop-Speech-Irish` + `shunyalabs/irish-speech-dataset` → `celtic.irish_speech`

## Stage 2.4 — Parallel (c123ian + CK0607 + FrancophonIA + JerrySweeney)

- [ ] 2.4.1. Create `dlt_sources/language/irish_parallel/__init__.py` wrapping `c123ian/Irish_English_Translation` + `c123ian/dpo_irish_eng_translations` + `c123ian/irish_eng_dpo` + `CK0607/IRISH-ENGLISH-ALPACA` + `CK0607/Irish_Dialect_to_English_Synthetic` + `FrancophonIA/NTEU_French-Irish` + `blaniel/NTEU_French-Irish_scored` + `JerrySweeney/Irish_Translations` + `astasol/irish-dataset` + `jojo-ai-mst/Roleplay-Irish` → `celtic.irish_parallel`

## Stage 2.5 — Eval + UD

- [ ] 2.5.1. Create `dlt_sources/language_models/irish_eval_hf.py` extending the existing UD pipeline with `tktung/irish_grammar_test` + `seamusl/gaHealth` + `dleemiller/irish_penny_journal` + `britllm/xnli_brit` + `isaacus/irish-legislative-summaries` → `celtic.irish_grammar_eval`
- [ ] 2.5.2. Create `baml_src/celtic/_shared/eval_extract.baml` with `ExtractGrammarEval` + `ExtractMathReasoningEval` + `ExtractExtractiveQA` + `ExtractReadingComprehension` + `ExtractHealthNLP` (5 BAML functions)
- [ ] 2.5.3. Verify: `baml-cli generate` produces the 5 functions

## Stage 2.6 — CocoIndex

- [ ] 2.6.1. Create `cocoindex_flows/biep_parity/hf_irish_pretrain.py` — embeds the UCCIX + alpaca + jmcinern + johndennehy101 mix into LanceDB `cianhoghlaim.celtic.irish_hf.pretrain_chunks`
- [ ] 2.6.2. Verify: `uv run python -c "from cocoindex_flows.biep_parity.hf_irish_pretrain import irish_hf_pretrain_embedding; print('OK')"`

## Stage 2.7 — DLT consolidation

- [ ] 2.7.1. Register `irish_pretrain` + `irish_eval` + `irish_parallel` to the `dlt_sources/common/__init__.py` registry (so `dagster dev` auto-discovers them)
- [ ] 2.7.2. Verify: `uv run python -c "from dlt_sources.common.huggingface_datasets import irish_pretrain, irish_eval; print('OK')"`

## Stage 2.8 — Dagster

- [ ] 2.8.1. Create `orchestration/defs/2_materials/hf_datasets/__init__.py` (aggregator)
- [ ] 2.8.2. Create `orchestration/defs/2_materials/hf_datasets/irish_hf_assets.py` with 9 assets (3 per source: ingested / extractions / embeddings)
- [ ] 2.8.3. Verify: `uv run python -c "from orchestration.defs.hf_datasets.irish_hf_assets import irish_hf_pretrain_embeddings; print('OK')"`

## Stage 2.9 — MotherDuck + marimo

- [ ] 2.9.1. Create `motherduck/dives/irish_hf_datasets_dive.py` (per-dataset + per-task breakdown — pretrain, eval, parallel, speech)
- [ ] 2.9.2. Create `notebooks/37_irish_hf_datasets_dashboard.py` (operator-facing)
- [ ] 2.9.3. Verify: `uv run python -c "from motherduck.dives.irish_hf_datasets_dive import create_dive; print('OK')"`

## Stage 2.10 — Per-phase verify + archive

- [ ] 2.10.1. `bash scripts/verify.sh` → 8/8
- [ ] 2.10.2. `mise run lint:registry` → 0 hardcoded model strings
- [ ] 2.10.3. `openspec validate --strict` → valid
- [ ] 2.10.4. `uv run pytest tests/dlt/test_hf_datasets.py` (new test) → pass
- [ ] 2.10.5. `openspec archive 2026-09-25-irish-hf-integration-v1 -y --skip-specs`
- [ ] 2.10.6. `git push origin main`
