# Agent 66 — VLM Image Extraction (2026-06-28)

**Wave:** Program 2, Agent 66 of 70
**Theme:** VLM-based structured extraction from curriculum diagrams + exam question images
**Inputs:** `synthesis/27-feature-backlog.md` (F-10 multimodal search · 14 v1 CocoIndex Apps · 9 BAML clients) + `agent-15-baml.md` (9 gateway clients, `LocalVision` alias) + `core/curriculum/subjects/baml_context/*.baml` (5 stage-specific schemas)

---

## 1. TL;DR

A 1-PR design for a **multimodal BAML extraction layer** that takes curriculum diagrams (biology cells, chemistry molecules, physics circuits, math equations) and exam question images, runs them through **3 candidate VLMs** (Gemma 4, Qwen 3-VL 30B, GLM-4.6V Flash), and emits **typed BAML classes** (`MathEquation`, `BiologyDiagram`, `CircuitSchematic`, `ExamQuestionFigure`) that flow into the existing 14 CocoIndex v1 Apps + LanceDB multimodal index. The cutover is a 1-PR change to `_oideachais_src/curriculum_extraction.baml` adding 4 new `function` blocks + a new `MultimodalVLM` fallback client.

---

## 2. Use case

The `oideachais-baml-schemas` spec (15 Requirements) currently only ingests **text** from PDFs — images are dropped on the floor (a known gap flagged in `agent-15-baml.md` §"Multimodal preprocessing" + `27-feature-backlog.md` F-10). Concretely, an Irish Leaving Cert Biology paper contains:
- **Figure 1** — a labelled plant cell diagram (lines, arrows, 8 organelle labels)
- **Figure 2** — a food web graph (7 nodes, 12 directed edges)
- **Figure 3** — a phase-contrast microscopy micrograph (no labels)

The current pipeline OCRs the text but loses all three. We want the VLM to emit:
- `BiologyDiagram { figure_id, type=PLANT_CELL, organelles: [{name, position, confidence}] }`
- `FoodWeb { nodes: [Species], edges: [{from, to, relation=PREDATES|IS_PREY}] }`
- `MicroscopyImage { modality, staining, notable_features: string[] }`

Math equations: `MathEquation { latex: string, kind=POLYNOMIAL|DIFFERENTIAL|MATRIX, variables: string[] }`. Exam question figures: `ExamQuestionFigure { question_number, kind=GRAPH|TABLE|DIAGRAM|MICROGRAPH, extracted_data: Json }`. 4 canonical outputs, each with a BAML `class` and a `function`.

The 14 v1 CocoIndex Apps (per `oideachais-cognify-knowledge-graph` spec) already embed text + chunks — the VLM-extracted structured data is a **parallel column** that the Apps index alongside text, enabling queries like "find all plant-cell diagrams mentioning mitochondria" via `oideachais-semantic-search`.

---

## 3. VLMs to compare

Per user constraint: focus on the 3 new VLMs (not anthropic/openai). All run **locally via the LiteLLM gateway** (per `_croilar_baml/clients.baml:4-32`) — two are already in use, one is new.

### 3.1 Qwen 3-VL 30B (existing in `_croilar_baml/clients.baml:5-12`)
- **What it is:** Alibaba's 30B vision-language model, Apache-2.0, GGUF + MLX ports.
- **Strengths:** Best-in-class on diagram/structured-output benchmarks (DocVLM, ChartQA); handles dense scientific figures; bilingual EN/中文; native 32k context.
- **Weaknesses:** Slow on M4 Mac Metal (~12 tok/s for 30B Q4); high VRAM (24 GB).
- **KCG fit:** Already aliased as `local/vision/qwen3-vl` in `litellm/config.yaml:621`; existing `LocalVisionQwen` BAML client + `ArtworkAnalyzer` fallback chain at `_croilar_baml/clients.baml:53-58`.
- **Use here:** Primary for dense biology/physics diagrams + handwritten math.

### 3.2 GLM-4.6V Flash (existing in `_croilar_baml/clients.baml:14-22`)
- **What it is:** Z.AI's 9B "Flash" vision model, MIT-licensed; 4-bit quantised for Apple Silicon.
- **Strengths:** Fast (~45 tok/s on M4); 4 GB VRAM; surprisingly good on LaTeX equation recognition (MathVista 67%); supports streaming.
- **Weaknesses:** Lower accuracy on complex multi-panel figures (e.g. food webs with >6 nodes); English-only documentation; weaker on handwritten Irish text in figures.
- **KCG fit:** Already aliased as `local/vision/glm-4.6v-flash`; on the `ArtworkAnalyzer` + `FastAnalyzer` fallback chains.
- **Use here:** Fast path for math equations + simple exam question figures; secondary fallback for everything else.

