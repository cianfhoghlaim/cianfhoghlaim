#!/usr/bin/env python3
"""Replace the README section between 'TL;DR' and 'The cianfhoghlaim plan throughout the British Isles'."""
from __future__ import annotations
from pathlib import Path

# Lines to find (start of section, end of section)
START_MARKER = "## TL;DR — What this is, today"
END_MARKER = "## The cianfhoghlaim plan throughout the British Isles"

NEW_SECTION = '''## TL;DR — What this is, today

`cianfhoghlaim` is a polyglot monorepo (`bun + uv + turbo`) that ingests
the curriculums, exam papers, marking schemes, and syllabi of the
**eight British Isles nations** (Ireland, England, Scotland, Wales,
Northern Ireland, Isle of Man, Jersey, Guernsey), makes them interactive
and bilingual through self-hosted AI, and serves as the personal
research-and-deployment platform of **Cian Mac an Déisigh Uí Liatháin
(Deacy-Lyons)** — a Mathematics & Education teacher / Dioplóma C1 in
Irish / agentic-AI engineer based in Galway and East Belfast. After the
**v4 consolidation of 2026-06-28**, the application code lives in a
single Python package, [`cianfhoghlaim/`](./cianfhoghlaim/), served by
**228 Dagster assets** across 21 groups. The GitOps foundation
(`bonneagar`) and the digital library (`leabharlann`) live in their
own sibling repos and are exposed here as **git worktrees at the root
of the workspace** — they are *not* `git subtree`s, so the monorepo
push stays small (a few KB of README + skill metadata, not 3.4 GB of
PDFs). The platform is wired together by a **5-subagent OpenCode
foundation** backed by a 59-skill knowledge library indexed by
[cocoindex-code (ccc)](.agents/skills/ccc/SKILL.md).

The author's purpose — the **Rí na Gaillimhe** claim, the **Ard-Rí na
hÉireann** stewardship, the East Belfast operational hub, the inter-Celtic
acquisition pathway, the §21e Saoí standard, the **Celtic AI Institute**
in the Isle of Man, and the **30-year Cultural Archipelago roadmap** to
2056 — is documented in 8 Gemini Deep Research PDFs in the
[`leabharlann/gemini_deep_research/culture/`](https://github.com/cianfhoghlaim/leabharlann/tree/main/gemini_deep_research/culture/)
archive of the `leabharlann` sibling repo. See the
**"Purpose of Cian Mac an Déisigh Uí Liatháin and cianfhoghlaim"**
section below for the direct citations.

---

## What cianfhoghlaim is now (post-v4 + post-baml-reorg)

The cianfhoghlaim project has been progressively consolidated through
**three openspec changes** (all archived):

- `2026-06-28-consolidate-sruth-into-cianfhoghlaim-v4` — the 5
  `sruthanna` quadrants (`oideachais`, `meaisinfhoghlaim`, `tuatha`,
  `croilar`, `crypteolas`) + the `browser` core + the `codeolas` C++
  sub-package + the `leabharlann` corpus were consolidated into a
  single `cianfhoghlaim/` Python package.
- `baml-reorganize-by-cluster` — the 60+ BAML files were moved into a
  **3-cluster taxonomy** (`education/`, `celtic/`, `processing/`) with
  `_shared/` homes per cluster. The 5 NCCA stage BAML files were
  merged (eliminating duplicate enums like `ExamLevel`); the
  1114-LOC `curriculum_extraction.baml` mega-file was split into 5
  focused `_shared/` files; the 12 dead `_v0_archive/` CocoIndex files
  were deleted.
- `wire-baml-to-consolidated-pipelines` — 17 consumer files
  (`dlt/`, `dagster/`, `agents/`, `cocoindex/`, `notebooks/`) were
  swept to remove 26 stale `baml_src/X.baml` path references; a BAML
  project config (`baml/baml.toml`) and `baml_src → baml` symlink
  were created so the BAML compiler can regenerate the client from
  the new cluster taxonomy.

The current state (after these 3 changes):

| Surface | Count | Shape |
|:--|--:|:--|
| **BAML files** (`cianfhoghlaim/baml/`) | 60+ | 3-cluster taxonomy (education/celtic/processing) with `_shared/` homes |
| **dlt sources** (`cianfhoghlaim/dlt/`) | 200+ | 8 top-level dirs (api_sources/british_isles/common/filesystem/language/official_media/portfolio + 8 nations × 4 domains in british_isles/) |
| **CocoIndex v1 Apps** (`cianfhoghlaim/cocoindex/`) | 14+ | v1 Apps with `_lifespan.py` shared runtime + R1-R4 conformance |
| **Dagster assets** (`cianfhoghlaim/dagster/`) | 228+ | Layered defs/{1_ingestion, 2_materials, 3_model_lifecycle, 4_asset_generation, 5_agent_ops}/ |
| **meaisinfhoghlaim** (`cianfhoghlaim/meaisinfhoghlaim/`) | 15+ subdirs | 24 OCR models + 5 PDF converters + 8 alignment models + RAGAS harness |
| **agents** (`cianfhoghlaim/agents/`) | 12-agent fleet | 9 sub-packages flattened from the v3 `_underscore` legacy dirs |
| **notebooks** (`cianfhoghlaim/notebooks/`) | 29+ | 7 dashboards/ + 12 per-subject pipelines + 3 PDF processing + 5 observability/duckdb/mmo |
| **web** (`cianfhoghlaim/web/`) | 7 apps + 1 API | TanStack Start + Babylon.js + Hono API gateway |
| **storage** (`cianfhoghlaim/storage/`) | 4-layer arch | `_shared/{falkordb,memgraph,neo4j,interface}.py` + top-level cache/temporal_client |

---

## The 5-stage pipeline (the architecture)

The cianfhoghlaim pipeline takes a corpus (PDFs, DOCX, EPUBs, Zotero
exports, Google Takeout, UoG coursework, exam papers, marking schemes,
syllabi) from raw disk all the way through to a queryable,
agent-consumable, semantically-indexed artifact. The pipeline is
organised as 5 sequential stages, each with a `defs/<stage>/` home
under the single Dagster code-location.

### Stage 1 — Ingestion (`dagster/defs/1_ingestion/`)

The 8-nation DLT lateralise: every British Isles nation has a per-domain
Dagster Component (the `CelticIngestionComponent`) under
`dagster/defs/1_ingestion/{nation}/{domain}/{source}/defs.yaml`.
The 8 nations × 4 canonical domains = 32 sources; the 3 special
sources (filesystem, api, language) add 24 more.

| Domain | Ingestion home | What it ingests |
|:--|:--|:--|
| `british_isles/{nation}/{domain}/` | dlt sources per nation × domain | The 8 nations × 4 domains = 32 DLT sources |
| `filesystem/` | 8 filesystem dlt sources | Personal corpus (books, zotero, takeout, CV) |
| `api_sources/` | 3 API dlt sources | GitHub, LinkedIn, ResearchGate REST APIs |
| `language/` | 25 Celtic/Irish sources | Canúint, Dúchas, Tearma, Logainm, AINM, etc. |
| `official_media/` | 9 Instagram sources | Instagram-export → British-Isles gov source resolver |
| `portfolio/` | 7 filesystem sources | Artwork, CV, labels, teaching |

The 8 nations (with full country names per the v3 plan):
**england** (London), **ireland** (Dublin + Galway), **scotland**
(Edinburgh), **wales** (Cardiff), **northern_ireland** (Belfast),
**isle_of_man** (Douglas), **jersey** (St Helier), **guernsey** (St Peter
Port).

The `british_isles/{nation}/{domain}/` shape is the canonical home.
The top-level `filesystem/`, `api_sources/`, `language/`, `official_media/`,
`portfolio/` are purpose-grouped cross-cutting sources.

### Stage 2 — Extraction (`dagster/defs/2_materials/`)

The BAML extraction layer: the 3-cluster BAML taxonomy (60+ BAML
files in `baml/{education,celtic,processing}/`) is consumed by
per-source BAML extraction functions. The 11 NCCA Leaving Cert
subjects each have a `qpack_*.baml` file (BAML function:
`Generate{Subject}QuestPack`) for formative assessment generation.
The 5 NCCA education stages each have a stage-specific BAML file
(`aistear.baml`, `primary.baml`, `junior_cycle.baml`, `senior_cycle.baml`,
`tertiary.baml`).

The 3 PDF extraction BAML files at `baml/education/pdfs/`:
- `leaving_cert_syllabus.baml` — `ExtractLeavingCertSyllabus`
- `leaving_cert_past_paper.baml` — `ExtractLeavingCertPastPaper`
- `leaving_cert_marking_scheme.baml` — `ExtractLeavingCertMarkingScheme`

The 5 shared files at `baml/education/_shared/`:
- `education_level.baml` — the canonical `LeavingCertSubject` (50+ values)
  + `EducationLevel` + `ExamLevel` + 7 more enums
- `strand_outcome.baml` — 17 cross-stage classes
- `curriculum_relationships.baml` — 4 relationship functions
- `subject_rubric.baml` — 4 rubric functions + 5 classes
- `document_metadata.baml` — 2 document metadata functions

### Stage 3 — Model Lifecycle (`dagster/defs/3_model_lifecycle/`)

The meaisinfhoghlaim OCR + embedding + cognify layer: the
`meaisinfhoghlaim/registry.py` exposes **24 OCR/vision models**
(9 vision + 4 classical + 3 image-gen + 8 alignment). The
`meaisinfhoghlaim/document_factory/converters/` provides **5 PDF
converters** (deepseekocr, docling, marker, pymupdf4llm, unstructured).
The 14+ CocoIndex v1 Apps embed the extracted text into LanceDB
(BGE-M3, 1024-dim) via the `mount_table_target` pattern.
The cognify stage populates the Cognee knowledge graph over 6 typed
datasets (`aistear`, `primary`, `junior_cycle`, `senior_cycle`,
`tertiary`, `cross_stage`) plus the 3 leabharlann cognify passes
(books, zotero, takeout) plus the 3 cross-archive edge rules.

### Stage 4 — Asset Generation (`dagster/defs/4_asset_generation/`)

The `marimo_dashboards/`, `orpc_routes/`, `tanstack_pages/` dirs
generate the 5 web apps, the Hono API gateway, and the marimo
notebooks from the 4 layers above. This is the read-side layer.

### Stage 5 — Agent Ops (`dagster/defs/5_agent_ops/`)

The 12-agent fleet at `agents/meaisinfhoghlaim/agents/`: curriculum,
translation, corpus, research, geospatial, voice, statistics,
education-research, bunchloch-research, AG-UI curriculum, MCP
curriculum, enhanced orchestrator, root. Each agent is a
`LlmAgent` (Google ADK) or `Agent` (Agno) wired to the BAML client.

---

## The 11 NCCA Leaving Cert subject asset groups

For each of the 11 NCCA LC subjects (mathematics, english, gaeilge,
applied_mathematics, chemistry, computer_science, biology, business,
french, geography, history), the dagster asset group follows a
**canonical 6-asset pattern** (the `mathematics_assets.py` template):

1. **`{subject}_syllabus_raw`** — DLT ingestion of NCCA syllabus PDFs
   into DuckLake (per level × language partition)
2. **`{subject}_syllabus_structured`** — BAML
   `ExtractLeavingCertSyllabus` per PDF row
3. **`{subject}_quest_pack`** — BAML `Generate{Subject}QuestPack`
   per level (FL/OL/HL)
4. **`{subject}_embedding`** — CocoIndex v1 embedding into LanceDB
5. **`{subject}_cognify`** — Cognee cognify pass (subject knowledge graph)
6. **`{subject}_dashboard`** — marimo notebook execution

The 11 subject files (in `dagster/assets/`):
- `mathematics_assets.py` (the template, ~330 LOC)
- `english_assets.py`, `gaeilge_assets.py`, `applied_mathematics_assets.py`
- `chemistry_assets.py`, `computer_science_assets.py`
- `biology_assets.py`, `business_assets.py`, `french_assets.py`
- `geography_assets.py`, `history_assets.py`

All 11 use canonical `cianfhoghlaim.dlt.british_isles.ireland.education.subjects.{subject}`
imports (no legacy `dlt_sources.*` paths).

---

## The PDF processing pipeline (`dagster/assets/by_domain/pdf_processing.py`)

The unified PDF processing pipeline processes the **133 PDFs in
`leaving_certificate/{11 subjects}/{en,ga}/`** through an **8-asset pattern**:

1. **`pdf_discover`** — scan `leaving_certificate/` for all 133 PDFs
2. **`pdf_convert`** — convert via the 5 PDF converters
   (deepseekocr, docling, marker, pymupdf4llm, unstructured)
3. **`pdf_ocr_compare`** — run the 24 OCR models + 3 backends, compare
   extraction quality + fada preservation
4. **`pdf_extract_baml`** — BAML `ExtractLeavingCertSyllabus` +
   `ExtractLeavingCertMarkingScheme` + `ExtractLeavingCertPastPaper`
5. **`pdf_embed_cocoindex`** — embed into LanceDB via CocoIndex v1
6. **`pdf_cognify`** — Cognee cognify pass
7. **`pdf_evaluate`** — RAGAS evaluation across all 11 subjects
8. **`pdf_quality_check`** — Irish content validation
   (fada preservation + dialect detection)

A separate `meaisinfhoghlaim_ocr` asset group (`by_domain/meaisinfhoghlaim_ocr.py`)
wraps the 24 OCR models + 5 PDF converters + 8 alignment models as a
unified asset group (3 assets: `meaisinfhoghlaim_ocr_models`,
`meaisinfhoghlaim_pdf_converters`, `meaisinfhoghlaim_alignment`).

---

## The Celtic AI Institute (Isle of Man) — the cianfhoghlaim output side

The cianfhoghlaim plan's output side is the **Celtic AI Institute** — a
proposed open-source research lab that builds **Sovereign LLMs for Irish,
Welsh, Manx, Scottish Gaelic, and Cornish**. The Institute is hosted in
the **Isle of Man**, the Celtic jurisdiction that uniquely combines:

- (a) the **Tynwald parliament** (the oldest continuous parliament in
  the world, est. ~979 AD)
- (b) the **Manx Pound** pegged 1:1 to Sterling (the model for a future
  "New Punt" / Monetary Dualism)
- (c) **data-regulation autonomy** that lets the Institute host the
  open-source Celtic LLMs without the regulatory friction of UK or EU
  jurisdiction

The cianfhoghlaim monorepo is the **Phase I delivery vehicle** for the
Institute. The 5-stage pipeline maps directly to the Institute's data
infrastructure:

- `dlt/ingest/` (Stage 1) picks up the Gaeltacht + Celtic-language PDFs
- `baml/extract/` (Stage 2) extracts the structured claims
- `cocoindex/embed/` (Stage 3) builds the per-language LanceDB indices
- `cognify/` (Stage 4) populates the cross-dataset knowledge graph
- `pipelines/distribute/` (Stage 5) exposes everything via the marimo
  notebooks + TanStack Start web apps + HuggingFace Spaces

### The 30-year Cultural Archipelago roadmap (2026-2056)

| Phase | Timeframe | Primary focus | Key deliverables | Strategic objective |
|:--|:--|:--|:--|:--|
| **I** | 2026-2036 | Stabilization & Digital Sovereignty | Expansion of the Bunscoill model to NI/ROI; "Protestant Gaelic" curriculum; **Celtic AI Institute founded in the Isle of Man** | Halt language erosion; neutralize sectarian binaries; secure digital borders via Sovereign AI |
| **II** | 2036-2046 | Integration & Mobility | Pan-Celtic Erasmus (Colmcille expansion); Celtic Broadcasting Union (TG4 + S4C + BBC Alba); Irish Sea Tunnel feasibility study complete | Build "Archipelagic" identity; economic interdependence; joint maritime defense culture |
| **III** | 2046-2056 | Normalization & Sovereignty | Bilingual Public Service (50% target); **Saoí Education Standard** in exams; New Punt / Dual Currency Zone implementation | De facto Dual Monarchy realization; cultural singularity; total cognitive security |

### The Sãoí Education Standard (Phase III capstone)

The **Saoí Education Standard** ("fluent in both the Fénechas and Python",
per `cultural_unity_for_british_isles.pdf` p. 4) is the capstone of
Phase III — a Leaving Cert / A-Level distinction that requires a
multidisciplinary project combining a Celtic language with a STEM
discipline (e.g. an AI chatbot in Manx, GIS mapping in Cornish, ML
analysis of Ogham inscriptions).

The cianfhoghlaim monorepo directly supports the Sãoí standard via
the 6-asset subject pipeline: a student can materialise
`gaeilge_embedding` + `computer_science_embedding` + `gaeilge_cognify`
+ a custom dagster asset to build a Leaving Cert project that combines
a Celtic language with a STEM discipline.

---

## What cianfhoghlaim commits to the heritage

The cianfhoghlaim plan, taken as a whole, is a **commitment to the
cultural stewardship** of the four provinces, the Gaeltachtaí, and
the wider Celtic-language family. The **Ard-Rí title** described in
§21c is not a constitutional claim; it is the stewardship role that
holds the cianfhoghlaim project accountable to the Gaelic inheritance
it serves. The §20 operational plan — the East Belfast hub, the
inter-Celtic acquisition pathway, the Isle-of-Man Celtic AI Institute,
the 30-year Cultural Archipelago roadmap — is the public-good output
of that stewardship.

The 30-year horizon is deliberately long: Phase I (2026-2036)
stabilizes, Phase II (2036-2046) integrates, Phase III (2046-2056)
normalises. Each phase is decoupled from any near-term political
event; the cianfhoghlaim project will continue to deliver open-source
Celtic-language LLMs and syllabus-informed resources regardless of
whether a border poll is held in 2030 or 2060 or never. The cultural
stewardship is apolitical in the constitutional sense and political in
the everyday sense (it requires the daily work of language teaching,
of community organising, of BAML extraction, of LanceDB embedding,
of marimo notebook maintenance, of Dagster asset materialisation).

---

## Notebooks and demos (29+ marimo notebooks)

The `cianfhoghlaim/notebooks/` directory demonstrates the pipelines.
**29+ marimo notebooks** are organised under `dashboards/`:

- `dashboards/education/` (12+ per-subject pipelines) — one
  `{subject}_full_pipeline.py` per LC subject showing the 6-asset
  DLT→BAML→CocoIndex→Cognee→marimo workflow end-to-end
- `dashboards/pdf_processing/` (3) — `pdf_ocr_model_comparison.py`
  (5 OCR models on 133 PDFs), `pdf_extraction_quality.py` (RAGAS
  eval), `pdf_processing_benchmark.py` (performance)
- `dashboards/observability/` (2) — `irish_extraction_quality.py`
  (fada + dialect), `baml_drift_audit.py` (250+ BAML functions vs
  actual usage)
- `dashboards/duckdb/` (2) — `dlt_pipeline_overview.py` (8
  nations × 4 domains), `cocoindex_embedding_coverage.py` (14+ v1
  Apps + their LanceDB tables)
- `dashboards/mmo/` (1) — `cianfhoghlaim_mmo_progress.py` (8 NCCA
  subject agent dashboards)
- `dashboards/{aistear,primary,junior_cycle,senior_cycle,tertiary,
  cross_domain,email_inbox_triage,leabharlann_full_stack_demo}.py`
  (the existing v4 dashboards)

---

## OpenSpec catalogue (46 specs, 8 groups)

The 46 capability specs across 8 groups document the cianfhoghlaim
project's contract surface:

- **oideachais** (10) — the curriculum pipeline
- **meaisinfhoghlaim** (6) — the OCR + model lifecycle
- **tuatha** (3) — the educational MMO + crypto platform
- **croilar** (3) — the multi-persona portfolio
- **infrastructure** (3) — stacks + secrets + monitoring
- **data-platform** (8) — DLT, Dagster, DuckLake, LanceDB, etc.
- **frontend** (5) — TanStack Start, AG-UI, Hono API
- **shared** (8) — the cross-cutting specs (agent-registry, BAML,
  CocoIndex, indexing-and-cognition)

`openspec list --specs` / `openspec validate <change-id> --strict` /
`openspec archive <change-id> --yes` is the canonical workflow.

---

## Repository constellation

This repository (`cianfhoghlaim/cianfhoghlaim`) is the **application
monorepo**. Two companion repositories live as their own GitHub repos
and are exposed here as **standalone git worktrees at the root of the
workspace**, so each domain has its own independent release cadence,
secrets boundary, and review surface — and so the monorepo push stays
small.

| Repo | Domain | Sibling repo | Worktree at the root |
|:--|:--|:--|:--|
| [**cianfhoghlaim/cianfhoghlaim**](https://github.com/cianfhoghlaim/cianfhoghlaim) (you are here) | Application monorepo: Python package, agents, web apps, Dagster pipelines, CocoIndex flows, OCR registry | n/a | this repo |
| [**cianfhoghlaim/bonneagar**](https://github.com/cianfhoghlaim/bonneagar) | GitOps foundation: Pulumi, Ansible, Komodo, Pangolin, Dagger, 90 compose stacks, secrets templates | [`bonneagar`](https://github.com/cianfhoghlaim/bonneagar) | `./bonneagar/` (branch `bonneagar-main` → `bonneagar/main`) |
| [**cianfhoghlaim/leabharlann**](https://github.com/cianfhoghlaim/leabharlann) | Digital library: Gaeilge, mata, aigne, ollscoil, Zotero papers, Gemini deep-research reports (2,400 files, 3.4 GB) | [`leabharlann`](https://github.com/cianfhoghlaim/leabharlann) | `./leabharlann/` (branch `leabharlann-main` → `leabharlann/main`) |

All three repositories are licensed under the **Business Source License
1.1** (BUSL-1.1) by the same Licensor. See [`LICENSE.md`](./LICENSE.md).

> *Bonneagar* — Scottish Gaelic for *infrastructure*.
> *Leabharlann* — Irish for *library*.

### Why worktrees, not subtrees?

The 3.4 GB of PDFs in `leabharlann` and the 6.9 MB of compose stacks in
`bonneagar` are too large to commit into the application monorepo's
git history. Embedding them as `git subtree`s would make every
`git push` upload 3 GB of binary data, slow CI to a crawl, and bloat
clone size for every contributor. The worktree approach keeps the
content *visible and editable* from this workspace without committing
it to this repo.

### Working with the sibling repos

```bash
# Edit the leabharlann corpus
cd leabharlann
# ... edit a PDF metadata file ...
git add -A
git commit -m "docs(zotero): add new paper on Irish NLP"
git push                       # → leabharlann-main → leabharlann/main → the GitHub repo

# Edit the bonneagar compose stacks
cd ../bonneagar
# ... edit infrastructure/stacks/litellm/compose.yaml ...
git add -A
git commit -m "chore(litellm): bump image tag"
git push                       # → bonneagar-main → bonneagar/main → the GitHub repo
```

From the monorepo's perspective, the worktrees are the canonical
*upstream* copies of the sibling repos. The monorepo consumes them
through relative paths:

- `./bonneagar/stacks/litellm/compose.yaml` — referenced in
  `infrastructure/AGENTS.md` (the bonneagar worktree's own quick-ref)
  and in [`docs/PHASE_0.3_DEPLOY_RUNBOOK.md`](docs/PHASE_0.3_DEPLOY_RUNBOOK.md)
- `./leabharlann/gaeilge/` — referenced in the Cognee dataset
  `oideachais_culture_heritage`
- `./leabharlann/zotero/` — referenced in the CocoIndex v1 App
  `leabharlann_zotero`

To pull the latest from the sibling repos:

```bash
git fetch bonneagar main
git fetch leabharlann main
cd bonneagar   && git merge --ff-only bonneagar/main   && cd ..
cd leabharlann && git merge --ff-only leabharlann/main && cd ..
```

---

## Temporary architecture diagram

> ⚠️ **Temporary.** This ASCII diagram is a stand-in for a Mermaid / d2
> diagram that will land in the next `docs-restructuring` openspec change.
> It shows the **3-tier host topology** (arm1-oci → cax41-hetzner →
> bunchloch) overlaid with the 3 repos, the 5 subagents, and the
> Lakehouse data plane.

```
                            ┌──────────────────────────────────────────────────────────┐
                            │  THE 5 DISPATCHABLE SUBAGENTS  (opencode.json)            │
                            │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───┴───┐
                            │  │   data-  │ │  infra-  │ │  agent-  │ │ frontend │ │research│
                            │  │ platform │ │ structure│ │ platform │ │  -apps   │ │       │
                            │  │   (15)   │ │   (16)   │ │   (23)   │ │   (20)   │ │  (11) │
                            │  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ └───┬───┘
                            └───────┼────────────┼────────────┼────────────┼───────────┼─────┘
                                    │            │            │            │           │
            ┌───────────────────────┼────────────┼────────────┼────────────┼───────────┼────────────┐
            │  APPLICATION MONOREPO │            │            │            │           │            │
            │  (cianfhoghlaim/)     │            │            │            │           │            │
            │  ┌────────────────────▼────────────▼────────────▼────────────▼───────────▼──────────┐ │
            │  │                        cianfhoghlaim/ Python package                              │ │
            │  │                                                                                    │ │
            │  │  core/  (16 first-class stack pkgs)   sources/nations/  agents/                  │ │
            │  │  pipelines/  (5-stage: ingest→expose)  assets/  (Dagster code-location)           │ │
            │  │  ocr/  stacks/  web/  libraries/codeolas/  notebooks/  cognify/  embeddings/    │ │
            │  │                                                                                    │ │
            │  │  BAML  •  DLT  •  Dagster  •  CocoIndex v1  •  DuckLake  •  LanceDB  •  Cognee   │ │
            │  │  Langfuse  •  MLflow  •  RAGAS  •  12-agent fleet  •  marimo  •  TanStack Start │ │
            │  └────────────────────────────────────────────────────────────────────────────────────┘ │
            │                                                                                        │
            │   ┌────────────────────────────────────────────────────────────────────────────────┐   │
            │   │  GIT WORKTREES at the root of the workspace  (NOT subtrees — no 3 GB push)   │   │
            │   │  ┌────────────────────────────┐    ┌────────────────────────────┐            │   │
            │   │  │  ./bonneagar/              │    │  ./leabharlann/            │            │   │
            │   │  │  branch: bonneagar-main    │    │  branch: leabharlann-main  │            │   │
            │   │  │  tracking: bonneagar/main  │    │  tracking: leabharlann/main│            │   │
            │   │  │                            │    │                            │            │   │
            │   │  │  90 compose stacks         │    │  2,400 files, 3.4 GB       │            │   │
            │   │  │  Pulumi, Komodo, Pangolin  │    │  Gaeilge, mata, aigne      │            │   │
            │   │  │  Dagger, Ansible, secrets  │    │  Zotero, gemini_research    │            │   │
            │   │  │  6.9 MB total              │    │  (NOT in this monorepo)    │            │   │
            │   │  └────────────────────────────┘    └────────────────────────────┘            │   │
            │   └────────────────────────────────────────────────────────────────────────────────┘   │
            │                                                                                        │
            │       web/  apps/{oideachais-web, tuatha-ui, croilar-web, croilar-portal, …}/         │
            │             + hono-api/                                                               │
            └────────────────────────────────────────────────────────────────────────────────────────┘
                                                                                                        ┌────────────────────────────────────────────────────────────────────────────────────────┐
            ┌────────────────────────────────────────────────────────────────────────────────────────┐   │
            │  LLM GATEWAY  (LiteLLM, http://litellm:4000/v1)                                       │   │
            │  default_model = "minimax" alias  →  7-tier fallback                                    │   │
            │  opencode-go/minimax-m3-slot{0,1,2} → qwen3.7-max → kimi-k2.6 → glm-4.6 → local/math  │   │
            └────────────────────────────────────────────────────────────────────────────────────────┘   │
                                                                                                        │
            ┌────────────────────────────────────────────────────────────────────────────────────────┐   │
            │  3-TIER HOST TOPOLOGY                                                                 │   │
            │                                                                                        │   │
            │  arm1-oci     Oracle Ampere A1, 4 OCPU, 24 GB   →  Pangolin + Komodo + Garage S3      │   │
            │  cax41-hetzner Hetzner CAX41 ARM, 16 vCPU, 32 GB  →  Memgraph + FalkorDB + MLflow   │   │
            │  bunchloch    MacBook M4 Max, 14c, 48 GB         →  llama-swap + mlx-omni + Bria FIBO │   │
            └────────────────────────────────────────────────────────────────────────────────────────┘   │
                                                                                                        │
            ┌────────────────────────────────────────────────────────────────────────────────────────┐   │
            │  LAKEHOUSE DATA PLANE                                                                 │   │
            │  DLT  →  DuckLake (Parquet on Garage S3 + Postgres catalog)                           │   │
            │              ↓                                                                       │   │
            │  BAML  →  CocoIndex v1  →  LanceDB (BGE-M3, HNSW)                                    │   │
            │              ↓                                                                       │   │
            │  Cognee  →  FalkorDB (GraphRAG) + Graphiti (bi-temporal episodes)                     │   │
            │              ↓                                                                       │   │
            │  MotherDuck (md:oideachais)  →  marimo dashboards  +  AG-UI agents                    │   │
            └────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## The v4 consolidation (2026-06-28)

The five original **sruthanna** (`oideachais`, `meaisinfhoghlaim`, `tuatha`,
`croilar`, `crypteolas`) — plus the **browser** core module and the
**codeolas** C++ sub-package — were consolidated into a single Python
package, `cianfhoghlaim/`. The work was tracked in the openspec change
[`2026-06-28-consolidate-sruth-into-cianfhoghlaim-v4`](openspec/changes/archive/)
and shipped as commit
`4bc20fd12 chore(v4): consolidate 5 sruth quadrants + browser + leabharlann into cianfhoghlaim`.

**Key outcomes:**

- **Single Python package** `cianfhoghlaim/` (with `libraries/codeolas/` as
  a publishable sub-package) instead of 5 sruthanna + a separate browser
  module.
- **Single Dagster code-location** at
  `cianfhoghlaim/dagster/definitions.py` with 228+ assets across 21
  groups (5 layered stages: `1_ingestion` through `5_agent_ops`).
- **60+ BAML source files** reorganised into a 3-cluster taxonomy
  (`education/`, `celtic/`, `processing/`) with `_shared/` homes
  per cluster.
- **CocoIndex v4 OCR-aware flows** (`ocr_aware_flow` +
  `leabharlann_flow`).
- **24 OCR models** in a single registry at `meaisinfhoghlaim/models/`.

The five subagent definitions in `opencode.json` were **rewritten** to
align with the v4 layout — see the
[`2026-06-28-rewrite-subagent-foundation-for-cianfhoghlaim-consolidation`](openspec/changes/2026-06-28-rewrite-subagent-foundation-for-cianfhoghlaim-consolidation/proposal.md)
openspec change.

The GitOps foundation (`infrastructure/`) and the digital library
(`leabharlann/`) were **split into their own repositories** so each
domain has an independent release cadence, secrets boundary, and review
surface. The 3.4 GB PDF corpus in leabharlann is too large to embed
as a `git subtree` (it would inflate every push to 3 GB), so the
sibling repos are exposed in this monorepo as **git worktrees at the
root of the workspace** — `./bonneagar/` and `./leabharlann/` — for
editing and inspection. The original openspec change
[`2026-06-28-split-leabharlann-bonneagar`](openspec/changes/2026-06-28-split-leabharlann-bonneagar/proposal.md)
is being **amended** to reflect the worktree approach instead of
the subtree approach.

---

## What you can deploy today

An honest, prioritised list of the working features and the work that
is still needed before each tier is "done".

### Tier 1 — production-ready (5 services)

| Service | What it does | Stack | Where |
|:--|:--|:--|:--|
| **LiteLLM gateway** | OpenAI-compatible proxy; `minimax` 7-tier fallback alias | LiteLLM | `./bonneagar/stacks/litellm/` (port 4000) |
| **Lakehouse** | Garage S3 + Lakekeeper (Iceberg REST) + Postgres catalog | Garage, Lakekeeper, Postgres | `./bonneagar/stacks/lakehouse/` (ports 3900-3904, 5433, 8181-8182) |
| **Cognee** | Knowledge-graph cognify over 6 typed datasets (aistear, primary, junior_cycle, senior_cycle, tertiary, cross_stage) | Cognee | `./bonneagar/stacks/cognee/` (port 8100) |
| **Dagster UI** | Single code-location, 228+ assets, 5 layered stages | Dagster | `mise run dagster:oideachais` (port 3000) |
| **OpenChamber** | OpenCode web/desktop UI; multi-agent parallel runs, branchable chat timelines, worktree isolation | OpenChamber | `./bonneagar/stacks/openchamber/` (port 3000, deployed to `openchamber.cianfhoghlaim.ie`) |

### Tier 2 — functional, needs polish (4 services)

| Service | What it does | Stack | Where |
|:--|:--|:--|:--|
| **Graphiti** | Bi-temporal knowledge-graph episodes; Neo4j backend | Graphiti + Neo4j | `./bonneagar/stacks/graphiti/` |
| **FalkorDB** | Vector + graph hybrid for GraphRAG | FalkorDB | `./bonneagar/stacks/falkordb/` |
| **Dragonfly** | In-memory store for agent state | Dragonfly | `./bonneagar/stacks/dragonfly/` |
| **RisingWave** | Streaming SQL for change-data-capture | RisingWave | `./bonneagar/stacks/risingwave/` |

### Tier 3 — works on `bunchloch` only, not yet on `arm1-oci`

- **DLT ingestion** — 200+ sources under `cianfhoghlaim/dlt/`
  (8 nations × 4 domains in `british_isles/` + 6 special source
  clusters: `filesystem/`, `api_sources/`, `language/`, `common/`,
  `official_media/`, `portfolio/`) + `USE_LOCAL_SCRAPES` cache for
  offline development. Needs the `oideachais-pipeline` openspec
  change to wire the full live-source sweep.
- **BAML extraction** — 60+ consolidated BAML files in a 3-cluster
  taxonomy (`education/`, `celtic/`, `processing/`), 2 named clients
  (`LitellmClient` + `Extractor` + `LlamaSwapClient`), all routing
  through LiteLLM `minimax`.
- **CocoIndex v1** — 14+ v1 Apps (`leabharlann_embedding`,
  `codebase_indexing`, `docs_skills_consolidation`, `unified_embedding`,
  plus 8 per-subject embeddings) with BGE-M3 embeddings mounted to
  LanceDB HNSW.
- **OCR registry** — 24 OCR models (9 vision + 4 classical + 3
  image-gen + 8 alignment) at `meaisinfhoghlaim/`.
- **The 12-agent fleet** at
  `cianfhoghlaim/agents/meaisinfhoghlaim/agents/`
  (curriculum, translation, corpus, research, geospatial, voice,
  statistics, education-research, bunchloch-research, AG-UI
  curriculum, MCP curriculum, enhanced orchestrator, root).
- **Web surfaces** — `oideachais-web` (TanStack Start, the largest),
  `tuatha-ui` (Babylon.js), `croilar-web` (multi-persona),
  `croilar-portal` (admin).
- **Observability** — Langfuse (remote MCP), MLflow, RAGAS, Logfire.
- **PDF processing pipeline** — 8-asset pattern in
  `dagster/assets/by_domain/pdf_processing.py` processes 133 PDFs
  through 5 converters + 24 OCR models + BAML + CocoIndex + Cognee
  + RAGAS.

### Tier 4 — early / experimental

- **Crypteolas** — Rust + SpacetimeDB backend for the Tuatha MMO; agent
  fleet needs to land on the `oideachais-agent-services` openspec change.
- **HuggingFace Spaces** — `an_scrudu` (Irish Leaving Cert tutor),
  `meaisin_cliste` (Celtic AI playground), `anam_tuatha` (Tuatha MMO
  teaser).
- **Spaces (anti-phish, data-engineering)** — local-only, not yet
  deployed.

### How to boot Tier 1

```bash
# Tier 1 (in order)
cd ./bonneagar/stacks/lakehouse  && ./scripts/stack.sh up -d
cd ../litellm                        && ./scripts/stack.sh up -d
cd ../cognee                         && ./scripts/stack.sh up -d
cd ../../../                          # back to monorepo root
mise run dagster:oideachais           # → http://localhost:3000
```

The full end-to-end runbook is at
[`docs/PHASE_0.3_DEPLOY_RUNBOOK.md`](docs/PHASE_0.3_DEPLOY_RUNBOOK.md).

---

## Key packages

The post-v4 `cianfhoghlaim/` package is organised so that **each
directory has a single, obvious purpose**. Read this section once and
you'll know where to add the next thing.

### `cianfhoghlaim/baml/` — 60+ BAML files in 3-cluster taxonomy

The 3-cluster BAML taxonomy (per the `baml-reorganize-by-cluster`
change) is the canonical shape:

```
baml/
├── clients.baml                      # canonical LLM clients
├── clients_llama_swap.baml           # specialty VL clients
├── shared/                            # generated client output (baml_client/, baml_client_ts/)
├── education/                         # CLUSTER 1 — NCCA education
│   ├── _shared/                       #   education_level, strand_outcome,
│   │                                  #   curriculum_relationships, subject_rubric,
│   │                                  #   document_metadata
│   ├── stages/                        #   5 NCCA stages (aistear, primary,
│   │                                  #   junior_cycle, senior_cycle, tertiary)
│   ├── pdfs/                          #   3 leaving_cert_*_extraction.baml
│   ├── subjects/                      #   8 qpack_*.baml (per-NCCA-subject)
│   ├── cross_nation/                  #   isles_education + multi_nation_curriculum
│   ├── statistics/                    #   education_statistics
│   └── university/                    #   university_extraction
├── celtic/                            # CLUSTER 2 — Celtic / Irish language
└── processing/                        # CLUSTER 3 — Generic file processing
```

### `cianfhoghlaim/dlt/` — 200+ sources in 8 top-level dirs

The 8 top-level dirs (per the recent reorg):

```
dlt/
├── api_sources/                       # REST API (github, linkedin, researchgate, soundcloud, spotify)
├── british_isles/                     # 8 nations × 4 domains (32 sources)
│   ├── england/  ireland/  scotland/  wales/  northern_ireland/  isle_of_man/  jersey/  guernsey/
├── common/                            # helpers (batching, firecrawl_source, destinations, ...)
├── filesystem/                        # personal corpus (books, zotero, takeout, CV)
├── language/                          # Celtic/Irish sources (canuint, duchas, tearma, gaeilge)
├── official_media/                    # Instagram → British-Isles gov source resolver
└── portfolio/                         # artwork, CV, labels, teaching
```

### `cianfhoghlaim/cocoindex/` — 14+ v1 Apps

The 14+ v1 CocoIndex Apps (per the `oideachais-cocoindex-v1` skill):

- 4 v1 Apps: `codebase_indexing`, `api_indexing`, `filesystem_indexing`,
  `config_indexing`, `storage_indexing`
- 8 per-subject embeddings: `gaeilge_embedding`, `english_embedding`,
  `mathematics_embedding`, `applied_mathematics_embedding`,
  `chemistry_embedding`, `computer_science_embedding`,
  `geography_embedding`, `history_embedding`
- 2 leabharlann: `leabharlann_embedding`, `leabharlann_flow`
- 3 content: `culture_heritage_embedding`, `unified_embedding`,
  `docs_skills_consolidation`
- 2 utilities: `file_graph`, `languages`

All follow the canonical v1 pattern: `@coco.fn` + `@coco.lifespan`
+ `lancedb.mount_table_target` + `Annotated[NDArray, EMBEDDER]`. The
shared `LANCE_DB` + `EMBEDDER` + `RESOLVED_FILE_REGISTRY` live in
`_lifespan.py` per the 4-rule v1 conformance contract (R1-R4).

### `cianfhoghlaim/dagster/` — single code-location, 228+ assets

The 5 layered stages:

```
dagster/
├── definitions.py                  # entry point
├── defs/
│   ├── 1_ingestion/                # 6 domains: curriculum, filesystem, law,
│   │                              #   medicine, site_analysis
│   ├── 2_materials/                # baml_extraction, dbt, embedding_pivot,
│   │                              #   ocr_comparison, pdf_processing
│   ├── 3_model_lifecycle/          # cocoindex_v1, cognify, cross_archive
│   ├── 4_asset_generation/         # marimo_dashboards, orpc_routes, tanstack_pages
│   └── 5_agent_ops/                # adk, agno, custom
├── components/                     # 3 layer files (CelticIngestionComponent, etc.)
├── defs.yaml                       # workspace config
├── partitions_v2.py                # 9+ partition types
├── resources.py                    # 8+ Dagster resources
└── sensors/                        # 16+ dagster sensors
```

Plus `dagster/assets/` for the 11 per-subject asset groups
(mathematics, english, gaeilge, applied_mathematics, chemistry,
computer_science, biology, business, french, geography, history) +
the 8-asset PDF processing pipeline in `dagster/assets/by_domain/`.

### `cianfhoghlaim/meaisinfhoghlaim/` — 15+ subdirs, 24 OCR models

The OCR + model lifecycle home:

```
meaisinfhoghlaim/
├── models/                  # 24 OCR models (9 vision + 4 classical + 3 image-gen + 8 alignment)
├── backends/                # adapters, author_archive_ocr, gaelic_metrics
├── alignment/               # sentence-level Irish↔English aligner, ColPali visual aligner
├── document_factory/        # exam paper → structured document (5 converters)
│   └── converters/           #   deepseekocr, docling, marker, pymupdf4llm, unstructured
├── evaluation/              # OCR + RAGAS evaluation harness
├── quality/                 # OCR quality scoring (canuint_validator, content_quality)
├── training/                # OCR model training pipelines (modal_finetune)
├── datasets/                # irish_htr_dataset, line_segmentation
├── process/                 # 7 meaisinfhoghlaim pipelines (canuint_audio_slicer, dialect_classifier, etc.)
├── config/                  # BaseSettings + YAML configs
├── ci/                      # HF watchdog
├── cli.py                   # meaisinfhoghlaim CLI entrypoint
└── federated/               # (empty for now)
```

### `cianfhoghlaim/agents/` — 12-agent fleet

The 12-agent fleet is flattened from the v3 `_underscore` legacy
dirs. The sub-packages:

```
agents/
├── adk/                  # Google ADK integration (the original 12-agent fleet home)
├── agno/                 # Agno framework integration (recently added)
├── api/                  # FastAPI/Hono API surface
├── tuatha/               # Babylon.js + SpacetimeDB + crypteolas crypto platform
├── mcp_server/           # MCP server glue
├── root.py               # Orchestrator
├── ocr/                  # Image generation and processing
├── language/             # Language-specific agent adapters
├── shared/               # Shared agent utilities
├── image_pipeline/       # (legacy)
└── amam_tuatha.py        # Tuatha MMO teaser agent
```

The 12 agents (per `agents/adk/root_agent.py`): `root_agent` (the
orchestrator), `curriculum_agent`, `translation_agent`, `corpus_agent`,
`research_agent`, `geospatial_agent`, `voice_agent`, `statistics_agent`,
`education_research_agent`, `bunchloch_research_agent`, `agui_curriculum_agent`,
`mcp_curriculum_agent`, plus `enhanced_orchestrator`.

### `cianfhoghlaim/storage/` — 4-layer multi-graph architecture

```
storage/
├── _shared/                          # generic multi-graph abstraction
│   ├── falkordb.py                   #   generic GraphClient interface
│   ├── memgraph.py                   #   Memgraph implementation
│   ├── neo4j.py                      #   Neo4j implementation
│   └── interface.py                  #   GraphClient ABC
├── cache.py                          # unified hot-path cache (uses falkordb)
├── graphiti_client.py                # graphiti_core wrapper (bi-temporal)
├── falkordb_client.py                # FalkorDB cache wrapper (used by cache.py)
├── memgraph_client.py                # Memgraph curriculum graph (used by dagster/resources.py)
├── temporal_client.py                # graphiti_core wrapper
├── lancedb.py                        # vector DB + HNSW indexing
├── cognify/                          # the Cognee cognify layer
│   ├── cognee_integration/            #   7 cognify asset wrappers
│   └── rules/                        #   4 cross-corpus edge rules
├── letta_memory.py                   # agent memory
├── lightrag_curriculum.py            # LightRAG + Cognee hybrid
├── cognee_config.py
├── cognee_service.py
└── research.py
```

The top-level `falkordb_client.py` and `memgraph_client.py` are
**complementary** to the `_shared/` layer (not duplicates). They serve
the cache + Dagster-resource layers respectively. The `temporal.py`
file (hand-rolled Graphiti-in-Python) is superseded by `temporal_client.py`
(graphiti_core wrapper).

### `cianfhoghlaim/web/` — 7 web apps + 1 Hono API

| App | Stack | What it is |
|:--|:--|:--|
| `apps/oideachais-web/` | TanStack Start | The public Celtic education data platform (the largest) |
| `apps/tuatha-ui/` | Babylon.js | The Tuatha educational MMO front-end |
| `apps/croilar-web/` | TanStack Start | The Croílár multi-persona portfolio (public site) |
| `apps/croilar-portal/` | TanStack Start | The Croílár portfolio dashboard (admin) |
| `apps/game_showcase/` | React | Web game showcase |
| `apps/tuatha-demo/` | Babylon.js | Tuatha Babylon.js demo |
| `hono-api/` | Hono | The Hono API gateway (backend) |

The 5-web-app → 1-`cio-web` consolidation plan is in
[`docs/audit/web-app-consolidation-plan.md`](docs/audit/web-app-consolidation-plan.md).

### `cianfhoghlaim/notebooks/` — 29+ marimo notebooks

See **"Notebooks and demos"** above for the full breakdown.

### `cianfhoghlaim/libraries/codeolas/` — publishable sub-package

A C++ + WASM + MCP code-analysis library: semantic search, AST
knowledge graph, MCP server. The publishable wheel name is **`codeolas`**.

### `./bonneagar/` (worktree) — 90 compose stacks

The canonical 90-stack catalogue lives in
[`./bonneagar/stacks/`](./bonneagar/stacks/). The 4 priority stacks
are `oideachais`, `litellm`, `langfuse`, and `lakehouse`; see
[`./bonneagar/AGENTS.md`](./bonneagar/AGENTS.md) for the full
inventory. 90 stacks × ~10 KB each = 6.9 MB total, all in the
sibling repo (not in this monorepo).

#### The bonneagar directory tree (canonical 10-subdir layout)

```
bonneagar/
├── AGENTS.md                   # bonneagar quick reference
├── GOLD_STANDARD.md            # the 6-file stack pattern (compose + sidecar + secrets + pangolin + blueprint + .env.example)
├── DEPLOYMENT-STRATEGY.md      # 3-tier host topology + roll-out sequence
├── PANGOLIN-SETUP.md           # Pangolin private-resources setup (the 6-label pattern)
├── package.json                # bun workspace + scripts
├── bun.lock
├── ansible/                    # legacy IaC + playbooks
├── ci/                         # CI scripts
├── dagger/                     # 8-step GitOps pipeline (the `infrastructure/dagger/` README)
├── deploy-runbooks/            # per-stack deploy runbooks
├── docs/                       # bonneagar internal docs
├── firecrawl/                  # self-hosted Firecrawl instance configs
├── iac/                        # Pulumi IaC (3-tier host topology: arm1-oci / cax41-hetzner / bunchloch)
├── infisical_secret/           # the 3-way secrets contract (source-of-truth → template → hydrated runtime)
├── komodo/                     # deploy procedures for every stack (one .toml per stack)
├── legacy/                     # retired IaC artefacts
├── observability/              # shared Grafana / Loki / Prom / OTel configs
├── pangolin/                   # Pangolin private-resources + 6-label pattern
└── audit/                      # security + compliance + drift audits
```

The 6-file GOLD_STANDARD pattern is the contract every new stack must
follow. See `./bonneagar/GOLD_STANDARD.md` for the full spec; in short,
a new stack `infrastructure/stacks/<name>/` must contain:

1. `compose.yaml` — the Docker Compose service definition
2. `sidecar.yaml` — the Locket / Infisical sidecar that injects secrets at runtime
3. `secrets.env` — the secret *names* (never the values)
4. `pangolin.yaml` — the 6-label private-resources shape
   (`pangolin.private-resources.<name>.*`)
5. `blueprint.yaml` — the Komodo procedure that deploys the stack
6. `.env.example` — the developer-onboarding template

Adding a new stack is then a 4-step `bun run` sequence; the
`stack-doctor.sh` validation script enforces the pattern.

### `./leabharlann/` (worktree) — 2,400 files, 3.4 GB

```
leabharlann/
├── gaeilge/                    # 38+ Irish-language PDFs
├── mata/                       # 27+ mathematics textbooks
├── aigne/                      # 72+ cognitive science / mind books
├── ollscoil_na_gaillimhe/      # 21+ University of Galway coursework archives
├── zotero/                     # 34+ research papers (Zotero export)
└── gemini_deep_research/       # 24+ long-form Gemini deep research reports
                              # (culture/ medical/ politics/ — the corpus cited in the
                              #  cianfhoghlaim plan throughout the British Isles)
```

The 2,400 files / 3.4 GB corpus lives entirely in the sibling
`leabharlann` repo and is exposed here as a worktree. To use the
corpus from the monorepo, reference it through the relative path
`./leabharlann/...` (or symlink it into a working location).

#### The leabharlann directory tree (canonical 6-subdir layout)

| Subdir | Contents | Used by |
|:--|:--|:--|
| `gaeilge/` | 38+ Irish-language PDFs (curriculum, dictionaries, grammar) | the `oideachais_gaeilge` CocoIndex v1 App; the `ExtractEn` BAML function; the marimo notebook at `cianfhoghlaim/notebooks/dashboards/gaeilge.py` |
| `mata/` | 27+ mathematics textbooks (algebra, calculus, statistics, applied maths) | the `oideachais_mata` CocoIndex v1 App; the `ExtractEn` BAML function; the marimo notebook at `cianfhoghlaim/notebooks/dashboards/mata.py` |
| `aigne/` | 72+ cognitive science / mind books (neuroscience, psychology, linguistics) | the `oideachais_aigne` CocoIndex v1 App; the `meaisinfhoghlaim_aigne` cognify pass |
| `ollscoil_na_gaillimhe/` | 21+ University of Galway coursework archives (transcripts, parchments, teaching portfolio, Irish-language exam results, the 5 mat / 5 education / 5 software-dev / 3 irish / 3 past evidence folders) | the README's "On the verified qualifications" section; the `leabharlann_full_stack_demo` Dagster asset group |
| `zotero/` | 34+ research papers (Zotero export with full text + metadata) | the `leabharlann_zotero` CocoIndex v1 App; the `leabharlann_zotero_embedding` LanceDB index |
| `gemini_deep_research/` | 24+ long-form Gemini deep research reports across `culture/`, `medical/`, `politics/` — the corpus that grounds the cianfhoghlaim plan throughout the British Isles | the `culture_extraction.baml:ExtractCultureClaims` BAML function; the `culture_heritage` Cognee dataset; the §20 and §21d/f of the README |

The 8 PDF clippings in
`./leabharlann/../cian_mac_an_déisigh_uí_liatháin/identity/lineage/references/clippings/`
(Uí Liatháin, Delbhna Tír Dhá Locha, Eamonn Deacy Park, Leath Cuinn
and Leath Moga, Cian, Aos Sí, Tuatha Dé Danann, Déisi) are the
canonical Wikipedia dual-write corpus for the §21c heritage section
of the README; their SHA-256 is recorded in the 8 DLT fixtures at
`cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/official_media/fixtures/identity_*.json`
(see the `Wikipedia fixture storage convention` Requirement in
`openspec/specs/cross-domain-registry/spec.md` for the
drift-detector invariant).

#### Why two sibling repos, not subtrees

The `leabharlann` corpus (3.4 GB of PDFs) and the `bonneagar` IaC +
compose-stack catalogue (6.9 MB across 90 stacks) are too large to
commit to the application monorepo's git history. Embedding them as
`git subtree`s would make every `git push` upload 3 GB of binary
data, slow CI to a crawl, and bloat clone size for every contributor.
The worktree approach keeps the content *visible and editable* from
this workspace without committing it to this repo. See
[Why worktrees, not subtrees?](#why-worktrees-not-subtrees) above
for the full rationale.

### `spaces/` — HuggingFace Spaces

HuggingFace Spaces published from this monorepo (deploy with the
reusable workflow at `.github/workflows/spaces-sync.yml`):

| Space | Stack | Domain |
|:--|:--|:--|
| `an_scrudu` | Gradio + Gemma-3 | Irish Leaving Cert tutor |
| `meaisin_cliste` | Gradio + BAML + LiteLLM | Celtic AI playground |
| `cianfhoghlaim` | Static SDK landing | Project landing |
| `anam_tuatha` | Static SDK + Babylon.js | Tuatha MMO teaser |

---

## The pipelines — what cianfhoghlaim can do

The post-v4 cianfhoghlaim monorepo is organised around 5 sequential
pipelines that take a corpus (PDFs, DOCX, EPUBs, Zotero exports,
Google Takeout, UoG coursework, exam papers) from raw disk all the
way through to a queryable, agent-consumable, semantically-indexed
artifact. This section walks each pipeline with the exact Python
files, Dagster asset names, BAML function names, and entry-point
commands. The next section ([5 cookbook recipes](#5-cookbook-recipes))
turns the same map into worked end-to-end examples.

### Stage 1 — Ingestion (`dagster/defs/1_ingestion/`)

**Purpose.** Pull a corpus (PDFs, DOCX, EPUBs, Zotero exports, Google
Takeout, UoG coursework, exam papers, marking schemes, syllabi) into
the Lakehouse (DuckLake: Parquet on Garage S3 + Postgres catalog). The
DLT sources are domain- and nation-aligned: the **8 British Isles
nations** (england, ireland, scotland, wales, northern_ireland,
isle_of_man, jersey, guernsey) × 4 canonical domains (education, law,
medicine, statistics) = **32 sources**; plus 6 special clusters
(filesystem, api_sources, language, official_media, portfolio, common)
adding **24+ sources**.

| Field | What it contains |
|:--|:--|
| Source files | `cianfhoghlaim/dlt/british_isles/{nation}/{domain}/{source}.py` (the 32 per-nation DLT sources); `cianfhoghlaim/dlt/filesystem/` (8 leabharlann sources); `cianfhoghlaim/dlt/api_sources/` (3 REST APIs); `cianfhoghlaim/dlt/language/` (25 Celtic sources); `cianfhoghlaim/dlt/official_media/` (9 Instagram sources); `cianfhoghlaim/dlt/portfolio/` (7 portfolio sources) |
| Asset names | `leabharlann_full_stack_demo` (asset group), `leabharlann_books`, `leabharlann_zotero`, `leabharlann_takeout`, `leabharlann_uog_coursework`, `ireland_primary_jc_*`, `ireland_leaving_cert_*`, `gemini_deep_research_culture`, `gemini_deep_research_medical`, `gemini_deep_research_politics` |
| BAML functions | n/a (this stage is DLT-only) |
| Command | `mise run dagster:oideachais` → open http://localhost:3000 → materialise the asset group. **Or** `USE_LOCAL_SCRAPES=true uv run python -m cianfhoghlaim.pipelines.ingest._oideachais_dlt_sources.official_media` to run a single DLT source offline against the `stedding/ingest_queue/` cache. |
| What you can do with it | Drop a new PDF in `leabharlann/gemini_deep_research/culture/` and it lands in `lakehouse.leabharlann_books` (and the `gemini_deep_research_culture` asset materialises) within the next materialisation. The `USE_LOCAL_SCRAPES=true` env var routes through the offline cache at `stedding/ingest_queue/` so that the scrape never goes live without an explicit decision. |

### Stage 2 — Extraction (`dagster/defs/2_materials/baml_extraction/`)

**Purpose.** Extract structured claims from the ingested corpus. The
**60+ BAML files in the 3-cluster taxonomy** (`baml/education/`,
`baml/celtic/`, `baml/processing/`) all route through the LiteLLM
`minimax` 7-tier fallback alias.

| Field | What it contains |
|:--|:--|
| Source files | `cianfhoghlaim/baml/education/stages/{aistear,primary,junior_cycle,senior_cycle,tertiary}.baml` (the 5 NCCA stage BAML); `cianfhoghlaim/baml/education/subjects/qpack_*.baml` (the 8 per-NCCA-subject quest-pack BAMLs); `cianfhoghlaim/baml/education/pdfs/leaving_cert_{syllabus,past_paper,marking_scheme}.baml` (the 3 PDF extraction BAMLs); the canonical BAML clients at `cianfhoghlaim/baml/clients.baml` (LitellmClient, Extractor) and `cianfhoghlaim/baml/clients_llama_swap.baml` (LlamaSwapClient); the BAML runtime at `cianfhoghlaim/baml/shared/baml_client/` (regenerated by `baml-cli generate`) |
| Asset names | `culture_heritage_extract`, `ireland_primary_jc_extract`, `ireland_leaving_cert_extract`, `official_media_extract`, `university_deep_extract` |
| BAML functions | `ExtractCultureClaims` (the `CultureHeritageClaim` Pydantic schema: lineage / region / canonical citation / claim type / confidence), `ExtractEn` (general), `ExtractEnStrong` (high-precision), `LocalVision` (vision), plus 6 domain-specific Extract functions |
| Command | `mise run baml:generate` to regenerate `baml_client/` after any `.baml` edit; then `mise run dagster:oideachais` → materialise the `culture_heritage_extract` asset. The `low_confidence_review` Dagster asset_check flags any extraction with `confidence < 0.7` for human review. |
| What you can do with it | Extract a structured `CultureHeritageClaim` record from a 15-page Gemini Deep Research PDF in ~3 seconds via LiteLLM; the BAML schema enforces that the `canonical_citation` field references a Wikipedia article, the `region` field is one of the 4 provinces, and the `confidence` is a 0.0-1.0 float. The 60+ source files in `baml/education/`, `baml/celtic/`, `baml/processing/` map to per-domain BAML extraction functions. |

### Stage 3 — Embedding (`dagster/defs/3_model_lifecycle/cocoindex_v1/`)

**Purpose.** Embed the BAML-extracted chunks into LanceDB (BGE-M3
+ BGE-large-en-v1.5) for semantic search. The **14+ v1 CocoIndex Apps**
each follow the canonical v1 App pattern: `@coco.fn` flow +
`@coco.lifespan` runtime + `lancedb.mount_table_target` +
`Annotated[NDArray, EMBEDDER]` typing. The canonical shared home for
`LANCE_DB` + `EMBEDDER` + `RESOLVED_FILE_REGISTRY` is `_lifespan.py` per
the 4-rule v1 conformance contract (R1-R4) enforced by the
`cocoindex_v1_conformance` App.

| Field | What it contains |
|:--|:--|
| Source files | `cianfhoghlaim/cocoindex/leabharlann_embedding.py` (the 3 leabharlann v1 Apps), `…/culture_heritage_embedding.py` (the 12th v1 App), `…/_lifespan.py` (the shared runtime), `…/unified_embedding.py` (the 4th App), plus 8 per-subject embeddings (`gaeilge_embedding.py`, `english_embedding.py`, `mathematics_embedding.py`, etc.) |
| Asset names | `leabharlann_books_embedding`, `leabharlann_zotero_embedding`, `leabharlann_takeout_embedding`, `culture_heritage_embedding`, `unified_embedding` |
| BAML functions | n/a (this stage is CocoIndex v1, not BAML). The embed stage consumes the BAML-extracted chunks from Stage 2 as `coco.datatypes.Sentence` records. |
| Command | `mise run cocoindex:dev` to run all 14+ v1 Apps locally; or materialise the `*_embedding` assets in Dagster. |
| What you can do with it | Query the semantic-search index across the 5 leabharlann corpora + the 6 oideachais domains + the 8 NCCA LC subjects in one LanceDB namespace. The 4-rule v1 conformance contract (R1-R4) is enforced by the `cocoindex_v1_conformance` App — see `.agents/skills/oideachais-cocoindex-v1/SKILL.md` for the canonical pattern. |

### Stage 4 — Cognify (`dagster/defs/3_model_lifecycle/cognify/`)

**Purpose.** Build the knowledge graph over the 6 typed Cognee
datasets (`aistear`, `primary`, `junior_cycle`, `senior_cycle`,
`tertiary`, `cross_stage`) plus the 3 leabharlann cognify passes
(`leabharlann_books_cognify`, `leabharlann_zotero_cognify`,
`leabharlann_takeout_cognify`) plus the 3 cross-archive edge rules
(`leabharlann_cross_archive`, `oideachais_cross_archive`,
`culture_cross_archive`). The cognify stage emits cross-dataset
edges to FalkorDB (for GraphRAG), to Graphiti (for bi-temporal
episodes), and to LanceDB (for unified vector retrieval).

| Field | What it contains |
|:--|:--|
| Source files | `cianfhoghlaim/storage/cognify/cognee_integration/_oideachais_main.py` (the orchestrator), `…/_oideachais_cognee_pipeline.py` (the per-dataset cognify), `…/rules/leabharlann_cross_archive.py` (the 3 edge rules), `…/rules/culture_cross_archive.py`, `…/rules/oideachais_cross_archive.py`, `…/leabharlann_cognify.py` (the 3 leabharlann cognify passes) |
| Asset names | `cognify_aistear`, `cognify_primary`, `cognify_junior_cycle`, `cognify_senior_cycle`, `cognify_tertiary`, `cognify_cross_stage`, `leabharlann_books_cognify`, `leabharlann_zotero_cognify`, `leabharlann_takeout_cognify` |
| BAML functions | n/a (Cognee does the LLM-driven entity extraction; BAML is upstream) |
| Command | `mise run cognee:cognify --dataset <name>` (or via the Dagster `cognify_*` assets). The Cognee server is reachable at `http://localhost:8100` after `cd ./bonneagar/stacks/cognee && ./scripts/stack.sh up -d`. |
| What you can do with it | Run `cognify` over the entire `culture_heritage` Cognee dataset and the 8 Wikipedia clippings at `cian_mac_an_déisigh_uí_liatháin/identity/lineage/references/clippings/` will appear as GraphRAG-queryable entities in the next 30 seconds, with cross-dataset edges to the `oideachais_heritage` and `leabharlann_heritage` datasets. |

### Stage 5 — Asset Generation (`dagster/defs/4_asset_generation/`)

**Purpose.** Expose the lakehouse + graph + embeddings to the 7 web
apps, 29+ marimo notebooks, 11 HuggingFace Spaces, and 12-agent fleet.
The asset-generation stage is the read-side mirror of the
ingest+process chain: MotherDuck (`md:oideachais`) for zero-ops
managed reads, TanStack Start for the 5 web apps (the largest is
`oideachais-web`), Babylon.js for the Tuatha MMO front-end, marimo for
the 29+ reactive notebooks at `cianfhoghlaim/notebooks/`.

| Field | What it contains |
|:--|:--|
| Source files | `cianfhoghlaim/pipelines/distribute/_oideachais_storage_targets.py` (the read-target registry), the 5 `*_to_*` Dagster assets (`parquet_to_motherduck`, `lancedb_to_marimo`, `falkordb_to_agent`, `cognee_to_web`, `lancedb_to_space`), the 7 web apps at `cianfhoghlaim/web/apps/`, the 1 Hono API at `cianfhoghlaim/web/hono-api/`, the 29+ marimo notebooks at `cianfhoghlaim/notebooks/dashboards/` |
| Asset names | `parquet_to_motherduck`, `lancedb_to_marimo`, `falkordb_to_agent`, `cognee_to_web`, `lancedb_to_space` |
| BAML functions | n/a (the asset-generation stage is read-only) |
| Command | `mise run turbo dev` boots the full local stack (lakehouse + litellm + llama-swap + mlx-omni + the 7 web apps + the 29+ marimo notebooks). Then open http://localhost:3000 for Dagster, http://localhost:8100 for Cognee, http://localhost:4000/v1 for LiteLLM, http://localhost:3001 for oideachais-web. |
| What you can do with it | Run `mise run turbo dev` and the entire ingestion-to-asset-generation chain is live on `bunchloch` (the MacBook M4 Max). A new PDF lands in the lakehouse via DLT, gets BAML-extracted, gets CocoIndex-embedded, gets Cognee-cognified, and is queryable in the marimo notebook + the oideachais-web TanStack Start app within the next materialisation. |

---

## 5 cookbook recipes

The 5-stage pipeline is the architecture. The 5 recipes are the
worked examples — each one is a 3-4 step "do this, then this, then
this" that takes you from a blank terminal to a concrete result.

### Recipe 1 — Ingest a new Gaeltacht PDF

```bash
# 1. Drop the PDF in the leabharlann corpus
cp my-gaeltacht-paper.pdf leabharlann/gemini_deep_research/culture/

# 2. Update the DLT source YAML to point at the new file
#    (edits: cianfhoghlaim/dlt/british_isles/ie/culture/gemini_deep_research.yaml)
$EDITOR cianfhoghlaim/dlt/british_isles/ie/culture/gemini_deep_research.yaml
#   append to the ie.culture.* asset keys:
#     - asset_key: ie.culture.my_gaeltacht_paper
#       kind: filesystem_pdf
#       path: leabharlann/gemini_deep_research/culture/my-gaeltacht-paper.pdf

# 3. Materialise the Dagster asset group
mise run dagster:oideachais            # http://localhost:3000
#    → asset group: gemini_deep_research
#    → click Materialize All

# 4. Verify the landing
uv run python -c "import duckdb; print(duckdb.sql('SELECT count(*) FROM lakehouse.leabharlann_books').fetchone())"
# Expected: count goes up by 1
```

### Recipe 2 — Add a new BAML extraction field

```bash
# 1. Edit the BAML schema
$EDITOR cianfhoghlaim/baml/processing/culture_extraction.baml
#   add a new field to the CultureHeritageClaim class:
#     field claim_confidence: float  # 0.0 = low, 1.0 = high

# 2. Regenerate the BAML Python client
mise run baml:generate

# 3. Re-materialise the extraction asset
mise run dagster:oideachais
#    → asset: culture_heritage_extract
#    → click Materialize
#    → the new field appears in the next extraction run

# 4. Validate
uv run python -c "from baml_client import b; print(b.ExtractCultureClaims.__fields__)"
# Expected: 'claim_confidence' is in the field list
```

### Recipe 3 — Run a cognify pass

```bash
# 1. Start the Cognee server
cd ./bonneagar/stacks/cognee && ./scripts/stack.sh up -d   # port 8100

# 2. Materialise the cognify assets
mise run dagster:oideachais
#    → asset group: cognify
#    → click Materialize All
#    → the 9 cognify assets materialise (aistear + primary + junior_cycle + senior_cycle + tertiary + cross_stage + 3 leabharlann)

# 3. Query the resulting knowledge graph
curl -X POST http://localhost:8100/api/v1/search \\
  -H 'Content-Type: application/json' \\
  -d '{"query": "Uí Liatháin Dyfed colonization", "datasets": ["culture_heritage", "oideachais_heritage"]}'
# Expected: 3-5 GraphRAG-style answers with citations to the Uí Liatháin Wikipedia clipping + the gemini_deep_research PDFs
```

### Recipe 4 — Query the LanceDB semantic-search index

```bash
# 1. Open the marimo notebook
uv run marimo edit cianfhoghlaim/notebooks/leabharlann/search.py
#    → http://localhost:2718

# 2. Paste a query in Irish
#    e.g. "An bhfuil aon trácht ar Uí Liatháin sa chorpás?"
#    → the notebook calls search_leabharlann_books(query, limit=10) and renders
#       the top-10 results with title, source, score, and snippet

# 3. The 4 LanceDB indices queried:
#    - leabharlann_books_embedding (BGE-M3, 1024-dim)
#    - leabharlann_zotero_embedding
#    - leabharlann_takeout_embedding
#    - unified_embedding (the cross-corpus index)
```

### Recipe 5 — Materialise a Dagster asset group end-to-end

```bash
# 1. Boot the local dev server
mise run turbo dev
#    → Dagster at http://localhost:3000
#    → Cognee at http://localhost:8100
#    → LiteLLM at http://localhost:4000/v1
#    → the 7 web apps + 29+ marimo notebooks

# 2. Open Dagster
xdg-open http://localhost:3000

# 3. Navigate to the asset group
#    → asset group: leabharlann_full_stack_demo
#    → click "Materialize All"
#    → Dagster runs the full chain: DLT → BAML → CocoIndex → Cognee
#    → each asset turns green within ~30 seconds

# 4. Open the marimo notebook to verify
xdg-open http://localhost:2718
#    → confirm the new BAML-extracted chunks appear in the search results
```

---
'''


def main() -> None:
    path = Path("/Users/cianmacandeisigh/dev/kings_college_galway/README.md")
    text = path.read_text()

    # Find start and end markers
    start_idx = text.find(START_MARKER)
    end_idx = text.find(END_MARKER)

    if start_idx == -1 or end_idx == -1:
        raise SystemExit(f"Could not find markers: start={start_idx}, end={end_idx}")

    # Keep the content before the start marker (intro + badges) and after the end marker
    before = text[:start_idx]
    after = text[end_idx:]

    new_text = before + NEW_SECTION + "\n" + after

    path.write_text(new_text)
    print(f"Wrote {len(new_text)} chars (was {len(text)} chars, added {len(new_text) - len(text)})")


if __name__ == "__main__":
    main()