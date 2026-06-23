---
name: kcg-leabharlann-pipeline
description: The canonical 5-stage KCG PDF flow (secret injection → DLT SHA-256 scan → BAML extraction → CocoIndex v1 embedding → Cognee cognify) for the leabharlann corpus. Use when adding a new leabharlann source, debugging a stage, understanding the asset materialisation order, or asking "how does a PDF become a queryable dataset?".
---

# KCG Leabharlann Pipeline

## When to use this skill

Use when you need to:

- "How does a leabharlann PDF become a queryable dataset?"
- "Add a new leabharlann source (e.g. a new Zotero export)"
- "Debug a stage in the pipeline (DLT scan, BAML, CocoIndex, Cognee)"
- "Understand the asset materialisation order"
- "Wire a new author-archive source through the same flow"

## The 5-stage flow

```
┌────────────────────────────────────────────────────────────────────────┐
│                     LEABHARLANN PDF PIPELINE (5 STAGES)                 │
└────────────────────────────────────────────────────────────────────────┘

Source (leabharlann/gaeilge/*.pdf)
    │
    ▼
[STAGE 1: Secret injection]
Komodo + Infisical + Locket
    │
    ▼
[STAGE 2: DLT filesystem scan + SHA-256 dedup]
FileHashTracker + dlt primary key file_hash
    │
    ▼
[STAGE 3: BAML structured extraction]
ExtractEn → ExtractEnStrong (via LiteLLM)
    │
    ▼
[STAGE 4: CocoIndex v1 incremental embedding]
BGE-large-en-v1.5 + RecursiveSplitter + 100-batch minimum
    │
    ▼
[STAGE 5: Cognee cognify + cross-archive edges]
Memgraph + FalkorDB cache + 8 canonical relationship types
    │
    ▼
Query (LanceDB vector + FalkorDB graph + MotherDuck SQL)
```

## Stage 1 — Secret injection (Komodo + Infisical + Locket)

When the Dagster container starts on `bunchloch` (MacBook M4)
or in production (`arm1-oci`), the **Locket sidecar** reads
the stack's `secrets.env` and hydrates
`infisical://dev-baile/...` references. The Dagster asset
materialisation runs with the resolved secrets in its
environment (no plaintext on disk).

Key secret categories:

- `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` — for BAML LLM calls
- `LITELLM_MASTER_KEY` — for the LiteLLM gateway
- `MOTHERDUCK_TOKEN` — for the MotherDuck read path
- `LANCEDB_API_KEY` — for the LanceDB REST
- `COGNEE_API_KEY` — for the Cognee cognify call
- `POCKET_ID_CLIENT_SECRET` — for the OIDC JWT validation

## Stage 2 — DLT filesystem scan with SHA-256 dedup

`oideachais/dagster_defs/assets/leabharlann_assets.py:leabharlann_books_raw`
materialises → `dlt_sources.author_archive.leabharlann_books_source()`
walks `leabharlann/{gaeilge,aigne}/`, hashes every file with
SHA-256, yields one row per file with metadata + preview_path.

`FileHashTracker` memoises the file-hash ledger. The dlt
primary key (`file_hash`) prevents re-loads on incremental
re-runs. Output goes to DuckLake
(`oideachais.author_archive_uog.documents` or similar).

Similarly:

- `leabharlann_zotero_raw` — 117 PDFs in real Zotero storage
  format with `__dup0` markers + arXiv IDs
- `leabharlann_takeout_v1_raw` — sample Google Takeout at
  `stedding/Takeout/`
- `author_archive_uog_raw` — 7 author-archive sources
  (UoG, Gemini, Takeout, BAML, 3 OCR+embedding flows)

Key Stage 2 properties:

| Property | Value |
|:--|:--|
| Primary key | `file_hash` (SHA-256 of file bytes) |
| Partition columns | `account` + `domain` |
| Incremental strategy | Hash-based (mtime-insensitive) |
| Output | DuckLake (`oideachais.<domain>.<account>.<entity>`) |
| Memoisation | `FileHashTracker` ledger in DuckDB |

## Stage 3 — BAML structured extraction

`leabharlann_paper_metadata` materialises → for each Zotero
PDF, calls `b.ExtractZoteroMetadata(pdf_text, file_name,
arxiv_id)` which returns a `ZoteroPaper` with `paper_kind`,
`arxiv_id`, `doi`, `title`, `authors`, `year`, `abstract`,
`venue`, `irish_relevant`, `htr_relevant`, `confidence`.

Memoised by `(file_hash, baml_function_name)` in the
`author_archive.extraction_metadata` DuckDB table.