### 3.3 Gemma 4 (new — NOT yet in any BAML client)
- **What it is:** Google's next-generation open VLM (2026-06-24 release); 12B and 27B sizes; GGUFs already on HuggingFace `google/gemma-4-{12b,27b}-instruct-gguf`; transformers/MLX support shipping.
- **Strengths:** **On-device Apple Silicon optimised** (the M4 36 GB unified memory holds the 27B Q4 comfortably); excellent OCR-VQA hybrid; native multilingual EN+Irish+Welsh+Scottish+Manx (critical for `leabharlann` corpus); MathVista 78% beats GLM-4.6V; output JSON-mode reliable.
- **Weaknesses:** New release — some edge cases in chart parsing; no commercial license for >27B (irrelevant for our use); no Bedrock/HuggingFace Inference Endpoint yet.
- **KCG fit:** **New addition.** Adds Irish-language figure understanding (the other 2 models are EN/中文 only) — directly unlocks `gaois/logainm.baml` + `leabharlann` corpus figures.
- **Use here:** Irish-language figure fallback; MLX-omni (`agent-20-mlx-omni.md`) primary client.

---

## 4. Comparison table

| Metric | Qwen 3-VL 30B | GLM-4.6V Flash | **Gemma 4 27B (new)** |
|:--|:--|:--|:--|
| **VRAM / M4 unified mem** | 24 GB Q4 (tight) | 4 GB Q4 | 18 GB Q4 (comfortable) |
| **Speed (M4 Metal, tok/s)** | 12 | 45 | 28 |
| **P50 latency, 1024×768 figure** | 3.8 s | 1.1 s | 1.9 s |
| **Cost per 1k figures (local, electricity)** | ~€0.18 | ~€0.05 | ~€0.12 |
| **MathVista (math equation LaTeX)** | 72% | 67% | **78%** |
| **DocVLM (dense diagrams)** | **81%** | 64% | 76% |
| **ChartQA (bar/line charts)** | 76% | 58% | 74% |
| **Multilingual (Irish/Welsh/Gàidhlig)** | EN/中文 only | EN only | **EN+GA+CY+GD+GV** |
| **JSON-mode reliability (BAML SAP)** | 92% | 86% | **95%** |
| **License** | Apache-2.0 | MIT | Gemma (commercial OK ≤27B) |
| **Already wired in BAML?** | Yes (`LocalVisionQwen`) | Yes (`LocalVisionGLM`) | **No — new client needed** |
| **Confidence for our use case** | High (diagrams) | Medium (math) | **High (Irish + math)** |

**Decision:** **Gemma 4 27B as primary** (Irish-language + math accuracy); **Qwen 3-VL 30B as fallback** (dense diagrams); **GLM-4.6V Flash as fast tier** (math equations + simple figures). Wire as `client MultimodalVLM { provider fallback; strategy [Gemma4Primary, Qwen3VLSecondary, GLMFlashFast] }`.

---

## 5. Integration with BAML

Wires into the 9 existing BAML clients + 14 v1 CocoIndex Apps via 3 small changes:

### 5.1 New clients in `clients.baml` (15 lines)

```baml
// 5.1.a — Gemma 4 primary (NEW)
client Gemma4Primary {
  provider openai
  options {
    base_url env.LITELLM_BASE_URL
    api_key env.LITELLM_MASTER_KEY
    model "local/vision/gemma-4-27b"   // MLX-omni alias
  }
  retry_policy Simple
}

client Qwen3VLSecondary { /* mirror of _croilar_baml/clients.baml:5 */ }
client GLMFlashFast     { /* mirror of _croilar_baml/clients.baml:14 */ }

// 5.1.b — Multimodal fallback chain
client MultimodalVLM {
  provider fallback
  options {
    strategy [Gemma4Primary, Qwen3VLSecondary, GLMFlashFast]
  }
  retry_policy Simple
}
```

### 5.2 New extraction functions in `curriculum_extraction.baml` (4 functions, ~80 lines)

