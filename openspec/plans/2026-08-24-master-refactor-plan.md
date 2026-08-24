# Master Refactor Plan — Cianfhoghlaim Monorepo (2026-08-24)

> **Read-only synthesis subagent deliverable.** This plan consolidates the three
> 2026-08-24 deep-analysis reports (orchestration/cocoindex/lakehouse, web frontend,
> and the missing DLT deep-analysis — substituted inline with the canonical
> `dlt_sources/AGENTS.md` + `LEGACY_ALIASES.md`) plus upstream-verified best
> practices from `dlthub.com`, `docs.dagster.io`, `cocoindex.io`, and
> `tanstack.com`. Date: 2026-08-24. Repo: `/Users/cianmacandeisigh/dev/kings_college_galway`.
>
> **Authoritative scope.** This plan supersedes the sub-reports; the source-of-truth
> for the action plan lives here. Sub-reports remain as evidence + line-level audit.

---

## Section 1 — Executive summary

### 1.1 What is being refactored

Six interleaved surfaces, in strict dependency order:

| # | Surface | Current state | Target state |
|--:|:--|:--|:--|
| 1 | **`dlt_sources/`** | 1,905 `.py` files · 920 `@dlt.source` · 13 top-level sub-trees · `language/` is a grab-bag of 11 unrelated sub-domains · 619 empty `defs.yaml` placeholders under `orchestration/defs/1_ingestion/` · dual `destinations_*.py` (`destinations_cianfhoghlaim.py` + `destinations_tuatha.py`) | KEEP-ENGLISH geographic packages · 3 themed sub-trees under `language/` (lexicographic / cultural_heritage / language_models) · layer-grouped `destinations/ducklake.py` + `destinations/motherduck.py` + `destinations/filesystem.py` · canonical `jurisdiction_pipeline_base.py` (already exists) · `cognee_health`, `lakehouse_staging`, `personal_archive_destinations` reused via `dlt_sources/_lakehouse/` |
| 2 | **`orchestration/`** | 5-layer Component model (1.13+ `dg.load_defs()`) is **partially** applied: L3 = 96 `defs.yaml` files (modern); L1 = hand-rolled + `_base` factory broken (`definitions.py:189`); L2 = mixed (BIEP v3 modern, 33 per-subject legacy); L4 = mixed; L5 = hand-rolled. Post-2026-08-23 UoG + NUI + media_intel batch bypasses Components. | Re-theme Dagster as **per-pipeline Components** that mirror the dlt source tree. Each dlt source gets a Dagster Component (`orchestration/pipelines/<pipeline>/`) — assets auto-derived from the dlt source schema via `DltLoadCollectionComponent` (per the Dagster 1.13+ canonical pattern). State-backed Components handle the per-jurisdiction factory pattern (`StateBackedComponents` with `LOCAL_FILESYSTEM` state). |
| 3 | **`cocoindex_flows/`** | v1 (PyPI package not installed — `COCOINDEX_AVAILABLE=False`). 96 Apps use legacy `mount_table_target` direct + module-scope `app`. **88 of 96 L3 `defs.yaml` use pre-v7 module path `cianfhoghlaim.cocoindex.<app>`** (the **Wave 0 blocker** — broken at execute time). | Install PyPI `cocoindex>=1.0,<2.0,!=1.0.8`. Convert 5 highest-impact Apps to Live mode (`LocalComponent` + `process_live(operator)`). Adopt target-state declarative API (`declare_row`/`declare_file`). Wire `coco.auto_refresh(interval=...)` for the polling Apps. |
| 4 | **`dlt_sources/_lakehouse/` (DuckLake)** | DuckLake v1.0 + Postgres catalog + Garage S3 + Iceberg REST (Lakekeeper). **6 legacy namespaces** (`ducklake_oideachais` / `ducklake_crypteolas` / `ducklake_croilar` / `ducklake_tuath` / `ducklake_meaisinfhoghlaim` / `ducklake_aleyum`) need consolidation into `ducklake_cianfhoghlaim`. No `data_inlining`, no `sort expressions`, no data change feed, no per-namespace encryption yet. | Single namespace `ducklake_cianfhoghlaim` · `data_inlining` for small tables (`media_descriptors`, `apple_photos_metadata`) · `sort expressions` for LC chunks (`ORDER BY (subject, board, year, language)`) · data change feed via `ducklake_table_changes` for cognify · per-namespace encryption for UoG · 30-day snapshot expiry policy. |
| 5 | **`web/`** | 12 apps under `web/apps/` · 18 framework roots (5 apps have nested sub-monorepos with their own `apps/api/` + `packages/{auth,db,...}/`) · 32 `package.json` files · 3 Hono gateways · 3 BetterAuth installs · 3+ independent Convex schemas · `web/AGENTS.md` describes only 4 apps (67% is undocumented drift). `_oideachais_apps/` is the legacy sruth-era archive (552 KB). | 5 apps + 5 packages + 1 hono-api. Archive `_oideachais_apps/` + `game_showcase/` + `tuatha-demo/`. Merge `croilar-portal/` → `croilar-web/`, `cianfhoghlaim-mmo/` → `tuatha-ui/`, `cianfhoghlaim-web/` → `cianfhoghlaim/`, `cianfhoghlaim-leaving-cert/` → `oideachais/`. Lift shared packages from sub-monorepos into root `web/packages/`. |
| 6 | **Frontend framework** | Mixed TanStack Start (some pre-1.0 Vinxi, some 1.0+) · CopilotKit v1.67 (the v1 line is approaching EOL) · no AG-UI · no A2UI · BetterAuth 1.0–1.4 (vs current 1.7) · Hono + oRPC where wired, raw handlers elsewhere. | TanStack Start 1.0+ (post-1.0 unified authoring model, multi-runtime deployment via wrangler). TanStack AI + TanStack DB + TanStack Form + TanStack Query + TanStack Router + TanStack Store (the full family). CopilotKit v2 + AG-UI (SSE protocol) + A2UI (Google declarative agent UI). Better Auth 1.7 (OIDC + 2FA + SIWE). Hono 4.8 on Cloudflare Workers. |

### 1.2 Why now

1. **The Wave 0 blocker is real.** The 88 `defs.yaml` files under `orchestration/defs/3_model_lifecycle/cocoindex_v1/` use `module: cianfhoghlaim.cocoindex.<app>` (the pre-v7 flat package path). The actual package is `cocoindex_flows/<subpkg>/<app>`. Every CocoIndex App fails at execute time with `cocoindex_v1_module_import_failed`. Per the orchestration report: *"88 of the 95 L3 defs.yaml files still use the pre-refactor flat layout — these Apps are broken at execute time."* This blocks BIEP, the Leabharlann embedder, the upstream monitors, and the 5th-leabharlann-corpus (Apple Photos) simultaneously.
2. **The language/ grab-bag.** `dlt_sources/language/` mixes 3 distinct domains: (a) **lexicographic** resources (ainm, canuint, duchas, gaois, tearma, logainm — 6 sources), (b) **cultural heritage** (heritage, hidden_heritages, celtic_mythology, local_documents_by_subject, local_education_documents — 5 sources), (c) **language models** (universal_dependencies — 1 source). Plus 4 canuint sub-shims (audio, dialect, search, alignment) and the 5 helper modules. The mixed bag forces every agent and every Dagster asset to enumerate by hand.
3. **The dual destinations split.** `dlt_sources/common/destinations_cianfhoghlaim.py` (canonical) and `dlt_sources/common/destinations_tuatha.py` (legacy v4 era) coexist. Same for the new `dlt_sources/_lakehouse/destinations.py` (the lakehouse bridge). Three files for one concern. Every destination code path must check all three.
4. **The 619 empty placeholder YAMLs.** Per the `dlt_sources/AGENTS.md` (line 246): *"The 619 empty placeholder YAMLs in orchestration/defs/1_ingestion/{american_nations,commonwealth,european_nations,...}/ are audited as dead. They reference nations/stages that have already been absorbed into the v3 generic pipeline pattern. They are NOT loaded by `mise run dagster:dev` and can be safely deleted in the cleanup follow-up (issue #146)."* Issue #146 was filed but never closed.
5. **Web sub-monorepo duplication.** Per the web frontend report: 2 of the 12 apps (`cianfhoghlaim-web` + `cianfhoghlaim-leaving-cert`) each maintain their own private `apps/api/` + `packages/{auth,config,convex,db,i18n,ui}/`. The root `web/packages/` is **3 source files total** — basically empty shells. Only 3 of 12 apps actually consume the root packages.
6. **The post-2026-08-23 batch bypasses Components.** The 8 hand-rolled files in `orchestration/defs/` (`uog_exam.py`, `uog_official_docs.py`, `uog_personal_archive.py`, `uog_personal_archive_figures.py`, `uog_students_union.py`, `nui_federation.py`, `british_isles_tertiary.py`, `media_intel.py`) are the UoG personal-archive delivery — but they were added as flat `.py` files instead of as Components. This is a regression that needs to be inverted (rebuilt as Components).
7. **2026-08-13 + 2026-08-22 drift docs.** The `mise run lint:drift-docs` gate (added 2026-07-29) caught 1959 pre-v7 occurrences. ~83% were auto-fixed; the rest are still pending manual review (per the orchestration report §E.4 — `orchestration/AGENTS.md` claims 199 assets + 16 sensors but actual is ~190 assets + 13 sensors).

### 1.3 The user's stated priorities (this session)

Per the brief, in execution order:

