# Merge Plan: meaisínfhoghlaim

**Date:** 2026-06-06
**Current state:** 271 .md files across 17 subdirs + 44 root-level files
**Target:** 0 subdirectories, all content in ~8 root-level .md files

---

## Existing Consolidated Docs (Keep & Complete)

These root-level mega-merges already exist. Subdirectory stubs must be deleted:

| Consolidated Doc | Source Subdirs | Stubs Remaining |
|---|---|---|
| `fine-tuning-reference.md` | `fine-tuning/` (12 files) | 12 stubs |
| `model-serving-guide.md` | `models/` (17 files) | 17 stubs |
| `document-processing-reference.md` | `ocr/` (9) + `colpali/` (3) | 12 stubs |
| `agent-patterns-reference.md` | `agents/` (11) + root files | 11 stubs |
| `ai-ml-systems-consolidated.md` | Root-level cross-cutting | N/A (1,809 lines) |

---

## Planned Merges (New)

### Merge 1: `celtic-language-ai.md`
**Subdirs to merge:** `celtic/` (21 .md files)
**Root files to absorb:** `Celtic Language OCR Resource Analysis.md`, `Gaelic in the Digital Age...md`, `Call for papers_...md`, `Enhancing English-Irish Translation...md`, `Neuro-Symbolic Translation Model Training.md`, `Multimodal Irish Handwriting Generation Model.md`, `AI Chemistry Education Image Generation.md`, `Chemistry Education Asset Generation.md`, `Finetuning Qwen3-VL for Gaelic OCR.md`, `iOS App Development Ecosystem Strategy.md`
**Firecrawl supplement:** HuggingFace Celtic model pages (gaBERT, UCCIX, BritLLM, Qomhrá, Welsh-BERT), Gaois API docs
**Result:** Single `celtic-language-ai.md` at root covering all 4 Celtic languages (Irish, Welsh, Scottish Gaelic, Manx) with models, datasets, TTS/ASR, education strategy, and digitisation pipelines.

### Merge 2: `open-source-models-reference.md`
**Subdirs to merge:** `models/` stubs that exist at root as duplicates
**Root files to absorb:** `Unsloth Model Catalog _ Unsloth Documentation.md`, `What Model Should I Use for Fine-tuning...md`, `transformers.md`, `huggingface.md`, `gguf.md`, `Introducing AnyLanguageModel...md`, `Introducing Bolmo...md`, `Llama.cpp Model Management.md`, `Swift Transformers Reaches 1.0...md`, `Tokenization in Transformers v5...md`, `Tongyi-Zhiwen_QwenLong...md`, `utter-project_EuroLLM...md`, `madroidmaq_mlx-omni-server.md`, `apple_ml-fastvlm...md`, `Blaizzy_mlx-vlm...md`
**Firecrawl supplement:** llama.cpp latest docs, MLX-LM docs, GGUF format spec, Swift Transformers release notes
**Result:** Single `open-source-models-reference.md` covering model catalogs, formats (GGUF/MLX/safetensors), HuggingFace ecosystem, and model comparisons.

### Merge 3: `speech-audio-research.md`
**Subdirs to merge:** `audio/` (3 .md files) + `sam-audio/` (5 .md files)
**Root files to absorb:** `LLM based TTS models.md`, `Multimodal Irish Handwriting Generation Model.md`
**Firecrawl supplement:** SAM-Audio docs (facebookresearch/sam-audio), Common Voice Irish, ABAIR TTS
**Result:** Single `speech-audio-research.md` covering Irish TTS/ASR, SAM-Audio sound separation, Gaelic speech dataset scraping, and audio model fine-tuning.

### Merge 4: `three-d-generation.md`
**Subdirs to merge:** `sam3d_objects/` (1 .md), `sam3d-api/` (1 .md)
**Root files to absorb:** `Train a tiny model to generate 3D files...md`
**Firecrawl supplement:** SAM 3D docs, TripoSR, 3D generation landscape
**Result:** Single `three-d-generation.md` covering 3D generation, SAM ecosystem, Celtic heritage 3D digitisation.

### Merge 5: `federated-learning-research.md`
**Subdirs to merge:** `federated/` (10 .md files)
**Root files to absorb:** `Federated AI Marketplace on iPhone.md`, `Federated RAG Tutorial...md`, `syft-flwr_notebooks_fedrag...md`
**Firecrawl supplement:** Flower framework docs, SyftBox protocol, OpenMined
**Result:** Single `federated-learning-research.md` covering SyftBox+Flower integration, FedRAG, FL diabetes prediction pattern, and Celtic language FL strategy for GDPR-compliant school data.

