# Change: Irish HuggingFace Dataset Integration (Phase 2)

## Why

This is **Phase 2** of the 5-phase × 10-stage Celtic pipeline overhaul (see `2026-09-25-celtic-pipeline-finalization-v1/proposal.md` §3).

The ciancheiltis sister repo carries `dlt_sources/common/huggingface_factory.py` — a DLT `@dlt.source` factory that wraps `datasets.load_dataset`. This wholesale-copy into cianfhoghlaim enables the integration of 50+ HuggingFace datasets for the Irish language (Gaeilge), covering:

- **Pretrain**: ReliableAI/Irish-Text-Collection + roisincrtai/llm-pretrain-gaelic-uccix-irish-textual-corpus + saillab/alpaca_irish_taco + saillab/alpaca-irish-cleaned + jmcinern/Irish_Prompt_Response_Human_Feedback + johndennehy101/irish-citizen-information-fine-tuning-data + ReliableAI/irish_fineweb_edu
- **Parallel**: c123ian/Irish_English_Translation + c123ian/dpo_irish_eng_translations + c123ian/irish_eng_dpo + CK0607/IRISH-ENGLISH-ALPACA + CK0607/Irish_Dialect_to_English_Synthetic + FrancophonIA/NTEU_French-Irish + blaniel/NTEU_French-Irish_scored + JerrySweeney/Irish_Translations + astasol/irish-dataset + jojo-ai-mst/Roleplay-Irish
- **Speech**: ymoslem/Living-Audio-Irish + ymoslem/Living-Audio-Irish-GA-EN-Mted + ymoslem/Wikimedia-Speech-Irish + ymoslem/Tatoeba-Speech-Irish + ymoslem/EUbookshop-Speech-Irish + shunyalabs/irish-speech-dataset
- **Eval**: ReliableAI/irish_belebele + ReliableAI/IrishQA + ReliableAI/irish_retrieval_data + ReliableAI/irish_aya_evaluation_suite + ReliableAI/irish_blimp + ReliableAI/irish_aime2024 + britllm/truthfulqa_irish + britllm/arc_irish + britllm/piqa_irish + britllm/xnli_brit + tktung/irish_grammar_test + tktung/irish_magpie_filtered + seamusl/gaHealth
- **Universal Dependencies**: universal-dependencies/universal_dependencies (configs: ga_idt, ga_twittirish, sga_dipsgg, sga_dipwbg, pgl_dipmitb, ow_ogam)
- **Domain**: dlite/tiny-corpus-ga + isaacus/irish-legislative-summaries + mawaskow/irish_forestry_incentives + dlite/dlite-tiny-corpus + dleemiller/irish_penny_journal

## What changes (10 stages)

### Stage 2.1 — LC datasets (ReliableAI Irish): `dlt_sources/common/huggingface_datasets/irish_pretrain.py`
- Wholesale-copy ciancheiltis's `huggingface_factory.py` → `dlt_sources/common/huggingface_factory.py`
- New: `dlt_sources/common/huggingface_datasets/irish_pretrain.py` (uses the factory)

### Stage 2.2 — JC datasets (ReliableAI eval + BritLLM): `dlt_sources/common/huggingface_datasets/irish_eval.py`

### Stage 2.3 — Speech (ymoslem Living-Audio): `dlt_sources/language/irish_speech/__init__.py`

### Stage 2.4 — Parallel (c123ian + CK0607 + FrancophonIA): `dlt_sources/language/irish_parallel/__init__.py`

### Stage 2.5 — Eval + UD (BritLLM + seamusl + tktung + UD treebanks): `dlt_sources/language/irish_eval/__init__.py` + BAML `eval_extract.baml`

### Stage 2.6 — CocoIndex: `cocoindex_flows/biep_parity/hf_irish_pretrain.py` (the UCCIX + alpaca + citizen-info mix)

### Stage 2.7 — DLT: 3 new sources registered to `celtic.irish_{pretrain, eval, parallel}` DuckLake namespaces

### Stage 2.8 — Dagster: `orchestration/defs/2_materials/hf_datasets/irish_hf_assets.py` (3 sources × 3 assets = 9 assets)

### Stage 2.9 — MotherDuck Dive `irish_hf_datasets_dive.py` + marimo `37_irish_hf_datasets_dashboard.py`

### Stage 2.10 — Tests + per-phase verify + archive

## Impact

- **Affected code**: ~10 new files (3 DLT sources + 1 CocoIndex App + 1 Dagster asset file + 1 MotherDuck Dive + 1 marimo notebook + 1 wholesale-copied huggingface_factory.py + 1 eval_extract.baml + 2 modification records)
- **Affected specs**: NEW `celtic-language-pipeline` (added by the umbrella change at Phase 5.9)

## Out of scope (deferred to Phase 4)

- Welsh + Manx + Cornish + Breton HF integration (the sibling phase)
- Tuatha sister-repo wholesale-copy
- Bonneagar IaC sister carry-over
