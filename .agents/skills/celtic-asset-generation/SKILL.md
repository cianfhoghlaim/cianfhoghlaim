---
name: celtic-asset-generation
description: KCG's canonical 5-stage pipeline for generating, extracting, and cognifying Celtic curriculum and cultural-heritage assets — BAML structured extraction → CocoIndex v1 embedding → Cognee/FalkorDB cognify → Graphiti temporal memory → LanceDB vector search. Anchored in the Tripartite Data Landscape (NCCA pedagogical intent + SEC evidentiary truth + Dept of Education temporal governance) and the bilingual en/ga strategy. Use when extracting an Irish curriculum PDF, wiring a new leabharlann source, building a knowledge graph for the Leaving Cert, scraping Dúchas / examinations.ie, or asking "how does a Celtic PDF become a queryable, time-aware, vector-indexed dataset?".
---

# Celtic Asset Generation

## When to use this skill

Use when you need to:

- "How does a Celtic PDF become a queryable dataset?"
- "Wire a new NCCA / SEC / Dúchas source into the KCG pipeline"
- "Extract structured curriculum data with BAML"
- "Build a knowledge graph for Leaving Cert content"
- "Add a syllabus-versioned, bi-temporal layer (Graphiti)"
- "Add a Celtic-language embedding index (BGE-M3)"
- "Generate a Leaving Cert study asset (question, marking, audio)"
- "Migrate from a one-off LLM script to the canonical 5-stage flow"

## Overview

The Celtic asset generation pipeline is the **Celtic-data counterpart of the leabharlann 5-stage flow**: the same BAML → CocoIndex → Cognee shape, re-anchored onto the **Tripartite Data Landscape** (NCCA pedagogical intent, SEC evidentiary truth, Dept of Education temporal governance) and the bilingual **en/ga** strategy.

The 5 stages, in order, are:

1. **BAML extraction** — structured JSON from a PDF / scrape /
   audio, typed against `baml_src/curriculum_extraction.baml` +
   the language-specific schemas (`celtic_linguistics.baml`).
2. **CocoIndex v1 embedding** — incremental BGE-M3 (1024-d,
   multilingual, 100+ langs incl. all 6 Celtic) via the v1 App
   pattern (`localfs.walk_dir` + `RecursiveSplitter` + 100-batch
   minimum + `IdGenerator`).
3. **Cognee cognify** — knowledge graph build, persisted to
   **FalkorDB** (vector + Cypher, hot path) and **Memgraph**
   (canonical graph, cold path).
4. **Graphiti temporal memory** — bi-temporal layer for
   syllabus versions, circular amendments, exam paper
   obsolescence, and student mastery decay.
5. **LanceDB vector search** — HNSW + FTS index for the final
   RAG retrieval, served at `lance-api.cianfhoghlaim.ie:8181`.

The same 5 stages appear (under different names) in 3 other
KCG skills: `kcg-leabharlann-pipeline` (leabharlann PDFs),
`oideachas-pipeline` (the leabharlann author-archive variant),
and `kcg-ml-models` (the model-fallback layer for the BAML
clients).

## The Tripartite Data Landscape

The Celtic curriculum has 3 orthogonal source authorities,
each with a different role in the model:

| Source | Domain | Role in the model | Examples |
|:--|:--|:--|:--|
| **NCCA** (curriculumonline.ie) | Pedagogical Intent | "What should the student learn?" — specifications, learning outcomes, strand / topic trees | Junior Cycle Maths spec, Senior Cycle Irish syllabus |
| **SEC** (examinations.ie) | Evidentiary Truth | "What was actually assessed?" — exam papers, marking schemes, grade boundaries | LC 2024 Higher Level Maths Paper 2 + marking scheme |
| **Dept of Education** | Temporal Governance | "What changed, and when?" — circulars, policy amendments, statutory instruments | Circular 0023/2024 (Senior Cycle reform), circular 0003/2018 |

The BAML extraction stage treats each source authority
differently:

- NCCA → `ExtractCurriculumSpec` → `Strand` / `Topic` /
  `LearningOutcome` graph nodes.
- SEC → `ExtractMarkingScheme` → `AssessmentItem` +
  `MarkingPoint` + 10A–10D scale nodes.
