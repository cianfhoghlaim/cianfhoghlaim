# Cianfhoghlaim — Coláiste na Déisigh

> **Cianfhoghlaim** — *long-distance, enduring learning*. A research-and-deployment platform for the **British Isles education corpus** (8 nations × 5 stages × bilingual Goidelic + Brythonnic), agentic AI, self-hosted infrastructure, and minority-language machine learning. Maintained by **Cian Mac an Déisigh Uí Liatháin (Deacy-Lyons)**, a Mathematics & Education teacher, Dioplóma C1 in Irish, and agentic-AI engineer based in Galway and East Belfast.

[![Leabharlann](https://img.shields.io/badge/leabharlann-2.4k_files_/_3.4_GB-blueviolet)](https://github.com/cianfhoghlaim/leabharlann)
[![Bonneagar](https://img.shields.io/badge/bonneagar-IN_THIS_REPO_(%2Fbonneagar%2F)-green)](./bonneagar/)
[![License](https://img.shields.io/badge/license-BUSL_1.1-green)](LICENSE.md)
[![v7 flat](https://img.shields.io/badge/v7-flattened_2026--07--17-informational)](openspec/changes/archive/2026-07-29-2026-07-17-v7-flatten-cianfhoghlaim-merge-bonneagar-rewrite-readme-license-v1/)

> **Useful companion resources:** To understand the container, data, indexing,
> storage, and infrastructure patterns used throughout this project, see the
> hands-on labs at [iximiuz Labs](https://labs.iximiuz.com/), the database
> references at [DBQuacks](https://dbquacks.com/), and the official
> documentation, blogs, and examples for
> [CocoIndex](https://cocoindex.io/), [dlt](https://dlthub.com/docs/),
> [LanceDB](https://lancedb.com/), [DuckDB](https://duckdb.org/docs/),
> [MotherDuck](https://motherduck.com/docs/), [Komodo](https://komo.do/), and
> [Pangolin](https://docs.pangolin.net/). These are useful external guides to
> the key technologies and design choices represented in the repository.

---

## Mise Tasks (priority quick reference)

The 3 priority `mise run` tasks shipped by the 2026-07-30 → 2026-08-01 trilogy at a glance. **Read this first**; the full priority quick-refs are in [`AGENTS.md`](AGENTS.md).

| Task | One-line purpose |
|:--|:--|
| [`cic:stack-doctor`](AGENTS.md) | Validate all 94 Docker Compose stacks against the 6-file `GOLD_STANDARD` (the canonical CI gate) |
| [`stack-doctor:strict`](AGENTS.md) | `cic:stack-doctor` + `--strict --check-grammar` — fails on missing `infisical://` refs OR mixed bare/Jinja grammar in any `secrets.env` (Change 1, 2026-07-30) |
| [`lint:mcp-runtime`](openspec/changes/2026-08-21-fix-wired-but-unloaded-mcps-v1/) | Verify every `enabled: true` MCP entry in `opencode.json` has a corresponding `mcp:smoke:<name>` task (NEW in 2026-08-21) |
| [`deploy:full`](bonneagar/AGENTS.md#deployfull-orchestrator) | One-command 10-phase full-stack deploy orchestrator (preflight → auth → oidc → pangolin → control-plane → lakehouse → data → ocr → agent-surfaces → dagster-materialize), with a resumable checkpoint at `~/.cianfhoghlaim/deploy-state.json` (Change 3, 2026-08-01, extended to 10 phases by 2026-08-15) |

Plus the **safety gate** for any `iac:bootstrap`, `iac:plan`, or `km deploy stack <arm-oci-*>` from opencode: [`preflight:arm-oci`](AGENTS.md#opencode-safety) (mandatory per the 2026-07-09 repo-boundary-lockdown openspec change).

---

## Addendum — A note for anyone looking at this project right now

> **The project is sprawling on purpose.** It is a research-and-deployment
> platform for the British Isles education corpus, an agentic AI fleet, a
> self-hosted infrastructure mesh, and a minority-language ML playground
> — all federated by a single `bun + uv + turbo` monorepo. Because the
> goal is a deliberately overcomplicated Master's completed in a year,
> many subsystems that *do* work are partially obscured by the design
> choices meant for *my* team's downstream use. Read this section before
> forming an opinion about the repo.
>
> **The value for anyone looking at this project today is in the
> specific combinations of already well-calculated open-source
> packages.** The data engineering (DLT + Dagster + BAML + CocoIndex +
> DuckLake + LanceDB + MotherDuck + Marimo), the DevOps (Komodo +
> Pangolin + Infisical + Locket + Pocket ID + Traefik + Garage S3), the
> web-development (TanStack Start + Convex + Hono + CopilotKit + oRPC +
> AG-UI + Cloudflare), and the agent layer (Agno + Google ADK + Pydantic
> AI + LiteLLM + Letta + Cognee + Graphiti + Langfuse + MLflow) are each
> real, working open-source compositions. You can copy any slice
> independently.
>
> **The 12-MCP agent surface is the new foundation layer** (added
> 2026-08-21). All agent runtime tools are now wired via `opencode.json`
> + `.mcp.json` with one canonical surface per domain — ccc for code
> search, firecrawl + crawl4ai + chrome for web data, dlt-workspace +
> motherduck for data engineering, cognee + graphiti + design-system
> for knowledge/memory, langfuse for observability, infisical for
> secrets, huggingface for model hub. See
> [`openspec/changes/2026-08-21-mcp-server-revival-overview.md`](openspec/changes/2026-08-21-mcp-server-revival-overview.md)
> for the canonical inventory.
>
> **You can take the same data pipelines and rewire them for any other
> jurisdiction.** The `dlt_sources/` + `baml_src/` + `cocoindex_flows/` +
> `motherduck/` + `notebooks/` stack already produces the official
> legal, medical, education, and government documents for the British
> Isles. Retargeting it for, say, the US CMS, the WHO IRIS repository,
> the *Bundesministerium für Bildung*, or the French *Ministère de
> l'Éducation* means changing the jurisdiction enum, the BAML schemas,
> the scrape cache roots, and the destination namespaces — the core
> pipeline shape stays the same. Use `USE_LOCAL_SCRAPES=true` while you
> rebuild; the curated cache at `stedding/ingest_queue/` lets you iterate
> without spending scrape credits.
>
> **The cheapest way to do this is a cheap coding agent.** A €20/month
> **Gemini Deep Research Pro** subscription is the right tool for the
> *first* hour (finding the authoritative ministry, exam-board, or
> medical-register endpoints). A **MiniMax coding plan** (or the local
> **OpenCode Go** CLI) is the right tool for the *next* two days (the
> iterative file-local refactor across `dlt_sources/` + `baml_src/` +
> `cocoindex_flows/` + `motherduck/`). **GitHub Copilot** is a fine
> runner-up for single-file edits. None of them need the full monorepo.
>
> **Use my notes as a blueprint for your own deep-research tangent.**
> The [`leabharlann`](https://github.com/cianfhoghlaim/leabharlann)
> repository (3.4 GB, 2,400+ docs × 7 subdirs) holds the source materials
> that informed *every* sub-agent, BAML schema, and CocoIndex flow in
> this repo. They are unique to my circumstances; treat them as a
> worked example of *how* to do a deep-research tangent in this domain,
> not as *what* to copy.
>
> **The full per-area deep-cuts report — what each package composes,
> which 3-5 files to copy, which 5 lines to change, which 1 assumption
> is hardest to escape, and which coding agent to point at which job
> — lives at [`docs/CHOP_AND_CHANGE_GUIDE.md`](docs/CHOP_AND_CHANGE_GUIDE.md).**

---

> ## ⚠️ Important Disclaimer
>
> The **data engineering pipelines** in this repository — DLT ingestion,
> BAML extraction, CocoIndex v1 embeddings, Cognee cognify passes, the
> 8 NCCA Leaving Certificate subject asset groups — process official
> Government syllabus exam papers + marking schemes of the Republic of
> Ireland (NCCA Leaving Certificate, Junior Cycle, Primary) and the
> wider British Isles education system. They are **grounded in the 8
> British Isles nations** (Ireland, England, Scotland, Wales,
> Northern Ireland, Isle of Man, Jersey, Guernsey) and bilingualised
> in EN + GA (Gaeilge).
>
> The **web UIs** (`cianfhoghlaim-web`, `tuatha-ui`, `croilar-web`,
> `croilar-portal`, `oideachais`, `oideachais-dashboard`, the
> `tuatha-demo`, `game_showcase`, the Hono API gateway) are packaged
> demos that prove the agentic-web wiring works. They are **not yet**
> the final pedagogical surface — the UI work is deferred until the
> data pipeline has produced the canonical syllabus-accurate assets.
>
> To self-host your own instance you need your own domain name and a
> free Cloudflare account — see [`bonneagar/README.md`](bonneagar/README.md).

## TL;DR — What this is, today

`cianfhoghlaim` is a **polyglot monorepo** (`bun + uv + turbo`) that:

1. **Ingests** the curriculums, exam papers, marking schemes, and
   syllabi of the **8 British Isles nations** (with bilingual EN + GA
   extraction for the Irish strand).
2. **Extracts** structured data via the BAML schema library at
   `baml_src/british_isles/` (NCCA, SEC, CCEA, SQA, WJEC, Edexcel +
   the European Union EUR-Lex / ECDC / EMA / Eurostat / Eurydice +
   multi-nation Commonwealth + Americas expansions).
3. **Embeds** in vector + graph form via 60 CocoIndex v1 Apps (7 model
   families) + Cognee cognify layers + the Graphiti temporal knowledge
   graph.
4. **Surfaces** through marimo reactive notebooks, MotherDuck Dives,
   TanStack Start web apps, and a 13-agent meaisínfhoghlaim fleet
   (LiteLLM-routed via the OpenCode Go API; 7-tier fallback alias
   `minimax`).
5. **Hosts itself** on a self-managed 93-stack Docker Compose fleet
   (`bunchloch` MacBook M4 Max for the data plane + `arm1-oci` Oracle
   Cloud free-tier for the control plane + Garage S3 storage + the
   Komodo / Pangolin / Infisical / Locket / Pocket ID / TinyAuth /
   Traefik mesh).
6. **NEW 2026-08-23** — Ingests **any university student's personal
   archive** (the maintainer's three UoG programmes are the worked
   example: BA Maths & Education, HDip Software Design, Diploma
   sa Ghaeilge C1) at F-granularity (per-question answers, per-assignment
   topics, handwritten-maths HTR) and joins it to the official
   `ModuleDescriptor` corpus via 10 typed Cognee edges. See
   [Tertiary-Level Personal Archive Pipeline](#tertiary-level-personal-archive-pipeline-new-2026-08-23--f-granularity) below.

The author is a [registered member of the Teaching
Council](cian_mac_an_déisigh_uí_liatháin/teaching/teaching_registration.pdf),
with verified memberships in [Fine
Gael](cian_mac_an_déisigh_uí_liatháin/identity/politics/fine_gael_member_latest.pdf)
and the [Alliance
Party](cian_mac_an_déisigh_uí_liatháin/identity/politics/alliance_membership.pdf)
of Northern Ireland, and the
[Deacy Tribe of the Morris-Conroy tribes of
Galway](cian_mac_an_déisigh_uí_liatháin/identity/lineage/neil_deacy_cookes_corner-galway_advertiser.pdf).
See the **Personal credential corpus** section below for the full
verified-PDF table, the **Verified academic archive** section for the
`leabharlann/` subdir summary, and the **Family history** section for
the Triple-Crown synthesis.

## Centralized Registries (the single source of truth)

The platform has **one canonical source of truth** for every model,
schema, pipeline, and stack (post-2026-08-15). It replaces the ~70
hardcoded model strings + 96 hand-written Pydantic duplicates + 54
nearly-identical CocoIndex Apps that the audit found.

**The 4 canonical artifacts:**

- [`meaisinfhoghlaim/models/model_registry.py`](meaisinfhoghlaim/models/model_registry.py) — the 60-entry `MODEL_REGISTRY` across 7 families (`ocr_vision` × 20 / `text_llm` × 21 / `embedder` × 3 / `rerank` × 3 / `image_gen` × 5 / `voice` × 5 / `translation` × 3).
- [`notebooks/_shared/schema.py`](notebooks/_shared/schema.py) — the 5 introspection helpers (`schema_introspect`, `schema_introspect_table`, `list_dlt_sources`, `list_cocoindex_apps`, `list_baml_classes`).
- [`notebooks/00_control_panel.py`](notebooks/00_control_panel.py) — the 5-tab marimo control panel (Models / Pipelines / Datasets / Stacks / Registry).
- [`deployment-choice.yaml`](deployment-choice.yaml) — the canonical enablement file (read/written by the notebook + web UI + CLI).
- [`opencode.json`](opencode.json) — the **12-MCP agent surface** (added 2026-08-21). One canonical entry per domain: ccc / firecrawl / crawl4ai / chrome / dlt-workspace / motherduck / cognee / graphiti / design-system / langfuse / infisical / huggingface.

**The 4 supporting artifacts:**

- [`scripts/registry_audit.py`](scripts/registry_audit.py) — drift detector (fails CI on hardcoded model strings).
- [`agents/adk/litellm_agent.py`](agents/adk/litellm_agent.py) — `make_litellm_agent()` + `litellm_model("minimax")` wrappers.
- [`orchestration/defs/2_materials/_base/jurisdiction_assets_base.py`](orchestration/defs/2_materials/_base/jurisdiction_assets_base.py) — the `JurisdictionAssetsBase` for the per-jurisdiction Dagster asset wrappers.
- 3 CocoIndex factories (`cocoindex_flows/european_nations/_factory.py` et al.).

**The canonical `model_for()` pattern:**

```python
from meaisinfhoghlaim.models import model_for

default = model_for("text_llm", "default")              # → "minimax-m3"
irish   = model_for("text_llm", "irish")                # → "uccix-mistral-24b"
embed   = model_for("embedder", "default")              # → "BAAI/bge-m3"
```

**The canonical `schema_introspect()` pattern:**

```python
from notebooks._shared.schema import schema_introspect, list_dlt_sources
conn = ibis.duckdb.connect("md:cianfhoghlaim")
rows = schema_introspect(conn)             # every BIEP DuckDB table's columns
print(f"{len(list_dlt_sources())} DLT sources, {len(rows)} columns")
```

**Lint gate:** `mise run lint:registry` — fails on any hardcoded
model string in `agents/`, `baml_src/`, `notebooks/`, `web/`,
`orchestration/`, `meaisinfhoghlaim/`.

Full guide: [`.agents/skills/centralized-registry/SKILL.md`](.agents/skills/centralized-registry/SKILL.md).

---

## Monorepo Topology (v7 — Flattened Polyglot)

Two language graphs live side by side, orchestrated by `turbo.json`
and a single `mise.toml` toolchain. Post-v7 (2026-07-17), the
Python package IS the repo root — no more `cianfhoghlaim/`
nesting.

### TypeScript graph (bun workspaces)

| Workspace | Path | Purpose |
|:--|:--|:--|
| `cianfhoghlaim-web` | `web/apps/cianfhoghlaim-web/` | TanStack Start + React front-end (the public web app) |
| `cianfhoghlaim` | `web/apps/cianfhoghlaim/` | The TanStack Start second surface (the consolidated home app) |
| `cianfhoghlaim-leaving-cert` | `web/apps/cianfhoghlaim-leaving-cert/` | The Leaving Cert portal (its own nested sub-monorepo) |
| `cianfhoghlaim-mmo` | `web/apps/cianfhoghlaim-mmo/` | The Tuatha Celtic-mythology MMO client |
| `tuatha-ui` | `web/apps/tuatha-ui/` | Túatha educational MMO front-end |
| `croilar-web` | `web/apps/croilar-web/` | Croílár multi-persona portfolio |
| `croilar-portal` | `web/apps/croilar-portal/` | Croílár portfolio dashboard |
| `oideachais` | `web/apps/oideachais/` | The education-data TanStack Start surface |
| `oideachais-dashboard` | `web/apps/oideachais-dashboard/` | Education-data operator dashboard |
| `tuatha-demo`, `game_showcase` | `web/apps/{tuatha-demo,game_showcase}/` | Babylon.js demos |
| `hono-api` | `web/hono-api/` | Hono API gateway (8 route categories) |
| `ui-kit` | `web/packages/ui-kit/` | Shared UI components + `analytics`/`config`/`hooks`/`i18n` sub-paths |
| `auth`, `db` | `web/packages/{auth,db}/` | Shared auth + DB clients |

### Python sub-packages (uv at root)

| Sub-package | Path | Purpose |
|:--|:--|:--|
| `agents` | `agents/` | The 13-agent meaisínfhoghlaim fleet — see [`agents/README.md`](agents/README.md) |
| `baml_src` | `baml_src/` | BAML extraction schemas (LC + Celtic + multi-nation) |
| `cocoindex_flows` | `cocoindex_flows/` | CocoIndex v1 embedding Apps (renamed from `cocoindex/` 2026-08-19 — the old name shadowed the installed `cocoindex` library) |
| `dlt_sources` | `dlt_sources/` | DLT sources + destinations |
| `orchestration` | `orchestration/` | Dagster assets + jobs + schedules + sensors — see [`orchestration/README.md`](orchestration/README.md) |
| `meaisinfhoghlaim` | `meaisinfhoghlaim/` | OCR/HTR/alignment sub-package — see [`meaisinfhoghlaim/README.md`](meaisinfhoghlaim/README.md) |

### IaC subdirectory

The GitOps infrastructure lives in `bonneagar/` and is reached via
`bun run --cwd bonneagar iac:<command>` from the root `package.json`.
The IaC is no longer a separate GitHub repo; the
`archive-bonneagar` remote is a frozen read-only relic. See
[`bonneagar/README.md`](bonneagar/README.md) for the full architecture,
the 93-stack inventory, the 7-day operator quick start, and the
known gaps.

| IaC area | Path |
|:--|:--|
| IaC source (TypeScript + Dagger) | `bonneagar/iac/` |
| 93 Docker Compose stacks | `bonneagar/stacks/<name>/` |
| Komodo resource-syncs + procedures | `bonneagar/komodo/` |
| Pangolin config | `bonneagar/pangolin/` |
| Deploy runbooks | `bonneagar/deploy-runbooks/` |
| Audit scripts | `bonneagar/audit/scripts/` |

## The 5-stage architecture

The pipeline walks a corpus from raw disk to an agent-consumable,
semantically-indexed artifact. Five sequential stages live under
`orchestration/defs/<stage>/`, with two `4_*` siblings alongside
`4_asset_generation/` for budget tracking and the docs-index memory
job:

| Stage | Home | What it does |
|:--|:--|:--|
| 1. Ingestion | `orchestration/defs/1_ingestion/` | DLT sources for 8 nations × 4 domains + filesystem + api + language special sources. Auto-discover via the global-region-source-contract. |
| 2. Materials | `orchestration/defs/2_materials/` | BAML extraction (the `baml_src/british_isles/` schemas) + pdf processing + asset pre-processing |
| 3. Model Lifecycle | `orchestration/defs/3_model_lifecycle/` | CocoIndex v1 embedding Apps + LanceDB / DuckLake materialisation + RAGAS eval |
| 4. Asset Generation | `orchestration/defs/4_asset_generation/` | Subject-specific asset packs (8 NCCA LC subjects × per-subject quest packs + the 8-ADK agent fleet) |
| 4b. Budget | `orchestration/defs/4_budget/` | Firecrawl credit tracking (the meter for the BIEP freshness loop) |
| 4c. Memory | `orchestration/defs/4_memory/` | The docs-index Cognee cognify job (the 6th sync layer) |
| 5. Agent Operations | `orchestration/defs/5_agent_ops/` | The 13-agent meaisínfhoghlaim fleet + OpenChamber/OpenClaw/Hermes/Croílár surfaces + RisingWave event stream |

Each stage has a matching `Component` class in
`orchestration/components/` that `dg`-style YAML `defs.yaml` files
instantiate (11 components in total; see
[`orchestration/README.md`](orchestration/README.md) for the
architecture, the `JurisdictionAssetsBase` pattern, and the R1–R4
conformance check at scaffold time).

## British Isles Education Pipeline (BIEP) — the flagship

The 6 Irish LC priority subjects — **Mathematics, Chemistry,
Geography, Gaeilge, English, Computer Science** — get the deep
treatment: NCCA syllabus + SEC exam papers + marking schemes + 7
v1 CocoIndex flows + 42 Dagster assets + 6 marimo notebooks + 4
MotherDuck Dives + a daily MotherDuck Flight.

The BAML extraction schemas
(`baml_src/british_isles/ireland/education/lc_extraction/*.baml`)
produce structured `LeavingCertSyllabus`, `LeavingCertPastPaper`,
`LeavingCertMarkingScheme` objects — rubric-anchored to NCCA PDF
page references. Web search by the agent fleet always lands on
an in-pipeline asset, never on a stale URL.

For the wider corpus (Junior Cycle, Primary, the 5 English boards,
SQA, WJEC, CCEA, plus the EU EUR-Lex / ECDC / EMA / Eurostat /
Eurydice + multi-nation Commonwealth + Americas expansions), the
same `JurisdictionAssetsBase` pattern scales to ~30-line
per-jurisdiction subclasses instead of ~380-line hand-written asset
files.

### Tertiary-Level Personal Archive Pipeline (NEW 2026-08-23) — F-granularity

A student's personal university archive is treated as a first-class
citizen at the same level as the Leaving Cycle subject pipeline. The
pipeline lifts any user's `leabharlann/<university>/` corpus
(auto-discovered from folder structure, no curated drop-PDF UI as
primary entry) to **feature parity with the Leaving Cycle subject
pipeline** — typed artefacts → assignments → questions → topics →
code cells → reading items → CA marks → transcript rows at
**F-granularity** (per-question), joined to the transcript for ground
truth, embedded in LanceDB via 4 CocoIndex v1 Apps, with 10 typed
Cognee cross-archive edges (including a cross-module
`Topic-RELATED-TO-Topic` graph), and surfaced via the canonical 8-tab
Marimo notebook + Convex chat action + CopilotKit component + Genie
UI tile + Google ADK agent.

Reference: [`openspec/changes/2026-08-23-uog-personal-archive-tertiary-modules-v1/`](openspec/changes/2026-08-23-uog-personal-archive-tertiary-modules-v1/)

#### Worked examples (the case study)

The University of Galway (Ollscoil na Gaillimhe) corpus — covering
**three programmes** the maintainer completed — is the canonical
worked example:

| Programme | Modules (examples) | Artefact volume |
|---|---|---|
| **BA Mathematics & Education** (2013–2017) | `CS4423` Networks, `MA335` Mathematical Statistics, `ST311/ST312` Applied Statistics, `MP491` Non-Linear Systems, Numerical Analysis 2, Modelling 2, ISLP labs | ~300 MB across 9 module folders |
| **Higher Diploma in Software Design & Development** (2019–2020) | `CT511` Software Engineering, `CT545` Enterprise Java, `CT853` Algorithmics, `CT861` Computer Architecture, `CT870` Internet Programming, `CT874` Programming 1 | ~50 MB across 6 module folders |
| **Diploma sa Ghaeilge C1** (2020–2021) | `GA101` / `GA201` Ceart na Gaeilge, `GA114` Saíocht, `GA81010` Éisteacht agus Labhairt, `G100` Cruinneas, `GF101` / `GF107` | ~80 MB across 7 module folders |

**Three example usage purposes** the pipeline surfaces end-to-end
(the per-question answers are chatable via the ADK agent
`personal_archive_module_assistant`):

##### 1. CS4423 Networks → eigenvector centrality, neighbours, M.Sc. AI bridge

The CS4423 (Networks) folder is the canonical worked example for
F-granularity extraction. From the 5 assignment PDFs plus the
lecture notes plus the past exam, the pipeline produces:

- **Module dossier** — every assignment + every question + my answer
  text + my mark + the HTR backend used + the LaTeX form of any
  maths + the topics covered.
- **Topic graph** — `eigenvector_centrality`, `neighbours_in_networks`,
  `graph_laplacian`, etc. The Cognee `Topic-RELATED_TO-Topic` edge
  then connects these to the M.Sc. AI future-modules story (because
  eigenvector centrality shows up in graph neural networks, which the
  maintainer will study next year on the MA in AI).
- **Transcript join** — exact match on `(module_code, academic_year)`
  against the BA Maths & Education transcript; CS4423, 2020–21, A1.

##### 2. MP491 Non-Linear Systems → handwritten maths, HTR ensemble

MP491 (Non-Linear Systems) is the canonical worked example for the
HTR pipeline. The handwritten answers were authored on an iPad with
an Apple Pencil in the Goodnotes app, then exported as vector PDFs.
The pipeline routes them through the **6-backend HTR ensemble**
(nougat + olmocr-2-7b + CogVLM + gemma-3 majority-vote consensus,
with nougat as the single-VLM best-of-breed fallback for scientific
papers):

- `my_answer_text` — the verbatim OCR'd answer.
- `my_answer_latex` — the LaTeX form (e.g. `\int_0^1 x^2 \, dx`).
- `htr_backend_used` — which of the 6 backends produced the answer.
- `htr_confidence` — 0.0–1.0, exposed in the Marimo notebook for
  manual override.

##### 3. Numerical Analysis 2 (splines, interpolation) → M.Sc. AI handoff

Numerical Analysis 2 covers splines and interpolation — topics
directly relevant to the M.Sc. AI modules the maintainer is starting
in 2027-09. The pipeline extracts the topics, joins them to the
official UoG `ModuleDescriptor` (from the existing
`2026-07-15-cianfhoghlaim-university-deep-extraction-v1` change),
and emits the cross-module Cognee edge that lights up in the future
M.Sc. AI Marimo notebook.

#### Transferability — the user-facing promise

Any university student can point the pipeline at their own
`leabharlann/<university>/` corpus by setting the 9 `UNIVERSITY_*`
env vars (see `.env.example`) and calling
`personal_archive_source(UniversityPersonalArchiveConfig(...))`. The
same 8 DLT resources, 7 BAML functions, 4 CocoIndex Apps, 10 Cognee
edges, 6 Dagster assets, 8 Marimo tabs, 5 Convex queries, CopilotKit
+ Genie + ADK agent, and 12 tests run unchanged. The canonical
`UniversityPersonalArchiveConfig` Pydantic v2 model is the single
surface for "who is the student, what is the institution, what
regex matches the module codes, where do the transcripts live".

#### Quickstart

```bash
# Validate the openspec change
openspec validate 2026-08-23-uog-personal-archive-tertiary-modules-v1 --strict

# Run the personal-archive test suite (12 passing)
uv run pytest tests/personal_archive/ -v

# Materialise the DuckLake tables
uv run python -c "
import duckdb
from dlt_sources.lakehouse import register_personal_archive_tables
con = duckdb.connect(':memory:')
register_personal_archive_tables(con)
print(sorted(t[0] for t in con.execute('SHOW TABLES').fetchall()))
"

# Open the 8-tab Marimo notebook (Health / Filters / Materials /
# URL Health / Heatmap / Recent / Lance Search / SQL Console)
marimo edit notebooks/15_personal_archive.py

# Auto-classify a sample artefact
uv run python -c "
from pathlib import Path
from dlt_sources.filesystem.uog_personal_archive import _classify_file
p = Path('leabharlann/ollscoil_na_gaillimhe/mata/networks/CS4423 - Networks/cian_mac_liathain_assignment_3.pdf')
print(_classify_file(p))
"
```

## The agent fleet

The 13 root agents (1 Custom + 8 ADK + 3 Agno + 1 image-generation)
plus the 8 NCCA Leaving Cert subject specialists (`gael_agent`,
`math_agent`, `appm_agent`, `chem_agent`, `comp_agent`, `engl_agent`,
`geog_agent`, `hist_agent`) all route through the LiteLLM gateway at
`litellm.cianfhoghlaim.ie:4000` and the canonical 7-tier `minimax`
fallback alias. The fleet spans **5 frameworks** (Custom + ADK +
Agno + Pipecat + CopilotKit), wires through a single canonical
surface (`AGENT_REGISTRY`), and is observed by a **5-layer
observability stack** (Langfuse + Logfire + MLflow + RAGAS +
structlog) backed by a **5-backend memory layer** (Cognee + Graphiti
+ LanceDB + FalkorDB + Memgraph). See
[`agents/README.md`](agents/README.md) for the architecture diagram
+ implementation decisions + how to lift a single agent out
independently.

## Personal credential corpus (verified references)

These are the records that ground the project's claims. The full
long-form index lives at
[`cian_mac_an_déisigh_uí_liatháin/README.md`](cian_mac_an_déisigh_uí_liatháin/README.md);
this table is the canonical subset a new visitor needs to verify
the author + the lineage:

| Credential | Verified PDF |
|:--|:--|
| Teaching Council of Ireland registration | [`cian_mac_an_déisigh_uí_liatháin/teaching/teaching_registration.pdf`](cian_mac_an_déisigh_uí_liatháin/teaching/teaching_registration.pdf) |
| MSc AI admission (2026-2027, University of Galway) | [`cian_mac_an_déisigh_uí_liatháin/achievement/2026_2027_msc_in_ai_university_gaillimhe.pdf`](cian_mac_an_déisigh_uí_liatháin/achievement/2026_2027_msc_in_ai_university_gaillimhe.pdf) |
| BSc Maths & Education (First Class Honours, 78.84%) | [`cian_mac_an_déisigh_uí_liatháin/achievement/ba_and_hdip_transcript.pdf`](cian_mac_an_déisigh_uí_liatháin/achievement/ba_and_hdip_transcript.pdf) + [`bachelors_degree_parchment.jpeg`](cian_mac_an_déisigh_uí_liatháin/achievement/bachelors_degree_parchment.jpeg) |
| Higher Diploma in Software Design (First Class Honours) | [`cian_mac_an_déisigh_uí_liatháin/achievement/higher_diploma_parchment.jpeg`](cian_mac_an_déisigh_uí_liatháin/achievement/higher_diploma_parchment.jpeg) |
| PGCE (BCS Computing scholarship) | [`cian_mac_an_déisigh_uí_liatháin/teaching/bcs_pgce_computing_scholarship.png`](cian_mac_an_déisigh_uí_liatháin/teaching/bcs_pgce_computing_scholarship.png) |
| Torthaí Gaeilge (Irish-language exam results) | [`cian_mac_an_déisigh_uí_liatháin/achievement/torthai_ghaeilge.pdf`](cian_mac_an_déisigh_uí_liatháin/achievement/torthai_ghaeilge.pdf) |
| Apple Award (2013) | [`cian_mac_an_déisigh_uí_liatháin/achievement/apple_award.pdf`](cian_mac_an_déisigh_uí_liatháin/achievement/apple_award.pdf) |
| Royal Book Club (Buckingham letter) | [`cian_mac_an_déisigh_uí_liatháin/achievement/buckingham_letter.pdf`](cian_mac_an_déisigh_uí_liatháin/achievement/buckingham_letter.pdf) |
| Deacy lineage (1986 Galway Advertiser article) | [`cian_mac_an_déisigh_uí_liatháin/identity/lineage/neil_deacy_cookes_corner-galway_advertiser.pdf`](cian_mac_an_déisigh_uí_liatháin/identity/lineage/neil_deacy_cookes_corner-galway_advertiser.pdf) |
| Late uncle's memorial (Éamonn "Chick" Deacy) | [`cian_mac_an_déisigh_uí_liatháin/identity/lineage/uncle_eamonn_memorial_combined.pdf`](cian_mac_an_déisigh_uí_liatháin/identity/lineage/uncle_eamonn_memorial_combined.pdf) |
| Dual citizenship (ROI + UK) | [`cian_mac_an_déisigh_uí_liatháin/identity/lineage/old_passports_dual_citizen_verification_roi_uk.pdf`](cian_mac_an_déisigh_uí_liatháin/identity/lineage/old_passports_dual_citizen_verification_roi_uk.pdf) |
| Fine Gael membership | [`cian_mac_an_déisigh_uí_liatháin/identity/politics/fine_gael_member_latest.pdf`](cian_mac_an_déisigh_uí_liatháin/identity/politics/fine_gael_member_latest.pdf) |
| Alliance Party membership | [`cian_mac_an_déisigh_uí_liatháin/identity/politics/alliance_membership.pdf`](cian_mac_an_déisigh_uí_liatháin/identity/politics/alliance_membership.pdf) |

## Verified academic archive (leabharlann)

The course material + examination scripts + the personal academic
corpus live at [`github.com/cianfhoghlaim/leabharlann`](https://github.com/cianfhoghlaim/leabharlann)
— a separate 3.4 GB repo, the only remaining separately-managed
repo. It contains **7 top-level subdirectories** that feed the
data platform:

| Subdir | Domain | Sample contents |
|:--|:--|:--|
| [`gaeilge/`](https://github.com/cianfhoghlaim/leabharlaim/tree/main/gaeilge) | Irish language + Celtic studies | Fáinne + Ór Fháinne proficiency materials, Cultúrlann McAdam Ó Fiaich, Proinsias Mac Cana's *Collège des Irlandais Paris*, *A Gaelic History of East Belfast* |
| [`aigne/`](https://github.com/cianfhoghlaim/leabharlaim/tree/main/aigne) | Mind + mental health + reflection | *Rebuilding Shattered Lives*, *Models of Madness*, *The Shallows* (Carr), *Buddhism without Beliefs*, neurogenesis + iatrogenic-trauma reading lists |
| [`mata/`](https://github.com/cianfhoghlaim/leabharlaim/tree/main/mata) | Foundational + advanced mathematics | Strang's *Linear Algebra* (6th ed.), Epp's *Discrete Mathematics*, Skiena's *Algorithm Design Manual*, *ISLP in Python*, Murphy's *Probabilistic ML*, *DuckDB in Action* |
| [`ollscoil_na_gaillimhe/`](https://github.com/cianfhoghlaim/leabharlaim/tree/main/ollscoil_na_gaillimhe) | University of Galway coursework | BSc Mathematical Science (9 modules: ST311/ST312, CS402 Cryptography, ISLP, Maple, MP307, CS4423, MP491, MA378) + Higher Diploma in Software Design (7 modules: CT511/CT545/CT853/CT861/CT870/CT874 + SE1) + PME placements + Dioplóma sa Ghaeilge |
| [`zotero/`](https://github.com/cianfhoghlaim/leabharlaim/tree/main/zotero) | Academic papers (NLP, OCR, Celtic, federated) | gaBERT, UCCIX, *Gaeilge Bhriste ó Shamhlacha Cliste*, Nougat, eScriptorium, CogVLM, Vintern, *HTR for Irish-Language Folklore*, Flower + SplitFed, EduGA, Irish-BLiMP |
| [`gemini_deep_research/`](https://github.com/cianfhoghlaim/leabharlaim/tree/main/gemini_deep_research) | AI-assisted research reports | 7 subdomains: `culture/` + `law/` + `medical/` + `politics/` + `technology/` + `other/` — 21 PDFs in `culture/` alone |
| [`saontacht_oideachais/`](https://github.com/cianfhoghlaim/leabharlaim/tree/main/saontacht_oideachais) | Education-specific (4 universities) | `dkit/` + `nuig/` + `qub/` + `ucl/` — syllabi, reading lists, programme handbooks |

### The 7 culture-PDF warrants grounding the family history

The Tuatha educational MMO's Ard-Rí na hÉireann framing is grounded
in 7 long-form research PDFs under
[`leabharlann/gemini_deep_research/culture/`](https://github.com/cianfhoghlaim/leabharlain/tree/main/gemini_deep_research/culture):

1. [`claiming_rí_na_gaillimhe_a_synthesis.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/claiming_r_na_gaillimhe_a_synthesis.pdf) — *Rí na Gaillimhe: An Ethnohistorical and Jurisprudential Warrant* (15 pp.)
2. [`heraldic_research_for_dual_blood_lineage.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/heraldic_research_for_dual_blood_lineage.pdf) — *The Heraldry of the Corrib Crown* (14 pp.)
3. [`british_isles_cianfhoghlaim.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/british_isles_cianfhoghlaim.pdf) — *Strategic Blueprint for Inter-Celtic Linguistic Acquisition, AI Integration, and Transnational Educator Credentialing* (16+ pp.)
4. [`claiming_irish_kingship_through_lineage.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/claiming_irish_kingship_through_lineage.pdf) — *The Crown of the Corrib: An Ethnohistorical and Genealogical Warrant* (13 pp.)
5. [`researching_neil_deacy's_galway_heritage.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/researching_neil_deacy_s_galway_heritage.pdf) — *The Socio-Economic, Athletic, and Genealogical Topography of the Deacy Family in Galway* (12 pp.)
6. [`royal_titles_celtic_heritage_and_claims.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/royal_titles_celtic_heritage_and_claims.pdf) — *The Crown of the Corrib and the Imperium of the Irish Sea* (13 pp.)
7. [`deacy_family_heritage_research.pdf`](https://github.com/cianfhoghlaim/leabharlann/blob/main/gemini_deep_research/culture/deacy_family_heritage_research.pdf) — *The Deacy and Conroy Dynasties: An Ethnohistorical Analysis of Galway's Commercial and Maritime Lineage* (9 pp.)

## Family history (Triple Crown of the Corrib)

The author's lineage is the **triple-crown** union of four kindreds of Connacht and Munster:

1. **Deacy** (maternal surname; Irish *Uí Dhéisigh*) — the sept of the [Déisi Muman](https://en.wikipedia.org/wiki/D%C3%A9isi) resettled in south Connacht (Co. Galway) during the 12th century; the family gave their name to the late [Éamonn Deacy](cian_mac_an_déisigh_uí_liatháin/identity/lineage/uncle_eamonn_memorial_combined.pdf) and the [Eamonn Deacy Park](https://galwayunitedfc.ie/eamonn-deacy-park) in Galway.
2. **Lyons** (paternal grandfather's lineage; Irish *Mac Liatháin*) — the [Uí Liatháin](https://en.wikipedia.org/wiki/U%C3%AD_Liath%C3%A1in) sept of Munster, who (per the *Historia Brittonum*) colonized Wales and Cornwall alongside the proto-Déisi.
3. **Morris** (maternal great-grandmother **Christina Morris**) — of the [City of Tribes](https://en.wikipedia.org/wiki/Tribes_of_Galway) merchant families of Galway.
4. **Conroy** (maternal great-great-grandmother **Polly Conroy**; Irish *Mac Conraoi / Ó Conaire*) — the [Sea-Kings of Connacht](https://en.wikipedia.org/wiki/Delbhna_T%C3%ADr_Dh%C3%A1_Locha) who held the tuath of [Delbhna Tír Dhá Locha](https://en.wikipedia.org/wiki/Delbhna_T%C3%ADr_Dh%C3%A1_Locha) (the barony of Moycullen in Connemara). **Polly Conroy was a cousin of Pádraic Ó Conaire**, the canonical modern Irish-language writer from Galway.

The **3-stream synthesis** is the 4-line modern incarnation: **Cian Mac an Déisigh Uí Liatháin (Deacy-Lyons)**. The Deacy side carries the *galwegian-historical* pedigree (Cooke's Corner, Aston Villa, Galway United, Eamonn Deacy Park). The Lyons side carries the *pan-Munster-Brythonic-imperial* pedigree (Uí Liatháin of Castlelyons and the Welsh / Cornish colonies). The hyphenation preserves both branches of the Triple Crown and acknowledges the previous achievement of the Lyons lineage while respecting the author's choice to bear his mother's Mac an Déisigh name first.

**The full discursive narrative** — the Triple-Crown synthesis, the Brehon-Law saoí framing, the sacred topography of Shantalla (*Sean Talamh*), the mythological warrant of Cian mac Cáinte (the swine-god and father of Lugh Lámhfhada), the philological restoration of the Aos Sídhe vow, and the dual-monarchy synthesis with King Charles III — lives at [`cian_mac_an_déisigh_uí_liatháin/FAMILY_HISTORY.md`](cian_mac_an_déisigh_uí_liatháin/FAMILY_HISTORY.md) (619 lines, preserved verbatim per the author's prior instruction that "the validated references to my credentials and family history relevant to the name and location of the project" stay in the repo).

## Repository constellation (post-v7)

| Repo | Path | URL | Purpose |
|:--|:--|:--|:--|
| cianfhoghlaim (this) | `.` (root) | [`github.com/cianfhoghlaim/cianfhoghlaim`](https://github.com/cianfhoghlaim/cianfhoghlaim) | The Python package IS the repo |
| bonneagar (in-tree + mirrored) | `bonneagar/` | [`github.com/cianfhoghlaim/bonneagar`](https://github.com/cianfhoghlaim/bonneagar) | The 93-stack GitOps fleet + Komodo + Pangolin + Infisical |
| leabharlann (separate) | `leabharlann/` symlink / 3.4 GB checkout | [`github.com/cianfhoghlaim/leabharlann`](https://github.com/cianfhoghlaim/leabharlann) | The digital library corpus that grounds every BAML schema + CocoIndex flow |

`bonneagar/` is **in-tree and authoritative here**; the standalone repo
at `github.com/cianfhoghlaim/bonneagar` is a **one-way published
mirror** of it, in root layout (`stacks/`, `komodo/`, `iac/` at the
repo root rather than under `bonneagar/`).

The mirror was frozen between 2026-07-12 and 2026-08-28, during which
it fell 643 files behind. It was resynced on 2026-08-28 by exporting
`bonneagar/` with `git filter-repo --subdirectory-filter`, which
force-updated the mirror's `main`. The pre-sync tip is preserved on the
mirror as `backup/pre-monorepo-sync-2026-08-28`.

**Never commit to the mirror directly** — it is force-updated from this
monorepo and any direct commit will be discarded on the next sync.
Refresh it with `mise run bonneagar:mirror`.

## Cross-cutting concerns

### OpenSpec workflow (canonical change management)
[`openspec/`](openspec/) is the single source of truth for capability
specs. The workflow: `list → write proposal/tasks/spec deltas →
validate --strict → implement → archive`. **96 specs** live under
`openspec/specs/`; **34 changes** are currently pending under
`openspec/changes/`. See [`openspec/AGENTS.md`](openspec/AGENTS.md)
for the full workflow and [`openspec/project.md`](openspec/project.md)
for conventions.

```bash
openspec list --specs                    # 96 capability specs
openspec list                            # 34 pending changes
openspec validate <change-id> --strict   # MUST pass before commit
openspec archive <change-id> --yes       # after deploy
```

### Secrets management (Infisical + Locket + mise)
The 3-way contract: the `dev-baile` Infisical vault is the source
of truth → the committed `.infisical.env` template holds every
value as an `infisical://dev-baile/...` reference → the gitignored
`.env` is hydrated by `mise` directory hooks + the Locket sidecar
at runtime. The IaC binds each stack's `secrets.env` to Infisical
via the typed `InfisicalClient` at `bonneagar/iac/clients/`. Full
guide: [`bonneagar/SECRETS-MANAGEMENT.md`](bonneagar/SECRETS-MANAGEMENT.md).

### CCC + Cognee + Firecrawl dual-search
**CCC** ([`bun run ccc:search "<query>"`](AGENTS.md#ccc-code-search-always-use-before-grep))
gives every agent a per-project semantic index at
`.cocoindex_code/target_sqlite.db` (CocoIndex BGE-M3 embeddings over
~7,000 tracked files). **Cognee** (`cognee cognify`) gives a
knowledge-graph memory layer at `agents/meaisinfhoghlaim/memory/`
across 7 clusters. **Firecrawl** (`firecrawl_search` /
`firecrawl_scrape` / `firecrawl_research_*`) covers upstream +
biomedical + arXiv literature. Per the 2026-08-14 dual-search
convention, every Firecrawl call MUST be paired with a `ccc:search`
so both tool names appear in the Langfuse trace.

### How this project is developed
Agentically. The canonical configuration is at `opencode.json`.
The 13 + 8 agent fleet is wired through
`agents/agent_registry.py:AGENT_REGISTRY` with a single canonical
surface (the same conventions as
`agents/tuatha/wiring.py:SubjectAgentWiring`). See
[`AGENTS.md`](AGENTS.md) for the durable rules every coding agent
follows in this repo.

---

## §11 — Hardware footprint + cloud options

> **For:** Teachers, students, parents, NCCA subject specialists, university faculty, journalists, citizens, contributors — anyone who wants to know **which machine** to buy / which cloud to use, and **how that compares to the alternatives** (the Mac tiers, the Oracle ARM free tier, Google Cloud, Gemini API, MiniMax Token Plan, and the local GGUF models from the canonical `MODEL_REGISTRY`).
>
> **Canonical reference:** [`meaisinfhoghlaim/models/model_registry.py`](./meaisinfhoghlaim/models/model_registry.py) (52 entries across 7 families — the centralised registry).
>
> **Why this matters for cianfhoghlaim:** the British-Isles education corpus platform is **research-and-deployment** — every deployment option must be auditable + reproducible. Local GGUF gives the strongest audit story; Oracle ARM gives the cheapest 24/7 cloud; the APIs give the lowest capex but the weakest audit story.

### §11.1 — The 5-axis hardware landscape

| Axis | Option | RAM | Type | Cost | Sovereignty |
|---|---|---|---|---|---|
| **Apple Silicon** | MacBook Pro 14" M4 Max | 48 GB | Local GPU | ~$3,500 one-off | 100% local |
| **Apple Silicon** | MacBook Air 13" M5 (cheapest new) | 16 GB | Local GPU | ~$1,100 one-off | 100% local |
| **Apple Silicon** | MacBook Air 13" M1 (older entry) | 8 GB | Local GPU | (used market) | 100% local |
| **ARM cloud** | Oracle Cloud Always-Free Ampere A1 + PAYG upgrade | 24 GB | Cloud ARM vCPU | $0/month forever | Cloud (OCI region) |
| **x86 cloud** | Google Cloud $300 free-trial credit | 32 GB | Cloud x86 | $0 for ~45 days | Cloud (GCP region) |
| **API** | Gemini 3.1 Pro API | (infinite) | API token billing | $2/$12 per M tokens | Cloud (Google) |
| **API** | MiniMax Token Plan | (infinite) | API token billing | $0.30/$1.20 per M tokens | Cloud (MiniMax) |

### §11.2 — The 3 Mac tiers (the hardware case scenario)

| Tier | Machine | RAM | GPU cores | Apple Silicon GPU bandwidth | Best GGUF (Q4_K_M) | Monthly cost (electricity) |
|---|---|---|---|---|---|---|
| **Primary** (the canonical case) | MacBook Pro 14" M4 Max | 48 GB | 40 | 546 GB/s | Qwen3.8-27B (~17 GB) + DeepSeek V4-Pro (~17 GB) + Kimi K3 (~17 GB) + PaddleOCR-VL-1.6 (~3 GB) | ~$3 |
| **Cheapest new** | MacBook Air 13" M5 | 16 GB | 10 | ~100 GB/s | Qwen3.6-27B-MTP (~17 GB) + Gemma-4-E4B (~3 GB) + PaddleOCR-VL-1.6 (~3 GB) | ~$2 |
| **Older entry** | MacBook Air 13" M1 | 8 GB | 8 | ~70 GB/s | Llama-3.2-3B Q4_K_M (~2 GB) + BAAI/bge-m3 (~2 GB) | ~$2 |

### §11.3 — The 3 cloud options

#### §11.3.1 — Oracle Cloud Always-Free Ampere A1 ARM (with PAYG upgrade for 24 GB)

Per Oracle's official Always-Free tier + the documented PAYG workaround:

- **Without PAYG**: 2 OCPU + 12 GB RAM + 100 GB storage (the post-July 2026 reduction)
- **With PAYG upgrade**: **4 OCPU + 24 GB RAM + 200 GB storage** (the pre-reduction allocation; Oracle does NOT charge for the Always-Free resources, only for usage above the limits)
- 1,500 OCPU hours + 9,000 GB hours per month = 4 OCPU + 24 GB running 24/7
- ARM Ampere A1 architecture — most popular tools support ARM in 2026
- $0/month forever (with PAYG, as long as you stay within Always-Free limits)

5-step "Enable PAYG for the 24 GB upgrade" recipe:

```bash
# 1. Sign up at oracle.com/cloud/free with the Always-Free tier
# 2. Upgrade to Pay As You Go (Billing → Upgrade to Pay As You Go)
#    → This unlocks access to the full Always-Free allocation of 4 OCPU + 24 GB
#    → No charges as long as you stay within Always-Free limits
# 3. Provision an Ampere A1.Flex VM with 4 OCPU + 24 GB RAM in your home region
# 4. Set up Pangolin Newt on the Oracle VM (the WireGuard client that joins the cianfhoghlaim mesh)
# 5. Add the Oracle VM as a Pangolin private resource target
```

#### §11.3.2 — Google Cloud $300 free-trial credit

- $300 credit for 90 days on a new account
- Best value: `e2-highmem-4` (4 vCPU + 32 GB RAM = $0.068/hour = ~4,400 hours on $300)
- Use case: the x86 alternative to Oracle ARM; useful if your stack requires x86-only Docker images

#### §11.3.3 — The API options (Gemini 3.1 Pro vs MiniMax Token Plan)

| API | Input $/M | Output $/M | SWE-Bench Verified | Free tier | Best for |
|---|---|---|---|---|---|
| Gemini 3.1 Pro | $2.00 | $12.00 | ~78% | None (only Flash has free tier) | Long-context (>200K) |
| Gemini 3.5 Flash | $1.50 | $9.00 | n/a | None | Bulk extraction |
| **MiniMax M3** | **$0.30** | **$1.20** | **80.5%** | None | **SWE-Bench leader** |
| MiniMax M2.5 Standard | $0.15 | $1.20 | 80.2% | None | Cheapest option |

**Why MiniMax M3 wins for cianfhoghlaim specifically:**
- 80.5% on SWE-Bench Verified (the highest of any open-weight model)
- $0.30/$1.20 is 6.7× cheaper than Gemini 3.1 Pro for input tokens
- The canonical `MODEL_REGISTRY["text_llm"]["default"]` resolves to `minimax-m3` — the LiteLLM M3 chokepoint alias

### §11.4 — The canonical GGUF/MLX registry (from `meaisinfhoghlaim/models/`)

Per the `centralized-model-registry` openspec capability (post-2026-08-15) + the 2026-09-26 Firecrawl MCP research, the canonical model registry has 52 entries across 7 families.

#### §11.4.1 — Per-family features/benefits (7 paragraphs)

**text_llm (19 entries)** — covering the canonical LiteLLM M3 chokepoint (`minimax-m3` for cloud) + the local GGUF primary set (Gemma 4 + Qwen3 + DeepSeek V4 + Kimi K3 for on-device). Chosen because they cover the 3 key dimensions: SWE-Bench (coding), MMLU (general reasoning), and long-context (the 8 NCCA LC subject dossiers).

**ocr_vision (22 entries)** — covering OCR-specialised models (PaddleOCR-VL-1.6 at 96.33% OmniDocBench v1.6, dots-ocr, deepseek-ocr-2) + general VLMs (Gemma 4, Qwen3-VL-8B at 5.03 GB Q4_K_M with 32-language OCR, InternVL3, Llama-3.2-Vision). Chosen because BIEP needs both text extraction + chart/diagram understanding for the NCCA syllabus PDFs.

**embedder (5 entries)** — `BAAI/bge-m3` (1024 dim, 8192 tokens, multilingual dense+sparse+colbert), `BAAI/bge-large-en-v1.5`, `sentence-transformers/all-MiniLM-L6-v2`, `qwen3-embedding-4b`, `embeddinggemma-300m`. Chosen for the 3 size tiers matching the 3 hardware tiers.

**rerank (3 entries)** — `jina-reranker-v2-base-multilingual`, `rerank-v3.5`, `gte-rerank-v2`.

**image_gen (7 entries)** — `flux2-dev`, `z-image-turbo`, `qwen-image`, `sdxl`, `fibo`, `diffusiongemma-26b-a4b`, `qwen-image-2512`.

**voice (7 entries)** — ASR (Whisper-large, Wav2Vec2-Irish) + TTS (Chatterbox, ABA-TTS, Orpheus-TTS-3B, Sesame-CSM-1B). The Wav2Vec2-Irish is the canonical Irish ASR for the Gaeilge pipeline.

**translation (3 entries)** — Opus-MT, M2M100, NLLB. Chosen for the 3 scale tiers matching the 3 hardware tiers.

#### §11.4.2 — "Previously incorrect vs canonical" comparison

| What we previously had | What's actually in the canonical MODEL_REGISTRY | What Firecrawl research confirmed |
|---|---|---|
| "Gemma 4 26B has 84.3% SWE-Bench Verified" | The actual is **17.4%** — Google deliberately omitted SWE-bench from official benchmarks | Per independent tests (grigio.org) |
| "Qwen3.8-27B primary" | ✓ Correct — SWE-bench Pro 61.7, MTP trained | Qwen3.8-27B is the canonical primary |
| "DeepSeek V4 Pro has 80.6% SWE-Bench" | The actual is **95.2%** | DeepSeek V4 Pro is the SWE-Bench leader of open-weight |
| "Kimi K3 unspecified" | Kimi K3: 2.8T MoE, 1M context, 92.6% SWE-Bench | Moonshot AI flagship July 16, 2026 |
| "BAAI/bge-m3 is 1024 dim, 8192 tokens" | ✓ Correct | Multilingual, dense+sparse+colbert |

The journey from "previously incorrect" to "canonical" is exactly what `mise run lint:registry` catches.

#### §11.4.3 — Per-PIRP (Personal Information Retrieval Pipeline) — adapted for education

The cianfhoghlaim-specific use case (instead of cianchosaint's political-accountability pipeline):

| Subject | M4 Max 48 GB | M5 Air 16 GB | M1 Air 8 GB | Oracle ARM 24 GB | GCP x86 32 GB | Gemini API | MiniMax API |
|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| Mathematics (LC) | ✓ local | ✓ local | ✓ local | ✓ cloud | ✓ cloud | ✓ | ✓ |
| Chemistry (LC) | ✓ local | ✓ local | ✓ local | ✓ cloud | ✓ cloud | ✓ | ✓ |
| Geography (LC) | ✓ local | ✓ local | ✓ local | ✓ cloud | ✓ cloud | ✓ | ✓ |
| Gaeilge (LC) | ✓ local (Wav2Vec2-Irish) | ✓ local | ✓ local | ✓ cloud | ✓ cloud | ✓ | ✓ |
| English (LC) | ✓ local | ✓ local | ✓ local | ✓ cloud | ✓ cloud | ✓ | ✓ |
| Computer Science (LC) | ✓ local | ✓ local | ✓ local | ✓ cloud | ✓ cloud | ✓ | ✓ |
| Welsh (vernacular) | ✓ local | ✓ local | ✗ | ⚠ tight | ✓ | ✓ | ✓ |
| Scottish Gaelic (vernacular) | ✓ local | ✓ local | ✗ | ⚠ tight | ✓ | ✓ | ✓ |
| Ulster Scots (vernacular) | ✓ local | ✓ local | ✗ | ⚠ tight | ✓ | ✓ | ✓ |

#### §11.4.4 — Why centralised (the audit)

Per the 2026-09-26 Firecrawl research of BAML best practices, the canonical pattern for runtime model override is `baml_py.ClientRegistry`. The `mise run lint:registry` audit fails CI on any hardcoded model string outside `MODEL_REGISTRY`. The 12 ocr_vision models + the 20 text_llm models + the 3 embedders + the 3 rerankers all resolve via this single canonical surface.

### §11.5 — The local-inference stack (Unsloth Studio + llama-swap)

The provider chain is **LiteLLM-primary** (different from cianchosaint's Unsloth Studio primary). The local-inference path uses:

```yaml
# The canonical 12 unsloth-served models (per the 2026-08-21-unsloth-v5 change)
# Each model has a LiteLLM alias in bonneagar/stacks/litellm/config/config.yaml
# The 12 routes point at http://host.docker.internal:8888/v1 (the Unsloth Studio)
```

### §11.6 — For file processing (the BIEP use case)

The 6 LC subjects + the 3 vernaculars + the 4 Irish stages + the 8 nations run on the same hardware axes as the model table above. The 4-stage orchestration (1_ingestion → 2_materials → 3_model_lifecycle → 4_asset_generation) runs end-to-end on the M4 Max 48 GB.

### §11.7 — For code development (the dev use case)

Same 9-task table as cianchosaint, plus:
- `bun run ccc:search "X"` — the canonical semantic code search (always use before grep)
- `mise run sync:all` — the 14-layer knowledge sync loop
- `mise run core:ci` — the canonical CI gate
- `mise run data:dagster:up` — launch the Dagster UI on :3335
- `mise run ml:registry:audit` — verify all 24 VISION_MODELS are live on HF Hub

### §11.8 — Pangolin.net private self-hosted resources

The 107 Docker Compose stacks are exposed as private Pangolin resources. The `arm1-oci` (Oracle Cloud) control plane + `bunchloch` (MacBook M4) workload host. From any UK / Irish / EU laptop enrolled in Pocket ID, the analyst reaches the platform without ever exposing a public port.

### §11.9 — Mapping the cianfhoghlaim user types to the 5-axis landscape

(Adapted from the 13 user types per the existing README — teachers, students, parents, NCCA specialists, university faculty, journalists, citizens, contributors, etc.)

| User type | M4 Max 48 GB | M5 Air 16 GB | M1 Air 8 GB | Oracle ARM 24 GB | GCP $300 trial | Gemini API | MiniMax API |
|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| Teacher (secondary) | ✓ all BIEP | ✓ 6 LC flagship | ✓ 6 LC flagship (basic) | ✓ all BIEP | ✓ all BIEP | ✓ | ✓ |
| Student (LC) | ✓ all BIEP | ✓ 6 LC flagship | ✓ 6 LC flagship (basic) | ✓ all BIEP | ✓ all BIEP | ✓ | ✓ |
| Parent | ✓ all BIEP | ✓ 6 LC flagship | ✓ 6 LC flagship (basic) | ✓ all BIEP | ✓ all BIEP | ✓ | ✓ |
| NCCA subject specialist | ✓ all BIEP | ✓ 6 LC flagship | ✓ 6 LC flagship (basic) | ✓ all BIEP | ✓ all BIEP | ✓ | ✓ |
| UoG undergraduate (personal archive) | ✓ all BIEP | ✓ 6 LC flagship | ✓ 6 LC flagship (basic) | ✓ all BIEP | ✓ all BIEP | ✓ | ✓ |
| Academic researcher | ✓ all BIEP | ✓ 6 LC flagship | ✓ 6 LC flagship (basic) | ✓ all BIEP | ✓ all BIEP | ✓ | ✓ |
| Journalist | ✓ 6 LC flagship | ✓ 6 LC flagship | ✓ 6 LC flagship (basic) | ✓ 6 LC flagship | ✓ 6 LC flagship | ✓ | ✓ |
| Citizen (self-host) | ✓ all BIEP | ✓ all BIEP (offline cache) | ✓ 6 LC flagship (basic) | ✓ all BIEP | ✓ all BIEP | n/a | n/a |
| Contributor (bug hunter, dev) | ✓ all BIEP | ✓ all BIEP | ✓ 6 LC flagship (basic) | ✓ all BIEP | ✓ all BIEP | ✓ | ✓ |

### §11.10 — The "pick your subset" cheat-sheet

| Scenario | Recommendation | Why |
|---|---|---|
| **Teacher on a budget** | M5 Air 16 GB + Oracle ARM 24 GB + MiniMax Token Plan | $1,100 one-off + $0 cloud + $20/month API covers all BIEP subjects |
| **Self-hosted citizen, no cloud** | M1 Air 8 GB (used market) | The 6 LC flagship subjects + offline SQLite cache; full sovereignty |
| **Power analyst (the canonical case)** | M4 Max 48 GB + Oracle ARM 24 GB + MiniMax Token Plan | $3,500 one-off + $0 cloud + occasional API |
| **Audit-grade sovereign deployment** | M4 Max 48 GB + Oracle ARM 24 GB (no API) | 100% local + cloud; no third-party API |

---

## §12 — The dev environment: OpenSpec + openchamber.dev + mise

> **For:** Anyone extending cianfhoghlaim — adding a new DLT source, a new BAML extraction, a new agent, a new web surface, or a new openspec change.
>
> **Canonical tools:** OpenSpec (change management), openchamber.dev (browser UI), mise (task runner), opencode.json (12-MCP runtime), `.cocoindex_code/guides.yml` (12 concept guides).

### §12.1 — Why this section exists

Cianfhoghlaim was built agentically, with the dev environment deliberately exposed so users can extend it without learning a new stack. The 4 load-bearing tools: **OpenSpec** (change mgmt — 96 specs, 13 pending changes), **openchamber.dev** (UI), **mise** (task runner — 6 domain namespaces), **opencode.json** (12-MCP runtime).

### §12.2 — OpenSpec (the spec-driven change-management workflow)

The canonical workflow:

```bash
# 1. Create the change directory
mkdir -p openspec/changes/<change-id>/specs/<capability>

# 2. Write the 3 artifacts
$EDITOR openspec/changes/<change-id>/proposal.md       # why + what + impact + dependencies
$EDITOR openspec/changes/<change-id>/tasks.md          # the ordered checklist
$EDITOR openspec/changes/<change-id>/specs/<capability>/spec.md  # ADDED/MODIFIED/REMOVED Requirements

# 3. Validate --strict
openspec validate <change-id> --strict

# 4. Implement the changes
# 5. Archive the change (after deploy)
openspec archive <change-id> --yes
```

**Why it matters for education:** every change is auditable in a way that matches what an academic records office needs. The `openspec list --specs` + `openspec validate --all --strict` + `openspec archive` workflow gives the audit trail the BUSL-1.1 licence requires.

The 3 priority specs (post-2026-08-15):
- `centralized-model-registry` — the 52-entry `MODEL_REGISTRY` driving LiteLLM + BAML + agents
- `centralized-schema-registry` — BAML is the single source of truth; Pydantic + Zod are codegen
- `deployment-control-panel` — the 5-tab marimo control panel + web UI + CLI

Cross-link to `openspec/AGENTS.md` for the full workflow.

### §12.3 — openchamber.dev (the browser-based OpenCode UI)

**What it is:** Browser-based OpenCode UI built on `oven/bun:1.3.5` + React. MIT-licensed upstream at `openchamber/openchamber`. 18+ themes, persistent session state, multi-device sync via the Pangolin mesh.

#### §12.3.1 — The 5 key features that matter for cianfhoghlaim

| Feature | Why it matters for cianfhoghlaim |
|---|---|
| **Bundled-runtime vs external-runtime dual-mode** | The same image serves both `arm1-oci` (production, bundled) and `bunchloch` (your MacBook, external — the host OpenCode owns the process + MCP config) |
| **18+ themes + persistent sessions** | Long-running research sessions (the 8 NCCA LC subject dossiers, the BIEP nightly batch) need to survive browser restarts |
| **Pangolin private-resource ingress** | Every OpenChamber instance is exposed as a Pangolin private resource — Pocket ID OIDC + WireGuard means no public ports |
| **Multi-device session sync** | A teacher starts research at school, continues on the iPad on the bus, finishes at home — same OpenChamber session |
| **Provider picker (OpenAI / Anthropic / OpenAI-compatible)** | Maps directly to the cianfhoghlaim 7-tier `minimax` LiteLLM chokepoint alias |

#### §12.3.2 — Capabilities alongside bonneagar + the dev setup

| openchamber.dev capability | How it uses the bonneagar stack |
|---|---|
| Browser chat with the AG-UI chat window | Routes through the `litellm` stack → falls through to the `unsloth-serve` stack → the `pangolin` private resource target → `host.docker.internal:8888` on your Mac |
| Persistent session state | Backed by the `locket` sidecar-injected SQLite volume |
| Multi-device sync | Goes through the `pangolin` Newt WireGuard tunnel; the `pocket-id` OIDC layer authenticates every device |
| MCP tool calls (firecrawl / ccc / cognee / etc.) | Routed through the `opencode.json` 12-MCP runtime |
| Provider switching | Driven by `MODEL_REGISTRY` + `baml_src/clients.baml`; the OpenChamber UI reads the same `deployment-choice.yaml` toggle |

#### §12.3.3 — How to add openchamber.dev to your deployment

```bash
cd bonneagar/stacks/openchamber
locket inject -- docker compose up -d
# (bunchloch only) Configure external-runtime mode
export OPENCODE_HOST=http://host.docker.internal:4096
export OPENCODE_PORT=4096
export OPENCODE_SKIP_START=true
open https://openchamber.cianchosaint.ie
```

### §12.4 — mise (the 107-task namespaced workflow)

The 6 domain namespaces: `core:`, `lint:`, `sync:`, `openspec:`, `devops:`, `data:`, `ml:`, `web:` (post-2026-08-19).

The 3 tasks a new user runs on day 1:

```bash
mise run sync:all                    # 14 sync layers
mise run core:ci                     # canonical CI gate
mise run openspec:validate-all       # 131 items pass
```

The 5 most useful daily tasks:

```bash
mise run data:dagster:up             # Dagster UI on :3335
mise run data:biep:milestone -- 1    # BIEP v3 milestone m1
mise run ml:registry:audit           # verify all 24 VISION_MODELS live on HF
mise run web:dev tuatha-ui           # per-app dev server
mise run devops:validate-stacks      # all 89 Docker Compose stacks
```

### §12.5 — `opencode.json` + the `.cocoindex_code/guides.yml` (the dual-search)

The 12-MCP runtime (per the 2026-08-21 MCP revival): ccc + firecrawl + crawl4ai + chrome + dlt-workspace + motherduck + cognee + graphiti + design-system + langfuse + infisical + huggingface.

The `.cocoindex_code/guides.yml` ships with 12 concept guides (each maps a high-level concept to the canonical files). When a search query matches a guide's description, `ccc:search` returns a `[guide]` hit pointing the user at the canonical set.

**Why dual-search matters for education:** every Firecrawl call MUST be paired with a `ccc:search` so both tool names appear in the Langfuse trace (the audit trail the licence requires).

### §12.6 — The 5 dispatchable opencode subagents

| Subagent | When to dispatch |
|---|---|
| `data-platform` | Adding a new DLT source + a BAML extraction + a CocoIndex flow |
| `infrastructure` | Adding a new Docker Compose stack to `bonneagar/stacks/` |
| `agent-platform` | Adding a new agent or specialist |
| `frontend-apps` | Adding a new web surface |
| `research` | BrowserBase + Firecrawl + CCC + Cognee + change-detection |

### §12.7 — The 16 domain packages — features/benefits/usage

Same 16-package table as cianchosaint §12.7 (with education-specific usage examples).

---

## Licensing

Business Source License 1.1 — see [`LICENSE.md`](LICENSE.md). Granted
for non-commercial, non-profit, cultural preservation, and academic
research use within the legal jurisdictions of Ireland, Northern
Ireland, the United Kingdom, the European Union, the British Isles,
the Commonwealth, the Crown, the United States of America, Mexico,
Brazil, Taiwan, Tibet, Nepal, South Korea, Japan, and China.

**Excludes**: sanctioned organisations, paramilitary groups, entities
in violation of international human rights conventions. **Change
Date**: 4 years from publication. **Change License**: AGPL v3.0.

---

## Quick start for new operators

> **Start here.** The canonical onboarding doc is [`NEW-USER-ONBOARDING.md`](NEW-USER-ONBOARDING.md) (~380 lines: 1-command setup + the 10-step cluster bringup + the 12-MCP verification checklist + the 3 secrets + the troubleshooting FAQ). The 60-second quick path is [`CHEATSHEET.md`](CHEATSHEET.md).

The per-stack onboarding scripts (Pocket ID + Komodo + Pangolin
for the auth mesh; Tuatha + SpacetimeDB for the educational MMO)
live in their respective hub READMEs rather than the root, to keep
this entry-point scannable:

- **Pocket ID + Komodo + Pangolin** (single-Passkey login mesh) → [`AGENTS.md` § opencode-safety](AGENTS.md#opencode-safety) + [`bonneagar/README.md`](bonneagar/README.md)
- **Tuatha Educational MMO** (Babylon.js + FastAPI + TanStack UI) → [`tuatha/README.md`](tuatha/README.md)
- **BIEP data platform** (DLT + Dagster + BAML + CocoIndex + MotherDuck) → [`orchestration/README.md`](orchestration/README.md) + [`dlt_sources/DATA_PLATFORM_ROUTER.md`](dlt_sources/DATA_PLATFORM_ROUTER.md)
- **Self-host a fresh cluster** → [`bonneagar/README.md`](bonneagar/README.md) (the 6-step operator quick start)
- **Onboarding wizard** (the 3-credentials TUI) → [`scripts/onboard-pocketid.sh`](scripts/onboard-pocketid.sh)

---

## Cianfhoghlaim-Nua V6 Era (2026-09-01) — What shipped

> **Cianfhoghlaim-Nua** ("new Cianfhoghlaim") is the consolidated platform target. The V6 era (2026-09-01) shipped **19 openspec changes** + **~10,000 LOC** that lift the GCP-first `gemini_hackathon/` sister-repo learnings into the canonical OSS-first `cianfhoghlaim/` substrate. The 5-pillar pattern: **BAML → Convex → A2UI → Hono → React**.

### 10 phases shipped (Phases 0-9)

| # | Phase | Openspec change | Key surface |
|--:|--|--|--|
| 0 | OpenSpec scaffolding | 7 changes (1 Phase 1 umbrella + 6 sister-side mirrors) | `openspec/changes/2026-09-01-{ci...}-*` |
| 1 | End-to-end showcase (4 subjects) | [`2026-09-01-cianfhoghlaim-nua-end-to-end-showcase-v1/`](openspec/changes/2026-09-01-cianfhoghlaim-nua-end-to-end-showcase-v1/) | `baml_src/british_isles/_shared/study_plan.baml` + `agents/adk/subjects/lc/planner.py` |
| 0.5 | BAML regeneration (343+ parser errors fixed) | [`2026-09-01-baml-regeneration-blocker-v1/`](openspec/changes/2026-09-01-baml-regeneration-blocker-v1/) | `baml_client/` regenerated; all Phase 1 BAML functions reachable |
| 2 | A2UI v0.9 catalog (11 components) | [`2026-09-01-cianfhoghlaim-nua-a2ui-catalog-v1/`](openspec/changes/2026-09-01-cianfhoghlaim-nua-a2ui-catalog-v1/) | `web/packages/a2ui/` |
| 3 | Web consolidation (5 apps → 1) | [`2026-09-01-cianfhoghlaim-nua-web-consolidation-v1/`](openspec/changes/2026-09-01-cianfhoghlaim-nua-web-consolidation-v1/) | `web/apps/cianfhoghlaim-nua/` |
| 4 | NCCE showcase (5 PDFs + 48 equivalencies + 12 pedagogy) | [`2026-09-01-cianfhoghlaim-nua-biep-ncce-showcase-v1/`](openspec/changes/2026-09-01-cianfhoghlaim-nua-biep-ncce-showcase-v1/) | `baml_src/british_isles/uk_ncce/learning_graph.baml` + `cocoindex_flows/uk_ncce/learning_graphs_app.py` |
| 5 | BAML/CocoIndex/DLT hardening | (partial) FTS index added to `ireland_lc_factory.py` | `cocoindex_flows/biep_parity/ireland_lc_factory.py:139-141` |
| 6 | Oral study plans (Pipecat + TTS router) | [`2026-09-01-cianfhoghlaim-nua-oral-study-plans-v1/`](openspec/changes/2026-09-01-cianfhoghlaim-nua-oral-study-plans-v1/) | `agents/api/_oideachais_api/services/{pipecat_client,tts_router}.py` + `web/packages/a2ui/src/components/OralStudyPlayer.tsx` |
| 7 | LC/JC certificate pipeline (7 stages) | [`2026-09-01-cianfhoghlaim-nua-certificate-pipeline-v1/`](openspec/changes/2026-09-01-cianfhoghlaim-nua-certificate-pipeline-v1/) | `meaisinfhoghlaim/certificate/` + `baml_src/british_isles/ireland/education/certification.baml` |
| 8 | Sister-side mirrors (6 per-sister transfers) | [`2026-09-01-sister-side-mirrors-v1/`](openspec/changes/2026-09-01-sister-side-mirrors-v1/) | `openspec/changes/2026-09-01-{bonneagar,tuatha,ciancheiltis,ciandlithe,cianchosaint,gemini-hackathon}-sister-umbrella-mirror-v1/` |
| 9 | GCP opt-in completion (6 mirror stacks) | [`2026-09-01-gcp-opt-in-completion-v1/`](openspec/changes/2026-09-01-gcp-opt-in-completion-v1/) | `bonneagar/stacks/gcp-*/` (6 stacks) |
| 10 | V7 from-the-ground-up | [`2026-09-01-v7-from-the-ground-up-v1/`](openspec/changes/2026-09-01-v7-from-the-ground-up-v1/) (DEFERRED) | 5-pillar pattern + 3 REDUCED ops surface (documented) |

### 10 follow-on Steps (Steps 0-9 of the Phase 11+ roadmap)

Per the operator's direction (2026-09-01), the v6 era plan was extended with 10 follow-on steps to close the feature parity gaps:

| # | Step | Openspec change | What |
|--:|--|--|--|
| S0 | Phase 3 web consolidation fix | [`2026-09-01-cianfhoghlaim-nua-web-consolidation-completion-v1/`](openspec/changes/2026-09-01-cianfhoghlaim-nua-web-consolidation-completion-v1/) | 7 missing skeleton files + 4 Hono mounts + 5 archives |
| S1 | DLT path drift fix | [`2026-09-01-dlt-path-drift-fix-v1/`](openspec/changes/2026-09-01-dlt-path-drift-fix-v1/) | 137-file bulk update (Wave 1 path) |
| S2 | Ireland LC completion | [`2026-09-01-cianfhoghlaim-nua-ireland-lc-completion-v1/`](openspec/changes/2026-09-01-cianfhoghlaim-nua-ireland-lc-completion-v1/) | 8 NCCA-adjacent + physics BAML + 16 Convex tables + 2 early-years CocoIndex Apps |
| S3 | Firecrawl England source discovery | [`2026-09-01-firecrawl-england-source-discovery-v1/`](openspec/changes/2026-09-01-firecrawl-england-source-discovery-v1/) | 7 official sources + England DLT scaffold |
| S4-S8 | 5-jurisdiction completion | [`2026-09-01-cianfhoghlaim-nua-5-jurisdiction-completion-v1/`](openspec/changes/2026-09-01-cianfhoghlaim-nua-5-jurisdiction-completion-v1/) | EN + WL + NI + IM + SC BAML (5 Extract<Jurisdiction>SubjectSpec functions + 4 vernacular overlay classes) |
| S9 | Vernacular language pipelines | [`2026-09-01-cianfhoghlaim-nua-v7-vernaculars-v1/`](openspec/changes/2026-09-01-cianfhoghlaim-nua-v7-vernaculars-v1/) | 7 vernacular BAMLs (Welsh + Scottish Gaelic + Breton + Cornish + Manx + Channel Islands French × 2 + Ulster Scots) |

### Quick validation

```bash
# 18 tests, all green
uv run pytest tests/test_adk_subject_actions.py tests/test_phase7_certificate_pipeline.py -v

# 19 openspec changes, all valid
for d in openspec/changes/2026-09-01-*/; do
  uv run openspec validate "$(basename $d)" --strict
done

# 22 BAML functions newly reachable (per the Step 4-8 + Step 9 adds)
uv run python -c "
from baml_client.baml_client.sync_client import b
fns = ['GenerateStudyPlanAssets', 'GenerateOralStudyPlan', 'ExtractNCCAPolicyCriteria', 'Extract<6 NCCE subjects>', 'Extract<6 per-subject marking schemes>', 'ExtractEnglandSubjectSpec', 'ExtractWalesSubjectSpec', 'ExtractNorthernIrelandSubjectSpec', 'ExtractIsleOfManSubjectSpec', 'ExtractScotlandSubjectSpec', 'ExtractWelshSubjectSpec', 'ExtractScottishGaelicSubjectSpec', 'ExtractManxSubjectSpec', 'ExtractBretonSubjectSpec', 'ExtractCornishSubjectSpec', 'ExtractJerseyFrenchSubjectSpec', 'ExtractGuernseyFrenchSubjectSpec', 'ExtractUlsterScotsSubjectSpec']
for f in fns:
    fn = f.replace('<6 NCCE subjects>', 'ComputerScienceLearningGraph').replace('<6 per-subject marking schemes>', 'AccountingMarkingScheme')
    if hasattr(b, fn): print(f'  ✓ {fn}')
"
```

### Phase 1 quick path: chat-with-syllabus → study-plan → oral-delivery

```bash
# 1. Open the consolidated app
cd web/apps/cianfhoghlaim-nua && bun install && bun dev

# 2. Visit /lc/chemistry/study-plan
# 3. The Phase 1 BAML function is reachable
uv run python -c "from baml_client.baml_client.sync_client import b; print(b.GenerateStudyPlanAssets)"
```

---

<!-- AGENT_TELEMETRY_START -->
> **Agent Telemetry (Last Updated: 2026-07-29 22:30:52 UTC)**
> - **Total Cached Structural Documents:** 0
> - **Examinations.ie Cache:**        0 files
> - **NCCA.ie Cache:**        0 files
> - **CurriculumOnline Cache:**        0 files
<!-- AGENT_TELEMETRY_END -->