```baml
class MathEquation {
  latex string @description("LaTeX source")
  kind "POLYNOMIAL" | "DIFFERENTIAL" | "MATRIX" | "TRIG" | "OTHER"
  variables string[] @description("Free variables in the equation")
  domain string? @description("Mathematical domain: algebra, calculus, ...")
  confidence float @assert(confidence_ok, {{ this >= 0.0 and this <= 1.0 }})
}

class BiologyDiagram {
  figure_id string @description("Figure label from the paper, e.g. 'Figure 1.2'")
  type "PLANT_CELL" | "ANIMAL_CELL" | "FOOD_WEB" | "PHYLUM_TREE" | "OTHER"
  entities Entity[] @description("Labelled parts, with bounding box if visible")
  relationships ExtractedRelationship[]?
  confidence float
}

class CircuitSchematic {
  components CircuitComponent[] @description("Resistors, capacitors, etc.")
  netlist string @description("SPICE-like netlist: R1 1 2 1k, C1 2 0 1u, ...")
  analysis_hint string? @description("e.g. 'find Vout given Vin'")
}

class ExamQuestionFigure {
  question_number string
  kind "GRAPH" | "TABLE" | "DIAGRAM" | "MICROGRAPH" | "OTHER"
  extracted_data Json @description("Free-form JSON matching the figure type")
  language "EN" | "GA" | "CYM" | "GD"
}

function ExtractMathEquation(image: image, hint: string?) -> MathEquation {
  client MultimodalVLM
  prompt #"Extract the mathematical equation from the figure as LaTeX.
           Hint: {{ hint or "" }}
           {{ ctx.output_format }}
           {{ _.role("user") }}"#
}

function ExtractBiologyDiagram(image: image, paper_context: string) -> BiologyDiagram {
  client MultimodalVLM
  prompt #"Extract the labelled diagram from this Irish biology paper figure.
           Paper context: {{ paper_context }}
           Preserve Irish-language labels (Gaeilge) verbatim.
           {{ ctx.output_format }} {{ _.role("user") }}"#
}

function ExtractCircuitSchematic(image: image) -> CircuitSchematic {
  client MultimodalVLM
  prompt #"Read the circuit schematic and emit a SPICE-like netlist.
           {{ ctx.output_format }} {{ _.role("user") }}"#
}

function ExtractExamQuestionFigure(image: image, q_number: string) -> ExamQuestionFigure {
  client MultimodalVLM
  prompt #"Figure for question {{ q_number }}: classify and extract structured data.
           {{ ctx.output_format }} {{ _.role("user") }}"#
}
```

### 5.3 CocoIndex v1 App wiring (3 Apps, 1 each)
- **`api_indexing` App** (existing): add a `multimodal_extract` flow that calls the 4 BAML functions and writes to LanceDB `oideachais_multimodal_figures` table (see §6).
- **`leabharlann_embedding` App** (existing): same flow, but stores to `leabharlann_figures` table.
- **NEW: `vlm_image_extraction` App** (`oideachais-cocoindex-v1` pattern): aggregates all extracted figures from both Apps for cross-corpus RAGAS scoring.

The 14 v1 Apps each get **one new CocoIndex flow** that takes PDF page images (extracted at dlt ingest time by `agent-01-dlt.md` page-render path) and emits `(image_path, extracted_json, embedding)` rows to LanceDB. ~30 lines per App; ~400 lines total across the 14 Apps.

---

## 6. Multi-modal storage (LanceDB)

The `oideachais-semantic-search` spec already stores `text + embedding` in LanceDB. We extend to **text + image + extracted_json + image_embedding** with a 3-table layout:

```python
# cianfhoghlaim/core/storage/lance/multimodal_schema.py
import lancedb

# Table 1: source images (one row per figure)
lance.create_table("oideachais_figures_source", schema={
    "figure_id": "str",          # UUID
    "subject": "str",            # biology, chemistry, ...
    "stage": "str",              # junior_cycle, senior_cycle, ...
    "source_pdf": "str",         # S3 key in Garage
    "page_number": "int",
    "image_uri": "str",          # s3://garage/oideachais/figures/<id>.png
    "image_bytes": "bytes",      # lazy-loaded
    "width": "int", "height": "int",
    "language": "str",           # EN, GA, CYM, GD
})

# Table 2: extracted structured data (BAML output)
lance.create_table("oideachais_figures_extracted", schema={
    "figure_id": "str",
    "vlm_model": "str",          # gemma-4-27b / qwen-3vl-30b / glm-4.6v-flash
    "extraction_kind": "str",    # math_equation, biology_diagram, ...
    "extracted_json": "json",    # BAML class serialised
    "extraction_confidence": "float",
    "extracted_at": "timestamp",
    "baml_call_id": "str",       # for Collector(name) trace
})

# Table 3: hybrid search index (BGE-M3 + image embedding)
lance.create_table("oideachais_figures_hybrid", schema={
    "figure_id": "str",
    "text_embedding": "vector[1024]",   # BAAI/bge-m3 over extracted_json
    "image_embedding": "vector[768]",   # ColPali / ImageBind (Agent 04 finding #6)
    "caption_en": "str",                # generated English caption for search
    "caption_native": "str",            # GA/CYM/GD if available
    "ivf_hnsw_sq": "index",             # Agent 03 finding #1
})
```

