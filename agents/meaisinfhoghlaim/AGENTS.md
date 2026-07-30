# agents/meaisinfhoghlaim — OCR/HTR/Alignment Sub-Package

> **The OCR/HTR/alignment sub-package** for the agent fleet.
> Houses the 10 OCR backends (split across `meaisinfhoghlaim/backends/adapters.py`
> for the 4 HTTP adapters + `meaisinfhoghlaim/ocr/ensemble/ensembled_extractor.py`
> for the 6 VLM/ensemble paths) + the 3 alignment primitives + the
> 3 educational agents. The canonical home for OCR/HTR processing of
> scanned curricula, manuscripts, and historical documents.

## Priority quick reference

### Priority skills (5 of 53)

| Skill | When to load |
|:--|:--|
| [`agent-observability`](../.agents/skills/agent-observability/SKILL.md) | The 5-layer observability stack (used by OCR/HTR pipelines) |
| [`cognee`](../.agents/skills/cognee/SKILL.md) | The knowledge graph backend (used by OCR/HTR pipelines) |
| [`baml`](../.agents/skills/baml/SKILL.md) | BAML extraction patterns for OCR outputs |
| [`centralized-registry`](../.agents/skills/centralized-registry/SKILL.md) | The single source of truth for models + schemas + pipelines + stacks |
| [`dignified-python`](../.agents/skills/dignified-python/SKILL.md) | Production Python standards |

## Centralized Registries

The `meaisinfhoghlaim/` package hosts the **canonical 4-artifact
centralized registry** (per the 2026-08-15
`centralized-model-registry` + `centralized-schema-registry` +
`deployment-control-panel` openspec change):

- **Canonical (4):**
  - `meaisinfhoghlaim/models/model_registry.py` — the 58-entry
    `MODEL_REGISTRY` across 7 families (ocr_vision / text_llm /
    embedder / rerank / image_gen / voice / translation).
  - `notebooks/_shared/schema.py` — the 5 introspection helpers
    (`schema_introspect`, `list_dlt_sources`, `list_cocoindex_apps`,
    `list_baml_classes`, `read_deployment_choice`).
  - `notebooks/00_control_panel.py` — the 5-tab marimo control
    panel (Models / Pipelines / Datasets / Stacks / Registry).
  - `deployment-choice.yaml` (repo root) — the enablement file.
- **Supporting (4):**
  - `scripts/registry_audit.py` — drift detector (fails CI on
    hardcoded model strings).
  - `agents/adk/litellm_agent.py` — `make_litellm_agent()` helper
    + `litellm_model("minimax")` wrapper.
  - `orchestration/defs/2_materials/_base/jurisdiction_assets_base.py`
    — `JurisdictionAssetsBase` (the 10 per-jurisdiction Dagster
    asset base class).
  - 3 CocoIndex factories (`european_nations/_factory.py` et al.).
- **Cascade target:** all subagents use `MODEL_REGISTRY.resolve()`
  (or `model_for()`) instead of hardcoded model strings.
- **Lint gate:** `mise run lint:registry` — fails on any hardcoded
  model string in `agents/`, `baml_src/`, `notebooks/`, `web/`,
  `orchestration/`, `spaces/`, `meaisinfhoghlaim/`.

See `.agents/skills/centralized-registry/SKILL.md` for the full
guide.

### Priority commands

```bash
# The 6 canonical CLASSICAL_OCR backends (post-v7)
python -c "from meaisinfhoghlaim.models.registry import CLASSICAL_OCR; print(len(CLASSICAL_OCR))"
# Expected: 6 (the canonical 6 from the 2026-07-17 phantom-agents fix)

# The M4-Max dispatch helper (post-v7)
python -c "from meaisinfhoghlaim.models.registry import select_optimal_for_m4_max; print(select_optimal_for_m4_max())"
# Expected: gemma-4-26B-A4B

# The 26 VISION_MODELS (post-v7)
python -c "from meaisinfhoghlaim.models.registry import VISION_MODELS; print(len(VISION_MODELS))"
# Expected: 26 (24 v4 + 2 v5 BIEP v2 entrants)
```

### Priority openspec specs (2)

