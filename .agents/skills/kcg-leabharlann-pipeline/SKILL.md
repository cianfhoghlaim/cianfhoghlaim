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