1. **CIANFHOGHLAIM IRISH streamlining** — keep English in geographic paths (don't translate `british_isles` / `american_nations` / `european_nations` / `european_union` / `commonwealth` / `celtic` to Irish). The Irish-language layer (`gaeilge.py`, `tearma.py`, `ainm.py`) lives as data files within these directories, not as directory names.
2. **Analyse-and-restructure for themed packages** — break up the `language/` grab-bag, the `media/` grab-bag, the `official_media/` half-and-half, the `portfolio/` grab-bag. Each themed sub-tree should hold ONE concern.
3. **Layer-grouped destinations** — replace `destinations_cianfhoghlaim.py` + `destinations_tuatha.py` + the lakehouse `destinations.py` with `destinations/{ducklake,motherduck,filesystem}.py` keyed by **what the destination is**, not by **who wrote it**.
4. **Dagster re-themed as pipeline-themed asset-based** — replace the 5-layer "by responsibility" model with a **per-pipeline** model where each pipeline Component mirrors a dlt source. Use the **dlt-Dagster integration** (`DltLoadCollectionComponent`) to auto-derive assets from the source schema.
5. **CocoIndex v0 → v1 migration** — install the PyPI package, adopt Live mode (`LocalComponent`), adopt target-state declarative API, adopt `coco.auto_refresh` for polling.
6. **DuckLake + Postgres catalog** — already canonical; consolidate the 6 legacy namespaces, add v1.0 best practices (`data_inlining`, `sort expressions`, data change feed, encryption).
7. **Firecrawl-driven Dagster auto-setup** — use Firecrawl MCP (the canonical `firecrawl_developer_search` tool) to fetch the latest Dagster Component patterns at scaffold time, so the agent that authors the per-pipeline Components always cites current upstream docs.

### 1.4 The 8-wave waterfall

```
Wave 0  Critical fixes         (3 days,  Blockers for everything)
  ↓
Wave 1  dlt_sources refactor    (3 weeks, KEEP-ENGLISH + themed packages + layer-grouped destinations)
  ↓
Wave 2  Dagster per-pipeline    (3 weeks, DltLoadCollectionComponent + StateBackedComponent)
  ↓
Wave 3  CocoIndex v1 Live       (2 weeks, install PyPI + 5 Apps to Live mode)
  ↓
Wave 4  Lakehouse hardening     (2 weeks, DuckLake v1.0 best practices + namespace consolidation)
  ↓
Wave 5  Web cascade             (4-6 weeks, 12 apps → 5 apps + 5 packages + 1 hono-api)
  ↓
Wave 6  Frontend modernisation  (3-4 weeks, TanStack Start 1.0+ + CopilotKit v2 + AG-UI + A2UI + Better Auth 1.7)
  ↓
Wave 7  Observability drift     (2 weeks, MlflowBackend + OTel semantic conventions + lint:drift-docs fixes)
  ↓
Wave 8  Final cleanup          (1 week,  openspec audit + AGENTS.md drift cleanup + tag)
```

Each wave depends on the prior. Wave 0 is a hard blocker. Wave 1–4 are the data platform (parallelisable with caveats). Waves 5–6 are the web/frontend stack (depend on the data platform being stable). Waves 7–8 are the final observability + audit cascade.

**Status (2026-08-24):** All 8 waves complete. See
`openspec/changes/2026-08-24-wave-8-final-cleanup/` for the
post-cascade audit.

### 1.5 The total budget

| Wave | Wall-time (1 person, sequential) | Wall-time (2 people, parallel) | Risk |
|--:|--:|--:|:--|
| 0 | 3 days | 3 days | None — pure mechanics |
| 1 | 3 weeks | 2 weeks | Medium — touches every DLT source import path |
| 2 | 3 weeks | 2 weeks | High — touches every asset |
| 3 | 2 weeks | 1 week | Low — additive only |
| 4 | 2 weeks | 1.5 weeks | Low — additive only |
| 5 | 6 weeks | 4 weeks | High — touches every web app |
| 6 | 4 weeks | 3 weeks | Medium — major version bumps |
| **Total** | **20 weeks** | **~14 weeks** | — |

### 1.6 Cross-cutting invariants (must hold throughout)

- **Relative imports inside packages.** `from .._shared.<file>` for cross-file references inside `dlt_sources/`. Never `from dlt_sources.x import y` from within `dlt_sources/x/` — import cycles (per `dlt_sources/AGENTS.md` §3, line 124).
- **No absolute namespaces in data pipelines.** Never `from cianfhoghlaim.dlt.*` — always `dlt_sources.*` (per root AGENTS.md §3).
- **MODULE_REGISTRY only.** No hard-coded model strings. Use `model_for(family, role, language)` or the equivalent in `meaisinfhoghlaim/models/model_registry.py` (per `centralized-model-registry` spec).
- **R1–R4 conformance** for every CocoIndex App (per `cocoindex_flows/AGENTS.md` line 62 + `orchestration/components/layer3_model_lifecycle.py:295`).
- **USE_LOCAL_SCRAPES=true** before any live scrape. Routes to `stedding/ingest_queue/` snapshot fallback (per `dlt_sources/AGENTS.md` §3).
- **Concurrent-write safety.** The 4-step edit protocol (status → edit → diff → stage) is mandatory (per the 2026-08-22 incident, see `openspec/specs/repo-hygiene-agent-routing/spec.md`).

---

## Section 2 — Current state audit

### 2.1 `dlt_sources/` (synthesised from `dlt_sources/AGENTS.md` + `LEGACY_ALIASES.md`)

The DLT deep-analysis report does **not yet exist** at
`openspec/plans/2026-08-24-dlt-deep-analysis.md` (confirmed via `ls`). This
section is therefore synthesised from the canonical
`dlt_sources/AGENTS.md` (the post-v7 reference doc) and
`dlt_sources/LEGACY_ALIASES.md` (the migration history).

#### 2.1.1 Top-level layout

```
dlt_sources/
├── __init__.py            (578 B)
├── AGENTS.md              (12.6 KB)
├── DATA_PLATFORM_ROUTER.md (15.6 KB)
├── LEGACY_ALIASES.md      (2.7 KB)
├── README.md              (5.0 KB)
├── cli.py                 (584 B)
├── future_nostalgia.json  (2.7 KB)
│
├── _lakehouse/            (the v1 lakehouse bridge — destinations + personal_archive_destinations)
├── american_nations/      (brazil, mexico, united_states, venezuela)
├── api_sources/           (15 sub-dirs: Spotify, SoundCloud, YouTube, GitHub, LinkedIn, ResearchGate, ...)
├── apple_photos/          (empty stub awaiting apple-photos-ingestion)
├── british_isles/         (BIEP focus — ireland, england, scotland, wales, ni, isle_of_man, jersey, guernsey, sct_wls_ni, crown_dependencies, _cross/)
├── common/                (25 helpers)
├── commonwealth/          (australia, canada, india, new_zealand, nigeria, south_africa)
├── crypteolas/            (Anam Web3 SBT + credential anchoring)
├── european_nations/      (40 nations × {education, government, law, medicine, statistics})
├── european_union/        (EUR-Lex, CEDEFOP, ECDC, EMA, Eurostat, Eurydice, ...)
├── filesystem/            (10 DLT filesystem pipeline utilities)
├── jobs/                  (long-running scheduled jobs — only government_circulars_job.py)
├── language/              (11 Celtic-language sources — the grab-bag)
├── media/                 (animation, celtic_history_research, comics, games, official, prose)
├── official_media/        (British Crown + Channel Islands feeds + fediverse + classifier)
├── portfolio/             (cv, teaching, artwork, labels, labels_scraper)
```

| Metric | Value | Source |
|--|--:|:--|
| `.py` files | **1,905** | `dlt_sources/AGENTS.md` line 5 |
| `@dlt.source` decorated functions | **920** | `dlt_sources/AGENTS.md` line 5 |
| `@dlt.resource` (helper) functions | **~4,900** | `dlt_sources/AGENTS.md` line 213 |
| Top-level sub-trees | **13** | `dlt_sources/AGENTS.md` line 6 |
| Schema-introspector returns | **1,963** rows (sources + resources) | `dlt_sources/AGENTS.md` line 217 |
| Generic BIEP v3 jurisdiction pipelines | **10** | `dlt_sources/AGENTS.md` line 101 |
| Empty placeholder YAMLs in `orchestration/defs/1_ingestion/` | **619** (audited dead) | `dlt_sources/AGENTS.md` line 246 |
| Legacy namespaces in DuckLake | **6** (`ducklake_oideachais`, `ducklake_crypteolas`, `ducklake_croilar`, `ducklake_tuath`, `ducklake_meaisinfhoghlaim`, `ducklake_aleyum`) | orchestration report §D.5 |
| Destination modules | **3** (`common/destinations_cianfhoghlaim.py` + `common/destinations_tuatha.py` + `_lakehouse/destinations.py`) | this audit |

#### 2.1.2 The `language/` grab-bag (the canonical example of the analysis-and-restructure ask)

```
dlt_sources/language/
├── ainm.py                    (Irish place-names)
├── canuint.py
├── canuint_audio.py
├── canuint_dialect_summary.py
├── canuint_search.py
├── canuint_word_alignment.py
├── celtic_mythology.py        (Mythological Cycle — Táin Bó Cúailnge etc.)
├── duchas.py                  (Schools' Collection — folklore)
├── duchas_images.py
├── gaois.py                   (Gaois/National Terminology Database)
├── gaois_combined.py
├── heritage.py                (Heritage Council of Ireland — sites & monuments)
├── hidden_heritages.py
├── local_documents_by_subject.py
├── local_education_documents.py
├── logainm.py                 (Placenames Database of Ireland)
├── tearma.py                  (tearma.ie — terminology)
├── tearma_search.py
├── universal_dependencies.py  (UD treebanks — a NLP dataset, not a heritage resource)
│
├── _canuint_helpers.py
├── _duchas_images_helpers.py
├── _gaois_helpers.py
├── _local_documents_helpers.py
├── _tearma_helpers.py
└── AGENTS.md
```

3 distinct domains conflated:

| Domain | Sources | Why it's distinct |
|:--|:--|:--|
| **Lexicographic / terminology** | `ainm.py`, `canuint.py` (×4), `duchas.py`, `gaois.py` (×2), `logainm.py`, `tearma.py` (×2) | Word-form + translation + definition — the *lexicon* |
| **Cultural heritage** | `celtic_mythology.py`, `duchas_images.py`, `heritage.py`, `hidden_heritages.py`, `local_documents_by_subject.py`, `local_education_documents.py` | Folklore + monuments + archival — the *narrative corpus* |
| **Language models / NLP** | `universal_dependencies.py` | Treebanks — a *training corpus* for ML, not a heritage source |

Each domain has different: ingestion cadence (lexicons ~monthly, heritage archival, UD snapshots), destination (lexicons → typed DuckLake tables, heritage → fulltext + BAML, UD → Arrow IPC for training), embedding strategy (lexicons → keyword sparse, heritage → BGE-M3 dense, UD → syntax-aware).

#### 2.1.3 The 619 empty placeholder YAMLs (the L1 dead code)

Per `dlt_sources/AGENTS.md` line 246:
> *"The 619 empty placeholder YAMLs in `orchestration/defs/1_ingestion/{american_nations,commonwealth,european_nations,...}/` are audited as dead. They reference nations/stages that have already been absorbed into the v3 generic pipeline pattern. They are NOT loaded by `mise run dagster:dev` and can be safely deleted in the cleanup follow-up (issue #146)."*

These are the legacy v4-era `defs.yaml` per-nation files that were created when there was a 1:1 file-per-jurisdiction mapping. They never had a real Component instance behind them — they were placeholders waiting for `dg scaffold`. Issue #146 was filed but never closed.

#### 2.1.4 The destinations duplication

Three files for one concern:

| File | Role | Status |
|:--|:--|:--|
| `dlt_sources/common/destinations_cianfhoghlaim.py` | Canonical (per `dlt_sources/AGENTS.md` §"The destination contract", line 138) | `get_dlt_destination()` factory at line 191; namespace defaults to `"cianfhoghlaim"` |
| `dlt_sources/common/destinations_tuatha.py` | Legacy v4-era Tuatha destinations | Used by the Tuatha MMO + crypteolas pipeline; not in AGENTS.md |
| `dlt_sources/_lakehouse/destinations.py` | DuckLake v1.0 bridge (newer, post-v7) | Used by `orchestration/resources.py:DuckLakeResource` per orchestration report §A.6 |
| `dlt_sources/_lakehouse/personal_archive_destinations.py` | UoG personal-archive DuckLake (post-2026-08-23) | Specific to the UoG batch |

#### 2.1.5 The LEGACY_ALIASES.md migration history

6 rename waves already complete on disk (per `dlt_sources/LEGACY_ALIASES.md`):

1. European nations ISO-3 → snake_case (39 codes: `alb` → `albania`, `cze` → `czechia`, …)
2. Commonwealth (6 codes: `aus` → `australia`, …)
3. Canada provinces (13 codes: `ab` → `alberta`, …)
4. Nigeria states (36 codes: `nga_abi` → `abia`, …)
5. British Isles collapse dual naming (`en` → `england`, `ni` → `northern_ireland`, `sct` → `scotland`, `wls` → `wales`, `iom` → `isle_of_man`, `jey` → `jersey`, `ggy` → `guernsey`)
6. Americas (`americas/` → `american_nations/`, `bra` → `brazil`, …)

The doc is **historical** (no `import dlt.european_nations.alb` shim remains).

---

### 2.2 `orchestration/` (synthesised from orchestration report §A)

| Metric | Value |
|--|--:|
| Total `.py` files | **127** |
| Core LOC | **~5,000** |
| Total LOC | **19,464** |
| Dagster version | **1.13+** (`dg.load_defs(defs_root=...)` canonical) |
| Walker fallback for Dagster <1.13 | **131 LOC** (`_defs_walker.py`) — bypasses Python 3.13 tokenizer bug |
| Components defined | **11** (5 KCG + 5 jurisdiction/topic + 1 federated OCR) |
| Components instantiated via `defs.yaml` | **~96** (all in L3 model_lifecycle) |
| Resources (`ConfigurableResource`) | **22** |
| Layers fully Componentised | **1/5** (only L3) |
| Schedules (`@schedule` decorators) | **8** (legacy, not componentisable in 1.13) |
| Sensors (`@sensor` decorators) | **13** (legacy) |
| Asset checks | **22** |

#### 2.2.1 The 5 layers — what's modern vs legacy

| Layer | Style | Notes |
|:--|:--|:--|
| **L1 ingestion** | **Legacy** | `CelticIngestionComponent` exists at `orchestration/components/layer1_ingestion.py:324` but **no** `1_ingestion/*/defs.yaml` files instantiate it. The 619 empty placeholder YAMLs (per §2.1.3) are here. |
| **L2 materials** | **Mixed** | BIEP v3 uses `BIEPSubjectComponent` via `defs.yaml`. The 33 per-subject Python `@asset` files (one per `<jurisdiction>_education/<subject>_assets.py`) are hand-rolled. |
| **L3 model_lifecycle** | **Modern** | **96 `defs.yaml` files** instantiate `CelticModelLifecycleComponent`. **88 of the 96 use the wrong module path** (`cianfhoghlaim.cocoindex.<app>` — the pre-v7 flat path). |
| **L4 asset_generation** | **Mixed** | `marimo_dashboards/` uses Component; `education_asset_assets.py` + `secrets/` + `orpc_routes/` + `tanstack_pages/` are hand-rolled. |
| **L4 budget / memory** | **Legacy** | Single hand-rolled file each (`firecrawl_budget_asset.py`, `docs_index_memory_job.py`). |
| **L5 agent_ops** | **Legacy** | 4 dirs (adk, agno, custom, meaisinfhoghlaim) + 2 hand-rolled files (`credential_assets.py`, `heritage_assets.py`). `CelticAgentOpsComponent` exists but is **never** instantiated. |
| **Schedules / sensors** | **Legacy** | `@schedule` / `@sensor` decorators (not Componentisable in Dagster 1.13). |

#### 2.2.2 The post-2026-08-23 hand-rolled batch (regression)

| File | LOC | Purpose | Bypasses |
|--|--:|:--|:--|
| `defs/uog_exam.py` | 96 | UoG exam-papers SSO | Components |
| `defs/uog_official_docs.py` | 177 | UoG 5 official-doc assets | Components |
| `defs/uog_personal_archive.py` | 325 | UoG personal-archive (Stage 0 → Stage 6 with typed_join) | Components |
| `defs/uog_personal_archive_figures.py` | 362 | 6 thesis-figure PDFs | Components |
| `defs/uog_students_union.py` | 75 | 2 Students' Union assets | Components |
| `defs/nui_federation.py` | 93 | NUI 3-asset federation | Components |
| `defs/british_isles_tertiary.py` | 111 | QUB/Ulster factory | Components |
| `defs/media_intel.py` | 809 | The big one — 5-layer media-intel spine | Components |

All hand-rolled. The 2026-08-23 batch was added to ship the UoG personal-archive fast, but it created a precedent that bypasses the canonical pattern.

#### 2.2.3 The partition explosion vs fix

| Module | Partitions | Status |
|:--|--:|:--|
| `orchestration/partitions.py` | **208** NCCA + **780** SEC | **DEPRECATED** (kept for back-compat) |
| `orchestration/partitions_v2.py` | **4** (early_childhood / primary / junior_cycle / senior_cycle) + **2-axis** (scope × year) | **CANONICAL** |

The `biiep_v3_scope_year_partition` has a **typo**: `DynamicPartitionsDefinition(name="cianhoghlaim_scope")` — missing the 'a' in Cianfhoghlaim. Documented at `partitions_v2.py:308-309` as a pre-existing typo requiring a LanceDB migration to fix.

---

### 2.3 `cocoindex_flows/` (synthesised from orchestration report §B)

| Metric | Value |
|--|--:|
| CocoIndex version | **v1** (per `_lifespan.py`) |
| PyPI `cocoindex` package installed | **NO** (`COCOINDEX_AVAILABLE = False` per `_lifespan.py:59`) |
| Repo-local package shadow | **YES** (`cocoindex_flows/_shared/`) |
| Apps total | **~96** (the L3 model_lifecycle count) |
| Apps broken (wrong module path) | **88 of 96** (Wave 0 blocker) |
| Embedder | `BAAI/bge-m3` 1024-d (per `_lifespan.py:107`) |
| Big Apps | `leabharlann_embedding.py` (38 KB), `unified_embedding.py` (22 KB), `code_embedding.py`, `codebase_graph.py` |

#### 2.3.1 CocoIndex v1 features NOT yet adopted

| v1 feature | Adopted? | Target apps |
|:--|:--|:--|
| **Live mode** (`app.update_blocking(live=True)`) | ❌ | All 96 |
| **`LocalComponent` protocol** (`process()` + `process_live(operator)`) | ❌ | `leabharlann_embedding.py`, `apple_photos_geospatial.py` |
| **`LiveMapView` / `LiveMapFeed`** | ❌ | `leabharlann_embedding.py`, `code_embedding.py` |
| **`coco.auto_refresh(interval=...)`** | ❌ | `upstream_blog_monitor.py`, `upstream_api_surface.py`, `apple_photos_metadata.py` |
| **Target state declarative** (`declare_row(...)`, `declare_file(...)`) | ❌ | All target declarations |
| **Schema-evolution handling** | ❌ | LC subject schemas |
| **`SingleWatcherGuard`** for `watch()` | ❌ | New connectors |
| **`Annotated[NDArray, EMBEDDER]`** | ❌ | All embedder columns |
| **`batching=True`, `runner=coco.GPU`, `as_async`, `version`, `deps`, `logic_tracking`** | ❌ | Performance |

---

### 2.4 `observability/` (synthesised from orchestration report §C)

13 modules · ~4,200 LOC total. Mature stack.

| File | LOC | Purpose |
|--|--:|:--|
| `env_config.py` | 300 | Canonical `CIANFHOGHLAIM_*` env-var matrix (7 vars) |
| `langfuse_config.py` | 442 | Langfuse v3 SDK + `@observe` |
| `logfire_config.py` | 464 | Pydantic Logfire SaaS |
| `mlflow_config.py` | 426 | MLflow v3 |
| `platform_tracer.py` | 615 | 3-backend fan-out |
| `unified_tracer.py` | 465 | `TracingBackend` ABC + `DatadogBackend` concrete |
| `agent_tracing.py` | 445 | Agent-specific trace helpers |
| `fastapi_middleware.py` | 257 | FastAPI OTLP middleware |
| `logging.py` / `logging_config.py` | 222 / 109 | structlog + Python logging |
| `ocr.py` | 423 | OCR-specific telemetry |
| `ragas_evaluator.py` | 327 | RAGAS as a Dagster asset_check |
| `dashboards/personal_archive.json` | 102 | Grafana dashboard for UoG |

OTel fan-out collector (post-2026-08-25): 10 application services emit OTLP/gRPC + OTLP/HTTP to `otel-collector` → fan-out to Logfire + Langfuse + MLflow.

---

### 2.5 `web/` (synthesised from web frontend report)

| Metric | Value |
|--|--:|
| Apps under `web/apps/` | **12** (including `_oideachais_apps` legacy archive) |
| Distinct framework roots | **18** (5 apps contain nested sub-monorepos) |
| `package.json` files | **32** |
| `.tsx` source files | **443** |
| `.ts` source files | **439** |
| Disk footprint of `web/apps/` (excl. node_modules) | **~80 MB** |
| Independent Convex deployments | **≥ 3** (`oideachais-dashboard/convex`, `cianfhoghlaim-web/convex`, `croilar-portal/convex`, `cianfhoghlaim-mmo/convex`) |
| Independent Hono gateways | **≥ 3** (`web/hono-api/`, `cianfhoghlaim-web/apps/api/`, `cianfhoghlaim-leaving-cert/apps/api/`) |
| Independent Better-Auth installs | **≥ 3** |
| Independent CopilotKit installs | **≥ 5** |
| Root `web/packages/` source LOC | **3 ts files total** (the placeholders) |

#### 2.5.1 The 12 apps (full tier table from web frontend report §F.1)

| App | Tier | Action | LOC (tsx/ts) |
|:--|:--|:--|--:|
| `oideachais/` | **1 canonical** | KEEP + invest | 92 / 93 |
| `oideachais-dashboard/` | **1 canonical** | KEEP + invest | 10 / 100 |
| `cianfhoghlaim/` | **1 canonical** | KEEP + grow (absorb `cianfhoghlaim-web`) | 15 / 4 |
| `croilar-web/` | **1 canonical** | KEEP + invest (absorb `croilar-portal`) | 27 / 10 |
| `tuatha-ui/` | **1 canonical** | KEEP + refresh (absorb `cianfhoghlaim-mmo`) | 15 / 13 |
| `croilar-portal/` | **2 merge** | MERGE → `croilar-web` as `/admin/` | 21 / 26 |
| `cianfhoghlaim-mmo/` | **2 merge** | MERGE → `tuatha-ui` (Babylon.js + 2D) | 9 / 7 |
| `cianfhoghlaim-web/` | **3 merge** | MERGE → `cianfhoghlaim/` | 56 / 39 |
| `cianfhoghlaim-leaving-cert/` | **3 merge** | MERGE → `oideachais/` | 130 / 62 |
| `tuatha-demo/` | **4 move out** | MOVE → `demos/tuatha-demo/` | 0 / 0 |
| `game_showcase/` | **4 move out** | MOVE → `demos/game_showcase/` | 0 / 0 |
| `_oideachais_apps/` | **5 archive** | ARCHIVE → `openspec/archive/2026-08-24-...` | 23 / 3 |

#### 2.5.2 The sub-monorepo duplication (the deep drift)

| App | Has own `apps/web`? | Has own `apps/api`? | Inner packages count |
|:--|:--:|:--|--:|
| `cianfhoghlaim-web/` | ✅ | ✅ | 4 (`api`, `auth`, `config`, `db`) |
| `cianfhoghlaim-leaving-cert/` | ✅ | ✅ | 7 (`api`, `auth`, `config`, `convex`, `db`, `i18n`, `ui`) |
| `croilar-portal/` | ❌ | ❌ | 0 (uses root) |
| `oideachais-dashboard/` | ❌ | ❌ | 0 (uses root) |
| `oideachais/` | ❌ | ❌ | 0 (uses root) |

The two apps with sub-monorepos together account for **11 of the 11 inner packages** in the repo. The root `web/packages/{auth,db,ui-kit}/` is **3 source files total** — basically empty shells.

---

### 2.6 The inter-surface contract (the cascade)

Per orchestration report §F, the propagation order is fixed:

```
dlt_sources/                  ← changes originate
       │
       ▼
orchestration/defs/1_ingestion/        (CelticIngestionComponent)
orchestration/defs/2_materials/        (CelticMaterialsComponent, BAML extraction)
       │
       ▼
cocoindex_flows/                       (L3 cocoindex v1 Apps, CelticModelLifecycleComponent)
       │
       ▼
orchestration/defs/4_asset_generation/ (marimo, TanStack, oRPC — CelticAssetGenerationComponent)
       │
       ▼
observability/                          (sync_health, sync:dagster, sync:cognee, sync:ccc)
```

The 7-layer sync (`mise run sync:all`) is the consistency gate:
`sync:paths` → `sync:ccc` → `sync:cognee` → `sync:skills` → `sync:mcp` → `sync:dagster` → `sync:drift-docs`.

---

## Section 3 — Target architecture

### 3.1 Design principles

1. **KEEP-ENGLISH for geographic paths.** `british_isles/`, `american_nations/`, `european_nations/`, `european_union/`, `commonwealth/`, `celtic/` stay English — they're standard ISO/toponym conventions. The Irish-language layer (`gaeilge.py`, `tearma.py`, `ainm.py`) lives as data files within these directories, not as directory names.
2. **One concern per themed sub-tree.** `language/` splits into 3; `media/` splits into 5; `official_media/` consolidates; `portfolio/` keeps as-is.
3. **Layer-grouped destinations.** Key by **what the destination is** (`ducklake`, `motherduck`, `filesystem`), not by **who wrote it** (`cianfhoghlaim`, `tuatha`, `personal_archive`).
4. **Per-pipeline Dagster Components.** Each dlt source tree becomes a Dagster Component. `DltLoadCollectionComponent` (per the canonical Dagster 1.13+ pattern) auto-derives assets from the source schema. `StateBackedComponent` handles the per-jurisdiction factory.
5. **Live CocoIndex apps.** The 5 highest-impact apps get `process_live(operator)` instead of imperative `mount_table_target`.
6. **Single DuckLake namespace.** `ducklake_cianfhoghlaim` consolidates the 6 legacy v4 namespaces.
7. **5 apps + 5 packages + 1 hono-api.** Web surface.

### 3.2 The canonical `dlt_sources/` layout (Wave 1 target)

```
dlt_sources/
├── __init__.py
├── AGENTS.md                              (rewritten to reflect new structure)
├── DATA_PLATFORM_ROUTER.md                (updated routing)
├── LEGACY_ALIASES.md                      (updated with Wave-1 migrations)
├── README.md
├── cli.py
│
│   # === layer-grouped destinations (NEW) ===
├── destinations/                           (replaces destinations_*.py triplet)
│   ├── __init__.py
│   ├── ducklake.py                         (DuckLakeCredentials + Postgres catalog + Garage S3 + Iceberg REST)
│   ├── motherduck.py                       (MotherDuck SaaS)
│   ├── filesystem.py                       (local DuckDB + filesystem + R2)
│   └── _common.py                          (shared credential validation + namespace defaults)
│
│   # === lakehouse bridge (RENAME) ===
├── _lakehouse/                             (kept; coordinates destinations + DuckLake pool)
│   ├── __init__.py
│   ├── pool.py                             (renamed from ducklake_pool.py)
│   ├── options.py                          (renamed from ducklake_options.py)
│   ├── personal_archive.py                 (renamed from personal_archive_destinations.py)
│   └── cognify_health.py                   (new — Phase-2 health-check destinations)
│
│   # === cross-cutting helpers (MOVED) ===
├── common/                                (kept; helpers only)
│   ├── ... (25 helpers, with destination files now deleted; only ducklake_options.py and ducklake_pool.py kept as deprecation shims)
│
│   # === GEOGRAPHIC — KEEP ENGLISH (NO CHANGE) ===
├── british_isles/                         (KEEP ENGLISH — ISO convention)
├── european_nations/                       (KEEP ENGLISH — 40 nations via _factory.py + 40 shims)
├── european_union/                         (KEEP ENGLISH — EUR-Lex, CEDEFOP, ECDC, EMA, Eurostat, Eurydice)
├── commonwealth/                           (KEEP ENGLISH)
├── american_nations/                       (KEEP ENGLISH — 4 nations)
├── celtic/                                 (KEEP ENGLISH — language family level, not Irish)
│
│   # === THEMED — restructure the grab-bags ===
│
├── lexicographic/                          (NEW — split from language/)
│   ├── ainm.py                             (Irish place-names)
│   ├── canuint.py + canuint_*.py           (4 sub-shims)
│   ├── duchas.py                           (the lexicon — see also cultural_heritage/duchas_corpus.py)
│   ├── gaois.py + gaois_combined.py
│   ├── logainm.py
│   ├── tearma.py + tearma_search.py
│   ├── _shared/                            (4 helper modules co-located)
│   └── AGENTS.md
│
├── cultural_heritage/                      (NEW — split from language/)
│   ├── celtic_mythology.py
│   ├── duchas_corpus.py                    (folklore corpus, separate from the lexicographic Duchas)
│   ├── heritage.py                         (Heritage Council sites & monuments)
│   ├── hidden_heritages.py
│   ├── local_documents_by_subject.py
│   ├── local_education_documents.py
│   ├── _shared/                            (moved helper)
│   └── AGENTS.md
│
├── language_models/                        (NEW — split from language/)
│   ├── universal_dependencies.py           (UD treebanks)
│   ├── _datasets/                          (aligned corpora + CoNLL-U)
│   └── AGENTS.md
│
├── official_media/                         (CONSOLIDATED — was already half-and-half)
│   ├── _resolver_live.py
│   ├── _shared/                            (classifier, fediverse, allowlist, source_resolver)
│   ├── british_crown/                      (NEW — split out)
│   ├── channel_islands/                    (NEW — split out)
│   ├── companies/                          (NEW — split out: companies_house, cro)
│   ├── fediverse/                          (NEW — split out)
│   ├── hmgcc/
│   ├── instagram_export.py
│   ├── tests/
│   ├── fixtures/
│   └── AGENTS.md                           (rewritten)
│
├── portfolio/                              (kept as-is — already coherent)
├── apple_photos/                           (kept — 5th leabharlann corpus)
├── api_sources/                            (kept)
├── filesystem/                             (kept)
├── jobs/                                   (kept)
├── media/                                  (KEPT AS-IS — 5 sub-themes already distinct)
├── crypteolas/                             (kept)
└── tests/                                  (consolidated from per-sub-tree tests/)
```

**Key rename waves for Wave 1 (full table in §7.1):**

| Old | New | Reason |
|:--|:--|:--|
| `dlt_sources/language/` | **deleted** (split into 3 themed sub-trees) | The grab-bag |
| `dlt_sources/language/duchas.py` | `dlt_sources/lexicographic/duchas.py` (the lexicon) | Lexicographic concern |
| `dlt_sources/language/duchas_images.py` | `dlt_sources/cultural_heritage/duchas_corpus.py` (the folklore corpus) | **Split** — Duchas is both a lexicon and a corpus |
| `dlt_sources/language/universal_dependencies.py` | `dlt_sources/language_models/universal_dependencies.py` | ML/NLP concern |
| `dlt_sources/common/destinations_cianfhoghlaim.py` | `dlt_sources/destinations/ducklake.py` + `dlt_sources/destinations/filesystem.py` + `dlt_sources/destinations/_common.py` | Layer-grouped destinations |
| `dlt_sources/common/destinations_tuatha.py` | `dlt_sources/destinations/ducklake.py` (merged) | Layer-grouped |
| `dlt_sources/_lakehouse/destinations.py` | `dlt_sources/_lakehouse/pool.py` (renamed) + `dlt_sources/destinations/ducklake.py` (the dlt bridge) | Layer-grouped |
| `dlt_sources/_lakehouse/personal_archive_destinations.py` | `dlt_sources/_lakehouse/personal_archive.py` | Renamed |

### 3.3 The canonical `orchestration/` layout (Wave 2 target)

The key transformation: **Dagster reorganised as per-pipeline Components**.

```
orchestration/
├── components/                             (Python class definitions — UNCHANGED)
│   ├── layer1_ingestion.py                 (CelticIngestionComponent + CelticFederatedOcrComponent)
│   ├── layer2_materials.py                 (CelticMaterialsComponent)
│   ├── layer3_model_lifecycle.py           (CelticModelLifecycleComponent)
│   ├── layer4_asset_generation.py          (CelticAssetGenerationComponent)
│   ├── layer5_agent_ops.py                 (CelticAgentOpsComponent)
│   ├── biep_subject_component.py
│   ├── biiep_ocr_ensemble_component.py
│   ├── england_board_subject_component.py
│   ├── england_cross_board_comparator_component.py
│   ├── junior_cycle_subject_component.py
│   ├── kcg_cognify_component.py
│   └── federated_ocr_component.py
│
├── pipelines/                              (NEW — per-pipeline Components, mirror dlt_sources/)
│   ├── _shared/                            (shared load helpers, defs_state, asset checks)
│   │   ├── dagster_dlt_integration.py      (the DltLoadCollectionComponent wrapper)
│   │   ├── state_helpers.py                (StateBackedComponent utilities)
│   │   ├── asset_checks.py                 (verification.py lifted here)
│   │   └── translations.py                 (the `translation:` key helpers)
│   │
│   ├── british_isles/                       (mirrors dlt_sources/british_isles/)
│   │   ├── _cross/{defs.yaml, registry_defs.yaml}
│   │   ├── ireland/{education,law,university}/<subject>/defs.yaml  (~  ~45 files)
│   │   ├── england/{aqa,ocr,edexcel}/defs.yaml
│   │   ├── scotland/sqa/defs.yaml
│   │   ├── wales/wjec/defs.yaml
│   │   ├── northern_ireland/ccea/defs.yaml
│   │   ├── isle_of_man/defs.yaml
│   │   ├── jersey/defs.yaml
│   │   ├── guernsey/defs.yaml
│   │   ├── sct_wls_ni/defs.yaml
│   │   └── crown_dependencies/defs.yaml
│   │
│   ├── european_nations/{_factory,albania..ukraine,_comparators}/defs.yaml  (~  ~42 files)
│   ├── european_union/{eur_lex,cedefop,ecdc,ema,eurostat,eurydice,commission_press}/defs.yaml
│   ├── commonwealth/{australia,canada(+provinces),india,new_zealand,nigeria(+states),south_africa}/defs.yaml  (~  ~55 files)
│   ├── american_nations/{brazil,mexico,united_states,venezuela}/defs.yaml
│   ├── celtic/{irish,welsh,scottish_gaelic,manx,cornish,breton,_comparators}/defs.yaml
│   │
│   ├── lexicographic/{ainm,canuint,duchas,gaois,logainm,tearma}/defs.yaml  (NEW)
│   ├── cultural_heritage/{celtic_mythology,duchas_corpus,heritage,hidden_heritages,local_documents}/defs.yaml  (NEW)
│   ├── language_models/universal_dependencies/defs.yaml  (NEW)
│   │
│   ├── official_media/{british_crown,channel_islands,companies,fediverse,instagram_export}/defs.yaml  (NEW)
│   ├── portfolio/{cv,teaching,artwork,labels}/defs.yaml
│   ├── apple_photos/{metadata,chunks,geospatial}/defs.yaml
│   ├── api_sources/{spotify,soundcloud,youtube,github,linkedin,researchgate,...}/defs.yaml  (~  ~15 files)
│   ├── filesystem/.../defs.yaml  (~  ~10 utilities)
│   │
│   ├── media_intel/{l1_ingestion,official_sub_buckets,l2_baml,l3_cocoindex,l4_marimo,l5_adk}/defs.yaml  (the big spine)
│   ├── infrastructure_companion/{codebase_index,api_endpoints,filesystem_layout,storage_backends,config_files}/defs.yaml
│   ├── unsloth_serve/{model_registry_sync,vision_compare_job}/defs.yaml
│   └── sync/{sync_health,dagster_sync_health,baml_sync_health,ccc_sync_health,cognee_sync_health}/defs.yaml
│
├── sensors/                                (kept as-is — @sensor decorators not Componentisable in 1.13)
│   ├── ncca_registry_sensor.py
│   ├── ccea, sqa, wjec, jcq, jersey, guernsey, isle_of_man
│   ├── ocr_completion_sensor.py
│   ├── meaisin_education_ops_sensor.py
│   ├── garage_pdf_arrival_sensor.py
│   ├── upstream_breaking_change_sensor.py
│   ├── cognee_health_check_sensor.py
│   ├── ducklake_change_feed_sensor.py      (NEW — Wave 4)
│   └── jobs.py
│
├── automation/                             (kept — @schedule decorators)
│
├── definitions.py                          (rewritten — uses dg.load_defs(defs_root=orchestration))
├── resources.py                            (kept — 22 ConfigurableResource subclasses)
├── partitions.py                           (DEPRECATED shim)
├── partitions_v2.py                        (canonical — typo fix `cianhoghlaim_scope` → `cianfhoghlaim_scope`)
├── verification.py                         (kept)
├── dbt_translator.py                       (kept)
├── storage/                                (DEPRECATED — kept for back-compat)
│   └── ducklake_client.py
├── _defs_walker.py                         (FALLBACK — Dagster <1.13)
│
├── defs.yaml                               (root DefsFolderComponent — kept)
│
├── AGENTS.md                               (rewritten — references the new pipelines/ tree)
└── README.md
```

**Key transformations in Wave 2:**

1. The 619 empty placeholder YAMLs under `defs/1_ingestion/` are **deleted** (issue #146 closed).
2. Each dlt source gets a corresponding `defs.yaml` in `pipelines/`, backed by `DltLoadCollectionComponent` (per `https://docs.dagster.io/integrations/libraries/dlt`).
3. The hand-rolled `defs/uog_*.py` etc. are rewritten as `pipelines/british_isles/ireland/university/{exam,official_docs,personal_archive}/defs.yaml`.
4. The post-2026-08-23 batch (`defs/media_intel.py` 809 LOC) is split across `pipelines/media_intel/l{1..5}_*/defs.yaml`.
5. **State-backed Components** are adopted for the 5 high-churn sources (NCCA, SEC, CCEA, SQA, WJEC) per the canonical pattern at `https://docs.dagster.io/guides/build/components/state-backed-components`. The 3 strategies (LOCAL_FILESYSTEM default / VERSIONED_STATE_STORAGE via Garage S3 / LEGACY_CODE_SERVER_SNAPSHOTS) are wired into the `defs_state` cache.
6. The `destinations/` layer-grouped module is referenced by `DltLoadCollectionComponent` for the `pipeline: .loads.<name>` attribute.
7. `partitions_v2.py:308-309` typo (`cianhoghlaim_scope` → `cianfhoghlaim_scope`) is fixed during the LanceDB migration.

### 3.4 The canonical `cocoindex_flows/` layout (Wave 3 target)

The transformation: **5 high-impact Apps converted to Live mode**, plus the PyPI install.

```
cocoindex_flows/
├── _shared/
│   ├── _lifespan.py                        (modified — COCOINDEX_AVAILABLE now True after `uv add cocoindex>=1.0,<2.0,!=1.0.8`)
│   ├── caighdean_standardize.py
│   ├── cli.py
│   ├── cocoindex_query_api.py
│   ├── languages.py
│   ├── repo_embedding.py
│   ├── repo_type_detector.py
│   ├── reranker.py
│   ├── live_components.py                  (NEW — LiveComponent base + process_live mixin)
│   └── target_state.py                     (NEW — declare_row / declare_file helpers)
│
├── corpus/                                  (the big apps — 8 total)
│   ├── leabharlann_embedding.py            (CONVERTED to LocalComponent + LiveMapView)
│   ├── unified_embedding.py                (CONVERTED to target-state declarative)
│   ├── code_embedding.py                   (CONVERTED to localfs.LiveMapView)
│   ├── codebase_graph.py                   (CONVERTED to localfs.LiveMapView)
│   ├── leabharlann_inbox/                  (kept)
│   ├── upstream_blog_monitor.py            (WRAPPED in coco.auto_refresh(interval=6h))
│   ├── upstream_api_surface.py             (WRAPPED in coco.auto_refresh(interval=6h))
│   └── apple_photos_metadata.py            (WRAPPED in coco.auto_refresh(interval=15min))
│
├── biep_parity/                             (378 Apps — kept as-is, read-mostly path)
├── british_isles/                           (kept)
├── celtic/                                   (6 Apps)
├── commonwealth/                            (kept)
├── commonwealth_cross/                      (kept)
├── european_nations/                        (kept)
├── european_nations_cross/                  (kept)
├── european_union/                          (kept)
├── american_nations/                        (kept)
├── infrastructure/                          (5 codebase companion indexes — kept)
├── knowledge_graph/                         (kept)
├── media/                                   (kept)
├── media_intel/                             (kept)
├── portfolio/                               (kept)
└── subjects/                                (kept)
```

**Key transformations in Wave 3:**

1. Install PyPI: `uv add 'cocoindex>=1.0,<2.0,!=1.0.8'`.
2. `_lifespan.py:59` — flip `COCOINDEX_AVAILABLE = True`.
3. Convert `leabharlann_embedding.py` to `LocalComponent` with `process()` (initial scan via `localfs.walk_dir(leabharlann/, live=True).items()`) + `process_live(operator)` (file watcher via `LiveMapView`). Wrap with `SingleWatcherGuard`.
4. Wrap `upstream_blog_monitor.py` + `upstream_api_surface.py` in `coco.auto_refresh(process_fn, interval=datetime.timedelta(hours=6))`.
5. Convert `apple_photos_metadata.py` to `LiveComponent` with osxphotos watcher.
6. Convert `unified_embedding.py` to target-state declarative: `target.declare_row(row=ChunkEmbedding(...))` instead of imperative `mount_table_target`.
7. Convert `code_embedding.py` + `codebase_graph.py` to `localfs.walk_dir(sourcedir, live=True).items()` (replaces the CCC_REINDEX_CRON).
8. **88 defs.yaml files in `orchestration/defs/3_model_lifecycle/cocoindex_v1/` are rewritten** to use the canonical `cocoindex_flows.<subpkg>.<app>` module path (the Wave 0 blocker).

### 3.5 The canonical DuckLake + lakehouse layout (Wave 4 target)

```
dlt_sources/destinations/
├── __init__.py
├── _common.py                              (credential validation + namespace defaults)
├── ducklake.py                             (DuckLakeCredentials + Postgres catalog + Garage S3 + Iceberg REST)
│   # === Public surface ===
│   def get_dlt_destination(use_ducklake=True, mode="production") -> dlt.Destination
│   def get_ducklake_namespace() -> str     # always "ducklake_cianfhoghlaim"
│   def get_attach_syntax(env) -> str       # ATTACH 'ducklake:postgres:...'
│   # === DuckLake v1.0 best practices ===
│   # - data_inlining for small tables (<6 rows)
│   # - sort expressions: ORDER BY (subject, board, year, language)
│   # - data change feed via ducklake_table_changes
│   # - per-namespace encryption
│   # - 30-day snapshot expiry policy
├── motherduck.py                           (MotherDuck SaaS)
└── filesystem.py                           (local DuckDB + filesystem + R2)
```

**Namespace consolidation:**

| Old namespace | New namespace | Reason |
|:--|:--|:--|
| `ducklake_oideachais` | `ducklake_cianfhoghlaim` | Legacy v4 |
| `ducklake_crypteolas` | `ducklake_cianfhoghlaim` | Legacy v4 |
| `ducklake_croilar` | `ducklake_cianfhoghlaim` | Legacy v4 |
| `ducklake_tuath` | `ducklake_cianfhoghlaim` | Legacy v4 |
| `ducklake_meaisinfhoghlaim` | `ducklake_cianfhoghlaim` | Legacy v4 |
| `ducklake_aleyum` | `ducklake_cianfhoghlaim` | Legacy v4 |
| `ducklake_cianfhoghlaim` | `ducklake_cianfhoghlaim` | Already canonical (post-v7) |

**DuckLake v1.0 best practices adopted in Wave 4:**

1. **`data_inlining`** for small tables (`media_descriptors`, `apple_photos_metadata`, anything <6 rows).
2. **`sort expressions`** for LC chunks: `ORDER BY (subject, board, year, language)`.
3. **Data change feed** via `ducklake_table_changes` → feeds the Cognee cognify pipeline + the daily cron sensor.
4. **Per-namespace encryption** for UoG (student-data policy).
5. **Snapshot expiry policy**: 30 days for BIEP, 7 days for personal-archive.

### 3.6 The canonical `web/` layout (Wave 5 target)

```
web/
├── apps/                                    (5 apps + 1 legacy archive)
│   ├── _oideachais_apps_archive/           (MOVED to openspec/archive/ in Wave 5 Step 1)
│   ├── oideachais/                         (MERGED from cianfhoghlaim-leaving-cert — the LC content app)
│   ├── oideachais-dashboard/               (KEEP — operator dashboard)
│   ├── cianfhoghlaim/                      (MERGED from cianfhoghlaim-web — central homepage)
│   ├── croilar-web/                        (MERGED from croilar-portal — public + /admin)
│   └── tuatha-ui/                          (MERGED from cianfhoghlaim-mmo — Babylon.js + 2D MMO)
│
├── packages/                                (5 canonical packages)
│   ├── auth/                                (canonical BetterAuth — lifted from hono-api + clc/packages/auth/)
│   ├── db/                                  (canonical Convex generators + Drizzle helpers)
│   ├── ui-kit/                              (canonical UI surface)
│   ├── i18n/                                (canonical i18n — was @croilar/i18n)
│   └── convex/                              (canonical Convex helpers — was clc/packages/convex/)
│
├── hono-api/                                (canonical API gateway)
├── turbo.json
├── tsconfig.base.json
├── package.json
├── AGENTS.md                                (rewritten to reflect 5 apps + 5 packages + 1 hono-api)
├── README.md
└── .cache/webstack-snapshot.json            (canonical pre/post-merge snapshot)
```

**Post-Wave-5 metrics:**

| Metric | Before | After |
|--|--:|--:|
| Apps | 12 | **5** |
| `package.json` files | 32 | **11** |
| Duplicated Convex deployments | ≥3 | **1** |
| Duplicated Hono gateways | 3 | **1** |
| Duplicated BetterAuth installs | 3 | **1** |
| `.tsx` source files | 443 | **~350** |
| Disk footprint (excl. node_modules) | ~80 MB | **~50 MB** |

**The `demos/` directory (new, outside `web/`):**

```
demos/                                        (NEW — moved out of web/apps/)
├── game_showcase/                            (Python module — 5 YAML project descriptors)
└── tuatha-demo/                              (Python CLI — SIWE demo)
```

### 3.7 The frontend modernisation (Wave 6 target)

Per the 12 building blocks of AG-UI (per `https://ag-ui.com/`), the canonical 2026 stack:

| Layer | Technology | Per the docs |
|:--|:--|:--|
| **Framework** | TanStack Start (post-1.0 RC) | Router-first, SSR + streaming + server functions + routes + middleware. Portable across Cloudflare Workers, Node.js, Netlify, Railway. "Keep the routes. Change the output." |
| **Router / state** | TanStack Router + TanStack Query + TanStack AI + TanStack DB + TanStack Form + TanStack Store | The full TanStack family |
| **Auth** | Better Auth `^1.7` | OIDC + 2FA + passkey + multi-tenancy + multi-session + SSO. Plus MCP server |
| **Backend (real-time)** | Convex | Reactive queries/mutations/actions/HTTP actions/file storage/vector search/auth/cron/scheduled/agents/MCP server |
| **API gateway** | Hono `^4.8` on Cloudflare Workers | + oRPC for typed RPC |
| **Agent UI** | CopilotKit v2 (current major) | @copilotkit/react-core/v2 chat components (chat/popup/sidebar); publicLicenseKey canonical |
| **Agent protocol** | AG-UI (SSE) | RUN_STARTED, STATE_SNAPSHOT, MESSAGES_SNAPSHOT, etc. 12 building blocks. Google ADK has 1st-party support. |
| **Generative UI** | A2UI (Google) | Declarative agent UI protocol with constraints; complementary to AG-UI |
| **Runtime** | Bun `>= 1.4` + Nitro (for Vinxi back-compat until migration) | |
| **Cloud** | Cloudflare Workers + R2 + D1 + Vectorize + Pages | + wrangler.toml per app |
| **CSS / UI** | Tailwind 4 + Radix UI + shadcn/ui + d3 + reactflow + framer-motion + recharts + sonner | The de facto stack |
| **Observability** | Langfuse + Logfire + MLflow + Ragas | |
| **State** | Zustand + TanStack Store | |

---

## Section 4 — Phased refactor plan (7-wave waterfall)

### Wave 0 — Critical fixes (Days 1-3, blocker for everything)

**Goal: unblock the CocoIndex pipeline + repair the module path shadowing.**

| # | Task | Files touched | Tests | Verification |
|--:|:--|:--|:--|:--|
| **0.1** | Bulk-rewrite the 88 L3 `defs.yaml` files to use `cocoindex_flows.<subpkg>.<app>` instead of `cianfhoghlaim.cocoindex.<app>`. Use a Python script that parses the existing YAML, computes the canonical module path from the file location, and emits the corrected YAML. The script cross-checks each rewritten path against `cocoindex_flows/<subpkg>/__init__.py` exports before committing. | `orchestration/defs/3_model_lifecycle/cocoindex_v1/<app>/defs.yaml` (×88) | `dg check yaml` per file | `dg list components 2>&1 \| grep -c "Module: cocoindex_flows"` returns ≥88 |
| **0.2** | Install the PyPI `cocoindex` package. | `pyproject.toml` | `uv pip show cocoindex` returns `1.0.x` (not yanked) | `_lifespan.py:59` flips `COCOINDEX_AVAILABLE = True` automatically |
| **0.3** | Add the `[tool.dg] registry_modules = ["orchestration.components"]` entry to `pyproject.toml` (if not present). | `pyproject.toml` | `dg list components` shows the 11 KCG Components | Output lists all 11 |
| **0.4** | Run `dg check yaml` on the L3 layer and fix any apps that emit `dg.Failure`. | `orchestration/defs/3_model_lifecycle/cocoindex_v1/<app>/defs.yaml` (any remaining) | `dg check yaml` | Exit 0 |
| **0.5** | Delete the 619 empty placeholder YAMLs under `orchestration/defs/1_ingestion/{american_nations,commonwealth,european_nations,...}/` (issue #146 close). | `orchestration/defs/1_ingestion/**/defs.yaml` (619 files) | `find orchestration/defs/1_ingestion -name "defs.yaml" -empty \| wc -l` returns 0 | `mise run dagster:dev` loads |
| **0.6** | Validate the openspec change: `openspec validate 2026-08-24-master-refactor-v1 --strict` (must pass before commit). | `openspec/changes/2026-08-24-master-refactor-v1/` | `mise run openspec:validate` | Exit 0 |

**Effort:** 1 person × 3 days (the 88-path rewrite is the longest; ~3 min per file if scripted, ~4.5 hours total; plus testing + rollback safety net).

**Risk:** Low — these are mechanical changes. The biggest risk is the module-path rewrite breaking a non-obvious import. Mitigation: write a Python script that cross-checks each rewritten path against `cocoindex_flows/__init__.py` exports before committing.

### Wave 1 — `dlt_sources/` refactor (Weeks 1-3)

**Goal: clean the sprawl, theme the grab-bags, consolidate destinations.**

| # | Task | Files touched | Tests | Verification |
|--:|:--|:--|:--|:--|
| **1.1** | Create `dlt_sources/destinations/` directory with `__init__.py`, `_common.py`, `ducklake.py`, `motherduck.py`, `filesystem.py`. Lift the 3 destination modules into the new layout. | `dlt_sources/common/destinations_cianfhoghlaim.py` (split) + `dlt_sources/common/destinations_tuatha.py` (split) + `dlt_sources/_lakehouse/destinations.py` (split) | `python -c "from dlt_sources.destinations.ducklake import get_dlt_destination; ..."` | Round-trip: every existing `get_dlt_destination(mode=...)` call still resolves |
| **1.2** | Add deprecation shims at the old paths that re-export from the new layout. | `dlt_sources/common/destinations_cianfhoghlaim.py`, `dlt_sources/common/destinations_tuatha.py` | `python -c "from dlt_sources.common.destinations_cianfhoghlaim import get_dlt_destination"` still works | `mise run lint:registry` exits 0 |
| **1.3** | Create `dlt_sources/lexicographic/`, `dlt_sources/cultural_heritage/`, `dlt_sources/language_models/` directories. Split `language/`: 9 files → `lexicographic/` (ainm, canuint×5, duchas, gaois×2, logainm, tearma×2), 6 files → `cultural_heritage/` (celtic_mythology, duchas_images, heritage, hidden_heritages, local_documents×2 + helper), 1 file → `language_models/` (universal_dependencies). | `dlt_sources/language/` (split) + 3 new dirs | `python -c "from dlt_sources.lexicographic.ainm import ainm"` + 5 more | All 16 source files import |
| **1.4** | Resolve the Duchas split: `language/duchas.py` (lexicon) → `lexicographic/duchas.py`; `language/duchas_images.py` (folklore corpus) → `cultural_heritage/duchas_corpus.py`. Both keep the same `@dlt.source` name so existing registry lookups work. | `dlt_sources/lexicographic/duchas.py` + `dlt_sources/cultural_heritage/duchas_corpus.py` | AST check: `duchas.py` exposes only the lexicon; `duchas_corpus.py` exposes only the corpus | `mise run dlt:list-sources` |
| **1.5** | Update `dlt_sources/AGENTS.md` to reflect the new themed structure. Add new sections for `lexicographic/`, `cultural_heritage/`, `language_models/`, `destinations/`. | `dlt_sources/AGENTS.md` (rewrite §"Overview" + §"Routing table") | `mise run lint:drift-docs` exits 0 | AGENTS.md counts match ground truth |
| **1.6** | Update `dlt_sources/LEGACY_ALIASES.md` with the Wave-1 rename waves. | `dlt_sources/LEGACY_ALIASES.md` (append §"Wave 1 — themed packages (2026-08-24)") | `mise run lint:drift-docs` | Counts match |
| **1.7** | Update `dlt_sources/DATA_PLATFORM_ROUTER.md` routing table. | `dlt_sources/DATA_PLATFORM_ROUTER.md` (append the 3 themed sub-trees) | `mise run lint:drift-docs` | Counts match |
| **1.8** | Re-consolidate `dlt_sources/official_media/` sub-tree: split into `british_crown/`, `channel_islands/`, `companies/`, `fediverse/` sub-dirs. Each gets its own AGENTS.md stub. | `dlt_sources/official_media/{british_crown,channel_islands,companies,fediverse}/` (NEW) | `python -c "from dlt_sources.official_media.british_crown import ..."` | All split-out sources import |
| **1.9** | Run the full schema-introspector sanity check: `PYTHONPATH=... python -c "import schema; print(len(schema.list_dlt_sources()))"` returns 1,963 (the same count as before). | `notebooks/_shared/schema.py` (unchanged) | `schema.list_dlt_sources()` | Returns 1,963 |
| **1.10** | Add a `mise run lint:dlt-paths` task that fails CI if any source in `language/` exists. | `mise.toml` + `scripts/sync/lint_dlt_paths.py` (NEW) | `mise run lint:dlt-paths` | Exits 0 |
| **1.11** | Validate `openspec validate ... --strict`. | `openspec/changes/2026-08-24-master-refactor-v1/` | `mise run openspec:validate` | Exit 0 |

**Effort:** 1 person × 3 weeks (or 2 people × 2 weeks). The longest task is 1.1 (3-way destination split) — careful, must keep the surface backwards-compatible.

**Risk:** Medium — the destination split risks silent breakage if any caller uses the old module path with a class name that doesn't exist in the new layout. Mitigation: deprecation shims for 1 release cycle.

### Wave 2 — Dagster per-pipeline reorganisation (Weeks 4-6)

**Goal: re-theme Dagster as per-pipeline Components using the dlt-Dagster integration.**

**Pre-work: use Firecrawl MCP to verify the current Dagster Component API.**

```bash
# Via the FirecrawlMCPClient wrapper (per .agents/skills/firecrawl/SKILL.md)
python -c "
from agents.meaisinfhoghlaim.firecrawl_mcp import FirecrawlMCPClient
c = FirecrawlMCPClient()
# Verify the DltLoadCollectionComponent API is current
print(c.search('Dagster DltLoadCollectionComponent site:docs.dagster.io', categories=['developer'], limit=5))
print(c.search('StateBackedComponent defs_state site:docs.dagster.io', categories=['developer'], limit=5))
"
```

| # | Task | Files touched | Tests | Verification |
|--:|:--|:--|:--|:--|
| **2.1** | Scaffold the `orchestration/pipelines/` directory tree (mirror of `dlt_sources/`). | 18 dirs (NEW) under `orchestration/pipelines/` | `tree orchestration/pipelines/` | Tree matches dlt_sources/ |
| **2.2** | Write the shared helper at `orchestration/pipelines/_shared/dagster_dlt_integration.py` — wraps `DltLoadCollectionComponent` for the KCG namespace. Adds the `translation:` key defaults. | `orchestration/pipelines/_shared/dagster_dlt_integration.py` (NEW) | `dg check yaml` | Exits 0 |
| **2.3** | Write the State-backed helper at `orchestration/pipelines/_shared/state_helpers.py` — defaults to `LOCAL_FILESYSTEM` (the 1.13+ canonical). Wires `.local_defs_state/` for the 5 high-churn sources. | `orchestration/pipelines/_shared/state_helpers.py` (NEW) | `dg utils refresh-defs-state --help` | Exits 0 |
| **2.4** | For each dlt source in `dlt_sources/british_isles/`, create the corresponding `defs.yaml` in `orchestration/pipelines/british_isles/`. **Use the canonical `dg scaffold defs` pattern**: `dg scaffold defs dagster_dlt.DltLoadCollectionComponent ireland_lc_subjects --source dlt_sources.british_isles.ireland.education.lc_subjects --destination ducklake` | ~45 defs.yaml files | `dg check yaml` per dir | All British Isles defs.yaml validate |
| **2.5** | Repeat 2.4 for the remaining ~80 `defs.yaml` files (european_nations, european_union, commonwealth, american_nations, celtic, lexicographic, cultural_heritage, language_models, official_media, portfolio, apple_photos, api_sources, filesystem, media_intel). | ~80 files | `dg check yaml` per dir | Exits 0 |
| **2.6** | Move the 8 hand-rolled `orchestration/defs/{uog_*,nui_federation,british_isles_tertiary,media_intel}.py` files into Components. Each becomes a `defs.yaml` under `orchestration/pipelines/<pipeline>/<sub>/`. | 8 hand-rolled files → 8 Component defs.yaml | `dg check yaml` | Exits 0; `dg list defs` shows the moved assets |
| **2.7** | Fix the `cianhoghlaim_scope` typo in `partitions_v2.py:308-309` (the LanceDB migration). | `orchestration/partitions_v2.py` + the LanceDB schema migration script | `uv run python -c "from orchestration.partitions_v2 import biiep_v3_scope_year_partition; print(biep_v3_scope_year_partition.partition_defs[0].name)"` | Prints `cianfhoghlaim_scope` (with 'a') |
| **2.8** | Update `definitions.py` to use `dg.load_defs(defs_root='orchestration')` (the new root is the `pipelines/` tree under `orchestration/`). | `orchestration/definitions.py` | `dagster dev` starts | All assets load |
| **2.9** | Verify the 22 `ConfigurableResource` subclasses (`resources.py`) all still resolve. Add a `british_isles_state_resource` that wraps the State-backed cache. | `orchestration/resources.py` | `python -c "from orchestration.resources import *"` | Imports succeed |
| **2.10** | Standardize `group_name` convention to `{layer}_{domain}_{nation}_{...}`. Add a `dg check yaml` rule that enforces the pattern. | `orchestration/pipelines/_shared/group_name_lint.py` (NEW) | `dg check yaml` | All `group_name` values match |
| **2.11** | Update `orchestration/AGENTS.md` to reflect the new pipelines/ tree + the corrected asset count. | `orchestration/AGENTS.md` (rewrite) | `mise run lint:drift-docs` | Counts match ground truth |
| **2.12** | Validate `openspec validate ... --strict`. | `openspec/changes/...` | `mise run openspec:validate` | Exit 0 |

**Effort:** 1 person × 3 weeks (or 2 people × 2 weeks). The 80+ `defs.yaml` files are template-driven; the longest task is 2.4 (the BIEP v3 + 28 LC subjects).

**Risk:** High — touches every asset. Mitigation: keep the old `defs/<layer>/` tree around as a deprecation shim; agents can run either old or new DAG during the transition.

### Wave 3 — CocoIndex v1 Live migration (Weeks 7-8)

**Goal: install PyPI cocoindex, adopt Live mode, target-state declarative, auto_refresh.**

| # | Task | Files touched | Tests | Verification |
|--:|:--|:--|:--|:--|
| **3.1** | Verify the PyPI `cocoindex` package is at `>=1.0,<2.0,!=1.0.8` (re-confirm Wave 0.2). | `pyproject.toml` | `uv pip show cocoindex` | Returns `1.0.x` |
| **3.2** | Convert `cocoindex_flows/corpus/leabharlann_embedding.py` to `LocalComponent` with `process()` (initial scan via `localfs.walk_dir(leabharlann/, live=True).items()`) + `process_live(operator)` (file watcher via `LiveMapView`). Wrap with `SingleWatcherGuard`. | `cocoindex_flows/corpus/leabharlann_embedding.py` (rewrite) | `python -c "from cocoindex_flows.corpus.leabharlann_embedding import LeabharlannEmbedding; ..."` | Class importable; `update_blocking(live=True)` works |
| **3.3** | Wrap `cocoindex_flows/corpus/upstream_blog_monitor.py` in `coco.auto_refresh(sync, interval=datetime.timedelta(hours=6))`. | `cocoindex_flows/corpus/upstream_blog_monitor.py` (modify top-level) | `python -c "from cocoindex_flows.corpus.upstream_blog_monitor import sync; ..."` | First cycle runs immediately |
| **3.4** | Wrap `cocoindex_flows/corpus/upstream_api_surface.py` in `coco.auto_refresh(sync, interval=datetime.timedelta(hours=6))`. | `cocoindex_flows/corpus/upstream_api_surface.py` | Similar | First cycle runs |
| **3.5** | Convert `cocoindex_flows/corpus/apple_photos_metadata.py` to `LiveComponent` with osxphotos watcher (use `CocoIndex connectorkits.SingleWatcherGuard` to enforce the single-subscriber contract). | `cocoindex_flows/corpus/apple_photos_metadata.py` | `python -c "from cocoindex_flows.corpus.apple_photos_metadata import ApplePhotosMetadata; ..."` | `await operator.update(subpath, ...)` works |
| **3.6** | Convert `cocoindex_flows/corpus/unified_embedding.py` to target-state declarative: `target.declare_row(row=ChunkEmbedding(...))` instead of imperative `mount_table_target`. | `cocoindex_flows/corpus/unified_embedding.py` | Schema evolution: add a column, the next update reconciles | `app.update()` succeeds with new schema |
| **3.7** | Convert `cocoindex_flows/corpus/code_embedding.py` + `cocoindex_flows/corpus/codebase_graph.py` to `localfs.walk_dir(sourcedir, live=True).items()` (replaces the `CCC_REINDEX_CRON`). | `cocoindex_flows/corpus/{code_embedding,codebase_graph}.py` | `app.update_blocking(live=True)` triggers on file mtime | New chunks appear in LanceDB |
| **3.8** | Add the new shared helper `cocoindex_flows/_shared/live_components.py` — the LiveComponent base + `process_live` mixin used by 3.2 + 3.5 + 3.7. | `cocoindex_flows/_shared/live_components.py` (NEW) | `from cocoindex_flows._shared.live_components import LiveComponentBase` | Imports |
| **3.9** | Add the new shared helper `cocoindex_flows/_shared/target_state.py` — the `declare_row` / `declare_file` helpers used by 3.6. | `cocoindex_flows/_shared/target_state.py` (NEW) | `from cocoindex_flows._shared.target_state import declare_row` | Imports |
| **3.10** | Update the R1-R4 conformance check (in `orchestration/components/layer3_model_lifecycle.py`) to recognise Live mode (add R5: "if class has `process_live` method, allow `coco.mount()` instead of `@coco.fn` decorator"). | `orchestration/components/layer3_model_lifecycle.py` | `dg check yaml` | Live Apps pass |
| **3.11** | Validate `openspec validate ... --strict`. | `openspec/changes/...` | `mise run openspec:validate` | Exit 0 |

**Effort:** 1 person × 2 weeks (or 2 people × 1 week). The longest is 3.2 (the 38 KB App).

**Risk:** Low — Live mode is additive. The biggest risk is the LiveComponent protocol not being wired correctly for `leabharlann_embedding.py` — the largest App. Mitigation: keep the legacy `mount_table_target` direct path as a fallback flag (`use_live_mode: bool = False`).

### Wave 4 — Lakehouse hardening (Weeks 9-10)

**Goal: adopt DuckLake v1.0 best practices + consolidate the 6 legacy namespaces.**

| # | Task | Files touched | Tests | Verification |
|--:|:--|:--|:--|:--|
| **4.1** | Consolidate the 6 legacy DuckLake namespaces into the single `ducklake_cianfhoghlaim` namespace. Use `ALTER DATABASE ... RENAME TO` (per DuckDB) + LanceDB table-name migration. | `dlt_sources/destinations/ducklake.py` + Postgres migration script + LanceDB migration | `python -c "from dlt_sources.destinations.ducklake import get_ducklake_namespace; print(get_ducklake_namespace())"` | Prints `ducklake_cianfhoghlaim` |
| **4.2** | Add `data_inlining` for small tables (`media_descriptors`, `apple_photos_metadata`, anything <6 rows). | `dlt_sources/destinations/ducklake.py` (add the inlining config) | `select count(*) from ducklake_table_changes('media_descriptors')` | Returns 0 rows (data is inlined in the catalog) |
| **4.3** | Add `sort expressions` to LC chunks tables: `ORDER BY (subject, board, year, language)`. | `dlt_sources/destinations/ducklake.py` (add the sort expression) + `dlt_sources/british_isles/_cross/jurisdiction_pipeline_base.py` (wire the sort) | `describe table lc_chunks` shows the sort order | Sort expression present |
| **4.4** | Add `data change feed` consumption via `ducklake_table_changes` — feeds the Cognee cognify pipeline + the daily cron sensor. | `orchestration/sensors/ducklake_change_feed_sensor.py` (NEW) | `uv run python -c "from orchestration.sensors.ducklake_change_feed_sensor import ducklake_change_feed; ..."` | Sensor registered |
| **4.5** | Enable per-namespace encryption for UoG (student-data policy). Per the DuckLake v1.0 spec, set `encryption.key-id` per namespace. | `dlt_sources/destinations/ducklake.py` (add the encryption config) | `select encryption_key_id from ducklake_namespace_info where namespace = 'ducklake_cianfhoghlaim'` | Returns a non-null key |
| **4.6** | Set up snapshot expiry policy: 30 days for BIEP, 7 days for personal-archive. Per the v1.0 spec at `ducklake.select/docs/stable/duckdb/maintenance/expire_snapshots`. | `dlt_sources/destinations/ducklake.py` (add the expiry policy) + Dagster maintenance asset | `select count(*) from ducklake_snapshots where namespace = 'ducklake_cianfhoghlaim' and snapshot_time < now() - interval '30 days'` | Returns 0 |
| **4.7** | Use the Iceberg REST catalog (Lakekeeper) for cross-engine compatibility — wire the dlt Iceberg connector instead of raw DuckLake ATTACH. | `dlt_sources/destinations/ducklake.py` (add Iceberg REST config) | `select * from lakekeeper_namespace_properties where namespace = 'ducklake_cianfhoghlaim'` | Returns Iceberg properties |
| **4.8** | Update `orchestration/storage/ducklake_client.py` to a deprecation shim that re-exports from `dlt_sources/destinations/ducklake.py`. | `orchestration/storage/ducklake_client.py` | `python -c "from orchestration.storage.ducklake_client import DuckLakeResource"` | Imports from the new path |
| **4.9** | Update `orchestration/resources.py:DuckLakeResource` to use `dlt_sources.destinations.ducklake.get_dlt_destination` (already wired per orchestration report §A.6 — confirm). | `orchestration/resources.py` | `dagster dev` | DuckLake resource initialises |
| **4.10** | Update `orchestration/AGENTS.md` to reflect the single namespace. | `orchestration/AGENTS.md` | `mise run lint:drift-docs` | Counts match |
| **4.11** | Add a smoke-test: `mise run lakehouse:smoke-test` that runs the canonical 6-service health check from `docs/lakehouse/smoke-test-2026-08-09.md`. | `mise.toml` + `scripts/sync/lakehouse_smoke_test.py` (NEW) | `mise run lakehouse:smoke-test` | All 6 services healthy |
| **4.12** | Validate `openspec validate ... --strict`. | `openspec/changes/...` | `mise run openspec:validate` | Exit 0 |

**Effort:** 1 person × 2 weeks (or 2 people × 1.5 weeks). The longest is 4.1 (the namespace consolidation — requires the Postgres migration to be tested against a snapshot first).

**Risk:** Medium — the namespace consolidation risks losing data if the migration script has a bug. Mitigation: dry-run mode that emits the DDL without applying it; explicit confirmation step.

### Wave 5 — Web cascade (Weeks 11-16, 12 apps → 5 + 5 + 1)

**Goal: archive `_oideachais_apps/`, lift shared packages, merge sub-monorepos.**

**The 7-step plan (per web frontend report §G.3–G.5):**

| # | Task | Files touched | Tests | Verification |
|--:|:--|:--|:--|:--|
| **5.1** | Archive `_oideachais_apps/` → `openspec/archive/2026-08-24-archive-legacy-oideachais-apps/`. Move all 7 files. | `web/apps/_oideachais_apps/` → `openspec/archive/2026-08-24-archive-legacy-oideachais-apps/` | `find web/apps -name '_oideachais_apps' \| wc -l` returns 0 | bun workspaces glob stops matching |
| **5.2** | Move `game_showcase/` + `tuatha-demo/` to `demos/{game_showcase,tuatha-demo}/` at repo root. | `web/apps/game_showcase/` → `demos/game_showcase/` + `web/apps/tuatha-demo/` → `demos/tuatha-demo/` | `find web/apps -name 'game_showcase' -o -name 'tuatha-demo' \| wc -l` returns 0 | web-app bun workspaces glob stops matching |
| **5.3** | Lift `web/packages/auth/` wrapper to a real implementation: lift from `web/hono-api/src/auth.ts` + `oideachais-dashboard/convex/auth/` + `cianfhoghlaim-leaving-cert/packages/auth/`. Then update all 3 call sites. | `web/packages/auth/src/index.ts` (rewrite + lift) + 3 call sites | `bun run typecheck` in `web/packages/auth` | Passes |
| **5.4** | Same for `web/packages/db/`: lift from `cianfhoghlaim-leaving-cert/packages/db/` + `cianfhoghlaim-leaving-cert/packages/convex/` into one canonical `@cianfhoghlaim/db` + `@cianfhoghlaim/convex`. | `web/packages/db/src/index.ts` + `web/packages/convex/src/index.ts` (NEW) + 2 call sites | `bun run typecheck` | Passes |
| **5.5** | Promote `web/hono-api/src/copilotkit/` and `web/hono-api/src/ag-ui/` to be the **single canonical CopilotKit actions + AG-UI streamer** surface. Move the equivalent code from `cianfhoghlaim-leaving-cert/apps/api/src/copilotkit/` and `cianfhoghlaim-web/apps/api/` to here. | `web/hono-api/src/{copilotkit,ag-ui}/` (expand) + 2 source apps (delete duplicates) | `bun run typecheck` in `web/hono-api` | Passes |
| **5.6** | Merge `croilar-portal/` → `croilar-web/` as `/admin` routes. Move `croilar-portal/src/routes/admin/*` to `croilar-web/src/routes/admin/*`. | `web/apps/croilar-portal/` (delete) + `web/apps/croilar-web/src/routes/admin/` (NEW) | `bun run typecheck` in `croilar-web` | Passes |
| **5.7** | Merge `cianfhoghlaim-web/` → `cianfhoghlaim/`. Move routes to `/<stage>/<subject>/` per the BIEP v3 model. | `web/apps/cianfhoghlaim-web/` (delete) + `web/apps/cianfhoghlaim/src/routes/` (expand) | `bun run typecheck` in `cianfhoghlaim` | Passes |
| **5.8** | Merge `cianfhoghlaim-leaving-cert/` → `oideachais/`. Move `apps/web/` → `oideachais/src/routes/`, `apps/api/` → `web/hono-api/`, `packages/{auth,config,convex,db,i18n,ui}/` → `web/packages/*/`. | `web/apps/cianfhoghlaim-leaving-cert/` (delete) + `web/apps/oideachais/src/routes/` (expand) + `web/packages/{auth,db,convex,i18n,ui-kit}/` (expand) | `bun run typecheck` in `oideachais` | Passes |
| **5.9** | Merge `cianfhoghlaim-mmo/` → `tuatha-ui/`. Move the TanStack Start 2D MMO routes + Convex schema (`badges`, `credentialAnchors`, `questPacks`, `x402Payments`, `schema`) into `tuatha-ui/`. | `web/apps/cianfhoghlaim-mmo/` (delete) + `web/apps/tuatha-ui/src/routes/mmo/` (NEW) + `web/apps/tuatha-ui/convex/` (expand) | `bun run typecheck` in `tuatha-ui` | Passes |
| **5.10** | Update `web/AGENTS.md` to reflect the new topology (5 apps + 5 packages + 1 hono-api). | `web/AGENTS.md` (rewrite) | `mise run lint:drift-docs` | Counts match |
| **5.11** | Update `web/package.json` + `web/turbo.json` workspaces glob to match the new app set. | `web/package.json` + `web/turbo.json` | `bun install` | Passes |
| **5.12** | Run `bun run croilar:analyze` (per web frontend report §H.2) before and after each merge to capture the diff. | `.cache/webstack-snapshot.json` | `bun run croilar:analyze` | Snapshot captured |
| **5.13** | Validate `openspec validate ... --strict`. | `openspec/changes/...` | `mise run openspec:validate` | Exit 0 |

**Effort:** 1 person × 6 weeks (or 2 people × 4 weeks with 5.7 + 5.8 parallel).

**Risk:** High — touches every web app. Mitigation: the 7-step order matters. Steps 5.1–5.5 are low-risk (cleanup + canonical package lift). Steps 5.6–5.9 are the big merges; each requires `bun run typecheck` + a smoke test of the merged app.

### Wave 6 — Frontend modernisation (Weeks 17-20)

**Goal: TanStack Start 1.0+ + CopilotKit v2 + AG-UI + A2UI + Better Auth 1.7.**

**Per the 12 AG-UI building blocks** (streaming chat, multimodality, static generative UI, declarative generative UI, shared state, thinking steps, frontend tool calls, backend tool rendering, interrupts, sub-agents, agent steering, tool output streaming).

| # | Task | Files touched | Tests | Verification |
|--:|:--|:--|:--|:--|
| **6.1** | Upgrade TanStack Router + TanStack Start from Vinxi-based pre-1.0 to the 1.0+ model. Per the canonical pattern: "Start keeps TanStack Router as the application contract, then adds full-document rendering, streaming, typed server work, middleware, and output for the runtime you choose." Update each of the 5 apps. | `web/apps/{oideachais,oideachais-dashboard,cianfhoghlaim,croilar-web,tuatha-ui}/package.json` + `app.config.ts` | `bun run dev` per app | App boots on Cloudflare Workers (or local Node) |
| **6.2** | Adopt the TanStack family: TanStack AI (`@tanstack/ai`) for tool calling + TanStack DB (`@tanstack/db`) for differential sync + TanStack Form (`@tanstack/form`) for filter forms. | All 5 apps (add to deps) | `bun run typecheck` | Passes |
| **6.3** | Upgrade CopilotKit from v1.67 to v2 in all 5 apps. Per the canonical migration: `@copilotkit/react-core/v2` chat components (NOT react-ui); `publicLicenseKey` (canonical). | All 5 apps + `web/hono-api` | `bun run typecheck` | Passes |
| **6.4** | Wire the AG-UI protocol between the canonical Hono gateway (`web/hono-api/src/ag-ui/`) and the 5 apps. Use `@ag-ui/react` for the SSE consumer. | `web/hono-api/src/ag-ui/` + 5 apps | `bun run dev` + send an AG-UI RUN_STARTED event | AG-UI event stream consumed |
| **6.5** | Wire the A2UI protocol (Google declarative agent UI) in `oideachais-dashboard/` for the BIEP v3 dashboards. Per the canonical pattern: `createA2UIMessageRenderer` ships from `@copilotkit/react-core/v2`. | `oideachais-dashboard/src/components/a2ui/` (NEW) | Manual: send a `createSurface` A2UI operation | Surface renders |
| **6.6** | Upgrade BetterAuth from 1.0–1.4 to `^1.7`. Per the canonical BetterAuth MCP server: `https://mcp.better-auth.com/mcp`. Wire the OIDC plugin + the 2FA plugin + the passkey plugin + the SIWE plugin. | `web/packages/auth/` + `web/hono-api/src/auth.ts` | `bun run typecheck` | Passes |
| **6.7** | Consolidate the 3 Convex deployments into 1 (the umbrella at `oideachais-dashboard/convex/`). Move the schemas from `cianfhoghlaim-web/convex/` + `croilar-portal/convex/` + `cianfhoghlaim-mmo/convex/` to the umbrella. | 3 source dirs (delete) + `oideachais-dashboard/convex/` (expand) | `bunx convex dev` | Schema deploys |
| **6.8** | Adopt Bun >= 1.4 throughout (the canonical runner per `bun run --parallel`). Migrate the legacy Vinxi-nightly apps off Nitro nightly (per web frontend report §H.4). | All 5 apps | `bun --version` | Returns `1.4.x` or higher |
| **6.9** | Add per-app `wrangler.toml` files for Cloudflare deployment. Per the canonical TanStack Start deploy output: "wrangler deploy". | All 5 apps + `web/hono-api/` | `wrangler deploy --dry-run` | Passes |
| **6.10** | Add `mise run lint:web-stack` task that validates: 5 apps only, 5 packages only, 1 hono-api only, no nested `apps/api/`, no nested `packages/`. | `mise.toml` + `scripts/sync/lint_web_stack.py` (NEW) | `mise run lint:web-stack` | Exits 0 |
| **6.11** | Update `web/AGENTS.md` to reflect the new frontend stack. | `web/AGENTS.md` | `mise run lint:drift-docs` | Counts match |
| **6.12** | Validate `openspec validate ... --strict`. | `openspec/changes/...` | `mise run openspec:validate` | Exit 0 |

**Effort:** 1 person × 4 weeks (or 2 people × 3 weeks with 6.1 + 6.3 parallel).

**Risk:** Medium — major version bumps across the stack. Mitigation: per-app incremental migration (one app per day, with the rest still on v1).

---

## Section 5 — Per-wave tasks, files touched, tests, verification

This section consolidates Section 4 into a single per-wave matrix.

### Wave 0 — 6 tasks, ~6 file groups, ~93 tests

| # | Files (count) | Tests | Verification |
|--:|--:|--:|:--|
| 0.1 | 88 | 88 | `dg check yaml` per file |
| 0.2 | 1 | 1 | `uv pip show cocoindex` |
| 0.3 | 1 | 1 | `dg list components` |
| 0.4 | (any remaining) | 1 | `dg check yaml` |
| 0.5 | 619 | 1 | `find ... -empty \| wc -l` |
| 0.6 | 0 | 1 | `openspec validate --strict` |

### Wave 1 — 11 tasks, ~30 file groups, ~25 tests

| # | Files (count) | Tests | Verification |
|--:|--:|--:|:--|
| 1.1 | 3 (split) | 1 | Round-trip import |
| 1.2 | 2 (shims) | 1 | Round-trip import |
| 1.3 | 16 (split) | 5 | Per-source import |
| 1.4 | 2 (split Duchas) | 1 | AST check |
| 1.5 | 1 (rewrite) | 1 | `mise run lint:drift-docs` |
| 1.6 | 1 (append) | 1 | `mise run lint:drift-docs` |
| 1.7 | 1 (append) | 1 | `mise run lint:drift-docs` |
| 1.8 | 6 (split official_media) | 6 | Per-source import |
| 1.9 | 0 | 1 | `schema.list_dlt_sources()` returns 1,963 |
| 1.10 | 1 + 1 (NEW) | 1 | `mise run lint:dlt-paths` |
| 1.11 | 0 | 1 | `openspec validate --strict` |

### Wave 2 — 12 tasks, ~140 file groups, ~155 tests

| # | Files (count) | Tests | Verification |
|--:|--:|--:|:--|
| 2.1 | 18 dirs (NEW) | 1 | `tree orchestration/pipelines/` |
| 2.2 | 1 (NEW) | 1 | `dg check yaml` |
| 2.3 | 1 (NEW) | 1 | `dg utils refresh-defs-state --help` |
| 2.4 | ~45 (British Isles) | 45 | `dg check yaml` per dir |
| 2.5 | ~80 (rest) | 80 | `dg check yaml` per dir |
| 2.6 | 8 (move) | 8 | `dg check yaml` |
| 2.7 | 1 + 1 (migration) | 1 | `partitions_v2.py:308` prints `cianfhoghlaim_scope` |
| 2.8 | 1 (rewrite) | 1 | `dagster dev` |
| 2.9 | 1 (modify) | 1 | `python -c "from orchestration.resources import *"` |
| 2.10 | 1 + 1 (NEW) | 1 | `dg check yaml` |
| 2.11 | 1 (rewrite) | 1 | `mise run lint:drift-docs` |
| 2.12 | 0 | 1 | `openspec validate --strict` |

### Wave 3 — 11 tasks, ~6 file groups, ~8 tests

| # | Files (count) | Tests | Verification |
|--:|--:|--:|:--|
| 3.1 | 1 | 1 | `uv pip show cocoindex` |
| 3.2 | 1 (rewrite) | 1 | Class importable |
| 3.3 | 1 (modify) | 1 | First cycle runs |
| 3.4 | 1 (modify) | 1 | First cycle runs |
| 3.5 | 1 (rewrite) | 1 | `await operator.update(...)` works |
| 3.6 | 1 (rewrite) | 1 | Schema evolution reconciles |
| 3.7 | 2 (rewrite) | 1 | New chunks appear |
| 3.8 | 1 (NEW) | 1 | `from cocoindex_flows._shared.live_components import LiveComponentBase` |
| 3.9 | 1 (NEW) | 1 | `from cocoindex_flows._shared.target_state import declare_row` |
| 3.10 | 1 (modify) | 1 | `dg check yaml` |
| 3.11 | 0 | 1 | `openspec validate --strict` |

### Wave 4 — 12 tasks, ~6 file groups, ~10 tests

| # | Files (count) | Tests | Verification |
|--:|--:|--:|:--|
| 4.1 | 1 + migration | 1 | `get_ducklake_namespace()` returns `ducklake_cianfhoghlaim` |
| 4.2 | 1 (modify) | 1 | `ducklake_table_changes('media_descriptors')` |
| 4.3 | 2 (modify) | 1 | Sort expression present |
| 4.4 | 1 (NEW) | 1 | Sensor registered |
| 4.5 | 1 (modify) | 1 | Encryption key set |
| 4.6 | 1 + asset (modify) | 1 | Old snapshots expired |
| 4.7 | 1 (modify) | 1 | Iceberg REST properties |
| 4.8 | 1 (shim) | 1 | Round-trip import |
| 4.9 | 1 (confirm) | 1 | `dagster dev` |
| 4.10 | 1 (rewrite) | 1 | `mise run lint:drift-docs` |
| 4.11 | 1 + 1 (NEW) | 1 | `mise run lakehouse:smoke-test` |
| 4.12 | 0 | 1 | `openspec validate --strict` |

### Wave 5 — 13 tasks, ~25 file groups, ~30 tests

| # | Files (count) | Tests | Verification |
|--:|--:|--:|:--|
| 5.1 | 7 (move) | 1 | `find web/apps -name '_oideachais_apps'` returns 0 |
| 5.2 | 2 dirs (move) | 1 | `find web/apps -name 'game_showcase' -o -name 'tuatha-demo'` returns 0 |
| 5.3 | 1 + 3 (lift) | 1 | `bun run typecheck` |
| 5.4 | 2 + 2 (lift) | 1 | `bun run typecheck` |
| 5.5 | 1 + 2 (consolidate) | 1 | `bun run typecheck` |
| 5.6 | 1 (move) | 1 | `bun run typecheck` in `croilar-web` |
| 5.7 | 1 (move) | 1 | `bun run typecheck` in `cianfhoghlaim` |
| 5.8 | 1 + 5 (move) | 1 | `bun run typecheck` in `oideachais` |
| 5.9 | 1 (move) | 1 | `bun run typecheck` in `tuatha-ui` |
| 5.10 | 1 (rewrite) | 1 | `mise run lint:drift-docs` |
| 5.11 | 2 (modify) | 1 | `bun install` |
| 5.12 | 1 (snapshot) | 1 | Snapshot captured |
| 5.13 | 0 | 1 | `openspec validate --strict` |

### Wave 6 — 12 tasks, ~15 file groups, ~15 tests

| # | Files (count) | Tests | Verification |
|--:|--:|--:|:--|
| 6.1 | 5 (upgrade) | 5 | `bun run dev` per app |
| 6.2 | 5 (deps) | 5 | `bun run typecheck` |
| 6.3 | 6 (upgrade) | 6 | `bun run typecheck` |
| 6.4 | 1 + 5 (wire) | 5 | AG-UI event stream consumed |
| 6.5 | 1 (NEW) | 1 | A2UI surface renders |
| 6.6 | 2 (upgrade) | 2 | `bun run typecheck` |
| 6.7 | 4 (consolidate) | 1 | `bunx convex dev` |
| 6.8 | 5 (migrate) | 5 | `bun --version` |
| 6.9 | 6 (NEW) | 6 | `wrangler deploy --dry-run` |
| 6.10 | 1 + 1 (NEW) | 1 | `mise run lint:web-stack` |
| 6.11 | 1 (rewrite) | 1 | `mise run lint:drift-docs` |
| 6.12 | 0 | 1 | `openspec validate --strict` |

---

## Section 6 — Risks and mitigations

### 6.1 The Wave 0 blocker (88 of 96 L3 `defs.yaml` files broken)

**Risk.** Per orchestration report §A.9 + §E.1: *"88 of the 95 L3 defs.yaml files still use the pre-refactor flat layout — these Apps are broken at execute time."* The Components emit `dg.Failure` with `cocoindex_v1_module_import_failed`. The entire CocoIndex pipeline — BIEP embedder, Leabharlann embedder, upstream monitors, Apple Photos geospatial — is non-functional at execute time.

**Mitigation.**
- The Wave 0.1 task uses a Python script (not a manual sed) that parses each `defs.yaml`, computes the canonical module path from the file location (e.g. `orchestration/defs/3_model_lifecycle/cocoindex_v1/lc_subjects/defs.yaml` → `cocoindex_flows.biep_parity.lc_subjects`), and writes the corrected YAML. The script cross-checks each rewritten path against `cocoindex_flows/<subpkg>/__init__.py` exports before committing.
- Wave 0 must land before any other wave.
- Rollback strategy: `git revert` is clean because the script writes the corrected YAML directly (no intermediate state).

### 6.2 The L3 / L4 / L5 Components not instantiated in `defs.yaml`

**Risk.** Per orchestration report §A.9: L1 = "Legacy", L2 = "Mixed", L4 = "Mixed", L4 budget/memory = "Legacy", L5 = "Legacy". The `CelticIngestionComponent` (L1) + `CelticAgentOpsComponent` (L5) are **defined** but **never instantiated** anywhere. The 619 empty placeholder YAMLs under `defs/1_ingestion/` (per Wave 0.5) are the audit trail.

**Mitigation.**
- Wave 2 reorganises Dagster to per-pipeline Components. Every dlt source gets a `defs.yaml` backed by `DltLoadCollectionComponent`. The `CelticIngestionComponent` becomes the **shared base class** for these (the KCG wrapper around `DltLoadCollectionComponent`).
- The `CelticAgentOpsComponent` becomes instantiated by the 12-agent fleet (Wave 2.6, moves the agent ops files into Components).

### 6.3 The post-2026-08-23 UoG batch bypasses Components

**Risk.** The 8 hand-rolled files in `orchestration/defs/{uog_*,nui_federation,british_isles_tertiary,media_intel}.py` were added to ship the UoG personal-archive fast. They are hand-rolled `@asset` per module — bypassing the 5-layer Component architecture. This is a regression that compounds with each new addition.

**Mitigation.**
- Wave 2.6 explicitly moves each hand-rolled file into a Component (the `defs.yaml` under `pipelines/british_isles/ireland/university/<sub>/`).
- Add a CI gate (`mise run lint:dagster-architecture`) that fails if any hand-rolled `@asset` is added under `defs/` (the canonical locations are `pipelines/`).

### 6.4 The dual destinations problem

**Risk.** 3 destination modules (`common/destinations_cianfhoghlaim.py` + `common/destinations_tuatha.py` + `_lakehouse/destinations.py`) coexist. Every code path must check all three. Adding a new destination class requires touching all three.

**Mitigation.**
- Wave 1.1 + 1.2 splits the 3 files into the layer-grouped `destinations/{ducklake,motherduck,filesystem}.py` + `_common.py`. The 2 old modules become deprecation shims for 1 release cycle.

### 6.5 The language/ grab-bag

**Risk.** 16 sources + 5 helpers in `dlt_sources/language/` mixed across 3 distinct domains (lexicographic / cultural_heritage / language_models). Forces every agent and every Dagster asset to enumerate by hand.

**Mitigation.**
- Wave 1.3 splits the grab-bag into 3 themed sub-trees.
- Wave 1.10 adds `mise run lint:dlt-paths` that fails CI if any source in `language/` exists.

### 6.6 The 6 legacy DuckLake namespaces

**Risk.** `ducklake_oideachais` + `ducklake_crypteolas` + `ducklake_croilar` + `ducklake_tuath` + `ducklake_meaisinfhoghlaim` + `ducklake_aleyum` are the pre-v7 names. Data is split across them.

**Mitigation.**
- Wave 4.1 consolidates into `ducklake_cianfhoghlaim` via `ALTER DATABASE ... RENAME TO` + LanceDB migration.
- Dry-run mode that emits the DDL without applying; explicit confirmation step.

### 6.7 The 12 → 5 web app consolidation

**Risk.** 7 of 12 apps have data + routes + BAML + ADK agents + Convex schemas. Merging them risks losing functionality. The 2 apps with private sub-monorepos (`cianfhoghlaim-web`, `cianfhoghlaim-leaving-cert`) each have 4–7 internal packages — the lift + delete is the riskiest part.

**Mitigation.**
- The 7-step order (5.1 → 5.7) is canonical. Steps 5.1–5.5 are low-risk (cleanup + canonical package lift). Steps 5.6–5.9 are the big merges; each requires `bun run typecheck` + smoke test.
- The `bun run croilar:analyze` snapshot (per web frontend report §H.2) captures the baseline before each merge; post-merge comparison verifies no functionality was lost.

### 6.8 The TanStack Start 1.0+ upgrade

**Risk.** The current apps use Vinxi-based pre-1.0. TanStack Start 1.0+ is a major version bump. The migration affects routing + server functions + middleware + deployment output.

**Mitigation.**
- Per-app incremental migration (one app per day).
- TanStack Start's value proposition: *"Start keeps TanStack Router as the application contract. Start adds the server and build layers around that same tree."* — the routes don't change; only the deployment output + the server functions.
- The Bun runtime is a common ground between Vinxi and post-1.0 TanStack Start (both support `bun run dev`).

### 6.9 The CopilotKit v1 → v2 upgrade

**Risk.** CopilotKit v1.67 is on the v1 line (approaching EOL). v2 is the current major with breaking changes.

**Mitigation.**
- Per the canonical `react-core/SKILL.md`: v2 chat components ship from `@copilotkit/react-core/v2` — NOT `react-ui` (which is CSS-only in v2). `publicLicenseKey` is canonical (the `publicApiKey` alias is deprecated).
- A2UI is enabled via `CopilotRuntime({ a2ui: {...} })` + `<CopilotKit a2ui={{ theme }}>`.
- Per-app incremental migration; the v1 components can coexist with v2 via the v2 adapter.

### 6.10 The L1 → L2 → L3 → L4 cascade contract

**Risk.** If a DLT source is broken (Wave 1), every asset downstream is broken (Wave 2). If a CocoIndex App is broken (Wave 3), every agent memory + RAG call is broken. The cascade must hold end-to-end.

**Mitigation.**
- The `mise run sync:all` 7-layer sync (per orchestration report §F.1) is the consistency gate. Run it after every wave.
- The `mise run lint:drift-docs` check catches stale `AGENTS.md` numbers.
- The `dagster dev` smoke-test on the canonical BIEP v3 Ireland pipeline is the end-to-end check.

### 6.11 Concurrent-write safety (the 2026-08-22 PR #5 incident)

**Risk.** Per `openspec/specs/repo-hygiene-agent-routing/spec.md`: 8 file modifications were lost mid-session by a concurrent agent's `git reset --hard`. The 4-step edit protocol is mandatory.

**Mitigation.**
- Every agent that authors any file in any wave MUST follow the 4-step protocol:
  1. `git status -- <path>` + `git diff -- <path>` + `sha256sum <path>` BEFORE editing
  2. Make the edit (Edit tool, Write tool, or shell sed/awk)
  3. `git diff -- <path>` + `sha256sum <path>` AFTER editing
  4. `git add <path>` ONLY (NEVER `git add -A`) + `git status -- <path>`
- Forbidden patterns (per the 2026-08-22 incident): `git add -A` / `git stash --include-untracked` / `git reset --hard` without stash / `git checkout -- <path>` without verify / `git commit --amend` if concurrent agent may have pushed.
- "CLAIM A FILE" pattern when multiple agents touch the same area.

---

## Section 7 — Naming migration map

### 7.1 `dlt_sources/` migrations

| Old path | New path | Wave | Reason |
|:--|:--|:--:|:--|
| `dlt_sources/language/` | **DELETED** | 1 | The grab-bag |
| `dlt_sources/language/ainm.py` | `dlt_sources/lexicographic/ainm.py` | 1 | Lexicographic concern |
| `dlt_sources/language/canuint.py` | `dlt_sources/lexicographic/canuint.py` | 1 | Lexicographic |
| `dlt_sources/language/canuint_audio.py` | `dlt_sources/lexicographic/canuint_audio.py` | 1 | Lexicographic |
| `dlt_sources/language/canuint_dialect_summary.py` | `dlt_sources/lexicographic/canuint_dialect_summary.py` | 1 | Lexicographic |
| `dlt_sources/language/canuint_search.py` | `dlt_sources/lexicographic/canuint_search.py` | 1 | Lexicographic |
| `dlt_sources/language/canuint_word_alignment.py` | `dlt_sources/lexicographic/canuint_word_alignment.py` | 1 | Lexicographic |
| `dlt_sources/language/duchas.py` | `dlt_sources/lexicographic/duchas.py` | 1 | Lexicographic (the lexicon) |
| `dlt_sources/language/duchas_images.py` | `dlt_sources/cultural_heritage/duchas_corpus.py` | 1 | Cultural heritage (the folklore corpus) |
| `dlt_sources/language/gaois.py` | `dlt_sources/lexicographic/gaois.py` | 1 | Lexicographic |
| `dlt_sources/language/gaois_combined.py` | `dlt_sources/lexicographic/gaois_combined.py` | 1 | Lexicographic |
| `dlt_sources/language/logainm.py` | `dlt_sources/lexicographic/logainm.py` | 1 | Lexicographic |
| `dlt_sources/language/tearma.py` | `dlt_sources/lexicographic/tearma.py` | 1 | Lexicographic |
| `dlt_sources/language/tearma_search.py` | `dlt_sources/lexicographic/tearma_search.py` | 1 | Lexicographic |
| `dlt_sources/language/celtic_mythology.py` | `dlt_sources/cultural_heritage/celtic_mythology.py` | 1 | Cultural heritage |
| `dlt_sources/language/heritage.py` | `dlt_sources/cultural_heritage/heritage.py` | 1 | Cultural heritage |
| `dlt_sources/language/hidden_heritages.py` | `dlt_sources/cultural_heritage/hidden_heritages.py` | 1 | Cultural heritage |
| `dlt_sources/language/local_documents_by_subject.py` | `dlt_sources/cultural_heritage/local_documents_by_subject.py` | 1 | Cultural heritage |
| `dlt_sources/language/local_education_documents.py` | `dlt_sources/cultural_heritage/local_education_documents.py` | 1 | Cultural heritage |
| `dlt_sources/language/universal_dependencies.py` | `dlt_sources/language_models/universal_dependencies.py` | 1 | Language models / NLP |
| `dlt_sources/language/_canuint_helpers.py` | `dlt_sources/lexicographic/_canuint_helpers.py` | 1 | Helpers co-locate with sources |
| `dlt_sources/language/_duchas_images_helpers.py` | `dlt_sources/cultural_heritage/_duchas_corpus_helpers.py` | 1 | Renamed to match the source |
| `dlt_sources/language/_gaois_helpers.py` | `dlt_sources/lexicographic/_gaois_helpers.py` | 1 | Helpers co-locate |
| `dlt_sources/language/_local_documents_helpers.py` | `dlt_sources/cultural_heritage/_local_documents_helpers.py` | 1 | Helpers co-locate |
| `dlt_sources/language/_tearma_helpers.py` | `dlt_sources/lexicographic/_tearma_helpers.py` | 1 | Helpers co-locate |
| `dlt_sources/language/AGENTS.md` | split into `dlt_sources/lexicographic/AGENTS.md` + `dlt_sources/cultural_heritage/AGENTS.md` + `dlt_sources/language_models/AGENTS.md` | 1 | Split the AGENTS doc |
| `dlt_sources/common/destinations_cianfhoghlaim.py` | `dlt_sources/destinations/ducklake.py` + `dlt_sources/destinations/filesystem.py` + `dlt_sources/destinations/_common.py` | 1 | Layer-grouped destinations |
| `dlt_sources/common/destinations_tuatha.py` | `dlt_sources/destinations/ducklake.py` (merged into the ducklake file) | 1 | Layer-grouped |
| `dlt_sources/_lakehouse/destinations.py` | `dlt_sources/_lakehouse/pool.py` (rename) + `dlt_sources/destinations/ducklake.py` (the dlt-side bridge) | 1 | Layer-grouped |
| `dlt_sources/_lakehouse/personal_archive_destinations.py` | `dlt_sources/_lakehouse/personal_archive.py` | 1 | Renamed |
| `dlt_sources/common/ducklake_pool.py` | `dlt_sources/_lakehouse/pool.py` (shim → re-export) | 1 | Renamed |
| `dlt_sources/common/ducklake_options.py` | `dlt_sources/_lakehouse/options.py` (shim → re-export) | 1 | Renamed |
| `dlt_sources/official_media/companies_house/` | `dlt_sources/official_media/companies/companies_house/` | 1 | Sub-tree under `companies/` |
| `dlt_sources/official_media/{ggy,iom,jsy}/` | `dlt_sources/official_media/channel_islands/{ggy,iom,jsy}/` | 1 | Channel Islands split out |
| `dlt_sources/official_media/{sct,wls}/` | `dlt_sources/official_media/british_crown/{sct,wls}/` | 1 | British Crown split out |

**LEGACY_ALIASES.md additions for Wave 1** (appended to the file per Wave 1.6):

```markdown
## Wave 1 — themed packages (2026-08-24)

| Old | New |
|:--|:--|
| `dlt/language/` | **deleted** (split into 3 themed sub-trees) |
| `dlt/language/ainm.py` | `dlt/lexicographic/ainm.py` |
| `dlt/language/canuint*.py` | `dlt/lexicographic/canuint*.py` |
| `dlt/language/duchas.py` | `dlt/lexicographic/duchas.py` (the lexicon) |
| `dlt/language/duchas_images.py` | `dlt/cultural_heritage/duchas_corpus.py` (split) |
| `dlt/language/gaois*.py` | `dlt/lexicographic/gaois*.py` |
| `dlt/language/logainm.py` | `dlt/lexicographic/logainm.py` |
| `dlt/language/tearma*.py` | `dlt/lexicographic/tearma*.py` |
| `dlt/language/celtic_mythology.py` | `dlt/cultural_heritage/celtic_mythology.py` |
| `dlt/language/heritage.py` | `dlt/cultural_heritage/heritage.py` |
| `dlt/language/hidden_heritages.py` | `dlt/cultural_heritage/hidden_heritages.py` |
| `dlt/language/local_documents*.py` | `dlt/cultural_heritage/local_documents*.py` |
| `dlt/language/universal_dependencies.py` | `dlt/language_models/universal_dependencies.py` |
| `dlt/common/destinations_cianfhoghlaim.py` | `dlt/destinations/ducklake.py` + `dlt/destinations/filesystem.py` |
| `dlt/common/destinations_tuatha.py` | `dlt/destinations/ducklake.py` (merged) |
| `dlt/_lakehouse/destinations.py` | `dlt/_lakehouse/pool.py` (renamed) + `dlt/destinations/ducklake.py` (the dlt bridge) |
| `dlt/_lakehouse/personal_archive_destinations.py` | `dlt/_lakehouse/personal_archive.py` |
| `dlt/common/ducklake_pool.py` | `dlt/_lakehouse/pool.py` (shim) |
| `dlt/common/ducklake_options.py` | `dlt/_lakehouse/options.py` (shim) |
```

### 7.2 `orchestration/` migrations

| Old path | New path | Wave | Reason |
|:--|:--|:--:|:--|
| `orchestration/defs/1_ingestion/**/defs.yaml` (619 empty placeholders) | **DELETED** | 0 + 2 | Issue #146 close |
| `orchestration/defs/2_materials/ireland_education/<subject>_assets.py` (33 per-subject) | `orchestration/pipelines/british_isles/ireland/education/<subject>/defs.yaml` | 2 | Migrate to DltLoadCollectionComponent |
| `orchestration/defs/uog_exam.py` | `orchestration/pipelines/british_isles/ireland/university/exam/defs.yaml` | 2 | Migrate to Component |
| `orchestration/defs/uog_official_docs.py` | `orchestration/pipelines/british_isles/ireland/university/official_docs/defs.yaml` | 2 | Migrate to Component |
| `orchestration/defs/uog_personal_archive.py` | `orchestration/pipelines/british_isles/ireland/university/personal_archive/defs.yaml` | 2 | Migrate to Component |
| `orchestration/defs/uog_personal_archive_figures.py` | `orchestration/pipelines/british_isles/ireland/university/personal_archive/figures_defs.yaml` | 2 | Migrate to Component |
| `orchestration/defs/uog_students_union.py` | `orchestration/pipelines/british_isles/ireland/university/students_union/defs.yaml` | 2 | Migrate to Component |
| `orchestration/defs/nui_federation.py` | `orchestration/pipelines/british_isles/ireland/university/nui_federation/defs.yaml` | 2 | Migrate to Component |
| `orchestration/defs/british_isles_tertiary.py` | `orchestration/pipelines/british_isles/university/tertiary/defs.yaml` | 2 | Migrate to Component |
| `orchestration/defs/media_intel.py` | `orchestration/pipelines/media_intel/{l1_ingestion,official_sub_buckets,l2_baml,l3_cocoindex,l4_marimo,l5_adk}/defs.yaml` | 2 | Split the big spine |
| `orchestration/defs/sync_assets.py` | `orchestration/pipelines/sync/{sync_health,dagster_sync_health,baml_sync_health,ccc_sync_health,cognee_sync_health}/defs.yaml` | 2 | Per-Component split |
| `orchestration/partitions_v2.py:308` (`cianhoghlaim_scope` typo) | `orchestration/partitions_v2.py:308` (`cianfhoghlaim_scope` — fixed) | 2 | Typo fix during LanceDB migration |
| `orchestration/storage/ducklake_client.py` | `orchestration/storage/ducklake_client.py` (deprecation shim → `dlt_sources.destinations.ducklake`) | 4 | Renamed/layer-grouped |

### 7.3 `cocoindex_flows/` migrations

| Old path | New path | Wave | Reason |
|:--|:--|:--:|:--|
| (no renames; Live mode adoption is additive) | — | 3 | — |
| `cocoindex_flows/_shared/live_components.py` | (NEW file) | 3 | LiveComponent base + `process_live` mixin |
| `cocoindex_flows/_shared/target_state.py` | (NEW file) | 3 | `declare_row` / `declare_file` helpers |

### 7.4 `web/` migrations

| Old path | New path | Wave | Reason |
|:--|:--|:--:|:--|
| `web/apps/_oideachais_apps/` | `openspec/archive/2026-08-24-archive-legacy-oideachais-apps/` | 5 | Archive (the legacy sruth archive) |
| `web/apps/game_showcase/` | `demos/game_showcase/` | 5 | Python module, not a web app |
| `web/apps/tuatha-demo/` | `demos/tuatha-demo/` | 5 | Python demo, not a web app |
| `web/apps/cianfhoghlaim-web/apps/api/` | `web/hono-api/` (canonical lift) | 5 | Lift to canonical gateway |
| `web/apps/cianfhoghlaim-leaving-cert/apps/api/` | `web/hono-api/` (canonical lift) | 5 | Lift to canonical gateway |
| `web/apps/cianfhoghlaim-web/packages/{auth,config,db}/` | `web/packages/{auth,db,config}/` (canonical lift) | 5 | Lift to canonical packages |
| `web/apps/cianfhoghlaim-leaving-cert/packages/{auth,config,convex,db,i18n,ui}/` | `web/packages/{auth,config,convex,db,i18n,ui-kit}/` (canonical lift) | 5 | Lift to canonical packages |
| `web/apps/croilar-portal/` | `web/apps/croilar-web/src/routes/admin/` | 5 | Merge as admin routes |
| `web/apps/cianfhoghlaim-web/` | `web/apps/cianfhoghlaim/src/routes/<stage>/<subject>/` | 5 | Merge into central homepage |
| `web/apps/cianfhoghlaim-leaving-cert/apps/web/` | `web/apps/oideachais/src/routes/` | 5 | Merge into per-subject content app |
| `web/apps/cianfhoghlaim-mmo/` | `web/apps/tuatha-ui/src/routes/mmo/` + `web/apps/tuatha-ui/convex/` | 5 | Merge into Tuatha UI |

---

## Section 8 — Concrete next actions for the user

### 8.1 Approve (in order)

1. **Approve this master plan** (this document). This is the high-level plan; everything else flows from it.
2. **Open the canonical openspec change** at `openspec/changes/2026-08-24-master-refactor-v1/` with the canonical 3-artifact bundle (`proposal.md` + `tasks.md` + spec deltas for the 4 capability specs affected: `centralized-model-registry`, `centralized-schema-registry`, `deployment-control-panel`, plus the new `dlt-pipeline-architecture` + `dagster-pipeline-components` specs). Validate with `openspec validate 2026-08-24-master-refactor-v1 --strict`.
3. **Approve Wave 0** (the 3-day blocker fix). This is mechanical and low-risk; can run in parallel with the openspec change authoring.
4. **Approve the per-wave openspec changes** (one per wave: `2026-08-24-wave-1-dlt-sources`, `2026-08-24-wave-2-dagster-pipelines`, etc.) — or one big change with 7 sub-tasks. The former is cleaner; the latter is faster to archive.

### 8.2 Execute (in order)

1. **Wave 0 (Days 1-3)**: Run the 88-path rewrite script, install `cocoindex` PyPI, delete the 619 empty placeholders, validate `dg check yaml` exits 0, validate `openspec validate --strict` exits 0. **Commit + push** before Wave 1.
2. **Wave 1 (Weeks 1-3)**: Open the Wave-1 openspec change; do the destination split (Wave 1.1 + 1.2); do the language/ split (Wave 1.3 + 1.4); do the official_media/ consolidation (Wave 1.8); update the docs (Wave 1.5 + 1.6 + 1.7); add the lint-dlt-paths gate (Wave 1.10). **Commit + push** per task.
3. **Wave 2 (Weeks 4-6)**: Open the Wave-2 openspec change; scaffold the pipelines/ tree (Wave 2.1); write the shared helpers (Wave 2.2 + 2.3); scaffold the 125 `defs.yaml` files via `dg scaffold defs` (Wave 2.4 + 2.5); move the hand-rolled files (Wave 2.6); fix the partition typo (Wave 2.7); update definitions.py (Wave 2.8); verify resources (Wave 2.9); standardise group_name (Wave 2.10); update AGENTS.md (Wave 2.11). **Commit + push** per directory.
4. **Wave 3 (Weeks 7-8)**: Open the Wave-3 openspec change; confirm cocoindex install (Wave 3.1); convert the 5 highest-impact apps to Live mode (Wave 3.2 + 3.3 + 3.4 + 3.5 + 3.6 + 3.7); add the shared helpers (Wave 3.8 + 3.9); update the R1-R4 check (Wave 3.10). **Commit + push** per app.
5. **Wave 4 (Weeks 9-10)**: Open the Wave-4 openspec change; consolidate the 6 DuckLake namespaces (Wave 4.1); add data_inlining (Wave 4.2); add sort expressions (Wave 4.3); add data change feed (Wave 4.4); enable encryption (Wave 4.5); set up snapshot expiry (Wave 4.6); wire Iceberg REST (Wave 4.7); update shims (Wave 4.8 + 4.9); update AGENTS.md (Wave 4.10); add the smoke test (Wave 4.11). **Commit + push** per namespace.
6. **Wave 5 (Weeks 11-16)**: Open the Wave-5 openspec change; archive the legacy dirs (Wave 5.1 + 5.2); lift the canonical packages (Wave 5.3 + 5.4 + 5.5); merge the apps (Wave 5.6 + 5.7 + 5.8 + 5.9); update the docs (Wave 5.10 + 5.11); snapshot (Wave 5.12). **Commit + push** per merge.
7. **Wave 6 (Weeks 17-20)**: Open the Wave-6 openspec change; upgrade TanStack Start (Wave 6.1); adopt the TanStack family (Wave 6.2); upgrade CopilotKit (Wave 6.3); wire AG-UI (Wave 6.4); wire A2UI (Wave 6.5); upgrade BetterAuth (Wave 6.6); consolidate Convex (Wave 6.7); adopt Bun 1.4 (Wave 6.8); add wrangler.toml (Wave 6.9); add the lint gate (Wave 6.10); update AGENTS.md (Wave 6.11). **Commit + push** per app.

### 8.3 Quality gates (run after every wave)

- `mise run lint:drift-docs` — must exit 0 (every AGENTS.md count matches ground truth)
- `mise run lint:registry` — must exit 0 (no hardcoded model strings)
- `mise run openspec:validate` — must exit 0
- `mise run sync:all` — runs all 7 sync layers (paths + ccc + cognee + skills + mcp + dagster + drift-docs)
- `dagster dev` — must start cleanly
- `bun run typecheck` (per app after Wave 5 + 6)
- The 4-step edit protocol (status → edit → diff → stage) is mandatory (per `openspec/specs/repo-hygiene-agent-routing/spec.md`)

### 8.4 Quick wins (parallel to the waves)

- **Firecrawl-driven documentation**: Every openspec change that pins a dependency version (in `pyproject.toml` / `package.json` / `mise.toml`) MUST cite at least one Firecrawl result proving the version is current (per `openspec/AGENTS.md` § "Firecrawl search"). Pair with a `ccc:search` query so both tool names appear in the Langfuse trace.
- **Concurrent-write safety**: Use the "CLAIM A FILE" pattern when multiple agents touch the same area. The 2026-08-22 PR #5 incident is the cautionary tale.
- **Backward compatibility**: Every rename ships with a deprecation shim for 1 release cycle. The shim imports + re-exports from the new path; agents that call the old path see the new content transparently.

### 8.5 What to author next (the user)

1. **Open the openspec change** at `openspec/changes/2026-08-24-master-refactor-v1/`:
   - `proposal.md` — the high-level "why"
   - `tasks.md` — the 7-wave task list with per-wave effort + risk + verification
   - `specs/centralized-model-registry/spec.md` — MODIFIED requirement: add `dlt-pipeline-architecture` as a new canonical capability
   - `specs/centralized-schema-registry/spec.md` — MODIFIED requirement: add `dagster-pipeline-components` as a new canonical capability
   - `specs/deployment-control-panel/spec.md` — MODIFIED requirement: add `wave-status-panel` tab to the marimo control panel
   - `specs/dlt-pipeline-architecture/spec.md` — NEW (the per-pipeline Dagster Component + DltLoadCollectionComponent pattern)
   - `specs/dagster-pipeline-components/spec.md` — NEW (the StateBackedComponent + Live mode + target-state patterns)
2. **Validate with `--strict`**: `openspec validate 2026-08-24-master-refactor-v1 --strict`
3. **Run Wave 0** in parallel (the 3-day blocker fix doesn't need the openspec change to land)
4. **Commit + push** Wave 0; archive the openspec change once deployed

---

**Author:** Read-only synthesis subagent.
**Date:** 2026-08-24.
**Working directory:** `/Users/cianmacandeisigh/dev/kings_college_galway`.
**Scope:** `dlt_sources/` + `orchestration/` + `cocoindex_flows/` + `observability/` + `dlt_sources/_lakehouse/` + `web/`.
**Status:** Synthesis complete. Ready for openspec change authoring + Wave 0 execution.

---

## H. Cross-references (the canonical reads)

- `openspec/changes/2026-08-24-orchestration-cocoindex-lakehouse-deep-analysis/` (the Wave 2-4 evidence)
- `openspec/changes/2026-08-24-web-frontend-deep-analysis/` (the Wave 5-6 evidence)
- `dlt_sources/AGENTS.md` (the canonical post-v7 DLT reference doc)
- `dlt_sources/LEGACY_ALIASES.md` (the migration history; will be appended per Wave 1.6)
- `orchestration/AGENTS.md` (will be rewritten per Wave 2.11)
- `web/AGENTS.md` (will be rewritten per Wave 5.10 + 6.11)
- `.agents/skills/ccc/SKILL.md` — the ccc code search skill (used for the 88-path rewrite)
- `.agents/skills/openspec/SKILL.md` — the openspec workflow (use for change authoring)
- `.agents/skills/dagster/SKILL.md` — the Dagster 1.13+ Component framework
- `.agents/skills/cocoindex/SKILL.md` — the CocoIndex v1 + Live mode + R1-R4 conformance
- `.agents/skills/ducklake/SKILL.md` — the DuckLake v1.0 reference
- `.agents/skills/centralized-registry/SKILL.md` — the model + schema registries
- `.agents/skills/mise/SKILL.md` — the mise task authoring skill (for new tasks like `lint:dlt-paths`, `lint:web-stack`, `lakehouse:smoke-test`)
- `.agents/skills/tanstack-start/SKILL.md` — the TanStack Start 1.0+ skill (for Wave 6.1)
- `.agents/skills/copilotkit-develop/SKILL.md` — the CopilotKit v2 skill (for Wave 6.3)
- `.agents/skills/ag-ui/SKILL.md` — the AG-UI SSE protocol skill (for Wave 6.4)
- `.agents/skills/better-auth/SKILL.md` — the BetterAuth 1.7 skill (for Wave 6.6)
- `.agents/skills/firecrawl/SKILL.md` — the Firecrawl MCP wrapper (for Wave 2 pre-work)
- `.agents/skills/indexing-and-cognition/SKILL.md` — the CCC + Cognee + Firecrawl triple-search
- `openspec/specs/dagster-5-layer-component-architecture/spec.md` — the layer model this plan evolves
- `openspec/specs/centralized-model-registry/spec.md` — the 76-entry model registry
- `openspec/specs/centralized-schema-registry/spec.md` — the BAML → Pydantic/Zod codegen
- `openspec/specs/deployment-control-panel/spec.md` — the 5-tab marimo control panel
- `openspec/specs/british-isles-education-pipeline/spec.md` — the BIEP v3 flagship spec
- `openspec/specs/cianfhoghlaim-personal-archive-typed-modules/spec.md` — the UoG personal-archive spec
- `openspec/specs/agent-platform-cluster/spec.md` — the 8-stack cluster
- `openspec/specs/agent-observability/spec.md` — Langfuse + MLflow + Logfire + Ragas
- `openspec/specs/repo-hygiene-agent-routing/spec.md` — the 4-step concurrent-write protocol
- `openspec/specs/infrastructure-stacks/spec.md` — the 94 Docker Compose stacks
- `openspec/specs/indexing-and-cognition/spec.md` — the dual-search architecture
- `openspec/specs/knowledge-sync-loop/spec.md` — the 7-layer sync architecture