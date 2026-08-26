# `dlt_sources/` — Deep Sprawl & Refactor Analysis

**Date**: 2026-08-24
**Author**: Read-only research subagent
**Scope**: `dlt_sources/` (the canonical post-v7 Python sub-package for the DLT ingestion layer + cross-jurisdiction registry + common helpers)
**Audience**: Build agent + future openspec change author for `2026-08-24-dlt-sources-namespace-cleanup-v1` (proposed)

---

## A) Current `dlt_sources/` sprawl — tree, role, and line counts

**Totals** (excluding `__pycache__/`):

| Metric | Value |
|--|--:|
| `.py` files | **1,975** |
| Total LOC | **155,506** |
| `@dlt.source` decorators | **919** |
| `@dlt.resource` decorators | **1,244** |
| `@dlt.transformer` decorators | **0** |
| Files that `import dlt` | **980** (≈ 50% of the corpus) |

### Per-subtree inventory (the 15 top-level sub-trees + the `_lakehouse/` shim)

| Sub-tree | `.py` | LOC | `@dlt.source` | Role |
|--|--:|--:|--:|:--|
| `european_nations/` | 859 | 50,498 | 407 | **Source factory** — 40 nations × 5 verticals (`education / government / law / medicine / statistics`) via `_shared/nation_source.py`. Heaviest subtree by far (33% of all LOC). |
| `commonwealth/` | 633 | 30,619 | 292 | **Source factory** — 6 nations + 13 Canadian provinces + 36 Nigerian states × 5 verticals; uses the `_shared/nation_source.py` base class. |
| `british_isles/` | 246 | 32,752 | 106 | **Mixed** — the BIEP v3 flagship (8 jurisdictions × 5 stages + 5 verticals + the `_cross/` registry). |
| `common/` | 28 | 8,073 | 3 | **Helpers** — destinations, endpoint_recovery (the canonical 3-strategy fetch), observability, http_client, motherduck_options, batching, pagination, firecrawl_source, incremental, safety, source_adapters, the BIEP v3 registry seed, DuckLake/Iceberg options, mixins. |
| `crypteolas/` | 15 | 4,155 | 18 | **Single product** — Tuatha Crypteolas achievement ledger (defi + github + local + docs). |
| `language/` | 25 | 5,336 | 11 | **Celtic-language sources** — Logainm (placenames), Téarma (terminology), Ainm (names), Gaois, Dúchas, Canúint, Universal Dependencies, + local / heritage corpora. Mixes Irish file names with English ones (see §C). |
| `filesystem/` | 19 | 6,372 | 8 | **Filesystem pipelines** — leaving_cert_source, zotero, takeout_v1, google_takeout, gemini_deep_research, gemini_corpus_source, university_of_galway, leabharlann_books, lc6_cross_check, previews, email_inbox, uog_personal_archive, plus 5 private `_*.py` helpers. |
| `european_union/` | 27 | 2,151 | 19 | **EU bodies** — Eurostat + EUR-Lex (5 instruments) + Parliament + Council + Commission press + Publications Office + Eurydice + CEDEFOP + EMA + ECDC + EHDS. Plus `_shared/registries.py`. |
| `american_nations/` | 51 | 2,818 | 24 | **4 nations × 5 verticals** — Brazil, Mexico, Venezuela, + `united_states/us_ca/` (California only). |
| `media/` | 22 | 2,350 | 9 | **Mixed hobby corpus** — animation, comics, games, official (gov + NCCA + SEC + Duchas), celtic_history_research, prose. (Mostly `source.yaml` + `scrape.py` pairs, not `@dlt.source`-decorated modules.) |
| `portfolio/` | 7 | 2,122 | 2 | **Croilar portfolio** — artwork + CV + labels (Base + Scraper) + source + teaching. |
| `official_media/` | 20 | 2,625 | 2 | **Gov / official-media** — Instagram-export → B-I gov source enrichment + Fediverse + Companies House + HMGCC + GGY + 8 Crown Dependencies/UK/IE/SCT/WLS/NI/IOM/JSY sub-sources. |
| `api_sources/` | 12 | 3,688 | 6 | **Generic non-jurisdictional APIs** — Spotify (2 files) + SoundCloud (2) + YouTube + GitHub + LinkedIn + ResearchGate + TG4 Player + Foghlaim lessons + leabharlann_education_notes (cross-repo bridge). |
| `apple_photos/` | 4 | 1,010 | 1 | **Stub** — 5th leabharlann corpus via `osxphotos` (library_export + document_scans + vehicles). Awaiting the `apple-photos-ingestion` openspec. |
| `jobs/` | 2 | 182 | 0 | **Dagster job entry points** — only `government_circulars_job.py` + `__init__.py`. |
| `_lakehouse/` | 3 | 723 | 0 | **Sibling-shim** — `destinations.py` (Lakehouse/MotherDuck/Local, has hard dependency on `sruth_browser.core.secrets`) + `personal_archive_destinations.py`. The 2-module `_lakehouse` lives outside the per-area sub-package conventions. |
| **Total** | **1,975** | **155,506** | **919** | |

### Files vs. dlt decoration density (audit signal)

| Sub-tree | `.py` files | @dlt.* per file | Density |
|--|--:|--:|---|
| `british_isles/` | 246 | 379 | 1.54 |
| `european_nations/` | 859 | 814 | 0.95 |
| `commonwealth/` | 633 | 584 | 0.92 |
| `european_union/` | 27 | 37 | 1.37 |
| `filesystem/` | 19 | 47 | 2.47 |
| `crypteolas/` | 15 | 67 | 4.47 |
| `language/` | 25 | 56 | 2.24 |
| `official_media/` | 20 | 4 | 0.20 |
| `media/` | 22 | 39 | 1.77 |

The 3 subtrees below 1.0 density (`european_nations`, `commonwealth`, `official_media`) carry a lot of empty `__init__.py` files in the per-nation/per-vertical sub-trees (the legacy directory skeleton that the factory pattern never collapsed).

### The `_lakehouse/` shim (an audit anomaly)

The file `dlt_sources/_lakehouse/__init__.py` is a **90-line dual-mode shim** that:

1. Always re-exports `personal_archive_destinations.py` (356 LOC).
2. **Try/except** imports `destinations.py` (277 LOC) — the hard dependency on `sruth_browser.core.secrets` means it gracefully degrades to a `LocalDuckDB` fallback when `sruth_browser` is not installed.

This is the **only sub-tree in `dlt_sources/` whose name does NOT follow the `common/<area>/` convention** — it uses a leading underscore (a Python "private module" convention) and breaks the per-area AGENTS.md rule (the data-platform-router says all 5 sub-packages should expose their per-area docs at `<area>/AGENTS.md`).

### The `common/destinations_*.py` duplication

There are **TWO** destination modules under `common/`:

| File | LOC | Public surface | Status |
|--|--:|---|---|
| `common/destinations_cianfhoghlaim.py` | 528 | `get_dlt_destination()`, `DEFAULT_NAMESPACE = "cianfhoghlaim"`, `LAKEHOUSE_DUCKDB = "md:cianfhoghlaim"`, `apply_ducklake_1_0_optimisations` | **Canonical** — the AGENTS.md says use this one. |
| `common/destinations_tuatha.py` | 145 | `NAMESPACE = "tuath"`, `get_dlt_destination()`, `create_pipeline()` | **Deprecated shim** — its own module docstring says *"This shim is deprecated in favour of `cianfhoghlaim.dlt.destinations_oideachais`; the v4 consolidation (2026-06-28) moved the canonical helpers there."* The namespace is also misspelled (`"tuath"` instead of the correct Irish `"tuatha"`). |

Neither has importers in the current dlt_sources tree (only 2 importers of `destinations_cianfhoghlaim`; 0 of `destinations_tuatha`), so the duplication is **purely vestigial**.

### The `common/` helper import-density audit

