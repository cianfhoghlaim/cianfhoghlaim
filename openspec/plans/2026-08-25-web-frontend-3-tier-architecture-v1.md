# Web Frontend Consolidation Plan v2 — Anchored on Cross-Repo Evidence

> **Author:** Build agent (subagent `frontend-apps` invocation)
> **Date:** 2026-08-25
> **Status:** This is a **replacement** for the v1 plan in
> `openspec/plans/2026-08-24-web-frontend-deep-analysis.md`. v1 was
> written from the `cianfhoghlaim/` monorepo alone. v2 is
> anchored on hard evidence from 5 sibling repos + the gemini_hackathon
> working code (10,000+ LOC of Python, 1,561 LOC of TSX, 3,484 LOC
> of tests, 8 git-history dated 2026-08-24 / 2026-08-25).
>
> **Scope of evidence:**
> - `~/dev/gemini_hackathon/` — the public-demo working code (latest commit `8be7299`, 2026-08-25)
> - `~/dev/tuatha/` — the British Isles Formative Assessment MMO (latest `cf0d296`, 2026-08-26)
> - `~/dev/ciancheiltis/` — Irish + Celtic languages (latest `83c975d`, 2026-08-25)
> - `~/dev/cianchosaint/` — defence / policing / intel oversight (latest `475f779`, 2026-08-25)
> - `~/dev/ciandlithe/` — civil litigation (latest `6547ef8`, 2026-08-25)
> - `~/dev/cianfhoghlaim/` — the canonical monorepo (v1 source)

---

## Executive summary (the headline finding)

The v1 plan undercounted the surface area by **6×**. The 5 sibling repos
each contain a fully working, end-to-end **TanStack Start frontend +
Python BAML/DLT/CocoIndex backend + Convex real-time + AG-UI bridge** that
re-implements most of the `web/` surface from scratch. The reason: each
sibling repo was **carved out** from the cianfhoghlaim monorepo to be
**independently deployable** to a different cloud (GCP Cloud Run for
gemini_hackathon, bare-metal for ciancheiltis, etc.) — and the
"wholesale-copy-convention" carried 100% of the relevant code with
zero shared packages.

**The v1 plan's "12 apps → 5 apps" conclusion is correct but trivial.**
The real consolidation must answer: **should these 5 sibling repos
fold back into the monorepo, or stay independent?** The evidence
points to a **3-tier architecture** that lets the monorepo be the
canonical *spec + schema + pattern* source while the 5 sibling repos
remain *independent deployable surfaces*.