The BAML client (`ExtractEn`) routes through the **LiteLLM
gateway** → `litellm/gemini-2.5-flash` (cheap) or
`litellm/anthropic/claude-sonnet-4` via the `ExtractEnStrong`
fallback (accurate).

The BAML schemas (`oideachais/baml_src/`) cover the full
Celtic curriculum: `aistear.baml`, `primary.baml`,
`junior_cycle.baml`, `tertiary.baml`, `ui_components.baml`,
`curriculum_extraction.baml`, `author_archive.baml`
(12 classes), `image_generation.baml`, `site_analysis.baml`.

## Stage 4 — CocoIndex v1 incremental embedding

`leabharlann_cocoindex_zotero_update` materialises → invokes
`subprocess.run(["cocoindex", "update", "oideachais.cocoindex_flows.leabharlann_embedding:LeabharlannZoteroEmbedding"])`.

The v1 App:

- **Source**: `localfs.walk_dir(sourcedir, recursive=True,
  path_matcher=PatternFilePathMatcher(included_patterns=
  ["**/*.pdf"], excluded_patterns=["**/.DS_Store",
  "**/_.pdf"]), live=True)`
- **Per file**: `process_zotero_file` extracts text, chunks
  via `RecursiveSplitter(chunk_size=2000, chunk_overlap=500,
  language="markdown")`, embeds each chunk via
  `SentenceTransformerEmbedder("BAAI/bge-large-en-v1.5")` in
  100+ batches
- **Stable IDs**: `IdGenerator()` + `await id_gen.next_id(chunk.text)`
- **Memoised**: `@coco.fn(memo=True)` on the file-level processor
- **Output**: `rest://lance-api.cianfhoghlaim.ie:8181/leabharlann_zotero`
  (vector + FTS indexes)
- **Indexes**: IVF_HNSW + FTS

The asset materialisation returns a `MaterializeResult` with
`cocoindex_app=LeabharlannZoteroEmbedding, returncode=0,
lance_table=leabharlann_zotero`.

## Stage 5 — Cognee cognify (cross-archive)

`(queued — see oideachais/REFACTORING.md Feature 2)`. The
plan is to add `cognee_cognify_zotero` (and the equivalent
for books / takeout) + `cognee_cross_archive_edges` + 1
FastAPI route + 1 daily cron sensor.

Cognee `cognify()` builds the knowledge graph and persists
to **Memgraph** + **FalkorDB cache**. The cross-archive
edges asset computes relationships like:

- `GeminiDeepResearchReport -[:CITES]-> ZoteroPaper`
  (when an arxiv_id matches)
- `UoGArtifact -[:TEACHES]-> ZoteroPaper` (when the module
  title matches a paper title)

The 8 canonical relationship types are documented in
`.agents/skills/cognee/SKILL.md`.

## Asset materialisation order

The 5 stages are wired as 7 leabharlann-specific Dagster
assets (plus 7 author-archive assets, plus 18 ireland assets,
plus 16 UK assets, plus 8 crown_dependencies assets = 56
total assets across 7 groups):

1. `leabharlann_books_raw` (Stage 2)
2. `leabharlann_zotero_raw` (Stage 2)
3. `leabharlann_takeout_v1_raw` (Stage 2)
4. `leabharlann_paper_metadata` (Stage 3 — BAML)
5. `leabharlann_cocoindex_zotero_update` (Stage 4 —
   CocoIndex)
6. `cognee_cognify_zotero` (Stage 5 — Cognee, queued)
7. `cognee_cross_archive_edges` (Stage 5 — edges, queued)

The groups are:
`{multi_nation_curriculum, uk_education,
leabharlann_books, author_archive_uog,
ireland_primary_jc, crown_dependencies, leabharlann}`.

## Live URLs (post-deploy)

| Service | URL |
|:--|:--|
| Dagster UI | `https://dagster.cianfhoghlaim.ie` |
| BAML playground | `https://baml.cianfhoghlaim.ie` |
| LanceDB viewer | `https://lance.cianfhoghlaim.ie:8081` |
| Cognee | `https://cognee.cianfhoghlaim.ie:8000` |
| FalkorDB | `https://falkordb.cianfhoghlaim.ie:6379` |
| MotherDuck | `md:oideachais` (read-only) |
| TanStack Start (oideachais/web) | `https://oideachais.cianfhoghlaim.ie` |

## Cross-references

- `.agents/skills/kcg-bunchloch/SKILL.md` — the 3-tier
  host topology
- `.agents/skills/kcg-convergence/SKILL.md` — the 6
  docker-compose categories
