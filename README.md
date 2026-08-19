# Cianfhoghlaim — Coláiste na Déisigh

> **Cianfhoghlaim** — *long-distance, enduring learning*. A research-and-deployment platform for the **British Isles education corpus** (8 nations × 5 stages × bilingual Goidelic + Brythonnic), agentic AI, self-hosted infrastructure, and minority-language machine learning. Maintained by **Cian Mac an Déisigh Uí Liatháin (Deacy-Lyons)**.

[![Leabharlann](https://img.shields.io/badge/leabharlann-2.4k_files_/_3.4_GB-blueviolet)](https://github.com/cianfhoghlaim/leabharlann)
[![Bonneagar](https://img.shields.io/badge/bonneagar-IN_THIS_REPO_(%2Fbonneagar%2F)-green)](./bonneagar/)
[![License](https://img.shields.io/badge/license-BUSL_1.1-green)](LICENSE.md)

> **External references** for the technologies used throughout: [CocoIndex](https://cocoindex.io/), [dlt](https://dlthub.com/docs/), [LanceDB](https://lancedb.com/), [DuckDB](https://duckdb.org/docs/), [MotherDuck](https://motherduck.com/docs/), [Komodo](https://komo.do/), [Pangolin](https://docs.pangolin.net/).

## Addendum — a note for anyone looking at this project right now

> **The project is sprawling on purpose.** It's a research-and-deployment
> platform for the British Isles education corpus, an agentic AI fleet, a
> self-hosted infrastructure mesh, and a minority-language ML playground —
> all federated by a single `bun + uv + turbo` monorepo. The goal is a
> deliberately overcomplicated Master's completed in a year, so many
> working subsystems are partially obscured by choices meant for *my*
> team's downstream use.
>
> **The value for anyone looking at this project today is in the specific
> combinations of already well-calculated open-source packages.** The
> data engineering (DLT + Dagster + BAML + CocoIndex + DuckLake + LanceDB
> + MotherDuck + Marimo), the DevOps (Komodo + Pangolin + Infisical +
> Locket + Pocket ID + Traefik + Garage S3), the web development
> (TanStack Start + Convex + Hono + CopilotKit + oRPC + AG-UI +
> Cloudflare), and the agent layer (Agno + Google ADK + Pydantic AI +
> LiteLLM + Letta + Cognee + Graphiti + Langfuse + MLflow) are each real,
> working open-source compositions. You can copy any slice independently.
>
> **You can take the same data pipelines and rewire them for any other
> jurisdiction.** The `dlt_sources/` + `baml_src/` + `cocoindex_flows/` +
> `motherduck/` + `notebooks/` stack already produces the official legal,
> medical, education, and government documents for the British Isles.
> Retargeting it means changing the jurisdiction enum, the BAML schemas,
> the scrape cache roots, and the destination namespaces — the core
> pipeline shape stays the same.
>
> **The full per-area deep-cuts report** — what each package composes,
> which files to copy, which assumption is hardest to escape — lives at
> [`docs/CHOP_AND_CHANGE_GUIDE.md`](docs/CHOP_AND_CHANGE_GUIDE.md).

---

> ## ⚠️ Important disclaimer
>
> The **data engineering pipelines** — DLT ingestion, BAML extraction,
> CocoIndex v1 embeddings, Cognee cognify passes — process official
> government syllabus, exam paper, and marking scheme material of the
> Republic of Ireland (NCCA Leaving Certificate, Junior Cycle, Primary)
> and the wider British Isles education system. They are grounded in
> the **8 British Isles nations** (Ireland, England, Scotland, Wales,
> Northern Ireland, Isle of Man, Jersey, Guernsey) and bilingualised in
> EN + GA (Gaeilge).
>
> The **web UIs** (`cianfhoghlaim-web`, `tuatha-ui`, `croilar-web`, and
> siblings) are packaged demos that prove the agentic-web wiring works.
> They are **not yet** the final pedagogical surface.
>
> To self-host your own instance you need your own domain name and a
> free Cloudflare account — see [`bonneagar/README.md`](bonneagar/README.md).

## TL;DR — what this is, today

`cianfhoghlaim` is a **polyglot monorepo** (`bun + uv + turbo`) that:

1. **Ingests** the curriculums, exam papers, marking schemes, and
   syllabi of the 8 British Isles nations (with bilingual EN + GA
   extraction for the Irish strand).
2. **Extracts** structured data via BAML schemas (NCCA, SEC, CCEA,
   SQA, WJEC, Edexcel + European Union + Commonwealth + Americas
   expansions).
3. **Embeds** in vector + graph form via CocoIndex v1 Apps + Cognee
   cognify layers + the Graphiti temporal knowledge graph.
4. **Surfaces** through marimo reactive notebooks, MotherDuck Dives,
   TanStack Start web apps, and an agent fleet (LiteLLM-routed).
5. **Hosts itself** on a self-managed Docker Compose + Komodo GitOps +
   Pangolin reverse-proxy mesh — see [`bonneagar/README.md`](bonneagar/README.md).

The author is a Mathematics & Education teacher / Dioplóma C1 in Irish /
agentic-AI engineer based in Galway and East Belfast. Verified
credentials, teaching registration, and family history are recorded at
[`cian_mac_an_déisigh_uí_liatháin/`](cian_mac_an_déisigh_uí_liatháin/).

## Monorepo topology (v7 — flattened polyglot)

Two language graphs live side by side, orchestrated by `turbo.json` and
a single `mise.toml` toolchain. Post-v7 (2026-07-17), the Python
package IS the repo root — no `cianfhoghlaim/` nesting.

### TypeScript graph (bun workspaces)

| Workspace | Path | Purpose |
|:--|:--|:--|
| `cianfhoghlaim-web` | `web/apps/cianfhoghlaim-web/` | TanStack Start + React front-end (the public web app) |
| `cianfhoghlaim` | `web/apps/cianfhoghlaim/` | A second TanStack Start front-end |
| `cianfhoghlaim-leaving-cert` | `web/apps/cianfhoghlaim-leaving-cert/` | The Leaving Cert portal (its own nested sub-monorepo) |
| `cianfhoghlaim-mmo` | `web/apps/cianfhoghlaim-mmo/` | The Tuatha Celtic-mythology MMO client |
| `tuatha-ui` | `web/apps/tuatha-ui/` | Túatha educational MMO front-end |
| `croilar-web` | `web/apps/croilar-web/` | Croílár multi-persona portfolio |
| `croilar-portal` | `web/apps/croilar-portal/` | Croílár portfolio dashboard |
| `oideachais-dashboard` | `web/apps/oideachais-dashboard/` | Education-data dashboard |
| `hono-api` | `web/hono-api/` | Hono API gateway |
| `ui-kit` + 3 `@croilar/*` sub-packages | `web/packages/ui-kit/` | Shared UI components; `analytics`/`config`/`i18n` are independent scoped packages nested inside it |
| `auth`, `db` | `web/packages/{auth,db}/` | Shared auth + DB clients |

### Python sub-packages (uv at root)

| Sub-package | Path | Purpose |
|:--|:--|:--|
| `agents` | `agents/` | The agent fleet — see [`agents/README.md`](agents/README.md) |
| `baml_src` | `baml_src/` | BAML extraction schemas (LC + Celtic + multi-nation) |
| `cocoindex_flows` | `cocoindex_flows/` | CocoIndex v1 embedding Apps (renamed from `cocoindex/` 2026-08-19 — the old name shadowed the installed `cocoindex` library) |
| `dlt_sources` | `dlt_sources/` | DLT sources + destinations |
| `orchestration` | `orchestration/` | Dagster assets + jobs + schedules + sensors — see [`orchestration/README.md`](orchestration/README.md) |
| `meaisinfhoghlaim` | `meaisinfhoghlaim/` | OCR/HTR/alignment sub-package — see [`meaisinfhoghlaim/README.md`](meaisinfhoghlaim/README.md) |

### IaC subdirectory

The GitOps infrastructure lives in `bonneagar/` and is reached via
`bun run --cwd bonneagar iac:<command>` from the root `package.json`.
It is no longer a separate GitHub repo. See
[`bonneagar/README.md`](bonneagar/README.md) for the full architecture,
implementation decisions, and a 6-step operator quick start.

## British Isles Education Pipeline (BIEP) — the flagship

The 6 Irish LC priority subjects — Mathematics, Chemistry, Geography,
Gaeilge, English, Computer Science — get the deep treatment: NCCA
syllabus + SEC exam papers + marking schemes, CocoIndex flows, marimo
notebooks, and MotherDuck Dives.

The BAML extraction schemas (`baml_src/british_isles/ireland/education/lc_extraction/`)
produce structured `LeavingCertSyllabus`, `LeavingCertPastPaper`,
`LeavingCertMarkingScheme` objects, rubric-anchored to NCCA PDF page
references.

## The agent fleet

13 root agents (routed via `agents/agent_registry.py`) plus 8 NCCA
subject specialists, all routed through LiteLLM. See
[`agents/README.md`](agents/README.md) for the architecture, the
framework choices, and how to lift a single agent out independently.

## Centralized registries

The platform maintains one canonical source of truth per concern:

- [`meaisinfhoghlaim/models/registry.py`](meaisinfhoghlaim/models/registry.py) — the OCR/vision model registry
- [`meaisinfhoghlaim/models/model_registry.py`](meaisinfhoghlaim/models/model_registry.py) — the broader cross-family model registry (in progress; not yet the sole source — see [`meaisinfhoghlaim/README.md`](meaisinfhoghlaim/README.md#known-gaps))
- [`notebooks/_shared/schema.py`](notebooks/_shared/schema.py) — schema introspection helpers
- [`notebooks/00_control_panel.py`](notebooks/00_control_panel.py) — the marimo control panel (Models / Pipelines / Datasets / Stacks / Registry)
- [`deployment-choice.yaml`](deployment-choice.yaml) — the canonical enablement file

Full guide: [`.agents/skills/centralized-registry/SKILL.md`](.agents/skills/centralized-registry/SKILL.md).

## Verified academic archive (leabharlann)

Course material, examination scripts, and the personal academic corpus
live at `github.com/cianfhoghlaim/leabharlann` — a separate 3.4 GB
repo, the only remaining separately-managed repo. The
`archive-bonneagar` remote (`github.com/cianfhoghlaim/bonneagar.git`)
is a frozen, read-only relic of the pre-v7 layout; its history is
preserved in-tree here.

## Cross-cutting concerns

**OpenSpec** (`openspec/`) is the single source of truth for capability
specs: `list → write proposal/tasks/spec deltas → validate --strict →
implement → archive`. 32 changes are currently pending under
`openspec/changes/`. See [`openspec/AGENTS.md`](openspec/AGENTS.md) for
the full workflow and [`openspec/project.md`](openspec/project.md) for
conventions.

**Secrets management** — the 3-way contract (Infisical vault source of
truth → `.infisical.env` template → `.env` gitignored, hydrated by
mise + Locket) is documented in
[`bonneagar/SECRETS-MANAGEMENT.md`](bonneagar/SECRETS-MANAGEMENT.md).

**Semantic code search** — `mise run ccc:search "<query>"` (CocoIndex
BGE-M3 embeddings, backed by `cocoindex_flows/`) for finding code by
meaning across this repo's ~7,000 tracked files. `cognee cognify` for
the knowledge-graph memory layer.

**How this project is developed** — agentically. See [`AGENTS.md`](AGENTS.md)
for the durable rules Claude Code (and other coding agents) follow in
this repo.

## Licensing

Business Source License 1.1 — see [`LICENSE.md`](LICENSE.md). Granted
for non-commercial, non-profit, cultural preservation, and academic
research use. Change Date: 4 years from publication. Change License:
AGPL v3.0.

## Family history

The full family history — the Deacy/Lyons/Morris/Conroy lineage, the
Tuatha educational MMO's Ard-Rí na hÉireann framing — is preserved at
[`cian_mac_an_déisigh_uí_liatháin/FAMILY_HISTORY.md`](cian_mac_an_déisigh_uí_liatháin/FAMILY_HISTORY.md)
(moved out of this README during the 2026-08 docs consolidation so the
entry point stays scannable).

<!-- AGENT_TELEMETRY_START -->
> **Agent Telemetry (Last Updated: 2026-07-29 22:30:52 UTC)**
> - **Total Cached Structural Documents:** 0
> - **Examinations.ie Cache:**        0 files
> - **NCCA.ie Cache:**        0 files
> - **CurriculumOnline Cache:**        0 files
<!-- AGENT_TELEMETRY_END -->
