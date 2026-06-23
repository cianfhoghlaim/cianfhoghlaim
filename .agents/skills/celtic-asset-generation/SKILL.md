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