| Spec | One-liner |
|:--|:--|
| `meaisinfhoghlaim-platform` | The 10 sub-packages + the 4 heartbeat Dagster assets |
| `meaisinfhoghlaim-ocr-htr` | The 10 OCR models across the canonical 6 backends |

## Overview

`agents/meaisinfhoghlaim/` is the **OCR/HTR/alignment sub-package**
for the agent fleet. It houses:

- **10 OCR backends** split across 2 canonical surfaces:
  - **4 HTTP adapters** at `meaisinfhoghlaim/backends/adapters.py`:
    PaddleOCR / Docling / Dots-OCR / Unstract (the T4 modernisation
    wired to the v4 6-entry `CLASSICAL_OCR` registry)
  - **6 ensemble paths** at `meaisinfhoghlaim/ocr/ensemble/ensembled_extractor.py`:
    BAML (Phase B1 stub) + Unstract + qwen3-vl-8b + gemma-4-26B-A4B
    + 2 reserved for future PH2 entrants
- **3 alignment primitives** (cross-frame, cross-archive, cross-nation)
- **3 educational agents** at `agents/meaisinfhoghlaim/educational/`
  - `academic_history_agent` — the cross-archive academic history
  - `celtic_grammar_agent` — the Celtic grammar specialist
  - `celtic_morphology_agent` — the Celtic morphology specialist

The sub-package is part of the `meaisinfhoghlaim/` (top-level)
package which is the canonical home for OCR/HTR/alignment work.
The `agents/meaisinfhoghlaim/` sub-tree provides the agent-side
integration.

## The 6 CLASSICAL_OCR backends + 26 VISION_MODELS

The canonical 6 `CLASSICAL_OCR` backends (per the
`2026-07-17-fix-phantom-agents-and-ocr-backend-list-v1` change):

| Backend | Purpose | Port |
|:--|:--|--:|
| **Docling-serve** | Document layout + table extraction | 5001 |
| **PaddleOCR** | Multilingual OCR (100+ languages) | 8888 |
| **Tesseract** | The classic OCR engine | 8889 |
| **Tesseract-shadow** | Tesseract 4 shadow variant for A/B testing | 8890 |
| **Unstract** | No-code LLM-powered extraction | 8002 |
| **Dots-OCR** | High-fidelity OCR for handwritten text | 8001 |

The 26 `VISION_MODELS` (VLM + OCR-vision, separate from the
classical OCR Docker stacks):

- **Gemma 4 family** — `gemma-4-E2B`, `gemma-4-E4B`, `gemma-4-12B`, `gemma-4-26B-A4B` (M4 Max default)
- **GLM-4.6V Flash** (Z.ai)
- **Qwen 3-VL** — `qwen3-vl-4b`, `qwen3-vl-8b` (workhorse), `qwen3-vl-30b-a3b`
- **Qwen 3.6 27B MTP** (text-only)
- **DeepSeek-OCR-2**, **olmOCR-2-7B-1025**, **Granite-Docling 258M**
- **UCCIX** — `uccix-mistral-24b`, `uccix-llama-3.1-8b`, `uccix-llama2-13b` (DEPRECATED, `available=False`)
- **Dots-OCR**, **PaddleOCR-VL 1.6**
- **Molmo2 4B + 8B**
- **InternVL3-8B**, **Llama 3.2 Vision 11B** (legacy), **Gemma 3 4B** (legacy)
- **v5 BIEP v2** — `unstract-api`, `docling-serve`

> **Note:** The 4 historical HTR/Dúchas specialists (Pylaia, TrOCR,
> OlmOCR, VLM) referenced by earlier versions of this AGENTS.md have
> been retired from the canonical `CLASSICAL_OCR` registry per the
> `2026-07-17-fix-phantom-agents-and-ocr-backend-list-v1` change. The
> Pylaia Dúchas HTR specialist is preserved for the Dúchas corpus and
> remains available via `tuatha_root_agent`. The canonical 5 OCR
> Docker stacks on `bunchloch` are: `docling-serve`, `paddleocr`,
> `dots-ocr`, `unstract`, `olmocr` (under `bonneagar/stacks/`).

## The 4 ensemble patterns