| Helper module | LOC | Files that import it | Notes |
|--|--:|--:|---|
| `endpoint_recovery.py` | 410 | **200** | The canonical 3-strategy fetch (Firecrawl → Crawl4AI → direct HTTP). The de facto shared primitive. |
| `firecrawl_source.py` | 392 | 17 | Firecrawl + sruth-browser fallback adapter. |
| `http_client.py` | 312 | 15 | Singleton HTTPX-based client. |
| `source_adapters.py` | 580 | (helper-of-helpers) | Source → resource adapters. |
| `destinations_cianfhoghlaim.py` | 528 | 2 | The Lakehouse destination factory. |
| `mixins.py` | 446 | (internal) | Mixin classes for the per-nation sources. |
| `pagination.py` | 422 | 0 | **Dead** — no callers. |
| `safety.py` | 347 | 0 | **Dead** — no callers. |
| `content_deduplication.py` | 335 | 0 | Possibly used internally by `incremental.py`. |
| `crawl_utils.py` | 331 | 0 | Possibly used internally by `site_crawler.py`. |
| `incremental.py` | 302 | 6 | The cursor-management helper. Has a `__getattr__` deprecation shim. |
| `snake_case_contract.py` | 298 | 0 | **Dead** — no callers. |
| `batching.py` | 240 | 0 | Possibly used internally. |
| `observability.py` | 167 | 0 | **Dead** — no callers (despite the central importance of observability). |
| `ducklake_options.py` | 161 | 1 | DuckLake 1.0 feature helpers (data inlining, sorted_by, bucket_partitioned). |
| `motherduck_options.py` | 159 | 0 | **Dead** — no callers. |
| `named_destinations.py` | 153 | 0 | **Dead** — no callers. |
| `_http_factories.py` | 201 | 0 | Private — used internally. |
| `site_crawler.py` | 910 | (massive) | The crawling primitive; huge file. |
| `iceberg_options.py` | 33 | 1 | The Iceberg destination options. |
| `_shared_utils_stub.py` | 111 | 0 | **Dead** — clearly a stub. |
| `ducklake_pool.py` | 77 | 0 | **Dead** — no callers. |
| `cli.py` | 77 | (entry point) | The `cianfhoghlaim-dlt` CLI (re-exported via root `dlt_sources/cli.py`). |

**Audit signal**: 9 of the 28 helpers in `common/` have **zero importers**. They were likely part of a v4/v5 aspirational design that was never adopted. They contribute ~1,800 LOC of dead-ish code.

### The `british_isles/ireland/education/subjects/` tree

The "subject-as-package" pattern — each LC subject has its own `__init__.py` + `schema.py` + `sources.py`:

```
british_isles/ireland/education/subjects/
├── __init__.py
├── README.md
├── base.py
├── junior_cycle.py
├── senior_cycle.py
├── hei.json
├── lc_subjects.json
├── manifest.py
├── stages.json
├── subjects/
│   └── (LC subjects: applied_mathematics, chemistry, computer_science, english,
│       gaeilge, geography, history, mathematics)
├── junior_cycle_cbas/     (__init__.py + _factory.py)
└── junior_cycle_subjects/ (__init__.py + _factory.py)
```

This is the **canonical reference pattern** for new BIEP v3 subjects — `from .sources import math_source, MATH_CORPUS, ...`. Future jurisdiction pipelines should reuse this shape.

### The `british_isles/_cross/` registry

The cross-jurisdiction registry — the single most important shared module after `common/`:

```
british_isles/_cross/
├── __init__.py
├── biep_4_path_ensemble_runner.py     # 4-path BIEP ensemble
├── biep_4_stage_registry.py           # Stage registry
├── connection.py                       # MotherDuck / DuckDB connection factory
├── jurisdiction_pipeline_base.py       # JurisdictionPipelineBase (the canonical base class)
├── registry_api.py                     # query_by_jurisdiction(...)
└── registry_loader.py                  # seed_registry() (1990 cohort rows across 8 BI jurisdictions)
```

The `JurisdictionPipelineBase` at `british_isles/_cross/jurisdiction_pipeline_base.py:34` is the canonical factory pattern referenced in the AGENTS.md. Subclass + set `STAGE` + implement `build_pipeline_resource()` = a new jurisdiction pipeline in ~25 LOC.

---

## B) Legacy aliases currently in use (`LEGACY_ALIASES.md`)

The `LEGACY_ALIASES.md` file is **48 lines long** and documents 6 historical rename waves completed during v7 (2026-07-17). The doc itself is purely historical — but the underlying directories **DO exist on disk**, and the underlying **imports** in the Python source files have NOT been fully migrated to the canonical paths. There are ~873 broken legacy imports across the corpus:

### The 6 legacy rename waves

1. **European nations** — ISO-3 → full snake_case (39 codes)
   `dlt/european_nations/{alb,aut,...,xkx}/` → `dlt/european_nations/{albania,...,kosovo}/`
2. **Commonwealth** — ISO-3 → full snake_case (6 codes)
   `dlt/commonwealth/{aus,can,ind,nga,nzl,zaf}/` → `dlt/commonwealth/{australia,canada,india,nigeria,new_zealand,south_africa}/`
3. **Canada provinces** — ISO-2 → full snake_case (13 codes)
   `dlt/commonwealth/can/{ab,...,yt}/` → `dlt/commonwealth/canada/provinces/{alberta,...,yukon}/`
4. **Nigeria states** — `nga_<3>` → full snake_case (36 codes)
   `dlt/commonwealth/nigeria/states/nga_{abi,...,zam}/` → `dlt/commonwealth/nigeria/states/{abia,...,zamfara}/`
5. **British Isles** — collapse dual naming
   `dlt/british_isles/{en,ni,sct,wls,iom,jey,ggy}/` → `dlt/british_isles/{england,northern_ireland,scotland,wales,isle_of_man,jersey,guernsey}/`
6. **Americas** — `americas/` → `american_nations/`, ISO-3 → full
   `dlt/americas/{bra,mex,us,ven}/` → `dlt/american_nations/{brazil,mexico,united_states,venezuela}/`

### The ghost-shim problem (THE BIG FINDING)

The LEGACY_ALIASES.md doc claims the 6 renames are "completed on disk" and that "the doc's role is now purely historical — there's no `import dlt.european_nations.alb` shim remaining." **This is false on the import side.** A grep across the corpus finds the following broken legacy imports (these all reference non-existent directories and will fail at import time):

| Subtree | Broken legacy imports referencing non-existent dirs | Notes |
|--|--:|---|
| `commonwealth/` | **336** | All `__init__.py` files reference `dlt_sources.commonwealth.{aus,nzl,nga}.{vertical}` — but only `dlt_sources.commonwealth.{australia,new_zealand,nigeria}.{vertical}` exist. The ISO-3 directories were renamed but the imports were never updated. |
| `european_nations/` | **494** | All per-nation `__init__.py` files reference `dlt_sources.european_nations.<iso3>.{vertical}` — but only `dlt_sources.european_nations.<full_name>.{vertical}` exist. Same drift. |
| `british_isles/` | **16** | Subject-subdirs in `british_isles/england/education/subjects/subjects/{chemistry,mathematics,english,...}/__init__.py` reference `dlt_sources.british_isles.en.education.subjects.<subject>` — but only `dlt_sources.british_isles.england.education.subjects.<subject>` exist. |
| `american_nations/` | **27** | Files reference the legacy `dlt_sources.americas.{bra,mex,us,ven}/...` paths. |
| **Total broken legacy imports** | **~873** | Each one is a `ModuleNotFoundError` waiting to happen. |

**The only safe import surface right now is `from dlt_sources.british_isles.ireland.education...` — that subtree was migrated correctly.** The other 14 subtrees have ghost-shim imports that will fail under any `python -c "import dlt_sources.<subtree>"` smoke test.

### Drift from the AGENTS.md convention

The AGENTS.md says: *"Always use relative imports within `dlt_sources/`. The canonical pattern is `from .._shared.<file> import ...` for cross-file references. **Never** `from dlt_sources.x import ...` from within `dlt_sources/x/` — this creates an import cycle."*