- Dept of Ed → `ExtractCircularMeta` → `PolicyDirective` with
  `valid_at` / `invalid_at` bi-temporal windows (drives
  Graphiti).

The graph edge types are domain-specific. See
`irish-edtech/SKILL.md` for the per-subject ontology
(derivation trees for Maths, taxonomy + system for Sciences,
causal + spatial for Humanities, thematic web for Languages,
transaction graph for Business).

## The bilingual strategy (en / ga)

Every Celtic asset is a **bilingual pair**, not two separate
records. The canonical schema is:

```json
{
  "concept_id": "PYTHAG_THEOREM",
  "name_en": "Theorem of Pythagoras",
  "name_ga": "Teoirim Pythagoras",
  "definition_en": "The square of the hypotenuse ...",
  "definition_ga": "An chearnog ar an taobhagan ..."
}
```

This dual-field pattern is enforced at the BAML level (see
`baml_src/curriculum_extraction.baml` + `baml_src/celtic_linguistics.baml`).
The graph nodes carry both `name_en` and `name_ga`; the
embeddings are produced by **BGE-M3** (multilingual, 1024-d)
so a query in either language retrieves the same node.

Dialect handling (Ulster / Connacht / Munster / Standard) is
a separate axis tracked in the `Form` node (see the
`irish-edtech` skill's dialect cypher example).

## The 5-stage flow (canonical)

```
┌──────────────────────────────────────────────────────────────┐
│              CELTIC ASSET PIPELINE (5 STAGES)                │
└──────────────────────────────────────────────────────────────┘

Source (NCCA / SEC / Dept of Ed / Dúchas / leabharlann)
    │
    ▼
[STAGE 1: BAML structured extraction]
curriculum_extraction.baml + celtic_linguistics.baml
→ ExtractEn / ExtractEnStrong via LiteLLM
    │
    ▼
[STAGE 2: CocoIndex v1 incremental embedding]
BGE-M3 + RecursiveSplitter(chunk_size=2000, chunk_overlap=500)
+ 100-batch minimum + IdGenerator + memoisation
    │
    ▼
[STAGE 3: Cognee cognify]
FalkorDB (hot) + Memgraph (cold) + 8 canonical edge types
    │
    ▼
[STAGE 4: Graphiti temporal memory]
bi-temporal windows for syllabus version + circular amendments
    │
    ▼
[STAGE 5: LanceDB vector search]
HNSW + FTS index, served at lance-api.cianfhoghlaim.ie:8181
    │
    ▼
Query (TanStack Start front-end at oideachais.cianfhoghlaim.ie)
```

The 5 stages map to 3 Dagster asset groups (in
`oideachais/dagster_defs/`):

| Stage | Dagster asset group | Example assets |
|:--|:--|:--|
| 1 | `baml_extraction_assets` | `ncca_syllabus_extracted`, `sec_marking_extracted`, `circular_meta_extracted` |
| 2 | `cocoindex_embedding_assets` | `ncca_cocoindex_update`, `sec_cocoindex_update` |
| 3, 4, 5 | `cognify_graph_assets` | `cognee_cognify_ncca`, `graphiti_circular_temporal`, `lancedb_index_publish` |

The exact asset names live in
`oideachais/dagster_defs/assets/`. The grouping mirrors the
leabharlann pipeline (7 leabharlann + 7 author-archive + 18
ireland + 16 UK + 8 crown_dependencies assets = 56 total
across 7 groups).

## Model selection (per stage)

| Stage | Primary model | Fallback | Notes |
|:--|:--|:--|:--|
| 1 (BAML) | `litellm/gemini-2.5-flash` | `litellm/anthropic/claude-sonnet-4` via `ExtractEnStrong` | BAML `client` blocks chain the fallback per-call |
| 2 (embedding) | `BAAI/bge-m3` | `intfloat/multilingual-e5-large` | 1024-d, multilingual, M4 `mps` is fine |
| 3 (Cognee) | `gpt-4o-mini` (entity extraction) | `claude-sonnet-4` (relationship extraction) | Cognee is the orchestrator |
| 4 (Graphiti) | `gpt-4o-mini` (edge + window extraction) | n/a | Graphiti handles the bi-temporal model internally |
| 5 (LanceDB) | n/a (vector index) | n/a | IVF_HNSW + FTS, served via Lance Namespace REST |

The KCG production rule: **never let a single model failure
cascade**. Every BAML `client` block chains 2-3 models; the
fallback is per-call, not per-session.

## Live URLs (post-deploy)

| Service | URL |
|:--|:--|
| Dagster UI | `https://dagster.cianfhoghlaim.ie` |
| BAML playground | `https://baml.cianfhoghlaim.ie` |
| LanceDB viewer | `https://lance.cianfhoghlaim.ie:8081` |
| Cognee | `https://cognee.cianfhoghlaim.ie:8000` |
| FalkorDB | `https://falkordb.cianfhoghlaim.ie:6379` |
| Memgraph | `https://memgraph.cianfhoghlaim.ie:7687` |
| MotherDuck | `md:oideachais` (read-only) |
| TanStack Start (oideachais/web) | `https://oideachais.cianfhoghlaim.ie` |

## References (in this skill)

- `references/baml-irish-education-kg.md` — the canonical BAML
  schema for the NCCA / SEC / Dept-of-Ed tripartite KG.
- `references/baml-adaptive-syllabus.md` — dynamic BAML
  TypeBuilder per-syllabus, Agno + Restate workflow.
- `references/baml-fibo-chemistry.md` — BAML chem syllabus →
  Fibo structured JSON prompts.
- `references/cognee-cocoindex-graphiti-stack.md` — FalkorDB
  vs Memgraph dual-engine architecture.
- `references/asset-management-pixelart.md` — LC subject asset
  strategy + UploadThing / Cloudinary.
- `references/chemistry-react-assets.md` — React three-fiber
  chemistry asset pipeline for Irish LC.
- `references/invokeai-mlx-asset-workflow.md` — agentic
  Bria → InvokeAI + MLX workflow for TanStack Start.
- `references/gradio-copilotkit-fibo.md` — Gradio MCP server +
  CopilotKit AG-UI + Bria Fibo.
- `references/agent-knowledge-base.md` — self-healing ontology
  + R2 + Cloudflare + Cognee / Graphiti agent KB.
- `references/leaving-cert-tanstack-app.md` — LC prescribed
  material polymorphic TanStack schema.
- `references/multimodal-video-kg.md` — yt-dlp + WhisperX +
  Qwen3-Omni video → KG pipeline.
- `references/diffusion-irish-translation.md` — NeoDiff + Block
  Diffusion for low-resource Irish.
- `references/neuro-symbolic-gaeilge-engine.md` — Agno +
  GLM-4.6v + Cognee + BAML Irish HTR / KG blueprint.
- `references/neuro-symbolic-translation-engine.md` — InkSpire
  Masked-CFM neuro-symbolic Gaeilge engine.
- `references/inkspire-gaelic-handwriting-gen.md` — InkSpire
  diffusion + MVTM Gaelic handwriting synthesis.
- `references/olake-lakekeeper-risingwave.md` — second-gen
  open data lakehouse (canonical).
- `references/tanstack-db-integration.md` — differential
  dataflow client-side DB.
- `references/dlt-crawl4ai-lancedb-crypto.md` — crypto
  sentiment fear-and-greed + dlt + crawl4ai + LanceDB.
- `references/celtic-bench-educational-corpora.md` —
  pan-Celtic bilingual corpus via NCCA / examinations.ie / SQA.
- `references/celtic-linguistic-lakehouse.md` — Celtic-Bench +
  lakehouse (deduped teanga copy).
- `references/federated-linguistic-data-lakehouse.md` —
  non-Ireland Celtic corpora architecture.
- `references/british-isles-demographic-atlas.md` — DuckDB +
  Convex + TanStack Hilbert-curved demographic viz.
- `references/british-isles-edu-map.md` — same content as the
  demographic atlas (dedup pair; will be removed in Phase 4).
- `references/british-isles-parallel-edu.md` — UK + ROI
  parallel education data coverage map.
- `references/gaeilge-gaeltacht-poc-map.md` — Gaeltacht + LPA
  Tailte Éireann census data PoC.
- `references/gaois-irish-bilingual-dataset.md` — 1173-line
  DCU Gaois dataset acquisition blueprint.
- `references/hidden-heritages-duckdb.md` — DCU Gaois spatial
  stack + DuckDB analytics.
- `references/ibis-duckdb-education-geo.md` — cloud-native
  geospatial EdTech stack.
- `references/cloud-native-geospatial-webgpu.md` — cloud-native
  OLAP + WebGPU meteorological viz (primary).
- `references/cloud-native-geospatial-webgpu-2.md` — alt
  (teanga copy); same content.
- `references/skyvern-celtic-scrape.md` — Skyvern + LLM agent
  for NCCA / examinations / Dúchas scraping.
- `papers/bolmo.pdf` — Bolmo VLM tech report.
- `papers/molmo2-tech-report.pdf` — Molmo2 VLM tech report.
- `references/clippings/dr-lib-resources.md` — DR-LIB article.
- `references/clippings/dlt-marimo-ibis.md` — dlt + marimo +
  ibis.
- `references/clippings/planetscale-motherduck.md` —
  PlanetScale + MotherDuck.
- `references/clippings/planetscale-motherduck-quickstart.md`
  — PlanetScale + MotherDuck quickstart.
- `references/clippings/lance-namespace-ray.md` — Lance + Ray.
- `references/clippings/iceberg-browser-duckdb.md` — Iceberg
  in browser.
- `references/clippings/opengeos-geoai.md` — GeoAI Python pkg.
- `references/clippings/google-adk-litellm.md` — Google ADK +
  LiteLLM.

## Cross-references

- `.agents/skills/kcg-leabharlann-pipeline/SKILL.md` — the
  leabharlann variant of this 5-stage flow (the source of the
  pattern).
- `.agents/skills/oideachas-pipeline/SKILL.md` — the
  oideachais quadrant pipeline + leabharlann author-archive
  variant.
- `.agents/skills/celtic-language-ai/SKILL.md` — the 6 Celtic
  languages + curated model catalog (the BAML target).
- `.agents/skills/irish-edtech/SKILL.md` — the Irish-only
  comprehensive reference + the per-subject ontology
  (derivation tree, taxonomy, causal, thematic web, transaction
  graph).
- `.agents/skills/cross-domain-registry/SKILL.md` — the 8
  nations + fiscal context for the British Isles + Ireland
  Celtic data.
- `.agents/skills/baml/SKILL.md` — the BAML extraction
  language + `ExtractEn` / `ExtractEnStrong` clients.
- `.agents/skills/cocoindex/SKILL.md` — the CocoIndex v1 flow
  patterns.
- `.agents/skills/cognee/SKILL.md` — Cognee cognify + 8
  canonical relationship types.
- `.agents/skills/graphiti/SKILL.md` — bi-temporal Graphiti
  memory.
- `.agents/skills/lancedb/SKILL.md` — LanceDB HNSW + FTS
  hybrid search.
- `.agents/skills/oideachais-storage/SKILL.md` — the DuckLake
  + MotherDuck + Iceberg storage mental model.
- `.agents/skills/kcg-ml-models/SKILL.md` — the 70+ model
  fallback chain (the inference backends behind BAML).
- `.agents/skills/embedding-pipeline/SKILL.md` — the BGE-M3
  + CocoIndex embedding rules (100-batch minimum).
- `.agents/skills/asr/SKILL.md` — the ASR stack (Irish /
  Scottish Gaelic / Welsh).
- `.agents/skills/tts/SKILL.md` — the TTS stack
  (Chatterbox / MMS-TTS / Piper).
- `oideachais/STATUS.md` — pipeline state (single source of
  truth).
- `oideachais/REFACTORING.md` — refactor backlog.

## Frontend idea catalog (design mining) (round-9 deep dive)

The `references/frontend-design-mining.md` reference
(457 lines) establishes the canonical pipeline for
cataloging UI/UX patterns from best-in-class Celtic and
educational products. It's the **input stage** to
designing the Tuatha MMO, `oideachais/web` curriculum
viewer, and the crypteolas dashboards.

### The 3-stage mining pipeline

```
┌──────────────────────────────────────────────────────────────┐
│  Stage 1: Browserbase                                         │
│  → serverless Chromium with stealth + rrweb DOM recording    │
│  → 150+ geolocations, residential proxies, CAPTCHA solving   │
│  → exports CDP screencasts for canvas-based maps / video     │
└─────────────┬────────────────────────────────────────────────┘
              │
              ▼
┌──────────────────────────────────────────────────────────────┐
│  Stage 2: Stagehand (V3)                                      │
│  → `act("Click 'minimize'")` semantic actions                 │
│  → `observe()` returns all possible actions + selectors      │
│  → `extract({ instruction, schema })` typed extraction        │
│  → `agent()` autonomous multi-step workflows                  │
│  → modes: dom (fast) | hybrid (mixed) | cua (slow)           │
└─────────────┬────────────────────────────────────────────────┘
              │
              ▼
┌──────────────────────────────────────────────────────────────┐
│  Stage 3: BAML                                                │
│  → typed schema for the extracted "frontend idea"            │
│  → Schema-Aligned Parsing handles malformed LLM JSON          │
│  → multimodal: pass video clips to VLM (Gemini 1.5 Pro)      │
│  → output: queryable catalog of design patterns              │
└──────────────────────────────────────────────────────────────┘
```

### The 3 target archetypes (the KCG use case)

1. **PostHog.com** — the **Application OS / Windowing**
   pattern. React Context holds window state (x, y, zIndex,
   minimized). Framer Motion drives the spring physics.
   Stagehand's `act` primitive is critical because the
   window controls have non-standard class names (CSS
   selector scraping breaks)
2. **HiddenHeritages.ai** — the **Narrative Geospatial
   Visualization** pattern. 5,500+ folktales, Leaflet
   clustering, canvas rendering for high-density
   points. **Canvas-based maps need visual analysis
   (VLM), not DOM scraping** — the rrweb record alone
   is insufficient
3. **Canúint.ie** — the **Audio-Visual Synchronization**
   pattern. Dialect map + audio samples + waveform
   visualization. Stagehand's `observe` enumerates
   the interactive regions (per-dialect play button)

### Self-healing catalog

Stagehand caches the successful action path for each
prompt; if the UI changes (e.g. PostHog updates Tailwind
classes), Stagehand **re-evaluates the page with the
LLM and heals the action**. This makes the catalog
robust over months of operation — the agent
continuously re-monitors the target sites and updates
the design catalog.

### KCG integration

The mined catalog drives the **Celtic design tokens** in
the `ui-components` skill (see `references/sruth-ui-inspiration.md`):

- MotherDuck → `crypteolas/` analytics, `aleyum/` monitoring
- PostHog (Lemon UI) → `oideachais/` dashboards
- Duolingo (streaks, snake path) → `tuath/` XP / quest progression
- Khan Academy (mastery levels) → `oideachais/` curriculum
- Hades (diegetic UI, chiaroscuro) → `tuath/` NPC dialogue
- Clair Obscur (material library) → `tuath/` menu systems
- World of Warcraft (semantic quest icons) → `tuath/` quest log

The mining pipeline is what **feeds the KCG Celtic design
language** — without it, every UI decision is rebuilt
from scratch. The catalog is the single source of truth
for "how do other products solve this UI problem?".

See `references/frontend-design-mining.md` for the full
457-line design-mining architecture.

## KCG AI/ML pipeline

The 393-line reference for the **8,000+ pages of bilingual
curriculum documents** processed by the Leaving Cert
tutoring system, covering document understanding, model
fine-tuning, and RAG.

**5-tool OCR/VLM comparison** (the document processing
backbone):

| Tool | LaTeX | Diagrams | Tables | Irish | Size |
|:--|:--|:--|:--|:--|:--|
| DeepSeek-OCR | Excellent (95%) | Good | Very Good | Unconfirmed | 3B |
| Qwen2.5-VL | Very Good | Excellent | Excellent | Likely (European) | 2B-235B |
| Qwen3-VL | Very Good | Excellent | Excellent | Native (119 langs) | Various |
| Granite-Docling | Good | Good | Excellent | Experimental | 258M |
| ColPali | N/A (retrieval) | Excellent | Good (visual) | Visual-based | 3B |

The **recommended pipeline** routes by content type:
text/equations → DeepSeek-OCR → LaTeX extraction;
diagrams → ColPali → visual embeddings; tables →
Granite-Docling → structured extraction; then BAML
structured extraction → metadata + JSON.

**DeepSeek-OCR capabilities** (the workhorse): 95%
formula recognition, vision-as-compression (600-1000+
text tokens from 64-100 vision tokens), ~2,500 tokens/sec
on A100 (~200,000 pages/day), MIT licensed (3B
parameters).

**ColPali** is the revolutionary visual retrieval
approach: multi-vector embeddings directly from page
images, PaliGemma-3B + ColBERT late-interaction, **0.81
nDCG@5** vs 0.66 for traditional pipelines, ideal for
geometry diagrams in exam papers.

**Fine-tuning strategy** uses **Qwen2.5-Math-7B-Instruct**
as the base (85.3% on MATH, 21/30 AIME, native Irish
support), trained via **Unsloth** (2x faster, 70% less
VRAM, 7-8B with QLoRA 4-bit = ~6-7GB VRAM, achievable on
RTX 3060+). Critical hyperparameters: LoRA rank 64-128
(math), 1e-5 to 5e-5 learning rate, 4096+ token sequences.

**Irish language integration** addresses the 20%
performance gap: **UCCIX-Llama2-13B-Instruct** (trained
on ~520M Irish tokens, +12% over LLaMA 2-70B on Irish
tasks), **UCCIX-Llama3.1-70B-Instruct** (Dec 2024, latest
architecture), **GaBERT** (DCU-NLP, +3.7 LAS on dependency
parsing from 7.9M Irish sentences). Recommended:
Qwen2.5-Math-7B as base + UCCIX tokenizer additions +
bilingual training examples + Irish-BLiMP validation
(1,020 minimal pairs) + UCCIX fallback for Irish-only.

**RAG architecture** uses **BGE-M3** as the primary
embedding (3 retrieval modes, 100+ languages, 8,192 token
context, outperforms BM25) with **LaBSE** as the Irish
supplement (109 languages including Irish). **Hybrid
retrieval** combines BGE-M3 dense + sparse, ColPali
visual page embeddings, and payload filtering (year,
topic, language). **ColQwen2.5-v0.2** (Qwen2.5-VL-3B) for
29+ language visual retrieval, eliminating OCR errors
for equation-heavy pages. **Qdrant** as the vector DB
(advanced payload filtering, native multi-vector, highest
RPS). **Semantic double-pass merging** for math
chunking (1st pass standard, 2nd pass merges similar
chunks around equations that differ).

**BAML schema enforcement** is the type-safe extraction
contract: `MathQuestion` class with `number`, `text`,
`text_irish`, `marks`, `topic` (Algebra/Geometry/
Calculus/Statistics), `marking_criteria`, `requires_diagram`.
The `ExtractExamPaper` function uses `anthropic/claude-sonnet-4-20250514`
with compile-time-verified schemas.

**Deployment** uses **Modal serverless** (recommended)
with T4 ($0.59/hr, dev/test), L4 ($0.80/hr, 7B quantized),
A10 ($1.10/hr, 7B-13B prod), A100 40GB ($2.10/hr, 13B-70B).
Cold start <1s, per-second billing, scale-to-zero,
direct Unsloth export to GGUF/vLLM. **vLLM with
PagedAttention** for 2-4x throughput, semantic cache for
50-90% GPU cost reduction. Latency targets: TTFT <2s,
20-50 t/s minimum, always streaming.

**Evaluation** uses **IRLBench** (reveals 20% English-Irish
gap, best models 55.8% Irish vs 76.2% English) and
**Irish-BLiMP** (1,020 minimal pairs for grammaticality).
MLflow + Ragas integration for experiment tracking.

**Rapid prototyping roadmap**: Days 1-3 (BAML + PyMuPDF4LLM
+ ChromaDB + Streamlit single-paper demo), Week 1
(LlamaIndex + topic-filtered retrieval), Week 2 (ColPali
+ Unsloth fine-tuning), Weeks 3-4 (Modal deploy + caching
+ IRLBench eval).

**MVP cost**: $100-300/month on Modal (compute $100-200,
Qdrant $25, storage $10-20, BAML API $50-100).

See `references/ai-ml-pipeline/AI_ML_PIPELINE.md` for the
full 393-line reference: the OCR tool comparison, the
recommended pipeline architecture, the 3-section
fine-tuning strategy (base model + Unsloth + training
format), the Irish language integration, the RAG
architecture (BGE-M3 + ColPali + Qdrant), the BAML
schema enforcement, the Modal deployment architecture,
the IRLBench + Irish-BLiMP evaluation, the complete
architecture diagram, the 4-week rapid prototyping
roadmap, and the cost analysis.

## KCG critical constraints

The 336-line consolidated project standards, constraints,
and specifications, with 5 CRITICAL/HIGH-severity rules
that all data platform code MUST respect.

**Database Safety (CRITICAL/HIGH)**:

| Constraint | Severity | Rule |
|:--|:--|:--|
| **DuckDB SINGLE_THREADED** | CRITICAL | All operations through `SerialDatabaseExecutor` |
| **LanceDB MVCC safe** | HIGH | Within process: single-threaded; Between processes: MVCC + conflict resolution |
| **NEVER concurrent DB ops** | CRITICAL | Parsing parallelized, storage single-threaded |

**Violation causes**: Segfault, data corruption, "database
is locked", inconsistent queries. The fix is
`SerialDatabaseExecutor` (a `ThreadPoolExecutor` with
`max_workers=1` that submits via `future.result()`).

**Embedding Performance (CRITICAL/HIGH)**:

| Constraint | Severity | Rule |
|:--|:--|:--|
| **Batching MANDATORY** | CRITICAL | Minimum 100 texts per API call (100x faster) |
| **HNSW index management** | HIGH | Drop before bulk inserts >50 rows; Recreate after |
| **Minimum batch size** | CRITICAL | 100 embeddings per API call |

The batch-vs-unbatched numbers: 1,000 texts unbatched =
100s, batched = 1s (100x gain), 10 API calls vs 1,000
(rate-limit friendly).

**BAML Schema Validation (MEDIUM)**: `SCHEMA_VALIDATION_REQUIRED`
before all LLM extraction calls, type-safe extraction
for all curriculum documents, test schemas first in
`baml_src/` before production use.

**Irish Language Processing (HIGH)**: `SPECIALIZED_REQUIRED`
— use UCCIX or GaBERT (20% accuracy gap with generic
models). Model priority: (1) UCCIX-Llama2-13B-Instruct
(+12% over LLaMA 2-70B on Irish), (2) GaBERT (Irish
embeddings), (3) Qwen2.5-Math-7B (native multilingual).

**5 hard modification rules**: NEVER remove
`SerialDatabaseProvider` wrapper, NEVER add concurrent DB
ops, NEVER skip BAML schema validation, NEVER process
embeddings without batching; ALWAYS check existing skills
before implementing features, ALWAYS use uv for Python,
ALWAYS batch embeddings (min 100), ALWAYS drop HNSW
indexes for bulk >50 rows.

**6-item constraint checklist** (before any data op):
SerialDatabaseExecutor for DuckDB? Batch size >= 100?
HNSW dropped for >50 rows? BAML validated? Irish content
on specialized models? Deduplication on multi-result
queries?

**3 error-recovery procedures**: (1) Database corruption:
stop, restore from backup, verify single-threaded, restart;
(2) Embedding timeout: reduce batch to 50, exponential
backoff, check rate limits, consider local model; (3)
Index rebuild failure: drop all indexes, vacuum,
recreate one at a time, monitor memory.

**Performance thresholds**: embedding batch <100 → increase
batch size; DB ops/sec >10 → check for concurrent access;
index rebuild >60s → pre-drop; OCR per page >5s → check
model; memory per process >4GB → review batch sizes.

**Naming conventions**: capabilities kebab-case
(`curriculum-ingestion`), changes prefixed with action
(`add-`, `update-`, `remove-`, `refactor-`), Dagster
assets lowercase with underscores and noun-based
(`daily_active_users`), Irish names for core concepts
(`sruth` = flow, `bonneagar` = infrastructure), bilingual
support in all user-facing content.

See `references/critical-constraints/project-conventions.md`
for the full 336-line reference: the project identity +
capability areas, the naming conventions + requirement
language (SHALL/SHOULD/MAY), the 3 database safety rules
with code, the 3 embedding performance rules with code
+ numbers, the BAML schema validation with `MarkingPoint`
example, the Irish language processing model priority +
dialect table (Connacht/Munster/Ulster/Standard), the 5
performance thresholds, the directory map
(`sruth/`/`bonneagar/`/`agents/`/`baml_src/`/`.agents/skills/`),
the 6-item checklist, the 5 modification rules, the 3
error-recovery procedures, and the Oideachais Pipeline
Spec requirements.

## KCG docs taxonomy

The post-round-1 master routing index — **1,834 source
files consolidated into 7 canonical domains + 1
deploy-plans directory**, every canonical carrying
Cognee-clean frontmatter (`entities`, `related_skills`,
`ccc_query_hints`, `supersedes`).

**5 quadrants × 8 workspace members**:

| Path | Quadrant | Purpose | uv workspace |
|:--|:--|:--|:--|
| `oideachais/` | **Data lakehouse** | Dagster + DLT + DuckLake + LanceDB + Cognee + CocoIndex | member |
| `tuatha/` | **Celtic MMO consumer** | FastAPI + Axum + Babylon.js + Crypteolas + x402 | member (+ 3 sub) |
| `croilar/` | **Multi-persona portfolio** | TanStack + Hono + Convex + BetterAuth | member |
| `meaisínfhoghlaim/` | **AI/ML quadrant** | agents, OCR, Celtic language data, ML pipelines | member (adopted 2026-06-13) |
| `infrastructure/` | **Deploy** | Pangolin, Komodo, Forgejo, Infisical, Ansible, Pulumi | member (+ 1 sub) |

**The "I want to…, where do I go?" routing table** spans
~35 rows: project identity → `00-core/CLAUDE.md`;
constraints → `00-core/CONSTRAINTS.md`; Docker stack →
`infrastructure/AGENTS.md`; secrets → `infrastructure/SECRETS-MANAGEMENT.md`;
container audit → `infrastructure/audit/`; 6-step deploy
playbook → `infrastructure/DEPLOYMENT-STRATEGY.md`;
quadrant-to-stack map → `infrastructure/QUADRANT-TO-STACK-MAP.md`;
live health report → `infrastructure/stacks/HEALTH_REPORT.md`;
Komodo GitOps → `infrastructure/komodo/`; Pangolin →
`infrastructure/PANGOLIN-SETUP.md`; data lakehouse →
`02-data-platform/data-architecture.md`; DuckLake mental
model → `storage-mental-model.md`; cross-domain registry
→ `cross-domain-registry.md`; Dagster →
`dagster-orchestration.md`; DLT → `dlt-pipelines.md`;
LLM stack → `04-ai-ml/llm-stack-hierarchy.md`; OCR →
`oideachais/ocr/`; RAG eval → `04-ai-ml/rag-evaluation.md`;
browser/agent → `03-agents/browser-automation.md`; MCP
server → `03-agents/mcp-servers.md`; Celtic language AI
→ `05-celtic-language/`; Convex+Hono → `05-web/convex-hono-auth.md`;
UI components → `05-web/ui-components.md`; front-end
topology → `05-web/frontend-topology.md`; Celtic MMO →
`06-product/celtic-mmo.md`; crypto → `06-product/crypteolas.md`;
game dev → `06-product/game-development.md`; educational
platform → `06-product/educational-platform.md`;
conventions → `07-standards/project-conventions.md`;
observability → `07-standards/observability-patterns.md`;
deferred roadmaps → `00-deploy-plans/STATUS.md`.

**7 domains + 1 deploy-plans dir** (the post-2026-06-13
canonical tree): `00-core/` (3 active), `01-platform-architecture/`,
`02-data-platform/`, `03-agents/`, `04-ai-ml/`,
`05-celtic-language/`, `05-web/`, `06-product/`,
`07-standards/`, plus `00-deploy-plans/`.

**2 reference flavours** of the master index:
- `references/00-master-docs-index.md` (229 lines, the
  HEAD `docs/00_index.md` content — the round-1
  pre-cleanup version with the 8 subtrees + 9 manual
  `INDEX.md` files + the 12 `supersedes` chains)
- `references/docs-taxonomy/00_index.md` (250 lines, the
  post-2026-06-13 post-cleanup version with the
  7-domain taxonomy + the 5-quadrant map + the
  per-domain counts)

See `references/00-master-docs-index.md` for the 229-line
HEAD version, and `references/docs-taxonomy/00_index.md`
for the 250-line post-cleanup version. Both are
`status: stable` with `domain: standards` frontmatter.