| Pattern | Description | Used when |
|:--|:--|:--|
| **Single-best** | Pick the highest-confidence backend | Production: when 1 backend is the obvious winner |
| **Voting** | All backends vote; majority wins | Production: when backends are roughly equivalent |
| **Confidence-weighted** | Each backend's vote is weighted by confidence | Production: when backends have different reliability profiles |
| **Cascade** | Backend A first; fall through to B/C/D if confidence is low | Production: when one backend is fast + cheap + usually sufficient |

The canonical ensemble dispatcher is in
`agents/meaisinfhoghlaim/ocr/ensemble/` (the 4-path BIEP v2
ensemble runs ``baml + unstract + qwen3_vl + gemma4`` via
``asyncio.gather`` with RAGAS voting on the per-path outputs).

## The 4 alignment methods (in `aligner.py`)

The canonical `meaisinfhoghlaim/alignment/aligner.py` exposes
`IrishEnglishAligner` with 4 alignment methods (not the 3
"primitives" — those names were retired):

| Method | Description |
|:--|:--|
| **VecAlign** | Vector-based sentence alignment (multilingual embedding cosine) |
| **HunAlign** | The HunAlign statistical aligner (Gale-Church variant) |
| **GaoisAlign** | The Gaois.ie terminology-aware aligner |
| **Hybrid** | Combine VecAlign + GaoisAlign (fallback to HunAlign for low-confidence pairs) |

Plus two specialised aligners in `meaisinfhoghlaim/alignment/`:

| Module | Purpose |
|:--|:--|
| `colpali_aligner.py` | `ColPaliAligner` for manuscript bbox extraction (SigLIP 32×32 patch embeddings + Otsu thresholding) |
| `character_interpolator.py` | word→char timestamp interpolation for ASR alignment |

## The educational agents (3 agents + 1 manifest)

| Agent | Framework | Purpose |
|:--|:--|:--|
| `academic_history_agent` | ADK | The cross-archive academic history (research paper retrieval + citation extraction) |
| `academic_history_manifest.py` | (manifest) | The academic history manifest schema (Pydantic v2) — used by the agent to register its epistemic surface |
| `celtic_grammar_agent` | ADK | The Celtic grammar specialist (Irish + Welsh + Scottish Gaelic + Breton + Cornish + Manx) |
| `celtic_morphology_agent` | ADK | The Celtic morphology specialist (verb conjugation + noun declension + adjective agreement) |

> **Note:** The previous version of this AGENTS.md listed "3
> educational agents" — the canonical count is **3 agents + 1
> manifest** (4 files total under
> `agents/meaisinfhoghlaim/educational/`).

## Quick routing — "I want to add X, where do I go?"

| If you want to... | Look at... |
|:--|:--|
| Add a new HTTP OCR backend | `meaisinfhoghlaim/backends/adapters.py` (the 4 HTTP adapters: PaddleOCR / Docling / Dots-OCR / Unstract) |
| Add a new VLM / ensemble path | `meaisinfhoghlaim/ocr/ensemble/ensembled_extractor.py` (the 6 paths: BAML stub + Unstract + qwen3-vl-8b + gemma-4 + 2 reserved) |
| Add a new model to the centralized registry | `meaisinfhoghlaim/models/model_registry.py` (the 52-entry `MODEL_REGISTRY` across 7 families) |
| Add a new alignment primitive | `agents/meaisinfhoghlaim/alignment/` |
| Modify an educational agent | `agents/meaisinfhoghlaim/educational/<slug>_agent.py` |
| Add OCR/HTR Dagster assets | `orchestration/defs/5_agent_ops/ocr_assets/` |
| Deploy the OCR/HTR pipeline | `meaisinfhoghlaim/cli.py` |

## Cross-references

- [`agents/AGENTS.md`](../AGENTS.md) — the quadrant overview
- [`agents/api/AGENTS.md`](../api/AGENTS.md) — the Hono API layer
- [`agents/tools/AGENTS.md`](../tools/AGENTS.md) — the tools layer
- [`meaisinfhoghlaim/AGENTS.md`](../../meaisinfhoghlaim/AGENTS.md) — the top-level OCR/HTR package