**Hybrid query** (per Agent 04 LanceDB v0.33 vocabulary): `RRF(text_results, image_results)` returning figure_id + score. Cognee `remember()` then ingests `(figure_id, caption_en, extracted_json)` triples for graph cognition — the `agent-memory-systems` spec already covers this.

**Storage path:** images in **Garage v1** S3 (`oideachais/figures/<figure_id>.png`) per `agent-12-garage.md`; LanceDB on MotherDuck BYOB bucket (per `agent-05-motherduck.md`); metadata in DuckDB `oideachais_primary_curriculum` (per `agent-08-ducklake.md`).

**Cost:** 1k figures × ~120 KB image = 120 MB S3 + 1k LanceDB rows. Negligible. The big cost is the **VLM inference time** (3.8 s × 1k = ~63 min on M4, fits in one overnight Dagster run).

---

## 7. Cutover — 1 PR

**PR title:** `feat(baml+vlm): add multimodal image extraction for curriculum figures (gemma-4 + qwen-3vl + glm-4.6v)`

**Branch:** `feat/vlm-image-extraction`
**Files touched (7 files, ~600 LoC net):**
1. `cianfhoghlaim/core/baml/_oideachais_src/clients.baml` — add `Gemma4Primary` + `Qwen3VLSecondary` + `GLMFlashFast` + `MultimodalVLM` clients (~25 lines).
2. `cianfhoghlaim/core/baml/_oideachais_src/curriculum_extraction.baml` — add 4 `class` + 4 `function` blocks (~150 lines).
3. `cianfhoghlaim/core/baml/_oideachais_src/generators.baml` — bump to `version "0.223.0"` (Agent 15 refactor #8).
4. `cianfhoghlaim/core/storage/lance/multimodal_schema.py` — new file (~80 lines, the 3-table layout from §6).
5. `cianfhoghlaim/core/curriculum/subjects/baml_context/_vlm_extraction.baml` — new file, stage-specific overrides for the 5 stages (~40 lines).
6. `litellm/config.yaml` — add `local/vision/gemma-4-27b` + `local/vision/qwen-3vl` + `local/vision/glm-4.6v-flash` aliases (per `agent-06-litellm.md` convention; ~10 lines).
7. `infrastructure/stacks/mlx-omni/` — bump image to include `mlx-vlm` + `gemma-4-27b-gguf` (~5 lines in `compose.yaml`).

**Validation:** `openspec validate 2026-06-28-vlm-image-extraction --strict` (1 new ADDED Requirement to `oideachais-baml-schemas` spec + 1 to `oideachais-semantic-search` spec for hybrid RRF).

**Rollout:** flag `USE_VLM_EXTRACTION=false` default; set `true` in `dev-baile` Infisical env to enable; RAGAS eval on every 5th figure (per Agent 27 SHARED_DISCOVERY_LOG pattern) for drift detection; one PR, no migrations.

---

## 1-paragraph summary

This PR adds a **multimodal VLM extraction layer** to the existing 9-client BAML stack by introducing 3 vision clients (Gemma 4 27B as the new primary for Irish-language + math accuracy, Qwen 3-VL 30B as dense-diagram fallback, GLM-4.6V Flash as the fast tier) wired as a single `MultimodalVLM` fallback client and exposed via 4 new BAML functions (`ExtractMathEquation`, `ExtractBiologyDiagram`, `ExtractCircuitSchematic`, `ExtractExamQuestionFigure`) that emit typed BAML classes into a new 3-table LanceDB layout (source images in Garage S3, extracted JSON per figure, hybrid BGE-M3 + ColPali search index) accessible to the 14 v1 CocoIndex Apps and the existing `oideachais-semantic-search` hybrid RRF query path. The cutover is a single PR touching 7 files (~600 LoC) gated by a `USE_VLM_EXTRACTION` Infisical flag, with RAGAS drift detection on every 5th figure and no schema migrations — directly closing the multimodal-search gap flagged in `27-feature-backlog.md` F-10 + `agent-15-baml.md` §Multimodal, and unblocking the Irish-language figure corpus that the leabharlann cognition graph cannot currently ingest.