### Merge 6: `image-generation-models.md`
**Subdirs to merge:** `FIBO/` (5 .md files)
**Root files to absorb:** `AI Chemistry Education Image Generation.md`, `Chemistry Education Asset Generation.md`
**Firecrawl supplement:** Bria AI FIBO docs, FLUX, Stable Diffusion for education
**Result:** Single `image-generation-models.md` covering FIBO (JSON-native 8B model), LoRA/LoLKr fine-tuning, Celtic art generation, and structured image generation for education.

### Merge 7: `geospatial-remote-sensing.md`
**Subdirs to merge:** `olmoearth_projects/` (14 .md files)
**Firecrawl supplement:** Allen AI OLMo Earth docs, Sentinel Hub, rslearn
**Result:** Single `geospatial-remote-sensing.md` covering OLMo Earth fine-tuning, segmentation models, Irish geography curriculum applications, and satellite data processing pipelines.

### Merge 8: `training-llm-recipes.md`
**Subdirs to merge:** `training/` (35 .md files)
**Root files to absorb:** `Streaming datasets_ 100x More Efficient.md`, `LoRA Hyperparameters Guide...md`, `Datasets Guide...md`, `Fine-tuning LLMs Guide...md`, `We Got Claude to Fine-Tune...md`, `Fine-tuning VLMs for iOS HTR.md`, `Irish LLM for iPhone Development.md`, `gpu_experiment_guide.md`, `AI Syllabus to JSON Schema.md`
**Firecrawl supplement:** Open-Instruct docs (SFT, DPO, GRPO, RLVR recipes), Tülu 3 paper, Unsloth RL docs
**Result:** Single `training-llm-recipes.md` covering open-instruct pipeline (SFT→DPO→GRPO), Unsloth training, mobile deployment, Irish-specific training, and dataset streaming.

---

## Remaining Root-Level Files (Preserve)

These standalone files do NOT get absorbed into merges:

| File | Lines | Content |
|---|---|---|
| `ai-compute-allocation-strategy.md` | ~200 | Tiered compute model (Planner/Worker) |
| `dual-engine-graph-llm-serving-integration.md` | ~100 | Graph + LLM serving |
| `huggingface-design-patterns-analysis.md` | ~300 | HF API design patterns |
| `huggingface-ontologies-research.md` | ~200 | Ontologies from HF |
| `langfuse-guide.md` | ~1,000 | LLM observability |
| `langfuse_ragas.md` | ~200 | RAG evaluation |
| `litellm-comprehensive-guide.md` | ~500 | LiteLLM gateway |
| `litellm-deployment-guide.md` | ~200 | LiteLLM deployment |
| `mlflow-llm-guide.md` | ~500 | MLflow LLM tracking |
| `mlflow_ragas.md` | ~100 | MLflow + RAGAS |
| `mlflow-model-registry-deployment-reference.md` | ~200 | MLflow registry |
| `mlflow (dagster-mlflow) _ Dagster Docs.md` | ~100 | Dagster-MLflow integration |
| `motherduck_mcp.md` | ~100 | MotherDuck MCP |
| `notebooklm_1.md` | ~100 | NotebookLM research |
| `React Drag-and-Drop for Exam Builder.md` | ~200 | React DnD for exams |
| `Productionalize AI Workloads...md` | ~300 | LanceDB + Ray |
| `Interactive AI Pipeline Development.md` | ~200 | AI pipeline dev |
| `Prompt Optimization (Beta).md` (×3) | ~300 each | Prompt optimization research |
| `Building an Agentic Tutor.md` | ~300 | Agentic tutoring |
| `Setting Up Local LLM Services on Mac.md` | ~200 | Mac LLM setup |
| `Local macOS MLX_MPS LLM Workflow.md` | ~200 | MLX workflow |
| `Integrating Skyvern with Crawl4AI_Stagehand.md` | ~200 | Browser automation |
| `Resource Maximization and Project Planning.md` | ~100 | Project planning |
| `Supercharge your OCR Pipelines...md` (root dupe) | ~500 | OCR reference |
| `Open-Source VLMs For PDF Extraction.md` (root dupe) | ~300 | VLM docs |
| `AI_MEMORY.md` | ~100 | AI memory concepts |
| `AGENTS.md` | ~200 | Agent instructions |
| `IMPLEMENTATION_GUIDE.md` | ~200 | Implementation guide |
| `QUICK_REFERENCE.md` | ~100 | Quick reference |
| `README.md`, `README_1.md`, `README_ANALYSIS.md` | ~300 | Various readmes |

