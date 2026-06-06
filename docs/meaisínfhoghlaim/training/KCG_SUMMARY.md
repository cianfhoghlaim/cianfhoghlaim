# Training — KCG Summary

## What It Is
Three resources for LLM training and deployment. `open-instruct` (Allen AI) is the reference codebase for post-training open language models — used to build the Tülu 3 suite via SFT, DPO, and RLVR (reinforcement learning with verifiable rewards). `phone/` contains research notes on deploying fine-tuned LLMs and VLMs on iOS/Android devices. `utils/` holds auxiliary training utilities.

## Why This Matters for Kings' College Galway
Open-instruct is the blueprint for fine-tuning Irish-language models: the SFT → DPO → RLVR pipeline maps directly to curriculum-tuned LLMs that can generate Leaving Certificate answers with structured reasoning. The Tülu 3 recipe for mixing general + specialised data informs how to blend Irish educational content with general English capability. Phone deployment research supports the "Irish LLM on iPhone" vision — models accessible to every Irish secondary student without cloud dependency. The multi-node training scripts provide patterns for scaling from single-GPU Unsloth fine-tuning to distributed training on the M4 MacBook cluster.

## Key Patterns Preserved
- `open-instruct/README.md` — Project overview: Tülu 3 pipeline, available models, setup
- `open-instruct/AGENTS.md` — AI agent instructions for working with open-instruct
- `open-instruct/CLAUDE.md` — Claude-specific coding guidelines
- `open-instruct/docs/index.md` — Documentation index
- `open-instruct/docs/algorithms/finetune.md` — SFT training recipe and configuration
- `open-instruct/docs/algorithms/dpo.md` — Direct Preference Optimisation pipeline
- `open-instruct/docs/algorithms/grpo.md` — Group Relative Policy Optimisation (RLVR)
- `open-instruct/docs/algorithms/online_dpo.md` — Online DPO variant
- `open-instruct/docs/algorithms/ppo.md` — Proximal Policy Optimisation
- `open-instruct/docs/algorithms/rejection_sampling.md` — Rejection sampling for synthetic data
- `open-instruct/docs/algorithms/reward_modeling.md` — Reward model training
- `open-instruct/docs/algorithms/synthetic_preference_dataset.md` — Synthetic preference data generation
- `open-instruct/docs/algorithms/trained_model_location.md` — Where to find trained checkpoints
- `open-instruct/docs/data/preference-data.md` — Preference dataset format and sources
- `open-instruct/docs/get_started/installation.md` — Installation with uv
- `open-instruct/docs/get_started/ai2_internal_setup.md` — Allen AI internal infrastructure
- `open-instruct/docs/olmo2.md` — OLMo 2 model training specifics
- `open-instruct/docs/tulu1_tulu2.md` — Tülu 1 and 2 history
- `open-instruct/docs/tulu3.md` — Tülu 3 details and results
- `open-instruct/docs/safety.md` — Safety evaluation approach
- `open-instruct/docs/safety-eval/safety.md` — Safety evaluation methodology
- `open-instruct/docs/ai2_internal.md` — Internal infrastructure notes
- `open-instruct/docs/dataset_transformation.md` — Dataset transformation pipeline
- `open-instruct/human_eval/README.md` — Human evaluation setup
- `open-instruct/scripts/README.md` — Scripts overview
- `open-instruct/scripts/train/olmo3/README.md` — OLMo 3 training configuration
- `open-instruct/scripts/data/azure_batch/README.md` — Azure batch processing
- `open-instruct/scripts/data/filtering_and_updates/README.md` — Data filtering and deduplication
- `open-instruct/scripts/data/filtering_and_updates/TEST_README.md` — Testing for filtering scripts
- `open-instruct/scripts/persona_driven_data_gen/README.md` — Persona-driven synthetic data
- `open-instruct/scripts/synth_pref/README.md` — Synthetic preference data generation
- `open-instruct/decontamination/README.md` — Training set decontamination
- `phone/docs/Federated AI Marketplace on iPhone.md` — Federated learning on iOS research
- `phone/docs/Fine-tuning VLMs for iOS HTR.md` — Vision-language models for handwriting recognition on iPhone
- `phone/docs/How to Run and Deploy LLMs on your iOS or Android Phone _ Unsloth Documentation.md` — Mobile LLM deployment guide
- `phone/docs/Irish LLM for iPhone Development.md` — Irish-specific mobile LLM strategy

## Source Files
Full source removed (2026-06-06). Available at:
- open-instruct: https://github.com/allenai/open-instruct

## What Was Removed
Python source code, Jupyter notebooks (.ipynb), shell scripts (.sh), Dockerfiles, CI/CD configs, Python package files (pyproject.toml, setup.py), JSON data files, CSV datasets, model configs, training logs, Git metadata, images.