- `.agents/skills/oideachas-pipeline/SKILL.md` — the
  oideachais pipeline (the source of the flow)
- `.agents/skills/oideachais-storage/SKILL.md` — the
  DuckLake + MotherDuck + Iceberg mental model
- `.agents/skills/dagster/SKILL.md` — the Dagster asset
  + group + partition patterns
- `.agents/skills/dlt/SKILL.md` — the DLT source +
  `FileHashTracker` pattern
- `.agents/skills/baml/SKILL.md` — the BAML extraction
  + `ExtractEn` / `ExtractEnStrong` clients
- `.agents/skills/cocoindex/SKILL.md` — the CocoIndex v1
  flow patterns
- `.agents/skills/cognee/SKILL.md` — the Cognee cognify
  + 8 canonical relationship types
- `oideachais/STATUS.md` — pipeline state (single source
  of truth)
- `oideachais/REFACTORING.md` — refactor backlog (Stage 5
  is queued)

## Ingestion layer (Browserbase + Agno + GLM-4.6v + BAML + Cognee)

The 5-stage leabharlann flow assumes **known PDFs at
known paths**. The KCG extension (Q1 2026) adds a
**Stage 0: agentic web scraping** layer for the case
where the source is a live web property (e.g. an NCCA
sub-site, a DCU Gaois PDF, a teanglann.ie page) and we
need to **discover, fingerprint, and reconstruct** the
extraction schema as the site evolves.

This is the **neuro-symbolic web intelligence** pattern
that complements the static BAML extraction in Stage 3.

### The 5-component closed-loop

```
[Observation] Browserbase (CDP)
       │
       ▼
[Perception]  Z.AI GLM-4.6v (VLM via MCP)
       │
       ▼
[Cognition]   Cognee (knowledge graph)
       │
       ▼
[Systematization] BAML (TypeBuilder, self-rewriting)
       │
       ▼
[Creation]    Ag-UI (generative prototype)
```

Each stage is an **MCP tool** the Agno agent can invoke
on demand; the BAML schema is the contract between them.

### Stage 0a — Browserbase (Observation)

Use Browserbase (managed CDP, not raw Selenium) to:
- Navigate JS-heavy SPAs that the `dlt filesystem` source
  cannot reach
- Get **artifact-free full-page screenshots** via
  `Page.captureScreenshot` (vs the stitched images
  Selenium produces)
- Bypass anti-bot detection via residential proxies +
  human-like fingerprints (essential for protected
  education sources)

The Agno agent is a "transcoding bridge": it decodes the
Base64 screenshot from Browserbase, persists it to R2
(`s3://stedding/screenshots/{date}/{hash}.png`), and
hands the local path to the next stage. The MCP file
contract is what GLM-4.6v expects.

### Stage 0b — GLM-4.6v via Z.AI MCP (Perception)

Z.AI exposes 3 vision tools that the agent invokes in
sequence:

1. **`web_reader`** — fetches the raw DOM text + meta
   (Title, Description) for "ground truth"
2. **`extract_text_from_screenshot`** — OCRs the
   screenshot, **rank-orders text by visual prominence**
   (what the user actually sees first)
3. **`ui_to_artifact`** — reverse-engineers the visual
   bitmap into a semantic description (layout grid,
   color palette, component tree)

By cross-referencing the 3 outputs the agent answers
"this text is the H1 not just because of the `<h1>` tag,
but because OCR confirms it is the largest element in
the viewport". This triple-anchor is what makes the
downstream BAML schema stable.

### Stage 0c — Cognee (Cognition: persistent memory)

Cognee replaces the "stateless re-scrape every time"
problem. After `cognify()`, the design ontology lives
as a queryable graph:

- **Nodes:** `Page`, `Section` (Hero, Footer),
  `Component` (Button, Card), `Style` (Color, Font)
- **Edges:** `CONTAINS`, `LINKS_TO`, `STYLED_WITH`

Example triple from a CCEA page:
`(Hero Section) -[:CONTAINS]-> (Button) -[:STYLED_WITH]-> (Color: #FF5733)`

This is what the leabharlann Stage 5 (`cognee_cognify_*`
asset) generalises to: instead of one Cognee call per
file, the graph **persists across files** so a new
CCEA sub-page can be cross-referenced against
historical CCEA pages in a single Cognee query.

### Stage 0d — BAML self-rewriting (Systematization)

This is the **self-healing pipeline** pattern:

1. The vision layer detects a layout shift on, say,
   the NCCA primary curriculum site.
2. Cognee's graph updates with the new component tree.
3. The Agno agent queries the graph: *"Does this product
   page have a `review_count`? A `discount_price`?"*