**Recommendation:** These ~35 root files should be triaged in Phase 2 — some are duplicates of consolidated docs or stubs, others are unique research assets. A separate mini-plan (`ROOT_CLEANUP_PLAN.md`) should handle root-level deduplication.

---

## Deletion Plan

After each merge, delete the source subdirectory:

| Subdir | Status | Delete After |
|---|---|---|
| `agents/` | Already merged → `agent-patterns-reference.md` | ✅ Safe to delete |
| `audio/` | → `speech-audio-research.md` | After Merge 3 |
| `baml/` | Stubs (source removed via KCG) | ✅ Safe to delete |
| `celtic/` | → `celtic-language-ai.md` | After Merge 1 |
| `colpali/` | Already merged → `document-processing-reference.md` | ✅ Safe to delete |
| `federated/` | → `federated-learning-research.md` | After Merge 5 |
| `FIBO/` | → `image-generation-models.md` | After Merge 6 |
| `fine-tuning/` | Already merged → `fine-tuning-reference.md` | ✅ Safe to delete |
| `ml-models/` | Stubs (source removed) | ✅ Safe to delete |
| `models/` | Already merged → `model-serving-guide.md` | ✅ Safe to delete |
| `notebooks/` | → `training-llm-recipes.md` (unsolth/vlm docs) | After Merge 8 |
| `ocr/` | Already merged → `document-processing-reference.md` | ✅ Safe to delete |
| `olmoearth_projects/` | → `geospatial-remote-sensing.md` | After Merge 7 |
| `sam-audio/` | → `speech-audio-research.md` | After Merge 3 |
| `sam3d_objects/` | → `three-d-generation.md` | After Merge 4 |
| `sam3d-api/` | → `three-d-generation.md` | After Merge 4 |
| `training/` | → `training-llm-recipes.md` | After Merge 8 |

---

## Firecrawl Research Summary

| Tool/Framework | Firecrawl Result | Key Findings |
|---|---|---|
| **Unsloth** (docs.unsloth.ai) | ✅ Complete | Now supports Unsloth Studio (no-code UI), Dynamic 2.0 GGUFs, FP8 RL, API endpoint, 500+ models |
| **BAML** (boundaryml.com) | ⚠️ Blog post 404 | Need to scrape docs.boundaryml.com for current state |
| **ColPali** (github.com/illuin-tech/colpali) | ✅ Complete | Active development: ColQwen3, ColQwen3.5, ColSmol, BiGemma3, token pooling, Plaid indexing; 2.7k stars |
| **Agno** (docs.agno.com) | ✅ Complete | Rebranded from PhiData: AgentOS runtime, multi-user sessions, RBAC, audit logs, SDK + control plane |
| **Stagehand** (github.com/browserbase/stagehand) | ✅ Complete | V3 released: act/extract/observe API, AI-native browser automation, Playwright-based |
| **Google ADK** (adk.dev) | ✅ Complete | ADK 2.0: Graph workflows, multi-language (Python/TS/Go/Java/Kotlin), Agents CLI, enterprise deployment |
| **Flower FL** (not scraped) | ⏭️ Deferred | Covered by existing KCG summaries and syft-flwr docs |
| **Open-Instruct** (not scraped) | ⏭️ Deferred | Covered by existing training/ docs with 35 .md files |

---

## Execution Order

The merges should be executed in this order (dependencies noted):

1. **Phase 2a:** Delete already-merged stubs (agents/, colpali/, fine-tuning/, ml-models/, models/, ocr/, baml/)
2. **Phase 2b:** Merge 1 (celtic-language-ai.md) — largest merge, 21+ files
3. **Phase 2c:** Merge 2 (open-source-models-reference.md) — model catalog
4. **Phase 2d:** Merge 8 (training-llm-recipes.md) — training recipes
5. **Phase 2e:** Merges 3-7 in parallel (speech, 3D, federated, image-gen, geospatial)
6. **Phase 2f:** Root cleanup (deduplicate ~35 root files, remove stubs)
7. **Phase 2g:** Update INDEX.md and cross-references

---

## Stats Summary

| Metric | Count |
|---|---|
| Total .md files currently | 271 |
| Subdirectories to flatten | 17 |
| Planned merged files | 8 new + 5 existing |
| Subdirs safe to delete immediately | 7 (already merged) |
| Subdirs needing merge first | 10 |
| Root files preserved as-is | ~35 (Phase 3 cleanup needed) |
| Firecrawl scrapes completed | 6 |
