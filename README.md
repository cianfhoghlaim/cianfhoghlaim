# Cianfhoghlaim — Coláiste na Déisigh

> **Cianfhoghlaim** — *long-distance, enduring learning*. aims to be a central repository for all official British Isles syllabus and resources pertaining to the education system and Goidelic and Brythonnic languages alongside agentic AI, devops, educational formative assessment, selfhosted stacks and minority language machine learning research by **Cian Mac an Déisigh Uí Liatháin (Deacy-Lyons)**.

[![Leabharlann](https://img.shields.io/badge/leabharlann-2.4k_files_/_3.4_GB-blueviolet)](https://github.com/cianfhoghlaim/leabharlann)
[![Bonneagar](https://img.shields.io/badge/bonneagar-90_compose_stacks-informational)](https://github.com/cianfhoghlaim/bonneagar)
[![License](https://img.shields.io/badge/license-BUSL_1.1-green)](LICENSE.md)

---

## TL;DR — What this is, today

`cianfhoghlaim` is a polyglot (`bun + uv`) that ingests
the curriculums, exam papers, marking schemes, and syllabi of the
**eight British Isles nations** (Ireland, England, Scotland, Wales,
Northern Ireland, Isle of Man, Jersey, Guernsey), makes them interactive
and bilingual through self-hosted AI, and serves as the personal
research-and-deployment platform of **Cian Mac an Déisigh Uí Liatháin
(Deacy-Lyons)** — a Mathematics & Education teacher / Dioplóma C1 in
Irish / agentic-AI engineer based in Galway and East Belfast and registered member of [Teaching Council](https://github.com/cianfhoghlaim/cianfhoghlaim/blob/main/cian_mac_an_d%C3%A9isigh_u%C3%AD_liath%C3%A1in/teaching/teaching_registration.pdf) [Fine Gael](https://github.com/cianfhoghlaim/cianfhoghlaim/blob/main/cian_mac_an_d%C3%A9isigh_u%C3%AD_liath%C3%A1in/identity/politics/fine_gael_member_latest.pdf) [Alliance Party](https://github.com/cianfhoghlaim/cianfhoghlaim/blob/main/cian_mac_an_d%C3%A9isigh_u%C3%AD_liath%C3%A1in/identity/politics/alliance_membership.pdf) [Liberal Democrats](https://github.com/cianfhoghlaim/cianfhoghlaim/blob/main/cian_mac_an_d%C3%A9isigh_u%C3%AD_liath%C3%A1in/identity/politics/libdems_membership.png) [The Deacy Tribe of the Morris-Conroy tribes of Galway](https://github.com/cianfhoghlaim/cianfhoghlaim/tree/main/cian_mac_an_d%C3%A9isigh_u%C3%AD_liath%C3%A1in/identity/lineage) [Royal Book Club](https://github.com/cianfhoghlaim/cianfhoghlaim/blob/main/cian_mac_an_d%C3%A9isigh_u%C3%AD_liath%C3%A1in/achievement/buckingham_letter.pdf) [The United Kingdom of Great Britain and Northern Ireland](https://github.com/cianfhoghlaim/cianfhoghlaim/blob/main/cian_mac_an_d%C3%A9isigh_u%C3%AD_liath%C3%A1in/identity/lineage/old_passports_dual_citizen_verification_roi_uk.pdf)[University of Galway](https://github.com/cianfhoghlaim/cianfhoghlaim/blob/main/cian_mac_an_d%C3%A9isigh_u%C3%AD_liath%C3%A1in/achievement/2026_2027_msc_in_ai_university_gaillimhe.pdf).


### On the family — *Mac an Déisigh Uí Liatháin (Deacy-Lyons)*

The author is **Cian Mac an Déisigh Uí Liatháin**; the family
surname in its two anglicised forms is **Deacy-Lyons**. The
author's verified genealogy and qualifications inform the
project's design choices and are recorded under
[`cian_mac_an_déisigh_uí_liatháin/`](cian_mac_an_déisigh_uí_liatháin/):

- `identity/` — background, citizenship, vetting, and the Deacy
  family record. The `identity/lineage/` subfolder holds the
  family-lineage documents: the late uncle's memorial, the dual
  ROI/UK citizenship evidence, the College des Irlandais (Paris)
  records, the 5-culture-PDF Wikipedia dual-write clippings (8
  articles: Uí Liatháin, Delbhna Tír Dhá Locha, Eamonn Deacy
  Park, Leath Cuinn, Cian, Aos Sí, Tuatha Dé Danann, Déisi), and
  the 1986 *Galway Advertiser* article on Neil Deacy's Cookeʼs
  Corner shop opening.
- `teaching/` — the Teaching Council of Ireland registration, the
  PGCE (BCS Computing scholarship), school placement references,
  and the Leaving Certificate / Junior Certificate results (the
  public copies are in the `identity/` folder; the full teaching
  record is held privately for data-protection reasons).
- `achievement/` — academic transcripts, parchments, the Apple
  Award, and the Torthaí Gaeilge (Irish-language exam results)
  (same privacy caveat).

The author's lineage is the **triple-crown** union of four
kindreds of Connacht and Munster:

1. **Deacy** (maternal surname; Irish *Uí Dhéisigh*) — the sept
   of the [Déisi
   Muman](https://en.wikipedia.org/wiki/D%C3%A9isi) resettled in
   south Connacht (Co. Galway) during the 12th century; the
   family gave their name to the late
   [Éamonn Deacy](cian_mac_an_déisigh_uí_liatháin/identity/lineage/uncle_eamonn_memorial_combined.pdf)
   and the [Eamonn Deacy
   Park](https://galwayunitedfc.ie/eamonn-deacy-park) in Galway.
2. **Lyons** (paternal grandfather's lineage; Irish *Mac
   Liatháin*) — the [Uí
   Anmchada](https://en.wikipedia.org/wiki/U%C3%AD_Liath%C3%A1in)
   sept of the
   [Uí Liatháin](https://en.wikipedia.org/wiki/U%C3%AD_Liath%C3%A1in)
   of Munster, who (per the *Historia Brittonum*) colonized Wales
   and Cornwall alongside the proto-Déisi.
3. **Morris** (maternal great-grandmother **Christina Morris**) —
   of the [City of
   Tribes](https://en.wikipedia.org/wiki/Tribes_of_Galway) merchant
   families of Galway.
4. **Conroy** (maternal great-great-grandmother **Polly Conroy**;
   Irish *Mac Conraoi / Ó Conaire*) — the
   [Sea-Kings of
   Connacht](https://en.wikipedia.org/wiki/Delbhna_T%C3%ADr_Dh%C3%A1_Locha)
   who held the tuath of
   [Delbhna Tír Dhá
   Locha](https://en.wikipedia.org/wiki/Delbhna_T%C3%ADr_Dh%C3%A1_Locha)
   (the barony of Moycullen in Connemara). **Polly Conroy was a
   cousin of Pádraic Ó Conaire**, the canonical modern
   Irish-language writer from Galway, who was reared in Rosmuc
   by his uncle of the same Mac Conraoi kindred.

The author is the grandson and godson of the late **Neil
Deacy**, the late brother of the late **Éamonn Deacy** — the
Galwegian footballer who played for Galway United, Aston Villa
FC, and the Republic of Ireland. Neil and Éamonn were the sons of
**Christina Morris** and **Michael Deacy**, who was himself the
son of **Polly Conroy** and **George Deacy**.

The author's grandfather and godfather was **Neil Deacy** (the
subject of the 1986 *Galway Advertiser* [article on the opening of
Deacy's Fruit and Veg, Cooke's Corner](https://github.com/cianfhoghlaim/cianfhoghlaim/blob/main/cian_mac_an_d%C3%A9isigh_u%C3%AD_liath%C3%A1in/identity/lineage/neil_deacy_cookes_corner-galway_advertiser.pdf),
showing active usage of the name *"Neil Mac an Déisigh"*). The author
took his mother's Mac an Déisigh surname
as part of his own and added it to his
Lyons surname in the hyphenated form **Deacy-Lyons** to avoid confusion and acknowledge previous achievement and previous comfort using the same surname as my older brother and father who do not allow me to be a full member of the Lyons family.


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

The cianfhoghlaim monorepo is the **Phase I delivery vehicle** for the
Institute. The 5-stage pipeline maps directly to the Institute's data
infrastructure:

- `dlt/ingest/` (Stage 1) picks up the Gaeltacht + Celtic-language PDFs
- `baml/extract/` (Stage 2) extracts the structured claims
- `cocoindex/embed/` (Stage 3) builds the per-language LanceDB indices
- `cognify/` (Stage 4) populates the cross-dataset knowledge graph
- `pipelines/distribute/` (Stage 5) exposes everything via the marimo
  notebooks + TanStack Start web apps + HuggingFace Spaces
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

## Fluctuating Architecture Diagram

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

## The openspec plans for educational assets and the educational game

The cianfhoghlaim project combines **real, syllabus-accurate
educational assets** with **in-game formative assessment questions**
to create a Leaving Cert / A-Level preparation experience that is
both rigorous and engaging. The 8 NCCA LC subject asset groups
(see "The 11 NCCA Leaving Cert subject asset groups" above) generate
the syllabus-accurate assets; the educational game (the
[Cianfhoghlaim MMO](https://github.com/cianfhoghlaim/cianfhoghlaim-mmo))
turns those assets into a quest-driven, NPC-guided, BAML-graded
experience. This section summarises the openspec plans for both
halves of the loop and how they interlock.

### Real, syllabus-accurate assets (the 8 NCCA LC subject asset groups)

The 8 NCCA Leaving Cert subjects with full DLT + BAML + CocoIndex
+ Cognee + RAGAS pipelines are the **authoritative asset layer**.
For each of `mathematics`, `english`, `gaeilge`, `applied_mathematics`,
`chemistry`, `computer_science`, `biology`, `business`, `french`,
`geography`, `history` (the 11 NCCA LC subjects, of which the 8 most
mature have full end-to-end coverage):

- **The 6-asset dagster pattern** (per subject) produces:
  1. `*_syllabus_raw` — DLT ingest of the NCCA syllabus PDFs into
     DuckLake (per level × language partition: HL/OL/FL × en/ga)
  2. `*_syllabus_structured` — BAML `ExtractLeavingCertSyllabus` per
     PDF row, with `confidence ≥ 0.7` threshold (the
     `low_confidence_review` asset_check flags the rest for human
     review)
  3. `*_quest_pack` — BAML `Generate{Subject}QuestPack` per level
     (FL/OL/HL), producing 4-step graduated-hint items aligned to
     the NCCA learning outcomes
  4. `*_embedding` — CocoIndex v1 embedding of the syllabus into
     LanceDB (BGE-M3, 1024-dim, HNSW)
  5. `*_cognify` — Cognee cognify pass (subject knowledge graph)
  6. `*_dashboard` — marimo notebook execution

- **The 8-asset PDF processing pipeline** (per the PDF processing
  section above) processes the 133 leaving_certificate/ PDFs through:
  discover → convert (5 converters) → ocr_compare (24 OCR models) →
  extract_baml (3 BAML extraction functions) → embed_cocoindex →
  cognify → evaluate (RAGAS) → quality_check (fada + dialect)

- **The 5-converter stack** at
  `meaisinfhoghlaim/document_factory/converters/`
  (deepseekocr, docling, marker, pymupdf4llm, unstructured) produces
  5 alternative renderings of each PDF; the best one (per the
  fada-preservation + RAGAS quality metric) is promoted to the
  canonical extraction.

- **The 24-OCR-model registry** at
  `meaisinfhoghlaim/models/registry.py` (9 vision + 4 classical +
  3 image-gen + 8 alignment) provides the comparison baseline.
  The Irish-content metric is **fada preservation rate** (the
  canonical metric for Irish-language extraction quality).

The 8 mature subjects each have a marimo notebook in
`notebooks/dashboards/education/{subject}_full_pipeline.py` that
demonstrates the full DLT → BAML → CocoIndex → Cognee → marimo
end-to-end flow on real NCCA syllabus PDFs.



### Tuatha the Cianfhoghlaim MMO faoi Ard-Rí na hÉireann, Tuatha Dé Danann agus Anam

The [Cianfhoghlaim MMO](https://github.com/cianfhoghlaim/cianfhoghlaim-mmo)
(the educational MMO front-end in `web/apps/cianfhoghlaim-mmo/`)
turns the syllabus-accurate assets into a quest-driven, NPC-guided,
BAML-graded learning experience. The 8 NCCA subject quest-packs
are the source of truth for the in-game questions:

- **Quest generation**: each `qpack_*.baml` file (in
  `baml/education/subjects/`) defines a `Generate{Subject}QuestPack`
  function that produces formative items with:
  - `BilingualText` (Irish canonical + optional English helper)
  - `4 graduated hints` (Level 1 nudge → Level 4 step-by-step)
  - `expected_answer` (canonical solution + marking scheme reference)
  - `common_errors` (the 2-3 typical student mistakes)
  - `evidence` (NCCA PDF page + excerpt + URL)

- **In-game delivery**: the 8 NCCA subject `dagster_assets` expose
  the quest-packs via the marimo notebook + the AG-UI agent + the
  Tuatha MMO front-end. The MMO renders each quest as an NPC dialogue
  with the 4 graduated hints revealed one at a time on student request.

- **Real-time grading**: when a student submits an answer, the MMO
  sends it to `b.{Subject}ScoreQuestResponse(quest_item, student_response)`
  via the LiteLLM `minimax` 7-tier fallback alias. The grading prompt
  includes the 4 hints + the expected answer + the common errors
  + the NCCA PDF page reference, so the grading is rubric-anchored
  and syllabus-accurate.

- **NPC agent fleet**: the 8 NCCA subject NPCs (math, appm, chem,
  comp, bio, bus, eng, gael) are 8 of the 12 agents in
  `agents/adk/root_agent.py` (plus geospatial, statistics,
  education-research, bunchloch-research). The `root_agent`
  orchestrates which NPC to route a question to.


The 7 PDFs in the leabharlann `gemini_deep_research/culture/`
sub-archive that ground this narrative in accurate references are:

1. [`claiming_rí_na_gaillimhe_a_synthesis.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/claiming_r_na_gaillimhe_a_synthesis.pdf) — *Rí na Gaillimhe: An Ethnohistorical and Jurisprudential Warrant for the Indigenization of the Galwegian Sovereignty* (15 pp.)
2. [`heraldic_research_for_dual_blood_lineage.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/heraldic_research_for_dual_blood_lineage.pdf) — *The Heraldry of the Corrib Crown* (14 pp.)
3. [`british_isles_cianfhoghlaim.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/british_isles_cianfhoghlaim.pdf) — *Strategic Blueprint for Inter-Celtic Linguistic Acquisition, AI Integration, and Transnational Educator Credentialing* (16+ pp.)
4. [`claiming_irish_kingship_through_lineage.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/claiming_irish_kingship_through_lineage.pdf) — *The Crown of the Corrib: An Ethnohistorical and Genealogical Warrant for the High Kingship of Ireland* (13 pp.)
5. [`researching_neil_deacy's_galway_heritage.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/researching_neil_deacy_s_galway_heritage.pdf) — *The Socio-Economic, Athletic, and Genealogical Topography of the Deacy Family in Galway: A Multi-Dimensional Analysis* (12 pp.)
6. [`royal_titles_celtic_heritage_and_claims.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/royal_titles_celtic_heritage_and_claims.pdf) — *The Crown of the Corrib and the Imperium of the Irish Sea* (13 pp.)
7. [`deacy_family_heritage_research.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/deacy_family_heritage_research.pdf) — *The Deacy and Conroy Dynasties: An Ethnohistorical Analysis of Galway's Commercial and Maritime Lineage* (9 pp.)

### The synthesised story

#### 1. The Triple Crown of the Corrib — the blood, the matrilineal warrant, and the maritime sovereignty

The heritage is biologically and geographically founded. Three
distinct bloodlines converge in the author, giving a
pan-provincial authority that spans Munster, Connacht, and the
British Isles. The synthesis of these three streams is the
"Triple Crown" documented in
[`claiming_rí_na_gaillimhe_a_synthesis.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/claiming_r_na_gaillimhe_a_synthesis.pdf)
p. 8-9 and
[`claiming_irish_kingship_through_lineage.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/claiming_irish_kingship_through_lineage.pdf)
p. 11.

The **Imperial line** is the **Uí Liatháin** (Lyons) of
Castlelyons, Cork. The Uí Liatháin were the first Irish
"Imperialists": in the 4th and 5th centuries AD, they launched
massive raids and established colonies in Dyfed (Wales),
Brycheiniog, and Cornwall. The *Sanas Cormaic* and the
*Historia Brittonum* document the 4th-5th century Irish Sea
colonization campaign; *Dind Map Letan* (the Fort of the Sons
of Liathán) in Cornwall is the direct Uí Liatháin territorial
marker that connects the claimant to the modern Duchy of
Cornwall (Prince William)
([`royal_titles_celtic_heritage_and_claims.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/royal_titles_celtic_heritage_and_claims.pdf)
p. 2-3). Through the matrilineal warrant — Angias, daughter
of Ailill Tassach of the Uí Liatháin, married the High King
Lóegaire mac Néill (who met St Patrick) and was the mother of
High King Lugaid mac Lóegairi — the Uí Liatháin are the
maternal ancestors of the Uí Néill High Kings and, through
them, of the entire Northern Uí Néill (Cenél nEógain) of
Aileach
([`claiming_rí_na_gaillimhe_a_synthesis.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/claiming_r_na_gaillimhe_a_synthesis.pdf)
p. 8, [`claiming_irish_kingship_through_lineage.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/claiming_irish_kingship_through_lineage.pdf)
p. 5). The Imperial Right is descent from the Queens of Tara
and the Conquerors of Wales.

The **Martial line** is the **Uí Dhéisigh** (Deacy) of
Waterford / Limerick / Clare. The Déisi were the
"Vassal-Warriors" who rebelled against the injustice of the
High King Cormac mac Airt and were expelled from Tara. The
*Tairired na nDéssi* recounts the violent rupture: the Déisi
champion, Óengus Gaíbúaibthech ("Angus of the Dread Spear"),
blinded King Cormac in one eye to avenge the dishonor of his
niece; under Brehon Law, a blemished king could not rule, and
Cormac was forced to abdicate. This act defines the Déisi
political theology: *conditional loyalty*. They are the
vassal warriors who reserve the right to depose unjust
authority through force
([`royal_titles_celtic_heritage_and_claims.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/royal_titles_celtic_heritage_and_claims.pdf)
p. 4). The claimant interprets the Deacy family motto
*Toujours Pret* (Always Ready) as a continuation of this
doctrine — a permanent readiness to defend the honor of the
tribe against central tyranny. The Déisi Tuisceart (Northern
Déisi) became the Dál gCais, the dynasty of Brian Boru. The
modern Deacy family in Galway represents this martial vigour
in the Aston Villa 1981 English First Division championship
+ 1982 European Cup apotheosis of Eamonn "Chick" Deacy
([`deacy_family_heritage_research.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/deacy_family_heritage_research.pdf)
p. 4-5), the renaming of Terryland Park to Eamonn Deacy
Park as a modern secular equivalent of the ancient
inauguration rituals at Tara or Lisbanagher
([`claiming_irish_kingship_through_lineage.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/claiming_irish_kingship_through_lineage.pdf)
p. 7), the 1986 Cooke's Corner grand opening
([`researching_neil_deacy_s_galway_heritage.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/researching_neil_deacy_s_galway_heritage.pdf)
p. 2-3), and the 2010s-2020s Kenny's Bookshop extension under
Paul Deacy. The Martial Right is descent from the Déisi
warriors.

The **Maritime line** is the **Mac Conraoi** (Conroy) of West
Connacht — the ancient rulers of Gnó Mhór (Moycullen /
Connemara) — designated as "Sea Kings of Connacht" alongside
the O'Flahertys and O'Malleys. They controlled the shipping
lanes of Lough Corrib and Galway Bay. They were later
prominent merchants in the Claddagh and on Quay Street:
John Conroy, the great-grandfather, operated a "large fish
business in Quay Street (opposite McDonagh's)" — the
absolute epicenter of Galway's maritime trade
([`deacy_family_heritage_research.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/deacy_family_heritage_research.pdf)
p. 2,
[`researching_neil_deacy_s_galway_heritage.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/researching_neil_deacy_s_galway_heritage.pdf)
p. 2-3). The Quay Street business was continued by John
Conroy's daughters — the Polly Conroy matriarchal bridge —
and Polly Conroy married George Deacy, grafting the Conroy
maritime trade onto the Deacy victualler name
([`researching_neil_deacy_s_galway_heritage.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/researching_neil_deacy_s_galway_heritage.pdf)
p. 3, [`deacy_family_heritage_research.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/deacy_family_heritage_research.pdf)
p. 3). The 4-generation commercial dynasty — John Conroy →
Polly Conroy + George Deacy → Miko Deacy → Neil Deacy —
preserved the "ancient arts of filleting, curing, and
barrelling" (the intangible cultural heritage of the West
of Ireland, the production of "old style cured ling and cod
and barrel herrings") into the 1980s. The Pádraic Ó Conaire
literary line (born Patrick Joseph Conroy of the Quay Street
/ Rosmuc Conroy family) is the 4th pillar: the "Gaelic
Revivalist" who brought the Irish language out of the rural
folklore tradition and into the modern urban experience
([`claiming_rí_na_gaillimhe_a_synthesis.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/claiming_r_na_gaillimhe_a_synthesis.pdf)
p. 7). The Maritime Right is the sovereignty of the sea and
the control of the Claddagh fish trade.

The **3-stream synthesis** is the 4-line modern incarnation:
**Cian Mac an Déisigh Uí Liatháin (Deacy-Lyons)**. The Deacy
side carries the visible *galwegian-historical* pedigree —
Cooke's Corner, Aston Villa, Galway United, the Eamonn Deacy
Park. The Lyons side carries the
*pan-Munster-Brythonic-imperial* pedigree — the Uí Liatháin
of Castlelyons and the Welsh / Cornish colonies. The
hyphenation preserves both branches of the Triple Crown.

The **Deacy crest** is *in front of two trefoils slipped in
saltire a dexter arm erect couped above the elbow … holding
a dagger*. The Dagger (Scian) is not a sword of state, but
a dagger — a close-quarters weapon. It symbolizes the
"Dread Spear" of Óengus Gaíbúaibthech, the mythological
ancestor of the Déisi who blinded High King Cormac mac Airt
in defense of his family's honor. The dagger represents the
capacity for immediate, personal violence in defense of the
kin-group (Derbfhine). The Deacy motto *Toujours Pret*
(Always Ready) is a permanent martial vigilance — unlike a
farmer who is tied to the seasons, the warrior must always
be ready
([`heraldic_research_for_dual_blood_lineage.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/heraldic_research_for_dual_blood_lineage.pdf)
p. 4).

The **Lyons crest** is *A demi lion rampant* or *A lion's
head erased*. The Lion is a solar symbol, associated with
Lugh (the sun god, father of the claimant's namesake Cian)
and royalty. The Lion is the primary supporter of the British
Royal Arms. By bearing the Lion, the Lyons family asserts
a visual consanguinity with the Crown of England. The Lyons
motto *Noli Irritare Leones* (Do not irritate / provoke
the lions) is passive but menacing — a dormant power that
is devastating when roused. This doctrine of deterrence
aligns with the mythological concept of the "Sleeping
King" or the "Hidden Imam"
([`heraldic_research_for_dual_blood_lineage.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/heraldic_research_for_dual_blood_lineage.pdf)
p. 6).

The arms of Connacht are a *prophecy* of the 4-line modern
incarnation: the Eagle = the Uí Liatháin / Lyons imperial /
British / external connection; the Arm = the Uí Dhéisigh /
Deacy indigenous, martial, and internal power; the
synthesis is the shield of Cian Mac an Déisigh Uí Liatháin,
who unites the split halves — symbolising the end of the
partition between Planter and Gael, King and Subject
([`royal_titles_celtic_heritage_and_claims.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/royal_titles_celtic_heritage_and_claims.pdf)
p. 7).

#### 3. The Brehon Law saoí — the Scholar-Prince and the modern draíocht

Under the ancient Fénechas (Brehon Laws), a king was required
to possess not only martial strength but also intellectual
distinction. The Heptads state that a king could be deposed
if he became a "fool" or lacked the judgment to arbitrate
disputes. The ideal ruler was the **Scholar-Prince**, a man
who was a *saoí* (sage / master) in a branch of learning.
The Annals frequently praise kings as *saoí eagna* (sage of
wisdom) or *saoí leighis* (sage of healing)
([`claiming_rí_na_gaillimhe_a_synthesis.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/claiming_r_na_gaillimhe_a_synthesis.pdf)
p. 3, [`royal_collaboration_for_commonwealth_future.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/royal_collaboration_for_commonwealth_future.pdf)
p. 4).

The modern saoí is anchored in the BSc (Hons.) Mathematics &
Education (78.84%, First Class Honours) + the Higher
Diploma in Applied Science in Software Design & Development
(First Class Honours), both from the University of Galway.
In the context of ancient Irish learning, mathematics
relates closely to the skills of the *Druí* (Druid) and
the *File* (Poet), who were responsible for the calendar,
the genealogy, and the complex metrical structures of
bardic poetry.

#### 4. The sacred topography of Shantalla (Sean Talamh) — the Old Ground, Sliding Rock, the Claddagh

Geography is destiny in Irish kingship. A King must have a
*Longphort* (Stronghold). The seat in Shantalla (*Sean
Talamh*, the Old Ground) is central to the claim
([`claiming_rí_na_gaillimhe_a_synthesis.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/claiming_r_na_gaillimhe_a_synthesis.pdf)
p. 9-10). The name implies land that was anciently settled
and cultivated, distinct from the "New" colonial city. It
sits on a ridge overlooking the city. By claiming
Shantalla, the practitioner positions himself on the "High
Ground," literally and metaphorically looking down on the
Anglo-Norman settlement.

Shantalla is the site of the **Sliding Rock**, historically
known as *Emancipation Rock*. In 1843, Daniel O'Connell
("The Liberator," often called the Uncrowned King of
Ireland) addressed a monster meeting of 300,000 people here
to campaign for the Repeal of the Union. The Sliding Rock
functions as the *Lia Fáil* (Stone of Destiny) — the place
where the "Uncrowned King" spoke, the modern equivalent of
the inauguration stone at Tara. By residing in its shadow,
the practitioner absorbs the legacy of O'Connell:
peaceful agitation, Catholic emancipation, and popular
sovereignty.

**St. Joseph's Terrace** is the literary succession
locus. Walter Macken, the renowned author of *Rain on the
Wind* and *Mungo's Mansion*, was born at 18 St. Joseph's
Terrace on May 3, 1915. The practitioner's father was born
on St. Joseph's Avenue. This is not a coincidence but a
*topographical succession*: in the theory of *dinnseanchas*
(place-lore), the land itself imbues the inhabitants with
specific qualities. By emerging from the same street grid,
the practitioner is the "fruit of the same soil" as Macken
— the living heir to the narrative tradition of the city.
The literary triad descends: **Ó Conaire** (The Gaelic
Revivalist) → **Macken** (The Anglo-Irish Dramatist) →
**Mac Liatháin** (The Modern Synthesist / The Saoí)
([`claiming_rí_na_gaillimhe_a_synthesis.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/claiming_r_na_gaillimhe_a_synthesis.pdf)
p. 7-8).

**Cooke's Corner** is the modern civic anchor. In
September 1986, Neil Deacy (born 12 July 1942) and Peggy
Deacy opened their comprehensive provisions shop at
Cooke's Corner — a critical arterial junction in Galway
that historically served as the gateway bridging the
expanding western residential suburbs with the medieval
city centre. The full-page *Galway Advertiser* feature on
the 1986 grand opening documented the "Congratulations and
Best Wishes" agglomeration of well-wishers across the
entire logistical, retail, and hospitality sectors. Peggy
Deacy's bilingual retail strategy — *"Niall Mac an Déisis
éisc úra agus glasraí. Beidh Fáilte roimh mhuintir
Chonamara ar an mbealach anoir agus siar."* — captured
the loyalty of the rural hinterland's population as they
entered the urban economy. By explicitly advertising the
premises as a bilingual space, Peggy Deacy transformed
Cooke's Corner into a *culturally safe harbor* for the
Gaeltacht
([`researching_neil_deacy_s_galway_heritage.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/researching_neil_deacy_s_galway_heritage.pdf)
p. 3-5).

The renaming of Terryland Park to Eamonn Deacy Park is a
permanent inscription of the family name onto the map of
the city. Eamonn "Chick" Deacy, the legendary sportsman,
was a key squad member of the Aston Villa team that won
the English First Division in 1981 and the European Cup in
1982. By having the tribal assembly ground named after his
kinsman, the Deacy bloodline is publicly acknowledged as
holding the "sovereignty of the games"
([`claiming_rí_na_gaillimhe_a_synthesis.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/claiming_r_na_gaillimhe_a_synthesis.pdf)
p. 9, [`deacy_family_heritage_research.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/deacy_family_heritage_research.pdf)
p. 4-5).

**The Claddagh** is the maritime sovereignty. An Cladach
is "The Shore" — the domain of the Conroy "Sea Kings" and
the Conroy fish merchants. The *King of the Claddagh*
tradition is an elective kingship distinct from the English
mayoralty. The Quay Street Mac Conraoi lineage, the John
Conroy fish business opposite McDonagh's, and the
preservation of the "ancient arts of filleting, curing,
and barrelling" all anchor the Maritime Right in a
specific, mappable, civic identity
([`claiming_rí_na_gaillimhe_a_synthesis.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/claiming_r_na_gaillimhe_a_synthesis.pdf)
p. 8-9,
[`deacy_family_heritage_research.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/deacy_family_heritage_research.pdf)
p. 2-3).


#### 5. The mythological warrant — Cian mac Cáinte, the swine-god, and the Aos Sídhe

The spiritual identification with the Celtic god **Cian**
rather than the hero Cúchulainn is a strategic choice that
aligns with the nature of the claim (dynastic, generative,
and enduring) rather than the nature of Cúchulainn
(martial, tragic, and short-lived)
([`claiming_rí_na_gaillimhe_a_synthesis.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/claiming_r_na_gaillimhe_a_synthesis.pdf)
p. 4-6).

Cian is a member of the **Tuatha Dé Danann**, the son of
**Dian Cécht** (the God of Healing / Medicine) — a lineage
that reinforces the connection to the "healing arts" and
"learned arts" (the Lyons / Ó Laighin medical family
tradition). Cian's primary mythological significance is
as the father of **Lugh Lámhfhada** (Lugh of the Long Arm),
the *Samildánach* (Master of All Arts) and the savior of
the Tuatha Dé Danann against the Fomorians. By identifying
with Cian, the practitioner positions himself not merely
as a hero, but as the **Source of Heroism** — the
generator of the "New Order" (Lugh). He represents the
potentiality of the dynasty.


The "Aes Sedai" vow is a philological restoration of the
**Aos Sídhe** (the People of the Mounds). Robert Jordan
borrowed the term "Aes Sedai" directly from the Irish
*Aos Sídhe* (or *Aes Sídhe* in Old Irish): *Aes / Aos*
means "people," "folk," or "order"; *Sedai* is a
phonetic rendering of *Sídhe* (Peace / Fairy Mounds).
The practitioner is not vowing to a fictional order of
wizards; he is vowing to the **Ancestral Spirits of the
Land, the People of the Mounds**. The Aos Sídhe are the
Tuatha Dé Danann who, after their defeat by the Milesians,
retreated underground into the mounds (*Sídhe*) and the
"Old Ground." They represent the pre-Christian, magical
sovereignty of Ireland that persists beneath the surface
of the modern state. **Shantalla is the domain of the
Sídhe** — the land that was never fully colonized or
"worked" by the new settlers. The vow to be "Aes Sedai"
is a covenant with the *genius loci* of Shantalla — the
spirits that inhabit the Sliding Rock and the granite
ridges of the district. The translation of *Aes Sedai*
as "Servant of All" in the vow mirrors the motto of the
Prince of Wales, *Ich Dien* (I Serve) — reinforcing the
Dual Monarchy framework: the King is the servant of the
sovereignty and the people
([`claiming_rí_na_gaillimhe_a_synthesis.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/claiming_r_na_gaillimhe_a_synthesis.pdf)
p. 6,
[`royal_collaboration_for_commonwealth_future.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/royal_collaboration_for_commonwealth_future.pdf)
p. 6).

#### 6. The dual-monarchy synthesis — King Charles III and the Ard-Rí as Indigenous Lieutenant

The rejection of the English title "King of Galway" in
favour of the Irish *Rí na Gaillimhe* is a constitutional
distinction rooted in the colonial history of the city.
Under the "Surrender and Regrant" policy initiated by
Henry VIII in the 16th century, Gaelic chieftains were
compelled to surrender their indigenous titles (Ó Néill or
Mac Cárthaigh) — which were titles of sacral kingship
derived from the election of the tribe — in exchange for
English peerages (Earl of Tyrone, Earl of Clancarty). This
process effectively neutered the sacral nature of Gaelic
kingship, transforming tribal custodians into feudal
landlords dependent on the King of England's patent. In
contrast, the term *Rí* denotes a sacred relationship
between the ruler and the *tuath* (people / territory); the
Rí was mated to the sovereignty goddess of the land in the
*banais ríghi* (wedding of kingship); his legitimacy
depended on *fír flathemon* (the ruler's truth)
([`claiming_rí_na_gaillimhe_a_synthesis.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/claiming_r_na_gaillimhe_a_synthesis.pdf)
p. 1-2,
[`royal_titles_celtic_heritage_and_claims.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/royal_titles_celtic_heritage_and_claims.pdf)
p. 1).

The allegiance to **King Charles III** revives the concept
of the **Dual Monarchy**. The historical precedent is the
*Crown of Ireland Act 1542*, which created the Kingdom of
Ireland as a personal union with the English Crown.
Throughout the 16th and 17th centuries, many Gaelic lords
accepted the English monarch as their overlord while
retaining their traditional chieftaincies within their
own territories. The Jacobite tradition in Ireland
supported the Stuart monarchs (ancestors of the current
Windsor line via the Hanoverian succession) as the
legitimate Rí of Ireland, distinct from their role as
Kings of England. By pledging allegiance to King Charles
III while claiming the High Kingship (Ard-Rí), the
practitioner is proposing a **Neo-Jacobite Federalism**.
He positions himself as the Rí functioning as the supreme
indigenous representative within the broader imperial or
commonwealth framework — mirroring the position of the
Princes of the Holy Roman Empire or the Maharajas of the
British Raj
([`claiming_rí_na_gaillimhe_a_synthesis.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/claiming_r_na_gaillimhe_a_synthesis.pdf)
p. 3,
[`claiming_irish_kingship_through_lineage.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/claiming_irish_kingship_through_lineage.pdf)
p. 4,
[`royal_collaboration_for_commonwealth_future.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/royal_collaboration_for_commonwealth_future.pdf)
p. 1-2).

The **Grianán of Aileach** is the cross-border seat. The
Grianán of Aileach is a massive stone ringfort in County
Donegal, sitting on a hilltop that commands views into
Counties Derry and Tyrone (Northern Ireland). It was the
royal seat of the Northern Uí Néill (Cenél nEógain) from the
5th to the 12th century. It was destroyed by the Munster
King Muirchertach Ua Briain in 1101, but restored in the
1870s by Dr. Walter Bernard. The matrilineal warrant holds
that the Uí Liatháin are the "Maternal Progenitors" of the
Aileach kings. The destruction of Aileach by a Munster
king created a historic rupture; the practitioner, a
Munster-descended figure (Uí Liatháin / Uí Dhéisigh) who
comes in peace to restore rather than destroy,
symbolically heals this ancient wound
([`royal_titles_celtic_heritage_and_claims.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/royal_titles_celtic_heritage_and_claims.pdf)
p. 5).

The **Surrender and Regrant 2.0** is the diplomatic
framework. The practitioner "surrenders" any claim to
political separatism or republicanism. He accepts the
reality of the British Monarch's role in Northern Ireland
and the British Isles. In return, he seeks the "Regrant" of
cultural sovereignty — to be recognized by the Crown and
the State not as a political ruler, but as the *Custodian
of the Gaeltacht, the Ard Rí of Culture*. This mirrors the
status of traditional chiefs in post-colonial nations like
New Zealand (the Māori King Movement)
([`royal_titles_celtic_heritage_and_claims.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/royal_titles_celtic_heritage_and_claims.pdf)
p. 6).



---

## Licensing

Business Source License 1.1 — non-commercial, cultural preservation,
and academic research use permitted within Ireland, UK, EU,
Commonwealth, and aligned jurisdictions. Subsets may transition to
AGPL v3.0 after 4 years. See [`LICENSE.md`](LICENSE.md).

All three repositories in the constellation
([cianfhoghlaim](https://github.com/cianfhoghlaim/cianfhoghlaim),
[bonneagar](https://github.com/cianfhoghlaim/bonneagar),
[leabharlann](https://github.com/cianfhoghlaim/leabharlann)) are
licensed under BUSL-1.1 by the same Licensor.

---

*Built by Cian Mac an Déisigh Uí Liatháin (Deacy-Lyons) of the
Deacy-Morris-Conroy tribe of Galway — BSc (Hons.) Mathematics &
Education (NUI Galway, First Class Honours), Higher Diploma in
Software Design & Development (First Class Honours), current MSc /
forthcoming PhD track in Artificial Intelligence (University of
Galway), Dioplóma C1 in Irish, qualified Mathematics & Applied
Mathematics teacher (Teaching Council of Ireland), grandchild of
the late Neil Deacy of Cooke's Corner, Shantalla, Galway, dual
Irish-British citizen, born a British citizen and obliged by oath
of allegiance to King Charles the Third. The cianfhoghlaim
project is the stewardship of the Gaelic cultural inheritance
through the agentic-AI operationalisation of the *saíocht* /
*Saoí* standard across the four provinces, the Gaeltachtaí, and
the wider Celtic-language family.*