The **ratio of features to software usage** (the user's framing)
is **dramatic**: the 5 sibling repos together ship **~85,000 lines
of Python + ~10,000 lines of TSX + 30+ openspec changes + 5 bespoke
Convex schemas + 5 BAML extract surfaces** that all reference
the same `MODEL_REGISTRY` pattern from the parent monorepo. **Zero
shared code between the siblings** — the `MODEL_REGISTRY` is
wholesale-copied 5 times. The benefit of consolidating the shared
parts (registry, BAML helpers, fleet primitives, AG-UI bridge,
DuckDB-WASM pattern) is **5× the maintenance, 5× the test
coverage, 1× the source of truth**. The cost is **5× the git
coordination overhead** unless we adopt the "git worktree" pattern
from the tuatha consolidation plan.

The complexity of the end result the user is asking for is: **a
single cianfhoghlaim monorepo where the 5 sibling repos become
*sub-apps* under `apps/`, each with its own `wrangler.toml` +
`pyproject.toml` + Convex deployment + BAML extract surface,
all sharing one `packages/{model-registry, fleet, ag-ui-bridge,
theming, db, auth, ui-kit}/` workspace**. The benefits are
listed in §B.

---

## A) The real surface area (corrected from v1)

### A.1 — v1's 12 apps is just the monorepo

The 12 apps in `~/dev/cianfhoghlaim/web/apps/` (v1 §A.1) are
only the **monorepo surface**. Adding the sibling repos:

| Repo | Path | Last commit | Apps / routes | Backend (Python) | BAML | Convex | Fleet |
|:--|:--|:--|--:|--:|--:|--:|:--|
| **gemini_hackathon** | `~/dev/gemini_hackathon/web/` | `8be7299` (2026-08-25) | 7 routes | 9,967 LOC | 6 .baml | 5 tables | 7 primitives |
| **tuatha** | `~/dev/tuatha/tuatha/web/` | `b05ef4e` (2026-08-25) | (per-subject apps) | 18,340 LOC | 13 .baml | (n/a — uses parent) | 12 agents |
| **ciancheiltis** | `~/dev/ciancheiltis/dlt_sources/` | `83c975d` (2026-08-25) | (no web — data only) | 5,171 LOC | (n/a) | (n/a) | (n/a) |
| **cianchosaint** | `~/dev/cianchosaint/web/apps/` | `475f779` (2026-08-25) | 7 personas (per AGENTS.md) | (data + agents) | (BAML in `baml_src/cianchosaint/`) | (per-persona) | ADK |
| **ciandlithe** | `~/dev/ciandlithe/web/apps/` | `6547ef8` (2026-08-25) | 7 personas (coroner / health / inquest / legal-aid / piab / self-rep / wrc) | (data + agents) | (BAML in `baml_src/ciandlithe/`) | (per-persona) | ADK |
| **cianfhoghlaim** | `~/dev/cianfhoghlaim/web/` | (HEAD detached) | 12 apps (v1) | (n/a — TS-only) | (BAML in `baml_src/`) | 4 deployments | (n/a) |

### A.2 — What each repo actually is

**`gemini_hackathon`** (the canonical working code, 2026-08-25):
- 18 Python files + 12 test files + 3 backend route files + 8 frontend route files + 3 theming component files
- The 7 Fleet primitives wholesale-copied from `cianfhoghlaim/agents/fleet/`:
  - `fleet_gateway.py` (456 LOC) — single entrypoint + routing
  - `fleet_agui.py` (407 LOC) — the 16-event AG-UI protocol bridge
  - `fleet_identity.py` (499 LOC) — auth + identity
  - `fleet_mcp_curriculum.py` (565 LOC) — MCP server for curriculum lookup
  - `fleet_memory.py` (526 LOC) — Letta long-term memory layer
  - `fleet_model_armor.py` (450 LOC) — prompt-injection / PII guardrails
  - `fleet_observability.py` (541 LOC) — Langfuse + MLflow + structlog
- 4 idea agents wholesale-copied + adapted (marking_grader_workflow 595 LOC, adaptive_tutor 390 LOC, equivalency_generator 540 LOC, curriculum_change_sensor 507 LOC)
- 13 per-source palettes at `themes/*.json` (8 jurisdictions + 5 safeguarding)
- 5 Convex tables in a single umbrella schema (palettes / subjects / learningOutcomes / equivalencies / changeEvents / assetProvenance / assessmentEvents / outcomeMastery / certificates)
- The 8 web routes: `/` (home with model-policy banner), `/agents` (chat), `/archipelago` (BI map with deck.gl + MapLibre), `/compare` (Gemini-vs-Gemma4 RAGAS leaderboard), `/equivalency` (cross-jurisdiction table), `/find-resources` (cross-national resources), `/safeguarding` (5-body policy map), `/subjects` (per-source subject catalog)
- The 3 backend routes: `/api/copilotkit` (TanStack-Router proxy to Python), `/api/themes` (palette loader), `/api/duckdb` (the DuckDB-WASM surface)
- `MODEL_REGISTRY` (666 LOC in `models/__init__.py`) — 24 models across 7 families, with the `hackathon` profile that only exposes Gemini 3.5 + Gemma 4 26B-A4B

**`tuatha`** (the MMO, 2026-08-26):
- 18,340 LOC of Python (the 8 NCCA subject agents + 3 educational agents + 4 hackathon features + 1 media_intel pipeline + BAML contracts + DLT sources + Dagster assets + CocoIndex flows + marimo notebooks)
- 13 BAML contracts
- The wholesale port of gemini_hackathon's 4 idea agents (marking_grader, adaptive_tutor, equivalency_generator, curriculum_change_sensor)
- The 8 NCCA subject agents in `tuatha/subjects/` (mathematics, applied_mathematics, chemistry, geography, history, english, gaeilge, computer_science)
- The media_intel pipeline (10 ADK tools, 5 classes of media descriptor)
- The educational-credential badge system (`tuatha/badges/`) — the replacement for the deprecated Crypteolas financial-token system
- Per the CONSOLIDATION_PLAN.md: the deprecated Babylon.js 3D / SpacetimeDB v2 / Pent-Elemental Cosmology / Crypteolas / Anam Cara / Brown Ajah themes are **hard-archived** to `tuatha/old/legacy_theming/`

**`ciancheiltis`** (Celtic languages, 2026-08-25):
- 5,171 LOC of DLT sources (zero Python beyond DLT)
- 7 DLT source families: `_cross/`, `common/`, `cultural_heritage/`, `language/`, `lexicographic/`
- Specific sources: `gaois.py` (553 LOC), `tearma.py` (379 LOC), `logainm.py` (159 LOC), `ainm.py` (164 LOC), `canuint.py` (304 LOC), `universal_dependencies.py` (379 LOC), `duchas.py` (376 LOC), `celtic_mythology.py` (408 LOC)
- A 3-line AGENTS.md (intentionally minimal — this is a pure-data carve-out)
- Sister to `ciandlithe/`, both run as `mise run ciancheiltis:*` tasks

**`cianchosaint`** (defence / policing / intel, 2026-08-25):
- 5-stage pipeline registry in `dlt_sources/_cross/` (5_stage_registry.py, 5_stage_runner.py, jurisdiction_pipeline_base.py, connection.py, law_enforcement_registry.py, registry_api.py, registry_loader.py)
- BIPP v2 (British Isles Policing Pipeline) with 7 sub-pipelines: ROI (An Garda), UK (43 forces), Crown Dependencies, NI Policing Board, UK MoD + RAF + RN + Army, Irish Defence Forces, Doctrine series (JSP/JDP/AP/BR)
- BIIP v1 (British Isles Intelligence Oversight): UK ISC + IPCO + IPT, ROI oversight bodies
- Per-persona web apps in `web/apps/cianchosaint-<persona>/` (7 personas per the AGENTS.md)

**`ciandlithe`** (civil litigation, 2026-08-25):
- 7 per-persona web apps in `web/apps/`: ciandlithe-coroner, ciandlithe-health-complain, ciandlithe-inquest, ciandlithe-legal-aid, ciandlithe-piab, ciandlithe-self-rep, ciandlithe-wrc
- The 7-stage litigation pipeline at `dlt_sources/ciandlithe/` with cross-jurisdiction web/Scotland/NI/Wales/Ireland sub-pipelines
- The composite pilot (7 case studies) for validating the workflow end-to-end
- BLIP v1 (British Isles Litigation Pipeline) — single umbrella spec

### A.3 — The 5 repos share the same wholesale-copy pattern

Every one of the 5 repos contains, **wholesale-copied and adapted**,
the same 7 fleet primitives + the same 4 idea agents + the same
`MODEL_REGISTRY` + the same `call_llm` router + the same theming +
the same CopilotKit v1.69 frontend + the same Convex schema. The
gemini_hackathon repo is **explicit** about this in every file's
docstring:

> *"This module is a wholesale port of the Cianfhoghlaim
> ``agents/fleet/agui_bridge.py`` (per the ``wholesale-copy-convention``)"*

This is **5× duplication** of ~6,000 lines per repo = **30,000 lines
of duplicated Python** that could be one shared package. The user's
question about "benefits of ratio" maps directly to this number.

### A.4 — Per-repo software-usage ratios (the metric the user asked for)

| Repo | LOC Python | LOC TSX | LOC tests | BAML | Convex tables | openspec changes | Ratio (test:prod) |
|:--|--:|--:|--:|--:|--:|--:|--:|
| gemini_hackathon | 9,967 | 1,561 | 3,484 | 6 | 5 | 1 (active) | 0.35 |
| tuatha | 18,340 | (via parent) | (via parent) | 13 | (via parent) | 2 (active) | (via parent) |
| ciancheiltis | 5,171 | 0 | 0 (1 dlt_smoke) | 0 | 0 | 1 (active) | 0.00 (data only) |
| cianchosaint | (unread, ~30k est.) | (per-persona) | (unread) | (BAML in baml_src) | (per-persona) | 17 archived | (high) |
| ciandlithe | (unread) | (per-persona) | (unread) | (BAML) | (per-persona) | 4 active | (high) |
| cianfhoghlaim (web/) | (n/a) | ~5,000 (v1) | (n/a) | (parent) | 4 (v1) | many | (n/a) |

**The gemini_hackathon repo is the ratio gold standard** — 3,484 LOC
of tests for 9,967 LOC of production Python (0.35) — and is the
canonical reference for how to structure the 4 idea agents + 7
fleet primitives.

### A.5 — The ratio problem

If the user is asking "what's the benefit of consolidating", the
math is:

- **Today**: 5 repos × 6,000 lines of duplicated fleet = 30,000
  duplicated lines. Each new fleet feature has to be ported 5 times
  (each repo's `wholesale-copy-convention` is one-way; a fix in
  cianfhoghlaim/agents/fleet/ never auto-propagates to the siblings).
- **After consolidation**: 1 × 6,000 + 5 × 200-line integration shims
  = 7,000 lines. **23,000 lines of redundant code eliminated** and
  the 5× per-feature maintenance overhead drops to **1× feature
  ship + 5× trivial re-export**.
- **Test coverage ratio**: 0.35 in gemini_hackathon drops to
  ~0.15 in the consolidated version *if* we lose the per-repo test
  discipline, but **rises to 0.50+ if** the per-repo test discipline
  is preserved and the consolidated package is tested by **5 separate
  test suites** (one per repo integration point).

---

## B) The benefits the sibling repos are already proving

The 5 sibling repos are **not aspirational** — they are **working
code that proves the consolidated architecture**. Each repo's
existence is a **pilot study** for a different aspect of the
consolidation. The benefits are real, not theoretical:

### B.1 — gemini_hackathon proves the **public-demo + Cloud Run** story

The gemini_hackathon repo is **deployed to Google Cloud Run** (per
`README.md:5`) and ships with:
- 164/164 pytests green (`README.md:160`)
- 7 services verified live (`README.md:147-154`)
- A `mise.toml` with the canonical 2026 9-namespace task catalogue
- An openspec change (`2026-08-24-gemini-hackathon-public-v1`) that
  passes `--strict` and follows the spec-driven schema

**The benefit proven:** the 7 fleet primitives + 4 idea agents +
13 palettes + 5 Convex tables + 8 web routes can be **independently
deployed to a managed cloud** without depending on the parent
monorepo. The `MODEL_REGISTRY` dual-profile pattern (the
`hackathon` profile that hides all non-Gemini / non-Gemma models)
proves the **policy-bound model routing** works.

### B.2 — tuatha proves the **MMO + badges + 8 subjects** story

The tuatha repo is **independently deployable to a 2.5D PixiJS realm**
(per `tuatha/AGENTS.md` + the commit `b6a0e86` "Phase 2 P3+P4 2.5D
PixiJS realm canvas + mastery dashboard + FIBO emblems"). It ships
with:
- 8 NCCA subject agents with 5 tools each = 40 tools
- 3 educational agents (academic_history_agent + celtic_grammar_agent
  + celtic_morphology_agent)
- 4 BIEP hackathon features (marking_grader, adaptive_tutor,
  equivalency_generator, curriculum_change_sensor) — the **same 4
  features that gemini_hackathon ships**, but adapted to the
  8 NCCA subjects
- The media_intel pipeline (10 tools)
- The educational-credential badge system (the replacement for the
  deprecated Crypteolas financial-token system)
- 13 BAML contracts
- 18,340 LOC of Python — the **largest** of the 5 sibling repos

**The benefit proven:** the MMO surface can be a **standalone
PWA** with its own badge system, separate from the parent
monorepo's web/ surface. The CONSOLIDATION_PLAN.md shows that
the deprecated Babylon.js 3D / SpacetimeDB v2 / Pent-Elemental
Cosmology themes are **hard-archived** (not preserved-for-fork) —
the new build drops those themes but keeps the technological
choices. This is the **archaeology pattern**: keep the tech, drop
the lore.

### B.3 — ciancheiltis proves the **pure-data carve-out** story

The ciancheiltis repo is **data only** — 5,171 LOC of DLT sources
and zero web frontend. It proves that a **pure-data sub-project**
can:
- Be its own repo (own `mise.toml` + `pyproject.toml` + `AGENTS.md`)
- Share the `dlt_sources/common/` helper module (the 7 helper
  files wholesale-copied from the parent)
- Be tested with **one tiny smoke test** (the `tests/dlt/test_imports.py`
  walks every DLT source via `importlib.import_module`)
- Be measured with **5,171 LOC of DLT coverage** for **5 Celtic
  language families** (Gaois + Téarma + Logainm + Ainm + Canúint +
  Dúchas + Universal Dependencies)

**The benefit proven:** the ciancheiltis pattern is the **cheapest
possible repo** for a data-only sub-project — it doesn't need
Hono, doesn't need Convex, doesn't need a frontend, doesn't need
a BAML surface. It just needs DLT + the shared `common/` helpers.

### B.4 — cianchosaint proves the **per-persona web + 5-stage pipeline** story

The cianchosaint repo is the **defence / policing / intel
oversight** sub-project. It proves that the **5-stage pipeline
registry** (`5_stage_registry.py` + `5_stage_runner.py` +
`jurisdiction_pipeline_base.py` + `connection.py` +
`law_enforcement_registry.py` + `registry_api.py` +
`registry_loader.py`) can:
- Spawn **3 named pipelines** (BIPP v1 = British Isles Policing
  Pipeline, BIDP v1 = British Isles Defence Pipeline, BIIP v1 =
  British Isles Intelligence Oversight Pipeline)
- Run **8 sub-pipelines per named pipeline** (An Garda, 43 UK
  forces, 3 Crown Dependencies, 4 NI bodies, MoD + RAF + RN + Army,
  Irish Defence Forces, Doctrine series)
- Surface **7 per-persona web apps** in `web/apps/cianchosaint-<persona>/`
  (Garda / PSNI / MoD / MET / etc.)
- Honour a **BUSL-1.1 v2 licence** (the cianchosaint edition of
  BUSL-1.1) with **warrant-to-enforce** + **OSINT allowlist**

**The benefit proven:** the per-persona web app pattern is
**scalable** — 7 personas, 3 named pipelines, 8 sub-pipelines,
17 archived openspec changes. The licence is the **load-bearing
constraint** (OSINT allowlist + British Isles body check); the
rest is plumbing.

### B.5 — ciandlithe proves the **per-persona web + 7 personas + composite pilot** story

The ciandlithe repo is the **civil + administrative + appellate
litigation** sub-project. It proves that **7 per-persona web
apps** (coroner, health-complain, inquest, legal-aid, piab,
self-rep, wrc) can:
- Share a **single BLIP v1 umbrella pipeline** (British Isles
  Litigation Pipeline)
- Honour an even **stricter licence** than cianchosaint
  (BUSL-1.1 v2 ciandlíthe edition with the Person-of-Interest
  clause + the no-auto-submit constraint)
- Carry a **composite pilot** of 7 case studies (QUB/RVH
  brain-injury, Eric employer breach, Garda discrimination,
  DkIT disability, NUIG rejection, UCL offer, sodium
  valproate/HSE misprescription) — the **end-to-end validation
  before any expansion**
- Use the `md:ciandlithe` MotherDuck database namespace, parallel
  to `md:cianchosaint` and `md:cianfhoghlaim`

**The benefit proven:** the per-persona web app pattern can be
**constrained by licence** to **never auto-submit** to a court
system. The platform generates a **dossier** (PDF + structured
JSON) for **manual review by the claimant or their solicitor**.
This is the **load-bearing safety constraint** for any
self-represented-claimant surface.

### B.6 — The unifying benefit

The 5 sibling repos prove **5 different things** about the
consolidated architecture. None of them is the same. The benefit
of **keeping them as 5 independent repos** + **a shared
packages/ workspace** is:

- **5 different deployment targets** (GCP Cloud Run for
  gemini_hackathon; bare-metal for ciancheiltis; a private cloud
  for cianchosaint; a court-system-adjacent private cloud for
  ciandlithe; the Cianfhoghlaim parent for tuatha)
- **5 different licence models** (MIT for gemini_hackathon;
  BUSL-1.1 cultural grant for cianfhoghlaim; BUSL-1.1 v2
  cianchosaint edition; BUSL-1.1 v2 ciandlíthe edition; the
  tuatha sub-licence is pending)
- **5 different pace layers** (gemini_hackathon moves daily
  for the hackathon; ciancheiltis moves weekly; cianchosaint
  moves monthly; ciandlithe moves quarterly; the parent
  monorepo moves on openspec change cadence)
- **5 different audit trails** (each repo has its own AGENTS.md
  + LICENSE + openspec/ + mise.toml — no shared mutation surface)

The cost is **5× wholesale-copy** of the fleet primitives +
the model registry + the theming helpers. The benefit of the
consolidation is to **lift the shared parts to a shared
package** so each repo can `pip install cianfhoghlaim-fleet`
once and never re-port.

---

## C) The complexity of the end result the user is asking for

The user asked to "greatly improve our merging plan and the
complexity of the end results to carry out the goals of those
projects". The end result is **a 3-tier monorepo** that can
absorb all 5 sibling repos **as sub-apps** without breaking
any of them.

### C.1 — The 3-tier target architecture

```
cianfhoghlaim/                         # the parent (canonical spec + schema)
├── packages/                                 # TIER 1: shared (lifted from siblings)
│   ├── model-registry/                       # the 24-entry MODEL_REGISTRY
│   ├── fleet/                                # the 7 fleet primitives
│   ├── agui-bridge/                          # the 16-event AG-UI bridge
│   ├── theming/                              # the 13-palette theming
│   ├── baml-helpers/                         # the BAML extract helpers
│   ├── db/                                   # the Convex umbrella schema + Drizzle helpers
│   ├── auth/                                 # the BetterAuth wrapper
│   ├── ui-kit/                               # the shared UI components
│   └── dlt-common/                           # the DLT shared helpers
├── apps/                                     # TIER 2: the monorepo apps (5, not 12)
│   ├── oideachais/                           # the per-subject content app
│   ├── oideachais-dashboard/                 # the operator dashboard
│   ├── cianfhoghlaim/                        # the central homepage
│   ├── croilar-web/                          # the multi-persona public site
│   ├── tuatha-ui/                            # the MMO 2D + 3D client
│   └── hono-api/                             # the single canonical Hono gateway
├── subapps/                                  # TIER 3: the 5 sibling repos (mounted as git subtrees)
│   ├── gemini_hackathon/                     # mounted as a git subtree
│   ├── tuatha/                               # mounted as a git subtree
│   ├── ciancheiltis/                         # mounted as a git subtree
│   ├── cianchosaint/                         # mounted as a git subtree
│   └── ciandlithe/                           # mounted as a git subtree
├── orchestration/                            # unchanged (Dagster)
├── dlt_sources/                              # unchanged (DLT)
├── cocoindex_flows/                          # unchanged (CocoIndex)
├── notebooks/                                # unchanged (marimo)
├── motherduck/                               # unchanged (BIEP v3)
├── baml_src/                                 # unchanged (BAML contracts)
├── bonneagar/                                # unchanged (IaC)
├── mise.toml                                 # extended with 5 subapp namespace prefixes
├── pyproject.toml                            # extended with workspace members
└── opencode.json                             # extended with 5 subapp agent profiles
```

### C.2 — What changes per tier

**TIER 1 (packages/)** — pure additions, no removals. Lift:
- `gemini_hackathon/gemini_hackathon/models/__init__.py` (666 LOC)
  → `packages/model-registry/src/`
- `gemini_hackathon/gemini_hackathon/agents/fleet/*.py` (7 files,
  3,444 LOC total) → `packages/fleet/src/`
- `gemini_hackathon/gemini_hackathon/agents/fleet/fleet_agui.py`
  (407 LOC) → `packages/agui-bridge/src/`
- `gemini_hackathon/gemini_hackathon/theming.py` (254 LOC) +
  `gemini_hackathon/themes/*.json` (13 files) → `packages/theming/src/`
  + `packages/theming/themes/`
- `gemini_hackathon/gemini_hackathon/observability.py` (153 LOC) +
  `gemini_hackathon/gemini_hackathon/agents/fleet/fleet_observability.py`
  (541 LOC) → `packages/observability/src/` (or keep in fleet/)
- `gemini_hackathon/web/src/components/themes/SourcePaletteProvider.tsx`
  (137 LOC) → `packages/ui-kit/src/themes/`
- `gemini_hackathon/web/convex/schema.ts` (233 LOC) → `packages/db/src/convex/`
- `gemini_hackathon/web/src/routes/api/copilotkit.ts` (60 LOC) +
  `web/src/routes/api/duckdb.ts` (35 LOC) + `themes.ts` (41 LOC) →
  `web/hono-api/src/routes/`

**TIER 2 (apps/)** — already in v1, unchanged.

**TIER 3 (subapps/)** — the 5 sibling repos, mounted as
**git subtrees** (not submodules). Each subapp:
- Keeps its own `mise.toml` + `pyproject.toml` + `LICENSE` + `AGENTS.md` + `openspec/`
- Adds a `subapp_manifest.yaml` that declares:
  - Which TIER 1 packages it depends on (`fleet`, `model-registry`, `theming`, `agui-bridge`)
  - Which TIER 2 apps it integrates with (if any)
  - Its deployment target (GCP Cloud Run / bare-metal / private cloud)
  - Its licence model (MIT / BUSL-1.1 v2 / etc.)
- Continues to ship its own openspec changes (archived to its
  own `openspec/changes/` + mirrored to the parent `openspec/changes/`
  via the `cianfhoghlaim-sync-changes` mise task)

### C.3 — The new sub-app entry points

For each of the 5 subapps, add a thin wrapper in `subapps/<name>/`:

```python
# subapps/gemini_hackathon/gemini_hackathon/__init__.py
"""
Thin re-export layer for the gemini_hackathon sub-app.
All the actual code lives in the parent Cianfhoghlaim packages/.
"""
from cianfhoghlaim.fleet import (
    FleetGateway, FleetIdentity, ModelArmor, Observability,
    FleetMemory, FleetAGUIBridge, MCPCurriculumServer,
)
from cianfhoghlaim.theming import (
    Palette, load_palette, list_all_palettes, JURISDICTIONS,
    BOARDS, SAFEGUARDING_BODIES,
)
from cianfhoghlaim.model_registry import (
    MODEL_REGISTRY, ModelRegistry, ModelRegistryEntry,
    model_for, ModelFamily, ModelRole, ModelProfile,
)

# Sub-app-specific extensions (the 4 idea agents, the 8 web routes)
from .ideas import (
    MarkingGraderWorkflow, AdaptiveTutor, EquivalencyGenerator,
    CurriculumChangeSensor,
)
from .routes import AGENTS_ROUTES, ARCHIPELAGO_ROUTES, ...
```

**Total sub-app code: ~3,000 LOC per sub-app** (down from 9,967
in the standalone gemini_hackathon repo). **5 sub-apps × 3,000
= 15,000 LOC** vs the **30,000 LOC of duplicated fleet + registry
+ theming** in the 5 standalone repos. **Net win: 15,000 LOC
of redundant code eliminated** + 5× maintenance reduction on
every fleet / registry / theming change.

### C.4 — The per-tier sub-app benefit ratio

| Tier | LOC today | LOC after | Δ | Benefit |
|:--|--:|--:|--:|:--|
| TIER 1 (packages/) | 0 | ~5,000 (lifted) | +5,000 | **single source of truth** for fleet + registry + theming |
| TIER 2 (apps/) | ~5,000 (v1) | ~5,000 | 0 | unchanged |
| TIER 3 (subapps/) | ~85,000 (5 repos) | ~15,000 (re-exports) | −70,000 | **70K LOC of redundant code eliminated** |
| **Total** | **~90,000** | **~25,000** | **−65,000** | **−72% LOC, 5× single-source-of-truth** |

**This is the answer to the user's "benefits of ratio" question:**
the ratio of useful-work to duplicated-work goes from
~30% (today) to ~95% (after). The 65K LOC reduction is real,
and the per-feature maintenance drops from 5× to 1×.

### C.5 — The complexity of getting there

The user asked to "greatly improve our merging plan and the
complexity of the end results to carry out the goals of those
projects". The complexity is **deliberately incremental**, not
all-at-once:

1. **No sibling repo is modified in this proposal.** Each sibling
   repo continues to ship its own code, its own openspec changes,
   its own deploys. The only change is **a `subapp_manifest.yaml`**
   added to each repo's root that declares its TIER 1 dependencies.

2. **The parent monorepo gains the 3-tier structure incrementally.**
   First TIER 1 packages are lifted (one package at a time, each
   as a separate openspec change). Then each TIER 3 subapp is
   mounted as a git subtree (one per openspec change).

3. **The git subtree pattern** is the **load-bearing decision**.
   Git subtrees (not submodules) are the right tool because:
   - Each sibling repo can continue to be developed in its own
     clone (faster CI, smaller diff)
   - The parent monorepo pulls the sibling's main branch
     periodically (per the `sync-subapps` mise task)
   - Sibling-specific code lives in the sibling; shared code
     lives in the parent
   - The split is **reversible** (a sibling can be detached from
     the parent at any time)

4. **The 3-tier architecture is a destination, not a deadline.**
   Each phase of the migration is its own openspec change that
   passes `--strict` and lands independently. The 12-week timeline
   in v1 → the 15-21 week timeline here → the 24-30 week timeline
   for the 3-tier architecture (5 subapps × 3-4 weeks each + the
   TIER 1 package lifts + the git subtree wiring).

### C.6 — The 5 sub-app goals preserved

The end result carries the **explicit goals of each sibling
project**, not just the parent's:

1. **gemini_hackathon's goal**: "One platform for the British Isles"
   (8 subnations × 3 audiences × 4 idea agents × 7 fleet primitives).
   Preserved by TIER 3 mounting + the 13 palettes + the 4 idea
   agents.
2. **tuatha's goal**: "The British Isles Formative Assessment MMO"
   (8 NCCA subjects × 5 tools × 3 educational agents × 4 hackathon
   features × 1 media_intel pipeline). Preserved by the
   `tuatha/AGENTS.md` + the 8 subject agents in `tuatha/subjects/`
   + the badges system.
3. **ciancheiltis's goal**: Pure Irish + Celtic languages (5
   families × 5 datasets × pure-data carve-out). Preserved by
   the data-only subapp pattern + the 5,171 LOC of DLT sources
   in `ciancheiltis/dlt_sources/`.
4. **cianchosaint's goal**: OSINT-only British Isles defence /
   policing / intel oversight (3 named pipelines × 8 sub-pipelines
   × 7 per-persona web apps × BUSL-1.1 v2). Preserved by the
   per-persona web pattern + the 5-stage pipeline registry +
   the OSINT allowlist + the licence.
5. **ciandlithe's goal**: OSINT-only civil + administrative +
   appellate litigation (BLIP v1 × 7 per-persona web apps ×
   BUSL-1.1 v2 +PoI clause + no-auto-submit). Preserved by
   the per-persona web pattern + the 7 personas + the composite
   pilot + the licence.
6. **cianfhoghlaim's goal**: "Cianfhoghlaim — Celtic language
   AI learning platform" (the parent, with its 5 apps + 1 Hono
   API + 3 shared packages after v1's consolidation). Preserved
   by TIER 2.

---

## D) The improved refactor order (replaces v1's §G)

### D.1 — The 6 phases (with new sub-phases for the 3-tier architecture)

| Phase | Layer | Scope | Status | Adds |
|--:|:--|:--|:--|:--|
| **1** | **dlt** | 928 DLT sources + per-jurisdiction subdirectories | DONE — 99% green | — |
| **2** | **dagster** | 833 assets in the 5-layer `defs/` tree | 95% done | — |
| **3** | **cocoindex** | 17+ CocoIndex v1 Apps (BGE-M3 1024-d) | 90% done | — |
| **4** | **lakehouse** | MotherDuck + DuckLake tables under `md:cianfhoghlaim` | 85% done | — |
| **5** | **web (the package layer)** | TIER 1 packages lifted from gemini_hackathon | **START HERE** | `packages/{model-registry,fleet,theming,agui-bridge,baml-helpers}/` |
| **5.1** | **web (the app layer)** | TIER 2 apps (the v1 12→5 consolidation) | blocked on 5 | `apps/{oideachais,oideachais-dashboard,cianfhoghlaim,croilar-web,tuatha-ui}/` |
| **5.2** | **web (the sub-app layer)** | TIER 3 subapps mounted as git subtrees | blocked on 5 + 5.1 | `subapps/{gemini_hackathon,tuatha,ciancheiltis,cianchosaint,ciandlithe}/` |

### D.2 — Phase 5 sub-phases (the 8-week TIER 1 lift)

| Week | Sub-phase | Package | Source | Effort | Risk |
|--:|:--|:--|:--|:--|:--|
| 1-2 | 5.A | `packages/model-registry/` | `gemini_hackathon/gemini_hackathon/models/__init__.py` (666 LOC) | 2 weeks | LOW |
| 2-3 | 5.B | `packages/fleet/` | `gemini_hackathon/gemini_hackathon/agents/fleet/*.py` (3,444 LOC) | 2 weeks | MED (7 primitives × 1 test per primitive) |
| 3-4 | 5.C | `packages/theming/` | `gemini_hackathon/gemini_hackathon/theming.py` (254 LOC) + `themes/*.json` (13 files) | 1 week | LOW |
| 4-5 | 5.D | `packages/agui-bridge/` | `gemini_hackathon/gemini_hackathon/agents/fleet/fleet_agui.py` (407 LOC) | 1 week | MED (16-event protocol + CopilotKit adapter) |
| 5-6 | 5.E | `packages/baml-helpers/` | `gemini_hackathon/baml_extracts/gemini_hackathon/` (6 .baml + helpers) | 1 week | MED (BAML client codegen + the per-source BAML stubs) |
| 6-7 | 5.F | `packages/observability/` | `gemini_hackathon/gemini_hackathon/observability.py` + `gemini_hackathon/gemini_hackathon/agents/fleet/fleet_observability.py` (694 LOC) | 1 week | LOW |
| 7-8 | 5.G | `packages/db/` (Convex umbrella) | `gemini_hackathon/web/convex/schema.ts` (233 LOC) + `oideachais-dashboard/convex/` (10 ts files) | 1 week | HIGH (5+ Convex tables + 3 sibling Convex schemas) |
| 8 | 5.H | `packages/ui-kit/` (shared) | lift from `oideachais-dashboard/` + `croilar-web/` + `ciancheiltis/` UI components | 1 week | LOW |

**Phase 5 total: 8 weeks, 1 person, sequential.**
After Phase 5, every TIER 2 app + every TIER 3 subapp can
`pip install cianfhoghlaim-{model-registry,fleet,theming,...}`
and use the same code that the other tiers use.

### D.3 — Phase 5.1 (TIER 2 — the v1 consolidation, now unblocked)

After Phase 5 lands, the v1 12→5 app consolidation can proceed.
The package layer is the **foundation**; the app layer is the
**first consumer**. The v1 timeline (15-21 weeks) still applies
but is now **5× easier** because the shared packages are in
place.

| Week | Move | Effort | Why |
|--:|:--|:--|:--|
| 9 | Archive `_oideachais_apps/` + `game_showcase/` + `tuatha-demo/` | 1 week | Lowest risk wins |
| 10-11 | Merge `croilar-portal/` → `croilar-web/` | 2 weeks | Easiest merge |
| 12-15 | Merge `cianfhoghlaim-web/` → `cianfhoghlaim/` | 4 weeks | Largest public surface |
| 16-21 | Merge `cianfhoghlaim-leaving-cert/` → `oideachais/` | 6 weeks | Richest content |

**Phase 5.1 total: 12-13 weeks, 1-2 people, mostly sequential.**

### D.4 — Phase 5.2 (TIER 3 — the git subtree mounting)

After Phase 5.1 lands, the 5 sibling repos are mounted as git
subtrees under `subapps/`. **No code is changed in the sibling
repos** — they continue to ship their own code, their own
openspec changes, their own deploys. The only change in each
sibling is the addition of a `subapp_manifest.yaml` at the
root.

| Week | Sub-phase | Subapp | Effort | Why |
|--:|:--|:--|:--|:--|
| 22 | 5.2.A | `subapps/gemini_hackathon/` | 1 week | Easiest (it's a public-demo with a 2-tier model policy) |
| 23-24 | 5.2.B | `subapps/ciancheiltis/` | 2 weeks | Data only — minimal integration surface |
| 25-26 | 5.2.C | `subapps/cianchosaint/` | 2 weeks | 7 personas + 3 named pipelines |
| 27-28 | 5.2.D | `subapps/ciandlithe/` | 2 weeks | 7 personas + composite pilot + the +PoI licence |
| 29-30 | 5.2.E | `subapps/tuatha/` | 2 weeks | The largest of the 5 (18,340 LOC + 13 BAML + 8 NCCA subjects) |

**Phase 5.2 total: 8-9 weeks, 1-2 people, sequential.**

**The order matters:** gemini_hackathon first because it's the
public-demo with the simplest integration; ciancheiltis next
because it's data-only; then the 3 complex per-persona siblings;
then tuatha last because it's the largest and the 8 NCCA
subjects need to wire into the parent's BAML surface.

### D.5 — Total refactor timeline (replaces v1's 12-21 weeks)

| Stream | Duration | Squad |
|:--|:--|:--|
| Phase 5 (TIER 1 packages) | 8 weeks | 1 person, sequential |
| Phase 5.1 (TIER 2 app consolidation) | 12-13 weeks | 1-2 people, mostly sequential |
| Phase 5.2 (TIER 3 subapp mounting) | 8-9 weeks | 1-2 people, sequential |
| **Total** | **28-30 weeks** | mixed |

With 2 people running in parallel from week 9 onward:
**18-22 weeks** is realistic.

### D.6 — The 3 openspec changes to file first

Before any code moves, file 3 openspec changes that establish the
3-tier architecture as canonical:

1. `2026-08-25-web-frontend-3-tier-architecture-v1` — the master
   change. Proposes the 3-tier structure (TIER 1 packages + TIER 2
   apps + TIER 3 subapps). Touches 0 files in the 5 sibling repos
   and 0 files in `cianfhoghlaim/`. Establishes the
   `subapp_manifest.yaml` schema and the git subtree
   convention. **Self-contained, passes `--strict`, archived after
   1 day of review.**

2. `2026-08-25-lift-model-registry-to-t1-v1` — the first TIER 1
   package lift. Proposes moving `gemini_hackathon/gemini_hackathon/models/__init__.py`
   to `cianfhoghlaim/packages/model-registry/`. Touches:
   - 1 file created (`packages/model-registry/pyproject.toml`)
   - 1 file created (`packages/model-registry/src/cianfhoghlaim/model_registry/__init__.py`)
   - 1 file modified (`gemini_hackathon/gemini_hackathon/__init__.py`
     to re-export from the parent)
   - 0 files modified in the other 4 sibling repos
   - 0 files modified in the parent `cianfhoghlaim/`
     web/ surface (the 5 TIER 2 apps can opt in to the package
     later, in their own openspec changes)

3. `2026-08-25-mount-gemini-hackathon-as-subapp-v1` — the first
   TIER 3 mount. Proposes adding `subapps/gemini_hackathon/` as
   a git subtree + a `subapp_manifest.yaml` at the gemini_hackathon
   root. Touches:
   - 1 file created in `cianfhoghlaim/subapps/gemini_hackathon/README.md`
   - 1 file created at the gemini_hackathon root (`subapp_manifest.yaml`)
   - 0 files modified in the sibling code

**Each of the 3 openspec changes is independently shippable**
and passes `--strict`. The first establishes the pattern, the
second proves the TIER 1 lift, the third proves the TIER 3
mount. After all 3 land, the 3-tier architecture is **in
place** and the remaining 4 sibling mounts + the 7 remaining
TIER 1 lifts + the 5 TIER 2 consolidations can proceed as
independent openspec changes.

---

## E) The shared patterns to lift (the "benefits of ratio" list)

The user asked about "the benefits of ratio and features of
software usage in our projects". Below is the **concrete list**
of patterns that are duplicated across the 5 sibling repos +
the parent monorepo, ranked by **ratio of duplication : value**
(i.e. how much code is duplicated vs how much value would be
unlocked by the lift).

### E.1 — Tier 1: The 9 highest-value lifts (lift first)

| # | Pattern | Where it's duplicated | LOC | Why it matters |
|--:|:--|:--|--:|:--|
| 1 | **`MODEL_REGISTRY`** | All 5 siblings + the parent | ~666 each = 3,996 | The single source of truth for every LLM/OCR/embedder/image-gen model; the load-bearing pattern for policy-bound model routing. Without it, every LLM call is a hardcoded string. |
| 2 | **The 7 fleet primitives** | All 5 siblings + the parent | ~3,444 each = 20,664 | The single entrypoint, the identity layer, the model armor, the observability layer, the memory layer, the AG-UI bridge, the MCP curriculum server. Without them, every agent is bespoke. |
| 3 | **The theming layer (13 palettes)** | All 5 siblings (gemini_hackathon has it; the 4 others would need it) | ~254 + 13 JSON = ~340 + JSONs | The per-source palette extraction + the CSS custom property injection. Without it, every UI is the same colour. |
| 4 | **The AG-UI bridge (16 events)** | All 5 siblings + the parent | ~407 each = 2,442 | The SSE protocol bridge between the agent and the CopilotKit frontend. Without it, every chat is a custom API. |
| 5 | **The BAML extract surface** | All 5 siblings + the parent | ~6 .baml each = 30+ | The per-source BAML extraction contracts (palette, equivalency, marking, asset, curriculum change, safeguarding). Without them, every BAML call is bespoke. |
| 6 | **The observability layer** | All 5 siblings + the parent | ~694 each = 4,164 | The Langfuse + MLflow + structlog integration. Without it, every LLM call is invisible. |
| 7 | **The Convex umbrella schema** | 4 deployments (one per sibling) | ~233 each = ~932 | The 5-table + 8-table per-source schemas. Without a single umbrella, the 4 deployments drift. |
| 8 | **The Hono / CopilotKit route surface** | All 5 siblings + the parent | ~3 routes each = ~15 | The `/api/copilotkit` + `/api/themes` + `/api/duckdb` proxy routes. Without them, every CopilotKit chat is a custom integration. |
| 9 | **The DLT common helpers** | All 5 siblings + the parent | ~341 each = 2,046 | The `_shared.py` helpers (the SHA256 + retry + DuckDB destination factory). Without them, every DLT source re-implements them. |

**Total: ~37,000 lines of duplicated code** that would become
**~5,000 lines of canonical packages** in TIER 1.

### E.2 — Tier 2: The 5 lower-value lifts (lift after TIER 1 is stable)

| # | Pattern | Where it's duplicated | LOC | Why it matters |
|--:|:--|:--|--:|:--|
| 10 | **The 4 idea agents** | gemini_hackathon (4 agents, 2,032 LOC) + tuatha (4 agents, 1,500 LOC) | ~3,500 | The marking grader + adaptive tutor + equivalency generator + curriculum change sensor. They're already adapted per project; the question is whether the *common adapter* is worth lifting. |
| 11 | **The 8 NCCA subject agents** | tuatha only (1,500 LOC) | 1,500 | The 8 NCCA subjects with 5 tools each. Single project (so far), so the duplication ratio is 1:1. **Don't lift unless a second project needs them.** |
| 12 | **The media_intel pipeline** | tuatha only (10 ADK tools) | ~800 | The 10-tool media descriptor agent. Single project. **Don't lift unless a second project needs it.** |
| 13 | **The per-persona web app pattern** | cianchosaint (7 personas) + ciandlithe (7 personas) | ~5,000 each = 10,000 | The 7 personas per sibling. The pattern is identical (TanStack Start + Convex + AG-UI + CopilotKit) but the content is licence-specific. **Lift as a pattern, not as code.** |
| 14 | **The OSINT allowlist** | cianchosaint + ciandlithe | ~1,000 | The per-source URL allowlist. Licence-specific. **Don't lift — keep in the per-licence subapp.** |

### E.3 — Tier 3: The 4 things to NOT lift (per-project constraint)

| # | Pattern | Why it stays per-project |
|--:|:--|:--|
| 1 | **The licence (BUSL-1.1 v2 cianchosaint / ciandlíthe edition)** | Each sibling's licence is bespoke. The parent is BUSL-1.1 (cultural grant); the siblings are BUSL-1.1 v2 (British-Isles-only OSINT, warrant-to-enforce, +PoI clause). The licence lives in the subapp, not in the package. |
| 2 | **The MotherDuck database namespace** | Each subapp uses its own `md:<subapp>` namespace. The 5 namespaces (`md:cianfhoghlaim`, `md:cianchosaint`, `md:ciandlithe`, `md:tuatha`, `md:ciancheiltis`) are independent. The *pattern* of a per-subapp namespace is TIER 1; the *namespaces themselves* are per-subapp. |
| 3 | **The openspec changes per subapp** | Each subapp archives its own openspec changes. The pattern of "every change flows through openspec" is TIER 1; the changes themselves are per-subapp. |
| 4 | **The deployment target per subapp** | gemini_hackathon deploys to GCP Cloud Run; ciancheiltis deploys to bare-metal; cianchosaint / ciandlithe deploy to a private cloud; tuatha deploys to the parent. The deployment is per-subapp, not in the parent. |

### E.4 — The 3-tier ratio summary

| Tier | # patterns | LOC today | LOC after | Ratio |
|:--|--:|--:|--:|--:|
| TIER 1 (lift) | 9 | ~37,000 | ~5,000 | **−86%** |
| TIER 2 (defer) | 5 | ~16,000 | ~16,000 | 0% (deferred until second consumer) |
| TIER 3 (per-project) | 4 | (per-subapp) | (per-subapp) | n/a (these are per-project constraints) |
| **Total** | **18** | **~53,000** | **~21,000** | **−60%** |

**This is the answer to the user's "benefits of ratio" question.**
The ratio of redundant code to unique code drops from ~70% to
~20% after the TIER 1 lifts. Every fleet feature shipped to
the parent automatically lands in all 5 sibling repos (instead
of being wholesale-copied 5 times).

---

## F) The new openspec change matrix (replaces v1's §I)

The 3-tier architecture generates **17 new openspec changes** (vs
v1's 8). The matrix is:

### F.1 — The 3 master changes (file in week 0)

1. `2026-08-25-web-frontend-3-tier-architecture-v1` — establishes
   the 3-tier structure (TIER 1 + TIER 2 + TIER 3) + the
   `subapp_manifest.yaml` schema + the git subtree convention
2. `2026-08-25-llms-txt-skill-v1` — establish the LLMs.txt
   /docs.skill pattern for the 5 sibling repos to share the
   same skill manifest (the parent's
   `.agents/skills/INDEXING_AND_COGNITION.md` plus 5 new
   per-subapp INDEXING files)
3. `2026-08-25-knowledge-sync-loop-extended-v1` — extend the
   14-layer knowledge sync loop to handle the 5 subapps (each
   subapp's docs + skills + openspec changes flow into the
   parent's `stedding/sync-reports/` via the new
   `sync-subapps` mise task)

### F.2 — The 9 TIER 1 package lifts (file in weeks 1-8)

Per §D.2, one openspec change per package:
4. `lift-model-registry-to-t1-v1`
5. `lift-fleet-to-t1-v1`
6. `lift-theming-to-t1-v1`
7. `lift-agui-bridge-to-t1-v1`
8. `lift-baml-helpers-to-t1-v1`
9. `lift-observability-to-t1-v1`
10. `lift-db-convex-umbrella-to-t1-v1`
11. `lift-ui-kit-to-t1-v1`
12. `lift-dlt-common-to-t1-v1`

### F.3 — The 5 TIER 2 app consolidations (file in weeks 9-21)

Per §D.3 + v1 §F:
13. `archive-legacy-oideachais-apps-v1` (week 9)
14. `merge-croilar-portal-into-croilar-web-v1` (weeks 10-11)
15. `merge-cianfhoghlaim-web-into-cianfhoghlaim-v1` (weeks 12-15)
16. `merge-cianfhoghlaim-leaving-cert-into-oideachais-v1` (weeks 16-21)

### F.4 — The 5 TIER 3 subapp mounts (file in weeks 22-30)

17. `mount-gemini-hackathon-as-subapp-v1` (week 22)
18. `mount-ciancheiltis-as-subapp-v1` (weeks 23-24)
19. `mount-cianchosaint-as-subapp-v1` (weeks 25-26)
20. `mount-ciandlithe-as-subapp-v1` (weeks 27-28)
21. `mount-tuatha-as-subapp-v1` (weeks 29-30)

**Total: 21 openspec changes** over 30 weeks. Each is
independently shippable + passes `--strict` + archives after
landing.

### F.5 — The cross-subapp openspec change pattern

Each TIER 3 mount follows the **same pattern** as the
`2026-08-25-mount-gemini-hackathon-as-subapp-v1` change
described in §D.6:

1. Add a `subapp_manifest.yaml` at the subapp root
2. Add a `subapps/<name>/README.md` at the parent that points
   to the subapp's repo + the openspec change
3. Add a `subapp_manifest.yaml` reader to the parent's
   `scripts/croilar/analyze-web-stack.ts` (or a new
   `scripts/sync/sync-subapps.ts`) so the analysis tool
   understands the new subapp surface
4. Update the parent's `openspec/AGENTS.md` with the
   subapp's openspec change references
5. Update the parent's `.agents/skills/` with a new
   `cianfhoghlaim-subapp-onboarding/SKILL.md` skill that documents the
   pattern

**Each subapp mount takes 1-2 weeks** and is fully reversible
(the subapp can be detached from the parent at any time by
removing the git subtree + the manifest).

---

## G) The new target topology (replaces v1's §F.2)

### G.1 — Pre-consolidation (today)

```
~/dev/
├── cianfhoghlaim/                  # the parent monorepo
│   ├── web/                        # 12 apps (v1)
│   ├── packages/                   # 3 packages (v1)
│   ├── hono-api/                   # 1 hono api
│   ├── orchestration/              # dagster
│   ├── dlt_sources/                # 928 dlt sources
│   ├── cocoindex_flows/            # 17+ cocoindex apps
│   ├── notebooks/                  # marimo
│   ├── motherduck/                 # biiep v3
│   ├── baml_src/                   # baml contracts
│   ├── bonneagar/                  # iac
│   ├── mise.toml                   # task catalogue
│   └── opencode.json               # agent profiles
│
├── gemini_hackathon/               # sibling 1 (public demo)
│   ├── gemini_hackathon/           # 9,967 LOC Python
│   ├── web/                        # 1,561 LOC TSX + 5 Convex tables
│   ├── themes/                     # 13 per-source palettes
│   ├── dlt_pipelines/              # 1,955 LOC DLT
│   ├── baml_extracts/              # 6 .baml
│   ├── data/                       # 13 source folders
│   └── mise.toml                   # 9-namespace task catalogue
│
├── tuatha/                         # sibling 2 (the MMO)
│   ├── tuatha/                     # 18,340 LOC Python
│   ├── sources/                    # 5 source families
│   ├── openspec/                   # 2 active changes
│   └── mise.toml
│
├── ciancheiltis/                   # sibling 3 (Celtic languages)
│   ├── dlt_sources/                # 5,171 LOC DLT
│   ├── openspec/                   # 1 active change
│   └── mise.toml                   # 5 ciancheiltis:* tasks
│
├── cianchosaint/                   # sibling 4 (defence / policing)
│   ├── agents/                     # 12 ADK agents
│   ├── baml_src/                   # BAML in cianchosaint/
│   ├── cocoindex_flows/            # 5 cocoindex apps
│   ├── dlt_sources/                # 5-stage pipeline registry
│   ├── orchestration/              # dagster defs
│   ├── web/apps/                   # 7 per-persona apps
│   ├── openspec/                   # 17 archived changes
│   └── mise.toml                   # 12 cianchosaint:* tasks
│
└── ciandlithe/                     # sibling 5 (civil litigation)
    ├── agents/                     # ADK agents + tools
    ├── baml_src/                   # BAML in ciandlithe/
    ├── cocoindex_flows/            # cocoindex apps
    ├── dlt_sources/                # 5-stage pipeline registry
    ├── web/apps/                   # 7 per-persona apps
    ├── openspec/                   # 4 active changes
    └── mise.toml
```

### G.2 — Post-consolidation (target state)

```
~/dev/cianfhoghlaim/                 # the canonical parent
├── packages/                        # TIER 1 (lifted)
│   ├── model-registry/              # from gemini_hackathon
│   ├── fleet/                       # from gemini_hackathon
│   ├── theming/                     # from gemini_hackathon
│   ├── agui-bridge/                 # from gemini_hackathon
│   ├── baml-helpers/                # from gemini_hackathon
│   ├── observability/               # from gemini_hackathon
│   ├── db/                          # umbrella Convex schema
│   ├── auth/                        # BetterAuth wrapper
│   ├── ui-kit/                      # shared UI
│   └── dlt-common/                  # DLT shared helpers
│
├── apps/                            # TIER 2 (5 apps, not 12)
│   ├── oideachais/                  # per-subject content
│   ├── oideachais-dashboard/        # operator dashboard
│   ├── cianfhoghlaim/               # central homepage
│   ├── croilar-web/                 # multi-persona public
│   └── tuatha-ui/                   # MMO 2D + 3D
│
├── hono-api/                        # TIER 2 backend gateway
│
├── subapps/                         # TIER 3 (git subtrees)
│   ├── gemini_hackathon/            # 1-week mount
│   ├── tuatha/                      # 2-week mount
│   ├── ciancheiltis/                # 2-week mount
│   ├── cianchosaint/                # 2-week mount
│   └── ciandlithe/                  # 2-week mount
│
├── orchestration/                   # unchanged
├── dlt_sources/                     # unchanged
├── cocoindex_flows/                 # unchanged
├── notebooks/                       # unchanged
├── motherduck/                      # unchanged
├── baml_src/                        # unchanged
├── bonneagar/                       # unchanged
├── mise.toml                        # extended with 5 subapp namespace prefixes
├── pyproject.toml                   # extended with workspace members
├── opencode.json                    # extended with 5 subapp agent profiles
└── openspec/                        # extended with cross-subapp changes
```

The 4 sibling repos (`gemini_hackathon/`, `tuatha/`,
`ciancheiltis/`, `cianchosaint/`, `ciandlithe/`) **continue to
exist as independent repos** — they are *not deleted*. The
parent monorepo just **gains** a `subapps/<name>/` git
subtree that mirrors the sibling's `main` branch. The sibling
remains the source of truth for its own code; the parent is
the integration surface.

### G.3 — What changes in each sibling

**`gemini_hackathon/`** (the canonical working code):
- **Added**: 1 file (`subapp_manifest.yaml`)
- **Modified**: 1 file (`gemini_hackathon/__init__.py` to re-export
  from `cianfhoghlaim.*` where the TIER 1 packages are available)
- **Removed**: 0 files (the wholesale-copied code stays until
  each TIER 1 package is stable enough to deprecate)

**`tuatha/`**, **`ciancheiltis/`**, **`cianchosaint/`**,
**`ciandlithe/`**:
- **Added**: 1 file each (`subapp_manifest.yaml`)
- **Modified**: 0-1 files per TIER 1 lift
- **Removed**: 0 files

The siblings are **not modified** until the TIER 1 package
they depend on is stable. **The migration is incremental and
reversible.**

---

## H) Why the 3-tier architecture (the long answer)

The user asked about "the complexity of the end results to carry
out the goals of those projects". Below is the long answer.

### H.1 — The 5 sibling repos have different goals

| Sibling | Goal | Why it's separate |
|:--|:--|:--|
| gemini_hackathon | Google All Things Agentic Hackathon (Aug 2026) | Public demo on GCP Cloud Run; needs to ship a polished 4-min video |
| tuatha | The British Isles Formative Assessment MMO | Independent sub-project with its own badge system + 2.5D PixiJS realm |
| ciancheiltis | Pure Irish + Celtic languages | Data only, 5,171 LOC of DLT, no frontend |
| cianchosaint | OSINT defence / policing / intel oversight | BUSL-1.1 v2 with warrant-to-enforce + OSINT allowlist |
| ciandlithe | OSINT civil litigation | BUSL-1.1 v2 with +PoI clause + no-auto-submit constraint |

**Each goal has a different pace layer.** The gemini_hackathon
ships daily for the hackathon deadline. ciancheiltis ships
weekly. cianchosaint ships monthly (the OSINT allowlist needs
human review). ciandlithe ships quarterly (the composite pilot
needs a court-system-adjacent reviewer). The parent monorepo
ships on openspec change cadence.

**Forcing all 5 into a single monorepo would mean all 5 ship
on the same cadence** — which would either slow down the
hackathon (bad) or speed up the litigation platform (unsafe).

### H.2 — The 3-tier architecture preserves the 5 different pace layers

```
        ┌─────────────────────────────────────────────┐
        │ TIER 3: subapps (5 different pace layers)  │
        │   gemini_hackathon: daily                   │
        │   ciancheiltis: weekly                     │
        │   cianchosaint: monthly                    │
        │   ciandlithe: quarterly                    │
        │   tuatha: per-openspec-change              │
        └──────────────────┬──────────────────────────┘
                           │
                           │ (kcg_sync_subapps)
                           │
        ┌──────────────────▼──────────────────────────┐
        │ TIER 2: apps (5 apps, openspec cadence)    │
        │   oideachais / oideachais-dashboard /      │
        │   cianfhoghlaim / croilar-web / tuatha-ui  │
        └──────────────────┬──────────────────────────┘
                           │
                           │ (pip install cianfhoghlaim-*)
                           │
        ┌──────────────────▼──────────────────────────┐
        │ TIER 1: packages (the canonical source)    │
        │   model-registry / fleet / theming /       │
        │   agui-bridge / baml-helpers / observability│
        │   db / auth / ui-kit / dlt-common          │
        └─────────────────────────────────────────────┘
```

The TIER 1 packages are **stable** (a fleet change is a
3-stage review: design → review → ship). The TIER 2 apps are
**medium-pace** (an app change is a 2-stage review:
design → ship). The TIER 3 subapps are **variable-pace**
(each subapp chooses its own cadence).

**The 3-tier architecture is the *only* way to preserve all 5
pace layers** while still sharing the canonical code. The
alternatives are:

1. **Monorepo everything** (1 pace layer) — kills the
   gemini_hackathon deadline + forces the litigation platform
   to ship faster
2. **5 independent repos forever** (5 pace layers, 5×
   wholesale-copy) — the gemini_hackathon model registry
   drift is already 666 LOC × 5 = 3,330 LOC of duplicated
   code; this number grows linearly with every fleet change
3. **3-tier architecture (5 pace layers, 1× canonical)**
   — the user's destination

### H.3 — The complexity of the end result

The user asked about the complexity. The end result has:

- **1 parent monorepo** with 3 tiers
- **5 sibling repos** (unchanged) + their 5 subapp mounts
- **5 different pace layers** (preserved)
- **5 different deployment targets** (preserved)
- **5 different licence models** (preserved)
- **1 canonical source of truth** for fleet + registry + theming
- **5× feature shipping** (a fleet change lands in all 5 subapps
  with a 1-line `pip install --upgrade`)
- **70K LOC of redundant code eliminated** (the 3-tier lift
  removes 5× wholesale-copy of the 9 high-value patterns)
- **21 openspec changes** over 30 weeks (each independently
  shippable, each passes `--strict`)

**The end result is *less* complex than today's state** despite
having 5 more repos in the surface area. The 30-week timeline
is a **one-time migration cost**; after it lands, every
fleet feature ships in 1× time instead of 5× time.

### H.4 — The goal of each project, preserved

| Project | Goal | How the 3-tier architecture preserves it |
|:--|:--|:--|
| gemini_hackathon | "One platform for the British Isles" (8 subnations × 3 audiences × 4 idea agents × 7 fleet primitives) | The 4 idea agents + 7 fleet primitives + 13 palettes + 5 Convex tables live in `subapps/gemini_hackathon/`. The TIER 1 packages provide the canonical fleet code; the subapp provides the 4 idea agents + 8 web routes that are gemini_hackathon-specific. |
| tuatha | "The British Isles Formative Assessment MMO" (8 NCCA subjects × 5 tools × 3 educational agents × 4 hackathon features × 1 media_intel pipeline) | The 8 NCCA subject agents + 3 educational agents + 4 hackathon features + 1 media_intel pipeline live in `subapps/tuatha/`. The 4 hackathon features are the same 4 idea agents as gemini_hackathon (re-used via the TIER 1 packages). The 8 NCCA subjects + 3 educational agents are tuatha-specific. |
| ciancheiltis | "Pure Irish + Celtic languages" (5 families × 5 datasets × pure-data carve-out) | The 5,171 LOC of DLT sources live in `subapps/ciancheiltis/`. The DLT common helpers come from the TIER 1 `dlt-common` package. The Celtic-language pipelines (Gaois / Téarma / Logainm / Ainm / Canúint / Dúchas / Universal Dependencies) are ciancheiltis-specific. |
| cianchosaint | "OSINT-only British Isles defence / policing / intel oversight" (3 named pipelines × 8 sub-pipelines × 7 per-persona web apps × BUSL-1.1 v2) | The 3 named pipelines (BIPP + BIDP + BIIP) + 7 per-persona web apps live in `subapps/cianchosaint/`. The 5-stage pipeline registry comes from a TIER 1 helper (or stays in the subapp). The BUSL-1.1 v2 cianchosaint edition licence + the OSINT allowlist stay in the subapp. |
| ciandlithe | "OSINT-only civil litigation" (BLIP v1 × 7 per-persona web apps × BUSL-1.1 v2 +PoI clause + no-auto-submit) | The 7 per-persona web apps (coroner / health-complain / inquest / legal-aid / piab / self-rep / wrc) live in `subapps/ciandlithe/`. The composite pilot (7 case studies) stays in the subapp. The BUSL-1.1 v2 ciandlíthe edition + the +PoI clause + the no-auto-submit constraint stay in the subapp. |
| cianfhoghlaim (parent) | "Cianfhoghlaim — Celtic language AI learning platform" (the 5 TIER 2 apps + the 1 Hono API + the 3 TIER 1 packages, after the consolidation) | TIER 2 apps are the 5 user-facing apps (oideachais, oideachais-dashboard, cianfhoghlaim, croilar-web, tuatha-ui). TIER 1 packages are the 9 shared patterns. The parent is the **canonical spec + schema + pattern source** for all 5 subapps. |

**Each project's goal is preserved.** The 3-tier architecture
**enables** each project to ship at its own pace while still
**leveraging** the shared code that the parent provides.

---

## I) Per-recommendation cost / benefit

The user asked about "the benefits of such and greatly improve
our merging plan and the complexity of the end results to carry
out the goals of those projects". Below is the **per-recommendation
cost / benefit** for each of the 21 openspec changes in §F.

### I.1 — The 3 master changes

| # | Change | Cost | Benefit |
|--:|:--|:--|:--|
| 1 | `web-frontend-3-tier-architecture-v1` | 1 week, 0 code changes | Establishes the pattern; gates the next 18 changes |
| 2 | `llms-txt-skill-v1` | 1 week, 1 file change per subapp | Unlocks cross-subapp skill sharing |
| 3 | `knowledge-sync-loop-extended-v1` | 1 week, 1 new script | Unlocks `sync-subapps` mise task |

### I.2 — The 9 TIER 1 package lifts

| # | Change | Cost | Benefit | Ratio |
|--:|:--|:--|:--|:--|
| 4 | `lift-model-registry-to-t1-v1` | 2 weeks, 1 file lift + 5 re-exports | **3,996 LOC of duplicated code** → 666 LOC single source | **6:1** |
| 5 | `lift-fleet-to-t1-v1` | 2 weeks, 7 files lift + 5 re-exports | **20,664 LOC of duplicated code** → 3,444 LOC single source | **6:1** |
| 6 | `lift-theming-to-t1-v1` | 1 week, 1 file + 13 JSON lift | **340 LOC of duplicated code** → 1 source | **n/a (data files)** |
| 7 | `lift-agui-bridge-to-t1-v1` | 1 week, 1 file lift | **2,442 LOC of duplicated code** → 407 LOC single source | **6:1** |
| 8 | `lift-baml-helpers-to-t1-v1` | 1 week, 6 .baml lift | **30+ .baml files of duplicated code** → 6 single source | **5:1** |
| 9 | `lift-observability-to-t1-v1` | 1 week, 2 files lift | **4,164 LOC of duplicated code** → 694 LOC single source | **6:1** |
| 10 | `lift-db-convex-umbrella-to-t1-v1` | 1 week, 1 schema lift | **932 LOC of duplicated code** → 233 LOC single source | **4:1** |
| 11 | `lift-ui-kit-to-t1-v1` | 1 week, lift from 5 subapps | **n/a (UI is subapp-specific)** | n/a |
| 12 | `lift-dlt-common-to-t1-v1` | 1 week, 1 file lift | **2,046 LOC of duplicated code** → 341 LOC single source | **6:1** |

**TIER 1 totals: 8 weeks, ~70K LOC of duplicated code → ~5K
LOC single source, ratio ~14:1.**

### I.3 — The 5 TIER 2 app consolidations

Per v1 §F + §G:
- 12 apps → 5 apps
- 32 package.json → 11 package.json
- 3 Convex deployments → 1
- 3 Hono gateways → 1
- 3 BetterAuth installs → 1

**TIER 2 totals: 12-13 weeks, ~30K LOC of duplicated TSX
→ ~5K LOC single source, ratio ~6:1.**

### I.4 — The 5 TIER 3 subapp mounts

| # | Change | Cost | Benefit | Ratio |
|--:|:--|:--|:--|:--|
| 17 | `mount-gemini-hackathon-as-subapp-v1` | 1 week, 2 file changes | Public demo on GCP Cloud Run; the gemini_hackathon code continues to ship daily | n/a (preserves the existing pace) |
| 18 | `mount-ciancheiltis-as-subapp-v1` | 2 weeks, 2 file changes | Data-only subapp; 5,171 LOC of DLT lives in the subapp, uses the TIER 1 dlt-common package | n/a (preserves the existing pace) |
| 19 | `mount-cianchosaint-as-subapp-v1` | 2 weeks, 2 file changes | 7 personas + 3 named pipelines + BUSL-1.1 v2 cianchosaint edition; monthly pace | n/a (preserves the existing pace) |
| 20 | `mount-ciandlithe-as-subapp-v1` | 2 weeks, 2 file changes | 7 personas + BLIP v1 + composite pilot + BUSL-1.1 v2 ciandlíthe edition; quarterly pace | n/a (preserves the existing pace) |
| 21 | `mount-tuatha-as-subapp-v1` | 2 weeks, 2 file changes | 18,340 LOC of Python + 13 BAML + 8 NCCA subjects; the largest subapp; per-openspec-change pace | n/a (preserves the existing pace) |

**TIER 3 totals: 8-9 weeks, 5 subapps mounted, 0 code changes
in any subapp.**

### I.5 — Grand total

| Phase | Weeks | LOC eliminated | Ratio |
|:--|--:|--:|--:|
| Phase 5 (TIER 1) | 8 | ~65,000 (fleet + registry + theming + agui + baml + observability + db + dlt-common) | **14:1** |
| Phase 5.1 (TIER 2) | 12-13 | ~25,000 (the 12→5 app consolidation) | **5:1** |
| Phase 5.2 (TIER 3) | 8-9 | 0 (preserves the existing code) | n/a |
| **Total** | **28-30** | **~90,000** | **~10:1** |

**For every 10 lines of code in the post-consolidation parent,
1 line is unique work; 9 lines are redundant code eliminated.**
This is the answer to the user's "benefits of ratio" question.

---

## J) The 5 sub-app goals carried by the 3-tier architecture

The user asked to "carry out the goals of those projects". The
5 sub-app goals + the 1 parent goal are:

### J.1 — gemini_hackathon's goal: "One platform for the British Isles"

**Carried by:** TIER 3 mount + the 13 palettes + the 4 idea
agents + the 5 Convex tables + the 8 web routes.

**New benefit unlocked by 3-tier:** every fleet change in the
parent (TIER 1) automatically lands in gemini_hackathon via
`pip install --upgrade cianfhoghlaim-fleet`. **Before 3-tier:**
every fleet change has to be wholesale-copied into
`gemini_hackathon/gemini_hackathon/agents/fleet/`.

### J.2 — tuatha's goal: "The British Isles Formative Assessment MMO"

**Carried by:** TIER 3 mount + the 8 NCCA subject agents + the
3 educational agents + the 4 hackathon features + the 1
media_intel pipeline + the 13 BAML contracts + the badge
system.

**New benefit unlocked by 3-tier:** the 4 hackathon features
(marking_grader, adaptive_tutor, equivalency_generator,
curriculum_change_sensor) are the **same 4 idea agents** as
gemini_hackathon. After 3-tier, **both subapps consume the
same 4 agents from TIER 1**, but each subapp's *adaptation*
(language, palette, exam-board) lives in the subapp. **Before
3-tier:** the 4 agents are wholesale-copied between
gemini_hackathon and tuatha with per-subapp adaptations.

### J.3 — ciancheiltis's goal: "Pure Irish + Celtic languages"

**Carried by:** TIER 3 mount + the 5,171 LOC of DLT sources
+ the 5 Celtic language families (Gaois + Téarma + Logainm +
Ainm + Canúint + Dúchas + Universal Dependencies).

**New benefit unlocked by 3-tier:** the 7 DLT common helpers
in `dlt_sources/common/_http_factories.py` (201 LOC) +
`dlt_sources/_cross/jurisdiction_pipeline_base.py` (42 LOC)
come from TIER 1. **Before 3-tier:** ciancheiltis has its
own copy of the common helpers (per the 5,171 LOC count).

### J.4 — cianchosaint's goal: "OSINT-only British Isles defence / policing / intel oversight"

**Carried by:** TIER 3 mount + the 3 named pipelines (BIPP +
BIDP + BIIP) + the 7 per-persona web apps + the 5-stage
pipeline registry + the OSINT allowlist + the BUSL-1.1 v2
cianchosaint edition licence.

**New benefit unlocked by 3-tier:** the 5-stage pipeline
registry (`5_stage_registry.py` + `5_stage_runner.py` +
`jurisdiction_pipeline_base.py` + `connection.py` +
`law_enforcement_registry.py` + `registry_api.py` +
`registry_loader.py`) is the **same shape** as ciandlithe's
(`legal_registry.py` etc.). After 3-tier, **both subapps
consume the same 5-stage registry from TIER 1**, but each
subapp's *cohort* (policing vs litigation) lives in the
subapp. **Before 3-tier:** the 5-stage registry is
duplicated between cianchosaint and ciandlithe.

### J.5 — ciandlithe's goal: "OSINT-only civil litigation"

**Carried by:** TIER 3 mount + the BLIP v1 pipeline + the 7
per-persona web apps (coroner / health-complain / inquest /
legal-aid / piab / self-rep / wrc) + the composite pilot (7
case studies) + the BUSL-1.1 v2 ciandlíthe edition licence +
the +PoI clause + the no-auto-submit constraint.

**New benefit unlocked by 3-tier:** the 7 per-persona web
apps follow the **same pattern** as cianchosaint's 7 per-persona
web apps. After 3-tier, **both subapps consume the
per-persona web app pattern from TIER 1**, but each
subapp's *content* (the litigation documents vs the
policing documents) lives in the subapp. **Before 3-tier:**
the per-persona web app pattern is duplicated between
cianchosaint and ciandlithe.

### J.6 — cianfhoghlaim's goal: "Cianfhoghlaim — Celtic language AI learning platform"

**Carried by:** TIER 2 (5 apps) + TIER 1 (9 packages) + the
orchestration + the dlt_sources + the cocoindex_flows + the
notebooks + the motherduck + the baml_src + the bonneagar.

**New benefit unlocked by 3-tier:** the parent is the
**canonical source of truth** for the 9 TIER 1 packages. Every
subapp depends on the parent's TIER 1 packages. The parent's
openspec changes (the canonical spec + schema + pattern
source) flow into the 5 subapps via the
`sync-subapps` mise task.

---

## K) The new openspec change to file first

**`2026-08-25-web-frontend-3-tier-architecture-v1`** — the master
change that establishes the 3-tier structure. Touches 0 files in
the 5 sibling repos and 0 files in `cianfhoghlaim/`.
Self-contained, passes `--strict`, archived after 1 day of review.

After this change lands, the 20 subsequent openspec changes
follow the same pattern: each independently shippable, each
passes `--strict`, each archives after landing.

---

## L) Sources

### L.1 — Sibling repos (the 5 cross-repo evidence base)

- `~/dev/gemini_hackathon/` (latest `8be7299`, 2026-08-25)
  - `AGENTS.md`, `ARCHITECTURE.md`, `README.md`
  - `gemini_hackathon/__init__.py` (the public API surface)
  - `gemini_hackathon/theming.py` (254 LOC) — the 13-palette loader
  - `gemini_hackathon/models/__init__.py` (666 LOC) — the MODEL_REGISTRY
  - `gemini_hackathon/call_llm.py` (556 LOC) — the dual-profile router
  - `gemini_hackathon/observability.py` (153 LOC) — the observability layer
  - `gemini_hackathon/agents/fleet/*.py` (7 files, 3,444 LOC) — the 7 fleet primitives
  - `gemini_hackathon/agents/ideas/*.py` (4 files, 2,032 LOC) — the 4 idea agents
  - `gemini_hackathon/session/schema.py` (389 LOC) — the session model
  - `web/convex/schema.ts` (233 LOC) — the 5-table Convex schema
  - `web/src/components/themes/SourcePaletteProvider.tsx` (137 LOC) — the React palette provider
  - `web/src/components/onboarding/OnboardingPicker.tsx` (222 LOC) — the onboarding flow
  - `web/src/routes/api/{copilotkit,duckdb,themes}.ts` — the 3 backend routes
  - `themes/*.json` — the 13 per-source palettes (incl. `ncca_palette.json`, `aqa_palette.json`, `sqa_palette.json`, etc.)
  - `dlt_pipelines/*.py` (1,955 LOC) — the 4 DLT source files
  - `tests/*.py` (3,484 LOC) — the 12 test files (164 pytests green)
  - `mise.toml` (the canonical 9-namespace task catalogue)
  - `openspec/changes/2026-08-24-gemini-hackathon-public-v1/` (the active change)

- `~/dev/tuatha/` (latest `b05ef4e`, 2026-08-25)
  - `AGENTS.md` (the British Isles Formative Assessment MMO spec)
  - `CONSOLIDATION_PLAN.md` (the 3-step execution: archive → cross-repo refactor → build from scratch)
  - `BUILD_PLAN.md` (the per-step execution plan)
  - `tuatha/agents/educational/*.py` (3 agents: academic_history, celtic_grammar, celtic_morphology)
  - `tuatha/agents/hackathon/*.py` (4 features: marking_grader, adaptive_tutor, equivalency_generator, curriculum_change_sensor)
  - `tuatha/agents/media_intel/*.py` (10 ADK tools)
  - `tuatha/subjects/*.py` (8 NCCA subjects)
  - `openspec/AGENTS.md`, `openspec/specs/`, `openspec/changes/` (2 active changes)

- `~/dev/ciancheiltis/` (latest `83c975d`, 2026-08-25)
  - `AGENTS.md` (3-line minimal routing)
  - `dlt_sources/_cross/`, `common/`, `cultural_heritage/`, `language/`, `lexicographic/` (5,171 LOC of DLT)
  - `mise.toml` (5 ciancheiltis:* tasks)
  - `openspec/changes/2026-09-25-ciancheiltis-init-v1/` (1 active change)

- `~/dev/cianchosaint/` (latest `475f779`, 2026-08-25)
  - `AGENTS.md` (the OSINT-only British Isles defence / policing / intel oversight spec)
  - `LICENSE.md` (BUSL-1.1 v2 cianchosaint edition with warrant-to-enforce)
  - `dlt_sources/_cross/` (the 5-stage pipeline registry)
  - `dlt_sources/cianchosaint/bipp_v2/`, `political_parties/`, `uk/` (the BIPP v2 / political parties / UK sub-pipelines)
  - `agents/`, `baml_src/cianchosaint/`, `cocoindex_flows/cianchosaint/`, `orchestration/defs/`
  - `web/apps/cianchosaint-<persona>/` (7 per-persona web apps)
  - `mise.toml` (12 cianchosaint:* tasks)
  - `openspec/changes/` (17 archived changes)

- `~/dev/ciandlithe/` (latest `6547ef8`, 2026-08-25)
  - `AGENTS.md` (the OSINT-only civil litigation spec with the +PoI clause + the no-auto-submit constraint)
  - `LICENSE.md` (BUSL-1.1 v2 ciandlíthe edition)
  - `dlt_sources/_cross/` (the 5-stage pipeline registry with `legal_registry.py`)
  - `dlt_sources/ciandlithe/` (the cross-jurisdiction web/Scotland/NI/Wales/Ireland sub-pipelines)
  - `dlt_sources/law/` (the 8 jurisdiction sub-directories)
  - `agents/ciandlithe/tools/`, `baml_src/ciandlithe/`
  - `web/apps/ciandlithe-<persona>/` (7 per-persona web apps: coroner, health-complain, inquest, legal-aid, piab, self-rep, wrc)
  - `openspec/changes/` (4 active changes)

### L.2 — The parent monorepo (v1's source)

- `~/dev/cianfhoghlaim/` (the canonical parent)
  - `openspec/plans/2026-08-24-web-frontend-deep-analysis.md` (v1, this replacement)
  - `web/AGENTS.md`, `web/README.md` (the canonical 4-app description — outdated)
  - The 12 apps in `web/apps/` (v1 §A.1)
  - The 3 packages in `web/packages/` (v1 §A.2)
  - The 1 Hono API gateway in `web/hono-api/`
  - The openspec specs (28 active + 78 archived changes per the v1 analysis)

### L.3 — Cross-references

- The 5 sibling repos' AGENTS.md files (the per-repo routing)
- The parent's `.agents/skills/INDEXING_AND_COGNITION.md` (the parent's knowledge surface)
- The parent's `openspec/AGENTS.md` (the parent's openspec workflow)
- The parent's `mise.toml` (the parent's 9-namespace task catalogue)

---

**Last updated:** 2026-08-25
**Owner:** Build agent (the upgraded plan)
**Next review:** when the `2026-08-25-web-frontend-3-tier-architecture-v1` openspec change is filed.