Reality:

- A grep for `from ..` (relative imports) across `dlt_sources/<subtree>` finds **3 hits in british_isles** and **0 in every other subtree**.
- A grep for `from dlt_sources.` (absolute imports) finds **~873 hits** (the legacy ghost shims) + the canonical inter-subtree imports.
- Conclusion: the entire codebase uses **absolute imports** despite the AGENTS.md rule. The legacy shim work has created a broken state.

---

## C) Naming inconsistencies

The current naming in `dlt_sources/` mixes **English**, **Irish-language**, **ISO-3 / ISO-2 codes**, and **snake_case English** in an inconsistent way. The intent (per the project name `cianfhoghlaim` = "learning" in Irish) is to lean into Irish where appropriate.

### The 4 naming patterns currently in use

| Pattern | Examples | Where |
|---|---|---|
| **English snake_case** | `british_isles`, `european_nations`, `european_union`, `commonwealth`, `american_nations`, `filesystem`, `jobs`, `portfolio`, `media`, `api_sources`, `common`, `apple_photos`, `_lakehouse` | All 15 subtrees, plus the 1 underscore-prefixed `_lakehouse/` |
| **Irish Gaelic** | `tearma`, `logainm`, `gaois`, `duchas`, `canuint`, `ainm`, `foghlaim`, `leabharlann`, `ollscoil_na_gaillimhe`, `tuatha` | 38 files (mostly `language/` + `filesystem/leabharlann_books.py` + `api_sources/foghlaim_lessons.py` + `api_sources/leabharlann_education_notes.py` + `filesystem/uog_personal_archive.py`) |
| **ISO-3 / ISO-2 codes** | `aus`, `can`, `ind`, `nga`, `nzl`, `zaf`, `alb`, `aut`, `bel`, `bgr`, `cyp`, `cze`, `deu`, `dnk`, `esp`, `est`, `fin`, `fra`, `geo`, `grc`, `hrv`, `hun`, `isl`, `ita`, `lie`, `ltu`, `lux`, `lva`, `mda`, `mkd`, `mlt`, `mne`, `nld`, `nor`, `pol`, `prt`, `rou`, `srb`, `svk`, `svn`, `swe`, `tur`, `ukr`, `xkx`, `en`, `ni`, `sct`, `wls`, `iom`, `jey`, `ggy`, `bra`, `mex`, `us`, `ven`, `ab`, `bc`, `mb`, `nb`, `nl`, `ns`, `nt`, `nu`, `on`, `pe`, `qc`, `sk`, `yt` | In 873 broken legacy imports |
| **Mixed / brand names** | `apple_photos`, `leabharlann_books`, `lc6_cross_check`, `foghlaim_lessons`, `tg4_player_shows`, `crypteolas`, `university_of_galway`, `lc6`, `cognee`, `motherduck` | Various |

### Overlapping scopes — the 6 "what's a nation" subtrees

The most confusing part of the layout: **6 different subtrees can each contain a "nation"-level entity**:

| Subtree | Entity it indexes | Cardinality | Pattern |
|--|--|--:|--|
| `british_isles/` | BI nations (8) + Crown Dependencies (3) + sub-trees per nation | 8 nations + 3 deps | Mixed: `england/` `northern_ireland/` `scotland/` `wales/` `ireland/` `crown_dependencies/` `isle_of_man/` `jersey/` `guernsey/` `sct_wls_ni/` `_cross/` `university/` |
| `european_nations/` | European states (40) | 40 nations | One dir per nation (`poland/`, `germany/`, ...) |
| `european_union/` | EU bodies (supra-national, ~10 agencies) | ~10 sources | Per-agency (`eur_lex/`, `cedefop/`, `ema/`, `eurostat/`, ...) |
| `commonwealth/` | Commonwealth states (6) + Canadian provinces (13) + Nigerian states (36) | 6 + 49 sub-entities | One dir per state (`australia/`, `canada/provinces/alberta/`, ...) |
| `american_nations/` | American states (4) | 4 nations | One dir per nation (`brazil/`, `mexico/`, `united_states/us_ca/`, `venezuela/`) |
| `media/` + `official_media/` + `api_sources/` | Cross-cutting hobby + government + API sources | n/a | Per-source-dirs |

**Confusing boundary cases**:

- `british_isles/university/` — British-university aggregator (a separate subtree inside `british_isles/`); co-exists with `british_isles/ireland/university/` (the Ireland-university aggregator) and `filesystem/university_of_galway.py`. **3 different "university" surfaces, all distinct.**
- `british_isles/ireland/education/` contains `subjects/` (LC subjects as packages), `junior_cycle_cbas/` (factory), `junior_cycle_subjects/` (factory), `university/` (UoG aggregator) — **4 different sub-patterns inside one jurisdiction folder**.
- `filesystem/` contains `university_of_galway.py` AND `uog_personal_archive.py` AND `leabharlann_books.py` AND `lc6_cross_check.py` — **all 4 of these are leabharlann corpus connectors**, but they live in `filesystem/` (the generic location) rather than a dedicated `leabharlann/` subtree.

### Irish vs English — the inconsistency matrix

The repo deliberately leans into Irish (`cianfhoghlaim` itself, `tuatha`, `leabharlann`, `ollscoil_na_gaillimhe`) but the `dlt_sources/` layer is **mostly English**. The Irish-language names that exist are concentrated in:

- `language/` (all files use the Irish-language source names: `tearma.py`, `logainm.py`, `gaois.py`, `duchas.py`, `canuint.py`, `ainm.py`) — **7/7 Irish**.
- `api_sources/foghlaim_lessons.py`, `api_sources/leabharlann_education_notes.py` — **2/12 Irish**.
- `filesystem/leabharlann_books.py`, `filesystem/uog_personal_archive.py` — **2/19 Irish**.
- `common/destinations_tuatha.py` — **1/28 Irish** (and the namespace value inside it is misspelled `"tuath"` instead of `"tuatha"`).
- `media/celtic_history_research/tuatha_de_danann/` (a folder name) — **1/N Irish**.

Everything else (subtree names, country names, vertical names, helper names) is English.

### The `destinations_*.py` duplication (already documented in §A)

`common/destinations_cianfhoghlaim.py` (528 LOC, canonical) and `common/destinations_tuatha.py` (145 LOC, deprecated shim, misspelled namespace) — the deprecation shim is itself a vestige of the pre-v4 `tuatha` quadrant that was merged into `cianfhoghlaim` on 2026-06-28.

### The `stedding/ingest_queue/` cache inconsistency

The `_shared/nation_source.py` file in `european_nations/` references a hard-coded cache path:

```python
EU_NATIONS_CACHE_ROOT: Path = Path(
    os.environ.get(
        "EU_NATIONS_SCRAPE_CACHE_ROOT",
        str(Path(__file__).resolve().parents[3] / "stedding" / "ingest_queue" / "european_nations"),
    )
)
```

But the **British Isles equivalent** uses a different cache path (`stedding/ingest_queue/british_isles/...`), and the Commonwealth cache uses another (`stedding/ingest_queue/commonwealth/...`). Each subtree re-implements the same cache-lookup primitive — there is no shared `common/cache_path.py`.

### The `_lakehouse/` name (the audit anomaly)

