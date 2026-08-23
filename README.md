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
from dlt_sources._lakehouse import register_personal_archive_tables
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
| bonneagar (in-tree) | `bonneagar/` | (was `github.com/cianfhoghlaim/bonneagar`; now archived) | The 93-stack GitOps fleet + Komodo + Pangolin + Infisical |
| leabharlann (separate) | `leabharlann/` symlink / 3.4 GB checkout | [`github.com/cianfhoghlaim/leabharlann`](https://github.com/cianfhoghlaim/leabharlann) | The digital library corpus that grounds every BAML schema + CocoIndex flow |

The `archive-bonneagar` remote at
`github.com/cianfhoghlaim/bonneagar.git` is frozen — no further
commits will be pushed; its history is preserved in-tree.

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

<!-- AGENT_TELEMETRY_START -->
> **Agent Telemetry (Last Updated: 2026-07-29 22:30:52 UTC)**
> - **Total Cached Structural Documents:** 0
> - **Examinations.ie Cache:**        0 files
> - **NCCA.ie Cache:**        0 files
> - **CurriculumOnline Cache:**        0 files
<!-- AGENT_TELEMETRY_END -->