4. Based on the graph shape, the agent **writes a new
   `.baml` file** that adds `review_count int` (or
   whatever) to the extraction class.
5. `baml-cli generate` regenerates the Python + TS clients.
6. Stage 3 of the leabharlann flow (`leabharlann_paper_metadata`)
   now uses the new schema.

The BAML `TypeBuilder` is the escape valve when the
graph shows a field that **doesn't exist** in the static
`.baml` file — it lets the agent extract anyway, log the
deviation as a "Schema Patch" Dagster asset, and surface
it for human review (the human-in-the-loop consolidation
step).

### Stage 0e — Ag-UI (Creation: generative prototype)

The agent also reuses the Cognee graph + GLM-4.6v to
**render a React/Tailwind clone** of the analysed site,
streamed via the Ag-UI `gen_ui_event` protocol. This
is useful for design QA ("does the scraped structure
match the design system?") and for the
`oideachais/visual_archive` demo in the marimo
notebooks.

### Medallion R2 architecture (the asset-key contract)

The Cloudflare R2 bucket is split into 3 zones; this
maps directly to the leabharlann Stages 2-4:

| Zone | Path | Stage | Retention |
|:--|:--|:--|:--|
| **Raw (Bronze)** | `s3://stedding/raw/{nation}/{date}/{hash}.html` | Stage 0a | Permanent (re-extraction possible) |
| **Extracted (Silver)** | `s3://stedding/extracted/{nation}/{schema_ver}/{id}.json` | Stage 0d | Versioned (per BAML schema_ver) |
| **Knowledge (Gold)** | `s3://stedding/knowledge/{index_type}/{shard}.parquet` | Stage 4-5 | Current state (CocoIndex + DuckDB) |

The Bronze zone is the **time-travel** layer: if a BAML
schema improves (e.g. a new field for `dialect` is added),
Stage 0d can re-process every raw HTML without re-scraping.
The `{schema_ver}` in Silver captures the lineage.

### Dagster asset wiring (the `@dlt_assets` projection)

The whole Stage 0 is one Dagster asset group
(`agentic_ingest`) that wraps dlt via `@dlt_assets`:

```python
from dagster import AssetExecutionContext
from dagster_dlt import DagsterDltResource, dlt_assets
from dlt_sources.ccea import ccea_source

@dlt_assets(
    dlt_source=ccea_source(),
    dlt_pipeline=dlt.pipeline(
        pipeline_name="ccea_agentic_ingest",
        destination="filesystem",   # R2
        dataset_name="ccea_education",
        progress="log",
    ),
    name="ccea_agentic_raw",
    group_name="agentic_ingest",
)
def ccea_assets(context: AssetExecutionContext, dlt: DagsterDltResource):
    yield from dlt.run(context=context)
```

The dlt internal tables (`pages`, `screenshots`,
`vision_artifacts`, `cognee_episodes`) all surface as
**distinct assets** in the Dagster lineage graph — the
data engineer sees exactly when `ccea_agentic_raw` was
last materialised and which upstream failed.

### KCG production rules (anti-patterns)

- **Don't call GLM-4.6v on every URL** — the cost is
  real. Use it only after the Browserbase `web_reader`
  shows the page **isn't in our BAML coverage**.
- **Don't write the new BAML file directly** — let
  the Agno agent propose the diff, then a human
  approves via the `Schema Patch` Dagster asset.
- **Don't normalise the Cognee ontology per-page** —
  use the **shared** `oideachais.education.{nation}.{entity}`
  ontology from `cross-domain-registry`; Cognee adds
  nodes/edges, never redefines classes.
- **Don't bypass Dagster** — the whole point of the
  closed-loop is **asset lineage**. Browserbase
  screenshots must be an asset, not an ad-hoc fetch.

See [`celtic-asset-generation/references/agent-knowledge-base.md`](../celtic-asset-generation/references/agent-knowledge-base.md)
for the 631-line blueprint (4 domain case studies:
Ethereum, Cloudflare, UK Education, Godot) including
the complete BAML `EthereumProtocol` and
`CorporateEntity` schemas and the
Graphiti `add_episode` flow.

For the full neuro-symbolic web scraping architecture
(Browserbase + Agno + Z.AI + Cognee + BAML + Ag-UI)
see [`celtic-asset-generation/references/agent-knowledge-base.md`](../celtic-asset-generation/references/agent-knowledge-base.md) and
the source deep-dive (formerly at
`docs/tuatha/03-data-pipelines/Agentic Web Scraping Pipeline.md`,
superseded by the round-8 docs → skills migration).