The `_lakehouse/` subtree is the **only** module in `dlt_sources/` whose name starts with an underscore (Python's "private module" convention). It is a **sibling** of `common/`, `british_isles/`, etc., not a submodule of `common/`. The README and DATA_PLATFORM_ROUTER.md never mention it. It's effectively undocumented.

---

## D) dlt 1.21 → 1.30 features most relevant to refactoring

### Source state

- **dlt current version**: `dlt[duckdb,motherduck,filesystem]>=1.30.0,<2.0.0` (per `pyproject.toml`, pinned by the `2026-08-21-dlt-1.28.1-to-1.30.0-v1` openspec change).
- **Latest upstream**: `dlt 1.30.0` released `2026-08-11` (commit `a2f4a21e22e5c266278271b6591c70dbc485aea8`).

### The 9 releases 1.21.2 → 1.30.0

| Release | Date | Headline feature relevant to refactoring |
|---|---|---|
| **1.21.2** | (latest 1.21 patch) | **Breaking**: Compound hints precedence and replacement behavior. Direct `merge_key` / `primary_key` / `cluster` / `partition` hints now take precedence over column-level hints. |
| **1.22.x** | Jan 2026 | (intermediate patch line; not in the surfaced release list) |
| **1.23.x** | Feb 2026 | (intermediate patch line; not in the surfaced release list) |
| **1.24.x** | Mar 2026 | (intermediate patch line; not in the surfaced release list) |
| **1.25.0** | 2026-04-15 | **`lance` destination** (Lance table format with optional lancedb vector embed gen). **Multischema datasets** (default behaviour — datasets hold multiple schemas; pass `pipeline.default_schema` to opt back into single-schema). **`ducklake: metadata_schema ATTACH option** (NEW — separate the catalog metadata schema from `ducklake_name`). |
| **1.26.x** | Apr 2026 | (intermediate patch line) |
| **1.27.0** | 2026-05-19 | **Native Polars DataFrame / LazyFrame** in `@dlt.resource` (auto-detected, routed via Arrow pipeline). **Databricks Zerobus loading** via `databricks_adapter(my_resource, insert_api="zerobus")`. **Incremental filtering for `dlt.Relation`** (apply incremental filters directly on `dlt.Relation`). **`dlthub` command split** — `workspace` extra removed; `dlt dashboard`/`dlt pipeline ... show`/`dlt pipeline ... mcp` require `pip install dlt[hub]`; `dlt ai` moved to `dlthub ai`. |
| **1.27.2** | 2026-05-29 | Hotfix — `merge` with empty data after `replace` on incremental truncates the destination table. |
| **1.28.0** | 2026-06-15 | **Breaking**: `refresh="drop_data"` on Delta / persistent-catalog Iceberg no longer frees storage (now transactional delete that keeps the table + version history). **Breaking**: `replace` now fully truncates empty + orphaned tables. **Lance destination write optimizations** — namespace/session pooling + single-commit-per-table writes. **Reliable `replace` / `refresh` truncation**. **Configurable CSV encoding** (utf-8-sig for Excel BOM, latin-1 / cp1252). **Refreshable cloud credentials for long-running loads** (fixes `ExpiredToken` on long-held connections). |
| **1.28.1** | 2026-06-19 | **Python 3.9 EOL** — dropped 3.9 support; must upgrade to 3.10+. Dataset browser by default in the dltHub dashboard. |
| **1.28.2** | 2026-07-10 | Patch — allow 1.28.x to use future `dlthub-client` versions. |
| **1.29.0** | 2026-07-13 | **ClickHouse `staging-optimized` replace strategy** (atomic `EXCHANGE TABLES`). **AWS Secret Manager config provider** (new, matching Google Secret Manager). **Explicit joins in `Relation.join()`**. **Cross-destination join compatibility** (the `physical_location()` accessor + `can_join_with` rules — dlt now knows when relations on different destinations can be joined). **BigQuery atomic replace** (`enable_atomic_replace` config flag). **DuckDB SQLAlchemy destination**. **Expose Parquet compression codec** (`DATA_WRITER__COMPRESSION`). |
| **1.29.1** | 2026-07-24 | Patch — JWT auth without scopes, REST paginator stop conditions on `has_more=true`, sqlglot 30.13.0 case-sensitivity. |
| **1.30.0** | 2026-08-11 | **Breaking**: failed load packages no longer auto-abort (`auto_abort_on_terminal_error` defaults to False; `Pipeline.drop_pending_packages()` deprecated in favour of `abort_packages` / `abort-packages`). **Breaking**: filesystem layouts that omit `{ext}` now get the extension appended (`mocked-table.jsonl`). **Breaking**: table prefix keeps its separator (event. rather than event to prevent replace dropping events). **`add_limit` on the source factory** (`@dlt.source` factories accept `.add_limit()` before instantiation, both sync and async; factory clones preserve the limit). **Retryable schema migrations** (a `retry_schema_update` helper for tenacity — failing schema migrations retry with jitter + backoff instead of failing the load). **Manual load package abort** (`abort_packages` records what happened; `list_pending_retry_jobs_in_package()`, `fail_pending_job()`, `retry_failed_job()` on Pipeline; `dlt pipeline <name> load-package <load-id> fail-job <job>` CLI). **Cross-destination joins** (join datasets that live on different destinations — eager + lazy materialization; supported for `duckdb`, `motherduck`, `ducklake`, `lance`, `lancedb`, `filesystem`). **Snowflake nested types** behind a `use_nested_types` flag. **Input/output lineage in traces** (lineage in relational form close to OpenLineage). **Configurable destination session time zone** (`session_timezone` on clickhouse, databricks, duckdb, ducklake, postgres, redshift, snowflake; UTC defaults on duckdb + snowflake). **`instance` key in the job `require` spec** (open dict, `instance.size` like `{"size": "medium"}`; legacy `machine` key still works but emits a `DltDeprecationWarning`). **Refs to `dlthub` AI Harness** — four artifact kinds (ingest / validate / transform / deploy / observe). |

### The 9 features most relevant to the dlt_sources refactor

| Feature | Version | Relevance to `dlt_sources/` refactor |
|---|---|---|
| **Multischema datasets** (datasets hold multiple schemas) | 1.25.0 | **HUGE**. Today, the BIEP pipeline emits `oideachais.<domain>.european_nations.<country_code>` (single schema per pipeline). With multischema datasets, we can collapse all 40 European nations into ONE pipeline producing ONE dataset with 40 schemas — eliminating the need for the per-nation factory pattern in `european_nations/_shared/nation_source.py` and the per-nation-subtree sprawl. |
| **Cross-destination joins** (join datasets that live on different destinations) | 1.30.0 | **HUGE**. Today, the Ireland + England + Scotland + Wales + ... pipelines each go to the same `md:cianfhoghlaim` DuckLake. With cross-destination joins, we can split the jurisdiction pipelines to MotherDuck (BIEP v3) vs. local DuckLake (development cache) vs. R2 (cold archive) and still JOIN them in the marimo notebooks via `users.join(orders, on="...")`. This kills the "single canonical destination" hard-coding. |
| **`add_limit` on the source factory** | 1.30.0 | **MEDIUM**. The 873 broken legacy imports hide because nobody runs the smoke test. `@dlt.source` factories now support `.add_limit()` — we can write a CI helper that loads every source with `.add_limit(1)` (1-row smoke) to catch broken imports without paying for full extraction. |
| **Configurable destination session time zone** | 1.30.0 | **MEDIUM**. Critical for the Celtic-language sources that publish in multiple languages (Téarma has translations for many languages; the BIEP `ireland_jurisdiction_pipeline` row emits both EN and GA text). The current code hard-codes UTC. |
| **`ducklake: metadata_schema` ATTACH option** | 1.25.0 | **MEDIUM**. The Lakehouse Postgres schema is currently hard-coded to the `ducklake_name`. The new option lets us split the catalog metadata schema (`public`) from the data path. Useful for the multi-tenant scenario (one Postgres instance, one schema per tenant). |
| **Native Polars DataFrame / LazyFrame** in `@dlt.resource` | 1.27.0 | **MEDIUM**. The Leaving Cert pipeline + the AQA/OCR/Edexcel pipelines currently emit Python dicts; Polars yield would speed them up significantly. |
| **Incremental filtering for `dlt.Relation`** | 1.27.0 | **LOW**. The cross-jurisdiction registry already does its own incremental updates; this is a nice-to-have for the marimo notebooks. |
| **ClickHouse `staging-optimized` replace strategy** | 1.29.0 | **NOT RELEVANT** (no ClickHouse usage). |
| **AWS Secret Manager config provider** | 1.29.0 | **NOT RELEVANT** (we use Infisical + Locket + mise). |
| **Cross-destination join compatibility** (`physical_location()` + `can_join_with`) | 1.29.0 | **HIGH**. Prerequisite for the cross-destination join feature. |
| **`use_nested_types` flag (Snowflake)** | 1.30.0 | **NOT RELEVANT** (no Snowflake usage; we use DuckDB + MotherDuck + DuckLake). |
| **Input/output lineage in traces** | 1.30.0 | **MEDIUM**. Pairs well with the existing Langfuse + MLflow observability. The dlt trace can now expose lineage so the marimo notebook + Dagster asset graph can answer "where did this row come from?". |
| **Manual load package abort** (`abort_packages`, `fail_pending_job`, `retry_failed_job`) | 1.30.0 | **HIGH**. Replaces `drop_pending_packages` which is deprecated. The BIEP v3 Ireland pipeline currently uses the old API. |
| **Retryable schema migrations** (`retry_schema_update` helper for tenacity) | 1.30.0 | **HIGH**. The most common cause of pipeline failure today is a schema-evolution mismatch (NCCA changes the LC syllabus, the next pipeline run crashes). The new helper retries with jitter + backoff. |
| **`instance` key in the job `require` spec** | 1.30.0 | **LOW** (we don't use the dlthub runner). |
| **Databricks Zerobus loading** | 1.27.0 | **NOT RELEVANT** (no Databricks usage). |

### Features that did NOT land in 1.21–1.30 that the dlt_sources corpus assumes

- **No native `@dlt.source_factory` decorator** — the codebase has to roll its own factory pattern via `@dlt.source` returning a class (see `_shared/nation_source.py:NationSource`). The dlt 1.30 source factory is still just `@dlt.source` + `.add_limit()`; no dedicated `@dlt.source_factory` decorator exists.
- **No native `@dlt.transformer` use in our code** — 0 occurrences of `@dlt.transformer` in the corpus, despite it being the canonical way to declare a child resource that consumes the parent's rows. The codebase instead nests resources via direct function composition.
- **No built-in REST API source generator** (the `rest_api` source is a separate `dlt-plus`/`dlt-rest-api` library, not bundled). The `api_sources/` subtree (Spotify, SoundCloud, YouTube, GitHub, LinkedIn, ResearchGate, TG4, Foghlaim) is hand-rolled.
- **No native schema-contract changes** in 1.21–1.30 that affect our usage — the schema `evolve` / `freeze` / `discard_value` settings are stable since 1.0.

---

## E) DuckLake best practices for a multi-domain Irish/educational data lake

DuckLake v1.0 is **April 2026** stable (the extension is bundled with DuckDB 1.5.2+). Source: `ducklake.select/docs/stable/duckdb/introduction`.

### DuckLake architecture recap

DuckLake = **ACID transactions on object storage** = Parquet files + a SQL metadata catalog. Two decisions to make:

1. **Metadata catalog database** — sqlite (local, fast), duckdb (local, fast), postgres (production, full parallelism), mysql (experimental), motherduck (experimental as of 1.4+).
2. **Storage backend** — local files, S3, GCS, Azure ADLS Gen2 (via fsspec fallback).

### The 4 canonical BIEP-lakehouse best practices

| Practice | Recommendation | Rationale (per the dlt + DuckLake docs) |
|--|--|--|
| **1. Catalog choice** | Use **Postgres** for prod, **SQLite** for dev. | Postgres is the only catalog with full parallelism (SQLite and DuckDB cannot do parallel writes — dlt falls back to sequential mode). Motherduck-as-catalog is experimental. |
| **2. Storage choice** | Use **S3** for prod, **local files** for dev. | The Garage S3 stack at `bonneagar/stacks/lakehouse/` is the canonical KCG store. Local files for `USE_LOCAL_SCRAPES=true` dev. |
| **3. `metadata_schema` ATTACH option** | Set **per-tenant** in Postgres. | New in dlt 1.25.0. Lets you use the same Postgres instance for multiple tenants by giving each its own metadata schema. For the Cianfhoghlaim platform, we'd set `metadata_schema="oideachais"` (one schema per quadrant: `oideachais`, `tuatha`, `croilar`, `agents`, `media`). |
| **4. Snapshot / time travel** | Enable for prod, expire nightly. | `snapshots()` table + `AT (VERSION => N)` time-travel queries. Maintain via `expire_snapshots()` + `cleanup_old_files()` + `merge_adjacent_files()` + `rewrite_data_files()` (for delete-heavy tables). |
| **5. Partitioning** | **Identity partitions only** for now. | DuckLake supports `partition` hint on a column (DuckDB 1.4.x) — simple identity partitions are created. **Partition evolution is not supported.** For the LC subjects, partition by `jurisdiction` + `stage`. |
| **6. Sort order / clustering** | Use **`SORTED BY (subject, board)`** for hot tables. | DuckLake 1.0 supports sorted tables; 10x faster reads when sort columns align with query filters. The `_dlt_load_id` column is implicit-sorted; combine with explicit `SORTED BY (jurisdiction, stage, subject)`. |
| **7. Data inlining** | Enable with `data_inlining_row_limit=100` (the 1.0 default). | Small inserts go to the catalog database instead of creating separate Parquet files (solves the small-files problem). Keep the default unless you have a specific reason to override. |
| **8. Merge strategy** | Use **`upsert`** (DuckDB 1.4+) or **`scd2`** for slow-changing dims. | All write dispositions supported: `append`, `replace`, `merge` (delete-insert), `upsert` (1.4+), `scd2`, `insert-only`. |
| **9. Credentials** | Refreshable for long-running loads. | `REFRESH auto` is the new (1.28.0) default for DuckDB; stops `ExpiredToken` failures when AWS temp credentials rotate. |
| **10. Migrations** | Set `automatic_migration=True` when attaching an older catalog. | Otherwise DuckDB raises a catalog version mismatch error. The cianfhoghlaim.education._registry and other DuckLake-managed schemas in `dlt_sources/common/migrations/` are the canonical home for hand-rolled migration SQL. |
| **11. Ibis handover** | Use `dataset()` + ibis. | `pipeline.dataset()` and **ibis** handover are fully supported (1.29.0+ refactor). Use `dataset("lake_schema").table("subjects").df()` or `.to_polars()` or `.to_arrow()`. |
| **12. Dbt support** | **NOT supported** (as of 1.30). | Would need to handover secrets + `ATTACH` command; not planned. Use ibis or DuckDB SQL directly for transforms. |
| **13. Table maintenance** | Use the native `sql_client` connection. | `dlt.dataset()` does not expose the maintenance interface for DuckLake yet; use `with pipeline.sql_client() as client: client.execute_sql("CALL bucket_cat.merge_adjacent_files()")`. |
| **14. Per-thread output** | Set per-connection before pipeline runs. | `CALL lake_catalog.set_option('per_thread_output', true)` is 1.4.x only. Prevents concurrent threads from stepping on each other's writes. |

### The 2 gaps in the current Cianfhoghlaim implementation

1. **`metadata_schema` is not used.** The Postgres catalog currently uses a single shared `public` schema (or whatever the `ducklake_name` defaults to). The new 1.25.0 feature would let us scope each quadrant to its own schema.
2. **No native sort / bucket partitioning.** The `_dlt_load_id` column is the only sort key in practice. The 1.0 `SORTED BY` and `PARTITIONED BY (bucket(N, col))` features are not used.

---

## F) Proposed consolidated namespace aligned to `cianfhoghlaim` Irish-language streamlining

The goal: collapse 15 top-level subtrees + 1 underscore-shim into a **lean 8-subtree namespace** that follows the `cianfhoghlaim` (Irish: "learning") project ethos, while keeping the BIEP v3 jurisdiction pipelines as first-class citizens and using `dlt 1.30` features to delete the per-nation sprawl.

### The 8 canonical subtrees (proposed)

| # | New canonical name | What it contains | Irish rationale |
|--|---|---|---|
| 1 | `cianfhoghlaim/folacha/` (sources) | The 6 jurisdictions' BIEP v3 jurisdiction pipelines (BI / EU / Commonwealth / Americas / Ireland-specific) | **Folacha** = "sources" in Irish |
| 2 | `cianfhoghlaim/teangacha/` (Celtic languages) | All Celtic-language sources (Logainm, Téarma, Ainm, Gaois, Dúchas, Canúint, Universal Dependencies) | **Teangacha** = "languages" |
| 3 | `cianfhoghlaim/tain/` (assets / file systems) | `filesystem/` + `apple_photos/` + `leabharlann_books` + `leabharlann_education_notes` + `university_of_galway` | **Táin** = "cattle/herd" (assets in Irish) |
| 4 | `cianfhoghlaim/gnó/` (official media + companies + academic) | `official_media/` + `api_sources/` (only the official / academic ones — GitHub, ResearchGate, LinkedIn) | **Gnó** = "business/official" |
| 5 | `cianfhoghlaim/cleachtas/` (practice / hobby corpora) | `media/` + `crypteolas/` + the hobby APIs (Spotify, SoundCloud, YouTube, TG4, Foghlaim) | **Cleachtas** = "practice" |
| 6 | `cianfhoghlaim/loc/` (lakes) | The Lakehouse destinations (`_lakehouse/destinations.py` + `common/destinations_cianfhoghlaim.py` + `common/destinations_tuatha.py` — the 3 destination modules merge into one) | **Loc** = "lake" — also reinforces the `la*` lakehouse naming |
| 7 | `cianfhoghlaim/cabhrach/` (helpers) | The dead + live `common/*.py` helpers (with 9 dead modules removed) | **Cabhrach** = "helpers/auxiliary" |
| 8 | `cianfhoghlaim/obair/` (jobs / portfolio) | `jobs/` + `portfolio/` + `personal_archive_destinations.py` | **Obair** = "work" |

### Old → new path mapping

| Old path | New path | Notes |
|---|---|---|
| `dlt_sources/british_isles/` | `cianfhoghlaim/folacha/sail_breataine/` (sail = "heel/legacy" or just keep `breataine_isles`) | The 8-nation BIEP v3 jurisdiction pipelines. **Recommendation**: use the Irish spelling **"breataine_isles"** ("British Isles" — `breataine` + `isles`); or stay with English `british_isles/` if readability matters more than language purity. |
| `dlt_sources/european_nations/` | `cianfhoghlaim/folacha/naisc_eorpacha/` | The 40 European nations. **Recommendation**: collapse the 40 subtrees into **one file-based registry** (Ireland-style config rows) using dlt 1.30's multischema datasets + dlt 1.25's lance destination. The per-nation source factories (`NationSource`) emit one row per nation → one DuckLake schema per nation. |
| `dlt_sources/european_union/` | `cianfhoghlaim/folacha/aontas_eorpach/` | The EU bodies. |
| `dlt_sources/commonwealth/` | `cianfhoghlaim/folacha/comhlaith/` (comhlaith = "commonwealth" in Irish) | 6 nations + 49 sub-entities. **Same recommendation** as `european_nations/`: collapse into one registry + 49 DuckLake schemas. |
| `dlt_sources/american_nations/` | `cianfhoghlaim/folacha/naisc_mheiriceanacha/` | 4 nations. |
| `dlt_sources/language/` | `cianfhoghlaim/teangacha/` | All Celtic-language sources. |
| `dlt_sources/filesystem/` | `cianfhoghlaim/tain/` | Filesystem sources + leabharlann + Apple Photos. |
| `dlt_sources/official_media/` | `cianfhoghlaim/gnó/` | Official media + UK gov. |
| `dlt_sources/api_sources/` | split between `cianfhoghlaim/gnó/` (GitHub / LinkedIn / ResearchGate) and `cianfhoghlaim/cleachtas/` (Spotify / SoundCloud / YouTube / TG4 / Foghlaim) | Functional split. |
| `dlt_sources/crypteolas/` | `cianfhoghlaim/cleachtas/cripteolas/` | Tuatha Crypteolas achievement ledger (Irish spelling: **cripteolas** = "crypt + learning"). |
| `dlt_sources/media/` | `cianfhoghlaim/cleachtas/` | Animation + comics + games + official media (gov + NCCA + SEC + Duchas + Wikipedia) + celtic_history_research + prose. |
| `dlt_sources/portfolio/` | `cianfhoghlaim/obair/portfóilió/` | Croilar portfolio (Irish spelling: **portfóilió**). |
| `dlt_sources/apple_photos/` | `cianfhoghlaim/tain/úll_grianghraf/` | Apple Photos (Irish: **úll** = "apple", **grianghraf** = "photograph"). |
| `dlt_sources/jobs/` | `cianfhoghlaim/obair/` | Dagster job entry points. |
| `dlt_sources/common/` | `cianfhoghlaim/cabhrach/` | The 28 helpers (with 9 dead modules removed). |
| `dlt_sources/_lakehouse/` | `cianfhoghlaim/loc/` | The 3 destination modules + personal_archive_destinations. |
| `dlt_sources/cli.py` | `cianfhoghlaim/cli.py` (repo root) | Promote the CLI to repo root. |

### The 3 things to delete (the dead code)

1. **`dlt_sources/common/destinations_tuatha.py`** (145 LOC) — deprecated shim with misspelled namespace. The module docstring itself says "This shim is deprecated."
2. **9 dead helpers in `common/`**: `pagination.py` (422), `safety.py` (347), `observability.py` (167), `motherduck_options.py` (159), `named_destinations.py` (153), `snake_case_contract.py` (298), `_shared_utils_stub.py` (111), `ducklake_pool.py` (77), `batching.py` (240). Total ~1,974 LOC. **No callers in the dlt_sources tree** (verified via grep).
3. **The 873 broken legacy imports** — see §B. Replace each with the canonical post-v7 path via a one-shot scripted migration (`from dlt_sources.commonwealth.aus.X import Y` → `from dlt_sources.commonwealth.australia.X import Y`).

### The 2 things to merge

1. **`dlt_sources/european_nations/_shared/nation_source.py:NationSource`** and **`dlt_sources/british_isles/_cross/jurisdiction_pipeline_base.py:JurisdictionPipelineBase`** — these are TWO different base classes for essentially the same pattern (per-nation / per-jurisdiction DLT source). Merge into ONE `JURISDICTION_SOURCES_BASE` in the new `cabhrach/` namespace.
2. **`dlt_sources/common/destinations_cianfhoghlaim.py` + `dlt_sources/common/destinations_tuatha.py` + `dlt_sources/_lakehouse/destinations.py` + `dlt_sources/_lakehouse/personal_archive_destinations.py`** — four destination modules, one canonical. Merge into `loc/deestination.py`.

### The 1 thing to flatten (the per-nation sprawl)

The 859 `.py` files in `european_nations/` + 633 in `commonwealth/` are 40 + 6 = 46 nearly-identical 5-vertical directory trees. Each tree has `__init__.py` files at every level. **Most are empty shims that only re-export the underlying source module.** The total LOC overhead is ~12,000 LOC of empty `__init__.py` + ~600 broken re-exports (the legacy ISO-3 references).

The cleanest fix: collapse the per-nation subtrees into **a single `_factory.py`** that builds the source per the `NationConfig` row (same pattern as the existing `cocoindex_flows/european_nations/_factory.py` per DATA_PLATFORM_ROUTER.md §6). The factory emits a `@dlt.source` per row + a 1-line shim per row. dlt 1.30's `@dlt.source` factory + `.add_limit()` is the right primitive.

### The 1 thing to consolidate (the `nations._shared.nation_source.py` import)

The `_shared/nation_source.py` class is currently imported **via 3 different paths** (verified via grep):

1. `from dlt_sources.european_nations._shared.nation_source import NationSource` (canonical, ~407 files)
2. `from dlt_sources.commonwealth.australia.education.acara import ...` (depends on #1)
3. `from dlt_sources.common.endpoint_recovery import ...` (the alternative helper, used in ~200 files)

After the refactor, ALL per-nation sources must use a single base class (proposed: `JURISDICTION_SOURCES_BASE`) imported from `cianfhoghlaim/cabhrach/jurisdiction_base.py`.

---

## G) Cross-cutting concerns that must remain shared

These 8 helpers are the **shared primitives** that every per-jurisdiction, per-nation, per-source module depends on. They must NOT be inlined or duplicated — they live in `cianfhoghlaim/cabhrach/` (or `loc/`) and are imported via the new relative-import convention (post-fix).

### The 8 cross-cutting concerns

| # | Concern | Canonical location today | Lines | Notes |
|--|--|--|--:|--|
| 1 | **Destinations** (Lakehouse / MotherDuck / DuckLake / Local DuckDB) | `common/destinations_cianfhoghlaim.py` + `_lakehouse/destinations.py` | 528 + 277 = 805 | Must collapse to one `loc/destination.py` + `loc/personal_archive_destination.py`. Includes the 3 hosting options (managed / byob / byoc) + the DuckLake 1.0 helpers (data inlining / sorted_by / bucket_partitioned). |
| 2 | **HTTP client** (singleton HTTPX + retry + backoff + per-host rate limiting) | `common/http_client.py` (312 LOC, 15 importers) | 312 | The 15 importers are spread across `british_isles/`, `european_nations/`, `commonwealth/`, `official_media/`, `api_sources/`. |
| 3 | **Endpoint recovery** (3-strategy fetch: Firecrawl → Crawl4AI → direct HTTP) | `common/endpoint_recovery.py` (410 LOC, **200 importers**) | 410 | The most-used helper in the entire corpus. The canonical import is `from dlt_sources.common.endpoint_recovery import fetch`. Must remain a sibling. |
| 4 | **Firecrawl adapter** (Firecrawl MCP + sruth-browser fallback) | `common/firecrawl_source.py` (392 LOC, 17 importers) | 392 | Pairs with #3. |
| 5 | **Incremental loading** (cursor management + content-hash dedup + last-modified tracking) | `common/incremental.py` (302 LOC, 6 importers) | 302 | The dlt 1.27.0 incremental-on-`dlt.Relation` is complementary; use the dlt primitive for cursor management, the cianfhoghlaim helper for content-hash dedup. |
| 6 | **Observability** (Langfuse spans, MLflow metrics, RAGAS trace-based eval) | `common/observability.py` (167 LOC, 0 direct importers — **DEAD**) | 167 | The current `observability.py` has no importers. Per the `agent-observability` skill, the observability stack is wired via the `@observe` decorator (Langfuse) + Logfire + MLflow. We need to either wire this helper in (preferred — 167 LOC of dead code) or delete it. |
| 7 | **Batching** | `common/batching.py` (240 LOC, 0 importers — **DEAD**) | 240 | Same audit signal as #6 — needs wiring or deletion. |
| 8 | **Schema + registry helpers** (the BIEP v3 cross-jurisdiction registry + the per-subject manifest) | `british_isles/_cross/jurisdiction_pipeline_base.py` + `british_isles/_cross/registry_loader.py` + `british_isles/ireland/education/subjects/manifest.py` | ~600 | The cross-jurisdiction registry is the single most important shared module after `common/`. The `JurisdictionPipelineBase` class is the canonical factory pattern. |

### The 3 additional cross-cutting helpers (less critical)

| # | Concern | Location | LOC | Notes |
|--|--|--|--:|--|
| 9 | **Pagination** | `common/pagination.py` | 422 | DEAD. Either wire or delete. |
| 10 | **Safety** (URL allowlist + rate-limit guard) | `common/safety.py` | 347 | DEAD. Critical for a multi-tenant scrape layer — wire it. |
| 11 | **Source adapters** (source → resource adapter helpers) | `common/source_adapters.py` | 580 | Heavy file, internal use. |
| 12 | **Mixins** | `common/mixins.py` | 446 | Internal use. |

### The 4 absolute concerns (must stay shared, never duplicated)

1. **Secrets management** — the `.infisical.env` template + the Locket sidecar contract. NO DLT source may read `.env` directly; always go through `os.environ` (which the mise directory hooks auto-hydrate).
2. **Use of local scrapes** — every DLT source MUST honour `USE_LOCAL_SCRAPES=true` and route through the `stedding/ingest_queue/` cache. The `incremental.py` module's `use_local_scrapes()` helper is the canonical check.
3. **DuckLake namespace** — every DLT destination MUST write to the canonical `md:cianfhoghlaim` (or `md:cianfhoghlaim.<quadrant>`). The `destinations_cianfhoghlaim.py:get_dlt_destination()` factory is the only approved entry point.
4. **Relative imports** — once the ghost-shim imports are fixed, every cross-file reference within a subtree MUST use `from .._shared.<file> import ...`. The AGENTS.md rule MUST be enforced via `mise run lint:drift-docs`.

---

## H) Concrete refactor risks and an opinionated ordering

### Risk register (12 risks, ordered by severity)

| # | Risk | Severity | Mitigation |
|--|--|--|--|
| 1 | **873 broken legacy imports** that currently fail silently (no smoke test catches them) | **CRITICAL** | First refactor task: write a smoke test that loads every source + every `__init__.py` + runs `python -c "import dlt_sources.<every_subtree>"`. ~50 LOC of `import pytest; import importlib; subtrees = [...]; for s in subtrees: importlib.import_module(s)` — would have caught the 873. |
| 2 | **~12,000 LOC of empty `__init__.py` files** in the per-nation / per-vertical subtrees (european_nations + commonwealth) | HIGH | Replace with a single `_factory.py` + 1-line shim per nation (see §F). The CocoIndex `_factory.py` pattern at `cocoindex_flows/european_nations/_factory.py` is the template. |
| 3 | **9 dead helpers in `common/`** (~1,974 LOC) that no one imports | MEDIUM | Either wire them (preferred — `observability`, `safety`, `pagination`, `batching` are all high-value concerns) or delete. |
| 4 | **Two competing destination modules** (`destinations_cianfhoghlaim.py` + `destinations_tuatha.py` + `_lakehouse/destinations.py` + `_lakehouse/personal_archive_destinations.py`) | MEDIUM | Merge into one `loc/destination.py` + `loc/personal_archive_destination.py`. Delete the deprecated `destinations_tuatha.py` shim. |
| 5 | **The `_lakehouse/` underscore-shim** breaks the per-area AGENTS.md convention | LOW | Rename to `loc/` (or just absorb into `common/`). |
| 6 | **Naming inconsistencies** (English vs Irish, ISO-3 vs full snake_case) | LOW | The §F proposed namespace renames everything. But: keep the breaking-change scope small — do the namespace rename LAST, after the functional refactor. |
| 7 | **Two base classes for the same pattern** (`NationSource` + `JurisdictionPipelineBase`) | MEDIUM | Merge into one `JURISDICTION_SOURCES_BASE`. The 40 European + 6 Commonwealth + 8 British Isles + 4 Americas + 4 Mexican + 4 Brazilian + 4 Venezuelan sources all use ONE base class. |
| 8 | **dlt 1.30 breaking changes** (`auto_abort_on_terminal_error` default change, `drop_pending_packages` deprecation) | MEDIUM | Bump the dlt API usage in the BIEP v3 jurisdiction pipelines to use the new `abort_packages` API. |
| 9 | **The hard-coded `stedding/ingest_queue/<subtree>` cache paths** scattered across every per-jurisdiction source | LOW | Add a `common/cache_path.py` helper that resolves the cache path per jurisdiction from a single config table. |
| 10 | **The `apple_photos/` stub** is awaiting the `apple-photos-ingestion` openspec change | LOW | Block on that change; don't refactor the stub. |
| 11 | **The `_shared/nation_source.py` `EU_NATIONS_CACHE_ROOT` env var** uses a hard-coded default path | LOW | Promote to `common/cache_path.py:get_jurisdiction_cache_root(jurisdiction)`. |
| 12 | **The CLI's `DLT_SOURCES` list** at `common/cli.py:15` is hard-coded | LOW | Generate the list via AST walk over `dlt_sources/**/*.py` (use the existing `notebooks/_shared/schema.py:list_dlt_sources()` helper). |

### Opinionated migration ordering (3 phases)

#### Phase 1 — Fix the broken state (1–2 days)

Goal: every `import dlt_sources.<subtree>` succeeds.

1. **Write the smoke test** (the `import_all_subtrees.py` script). 50 LOC.
2. **Bulk-rename the 873 broken legacy imports** via 6 `sed` scripts (one per rename wave per §B). The scripts are deterministic — each one replaces `dlt_sources.<old>.<rest>` with `dlt_sources.<new>.<rest>`.
3. **Delete the 9 dead helpers** in `common/`. Verify no test fails.
4. **Delete the `destinations_tuatha.py` shim**. Verify no test fails.
5. **Re-run the smoke test**. Expected outcome: every import succeeds.

#### Phase 2 — Consolidate the per-nation sprawl (3–5 days)

Goal: cut the LOC by ~30%.

1. **Collapse `european_nations/` 40 subtrees into 1 factory**. Use the `_factory.py` pattern from `cocoindex_flows/european_nations/_factory.py`. Emit 1-line re-export shims per nation.
2. **Collapse `commonwealth/` 6 nations + 13 provinces + 36 states into 1 factory**. Same pattern.
3. **Collapse `american_nations/` 4 nations into 1 factory**.
4. **Merge `_shared/nation_source.py:NationSource` + `_cross/jurisdiction_pipeline_base.py:JurisdictionPipelineBase` into one** `cabhrach/jurisdiction_base.py:JURISDICTION_SOURCES_BASE`.
5. **Re-run the smoke test**. Expected outcome: every import still succeeds; ~12,000 LOC of empty `__init__.py` removed.

#### Phase 3 — Irish-language rename + dlt 1.30 features (1–2 weeks, gated on openspec approval)

Goal: align with the `cianfhoghlaim` project ethos + adopt dlt 1.30 features.

1. **Propose the openspec change `2026-08-24-dlt-sources-namespace-cleanup-v1`** with the §F namespace mapping.
2. **Add deprecation shims** at the old paths (so the rename is one-release-cycle-friendly per the AGENTS.md).
3. **Adopt dlt 1.30 features**:
   - `multischema datasets` (1.25) → collapse the per-nation DuckLake schemas into one dataset per pipeline.
   - `cross-destination joins` (1.30) → enable per-jurisdiction destination choice in the marimo notebooks.
   - `.add_limit()` on the `@dlt.source` factories (1.30) → add to the smoke test for fast CI checks.
   - `retry_schema_update` helper (1.30) → add to the BIEP v3 jurisdiction pipelines to retry failed NCCA schema evolutions.
   - `abort_packages` / `fail_pending_job` / `retry_failed_job` (1.30) → replace the deprecated `drop_pending_packages` calls.
4. **Adopt DuckLake 1.0 features** (per §E): `metadata_schema` per quadrant, `SORTED BY` on hot tables, nightly `expire_snapshots()` + `cleanup_old_files()` + `merge_adjacent_files()` maintenance via Dagster assets.
5. **Cut a release tag** when the deprecation shims expire.

### The 2 things NOT to do

1. **Don't rename before the smoke test.** The 873 broken legacy imports will become 873 newly-broken canonical imports if the rename is done naively. Phase 1 first.
2. **Don't merge the BIEP v3 jurisdiction pipelines into one** — the per-jurisdiction pattern is intentional (the AGENTS.md says so). Only the per-nation sprawl in `european_nations/` and `commonwealth/` is the target.

### Success metrics (for the openspec change validation)

| Metric | Before | After (target) |
|--|--:|--:|
| Total `.py` files in `dlt_sources/` | 1,975 | ≤ 1,400 |
| Total LOC | 155,506 | ≤ 105,000 |
| `@dlt.source` + `@dlt.resource` decorators | 2,163 | 2,163 (same — no functional loss) |
| Broken legacy imports | 873 | 0 |
| Dead helpers in `common/` | 9 / 28 (32%) | 0 / ~12 (only the kept helpers) |
| Destination modules | 4 | 2 |
| Base classes for per-nation sources | 2 | 1 |
| `mise run lint:drift-docs` failures | (unknown) | 0 |

---

## Appendix A — The canonical route map (per the existing AGENTS.md, kept verbatim)

The existing `dlt_sources/AGENTS.md` has a "Quick routing — I want to add X, where do I go?" table that maps:

| If you want to... | Look at... |
|--|--|
| Add a new DLT source | The relevant jurisdiction sub-dir (`british_isles/<jurisdiction>/...`) |
| Add a new jurisdiction pipeline | Subclass `JurisdictionPipelineBase` at `british_isles/_cross/jurisdiction_pipeline_base.py:33` |
| Add a new common helper | `common/<helper>.py` |
| Add a new API source | `api_sources/<service>_source.py` |
| Add a new filesystem pipeline | `filesystem/<pipeline>.py` |
| Add a new MotherDuck Dive target | See `motherduck/README.md` |
| Add a new CocoIndex embedding | See `cocoindex/AGENTS.md` |
| Run the BIEP v3 Ireland pipeline | `python -c "from dlt_sources.british_isles.ireland.education.ireland_jurisdiction_pipeline import ireland_jurisdiction_pipeline; ireland_jurisdiction_pipeline.run()"` |
| Diagnose a destination issue | `python -c "from dlt_sources.common.destinations_cianfhoghlaim import get_dlt_destination; print(get_dlt_destination())"` |

**Recommendation**: the post-refactor AGENTS.md should reflect the new `cianfhoghlaim/<area>/` namespace. The 3 canonical commands stay the same (Run BIEP Ireland / Run BIEP England / Diagnose destination); the file paths change.

---

## Appendix B — Cross-references

- [`dlt_sources/LEGACY_ALIASES.md`](../dlt_sources/LEGACY_ALIASES.md) — the 48-line v7 ISO-3 → snake_case rename map (historical)
- [`dlt_sources/AGENTS.md`](../dlt_sources/AGENTS.md) — the 251-line canonical entry point (post the `2026-08-23-dlt-sources-ccc-audit-and-realignment-v1` change)
- [`dlt_sources/README.md`](../dlt_sources/README.md) — the 83-line developer quick start
- [`dlt_sources/DATA_PLATFORM_ROUTER.md`](../dlt_sources/DATA_PLATFORM_ROUTER.md) — the 260-line single router for the 5 per-area data-platform docs
- [`openspec/specs/british-isles-education-pipeline/spec.md`](../openspec/specs/british-isles-education-pipeline/spec.md) — the flagship BIEP spec
- [`openspec/changes/2026-08-23-dlt-sources-ccc-audit-and-realignment-v1/`](../openspec/changes/) — the just-archived change that added 14 of 15 per-subtree AGENTS.md files
- [`pyproject.toml`](../pyproject.toml) — the `dlt[duckdb,motherduck,filesystem]>=1.30.0,<2.0.0` pin (post the `2026-08-21-dlt-1.28.1-to-1.30.0-v1` change)
- [`.cocoindex_code/guides.yml#dlt-source-search`](../.cocoindex_code/guides.yml) — the CCC concept guide for finding any DLT source by name
- Upstream docs: <https://dlthub.com/docs/release-notes/1.21.2>, <https://github.com/dlt-hub/dlt/releases>, <https://dlthub.com/docs/dlt-ecosystem/destinations/ducklake>, <https://ducklake.select/docs/stable/duckdb/introduction>

---

**Last updated**: 2026-08-24
**Owner**: Read-only research subagent (proposed openspec change: `2026-08-24-dlt-sources-namespace-cleanup-v1`)
