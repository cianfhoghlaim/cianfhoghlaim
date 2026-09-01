# `dlt_sources/` — v2 Plan: Multi-Repo Scaffold for the `cianfhoghlaim` Family

**Date**: 2026-08-24 (v2 supersedes v1)
**Author**: Read-only research subagent → build subagent
**Scope**: The 8-repo topology (cianfhoghlaim + 7 sister / core repos) and how `dlt_sources/` is reorganised to flow across them.
**Companion openspec change**: [`2026-08-24-dlt-sources-to-multi-repo-scaffold-v1`](../changes/2026-08-24-dlt-sources-to-multi-repo-scaffold-v1/)
**Companion spec**: [`cianfhoghlaim-dlt-sources-multi-repo`](../changes/2026-08-24-dlt-sources-to-multi-repo-scaffold-v1/specs/cianfhoghlaim-dlt-sources-multi-repo/spec.md)

---

## 0. Changelog vs v1

| v1 (rejected) | v2 (this plan) | Reason |
|---|---|---|
| Elaborate Irish per-folder names (`dlt_sources/folacha/`, `/teangacha/`, `/loc/`, `/cabhrach/`, `/obair/`, `/gnó/`, `/cleachtas/`, `/tain/`) | **English + clear folder names inside each repo** (`dlt_sources/`, `british_isles/`, `language/`, `_lakehouse/`, `common/`, etc.) | Per user: "no, we dont want to use elaborate irish naming for directory structure." Irish names go ONLY on repo roots. |
| Single comprehensive rename of all 15 subtrees | **Per-domain carve-out only** — cianfhoghlaim's existing tree stays put; only the moved subtrees get renamed | Per user: "this is something we wont be doing immediately and those repositories need to remain self-sufficient for now" |
| 9-repo topology assumption (cianfhoghlaim + 8 sisters, all carved out by Phase 5) | **3-repo active topology** now (cianfhoghlaim + tuatha + ciandlíthe), 8-repo future topology in Phases 3–4, **bonneagar + meaisinfhoghlaim hiving deferred past 12-month horizon with no ETA set** (per user Q4) | Per user: "later" |
| Two repos named `cianceiltis` and `cianchosaint` | **Spelling corrected to `ciancheiltis`** throughout | Per user Q2: "yes but it is called ciancheiltis not cianceiltis" |
| Single spoken-of carve rule for `language/` | **Bilingual educational rule**: Irish-language education resources stay in cianfhoghlaim (LC Gaeilge + WJEC Welsh-medium + UoG bilingual + duchas-as-curriculum reference); Irish-language datasets (gaois, duchas.ie, tearma, logainm, ainm) + non-educational Celtic-language pipelines go to ciancheiltis | Per user Q3 + Q5: "university of galway is an educational entity, such typically bilingual things … remain in cianfhoghlaim" |
| Cascade contracts vague | **6 explicit cascade contracts** (openspec / dlt-source / schema / destination / observability / knowledge-graph) with per-direction detail | Per user Q3: "a,b" (both daily sync + per-PR reusable workflow) |
| Stack mentions partial | **12-component stack inventory** with per-component reuse role + the skill that already implements it | Pulls in the full extent of the existing mise + openspec + Cognee + CCC + Infisical + Locket + Dagster + CocoIndex + Firecrawl + Langfuse + MLflow + MotherDuck + DuckLake + TanStack + CopilotKit stack |

---

## A. The 8-Repo Topology (today → Phase 4)

The plan covers an **8-repo topology**. Of these:
- 2 are **active today**: `cianfhoghlaim` (main, this repo) + `tuatha` (already carved to `/Users/cianmacandeisigh/dev/cianfhoghlaim/tuatha/` per `2026-08-25-tuatha-british-isles-mmo-consolidation-v1`).
- 2 are **3-month active**: `ciandlíthe` (BI legal) + `cianchosaint` (BI law-enforcement / defence).
- 2 are **6–12-month active**: `cianleighis` (medicine) + `ciancheiltis` (Irish + Celtic languages).
- 2 are **deferred past the 12-month horizon, no ETA set**: `bonneagar` (infra core) + `meaisinfhoghlaim` (ML core).

### Per-repo ownership table

| # | Repo | Status | Owns | Carved at |
|---|---|---|---|---|
| 1 | **`cianfhoghlaim`** | Active (this) | `common/` (cross-cutting hub), `_lakehouse/` (renamed to `lakehouse/`), `jobs/`, `british_isles/_cross/`, `british_isles/ireland/education/` (the flagship), `filesystem/` (generic cross-cutting), `api_sources/` (academic subset), `apple_photos/` (stub), `portfolio/` (stub). Context data: EU English-Irish alignment subset (`eurostat`, `eur_lex_celvic`, `publications_office`). | Today |
| 2 | **`tuatha`** | Already carved (DONE, per `2026-08-25-tuatha-british-isles-mmo-consolidation-v1`) | 8 NCCA subject agents + 40 per-subject tools + 3 educational agents + 4 BIEP hackathon features + 1 media_intel pipeline + game-asset generators + the `tuatha/dlt/` 40 source-per-subject surface | 2026-08-25 |
| 3 | **`ciandlíthe`** | Scaffold + first carve-out | BI legal system: WRC + UK statute + courts + statutory-law registry (BI jurisdictions only). Context data: EU statute (`eur_lex` general), Commonwealth law, European BI legal jurisdictions. **Court-facing procedural rules** per user-confirmed split. | Phase 3 (3–6 months) |
| 4 | **`cianchosaint`** | Scaffold + first carve-out | BI law enforcement + civil protection + defence. **Evidence-collection for law-enforcement purposes** per user-confirmed split. | Phase 3 (3–6 months) |
| 5 | **`cianleighis`** | Future | **Medical-malpractice law** + clinical + pharma per jurisdiction + EHDS health data space. Context data: Commonwealth medicine, European context medicine. | Phase 4 (6–12 months) |
| 6 | **`ciancheiltis`** | Future | **Pure Irish-language datasets** (gaois, duchas.ie, tearma, logainm, ainm, canuint, UD/ud_irish) + non-educational Celtic-language pipelines (Welsh, Scottish Gaelic, Breton, Manx, Cornish) + CLARIN-UK alignment (future). Does NOT own LC Gaeilge the educational subject (stays in cianfhoghlaim/tuatha). | Phase 4 (6–12 months) |
| 7 | **`bonneagar`** | Deferred past 12-month horizon | 89 Docker Compose stacks at `bonneagar/stacks/` + the Locket sidecar + the Infisical + mise contract + Pangolin resources. Currently in this repo at `bonneagar/`. | No ETA set (Phase 5+ deferred) |
| 8 | **`meaisinfhoghlaim`** | Deferred past 12-month horizon | 12-agent fleet + Langfuse + Logfire + MLflow + Ragas + fine-tuning + the centralized-model-registry + agent-observability stack. | No ETA set (Phase 5+ deferred) |

### Convention: which repo owns which sub-tree of `dlt_sources/`

```
dlt_sources/                                                            Owner
├── common/                                          ───→ cianfhoghlaim (Phase 0: stays)
│   ├── destinations_cianfhoghlaim.py
│   ├── endpoint_recovery.py                 (200 importers)
│   ├── firecrawl_source.py                  (17 importers)
│   ├── http_client.py                       (15 importers)
│   ├── incremental.py                       (6 importers)
│   ├── observability.py, batching.py,
│   │   safety.py, pagination.py,
│   │   motherduck_options.py, ...           (currently dead; Phase 0: wire or delete)
│   └── ...                                          (28 helpers total; 9 dead)
│
├── _lakehouse/                                         ───→ cianfhoghlaim (Phase 0: stays, rename → lakehouse/)
│   ├── destinations.py                               Phase 5: this one's possible hiving to bonneagar/
│   └── personal_archive_destinations.py
│
├── jobs/                                              ───→ cianfhoghlaim (Phase 0: stays)
│   └── government_circulars_job.py
│
├── apple_photos/                                      ───→ cianfhoghlaim (Phase 0: stays — stub)
├── portfolio/                                         ───→ cianfhoghlaim (Phase 0: stays — stub)
│
├── filesystem/                                        ───→ cianfhoghlaim (Phase 0: stays)
│   ├── zotero.py
│   ├── leave_cert.py
│   ├── takeout_v1.py
│   ├── gemini_corpus_source.py
│   ├── university_of_galway.py             ←── STAYS (UoG = educational)
│   ├── uog_personal_archive.py             ←── STAYS (UoG personal = educational)
│   ├── leabharlann_books.py                 ←── STAYS (cross-language UoG bibliography = educational)
│   ├── lc6_cross_check.py
│   ├── previews.py
│   └── email_inbox.py
│
├── api_sources/                                       ───→ cianfhoghlaim (Phase 0: stays; academic subset)
│   ├── spotify*.py, soundcloud*.py,
│   │   youtube*.py                                  Phase 5: possible carve to meaisinfhoghlaim/
│   ├── github.py, linkedin.py, researchgate.py
│   ├── tg4_player_shows.py                         (Phase 5: → tuatha for game-asset derivation)
│   ├── foghlaim_lessons.py                         (Phase 5: → tuatha for lesson derivation)
│   └── leabharlann_education_notes.py              ←── STAYS (UoG bilingual = educational)
│
├── british_isles/                                     ───→ cianfhoghlaim (Phase 0: stays)
│   ├── _cross/                                  ───→ cianfhoghlaim (the BIEP v3 jurisdiction registry)
│   │   ├── jurisdiction_pipeline_base.py            (canonical base class — shared contract)
│   │   ├── registry_api.py
│   │   ├── registry_loader.py
│   │   ├── connection.py
│   │   └── ...
│   ├── ireland/
│   │   ├── _cross/                              ───→ cianfhoghlaim
│   │   ├── education/
│   │   │   ├── subjects/
│   │   │   │   ├── gaeilge.py + ...             ←── STAYS in cianfhoghlaim (LC Gaeilge = educational)
│   │   │   │   ├── mathematics.py
│   │   │   │   ├── english.py
│   │   │   │   └── ...
│   │   │   ├── junior_cycle_cbas/   _factory.py  ───→ cianfhoghlaim
│   │   │   ├── junior_cycle_subjects/  _factory.py ───→ cianfhoghlaim
│   │   │   ├── university/                       ───→ cianfhoghlaim
│   │   │   ├── exam_papers/
│   │   │   ├── official_docs/
│   │   │   └── personal_archive/                 ───→ cianfhoghlaim
│   │   ├── law/                                       Phase 3: → ciandlíthe (per-vertical)
│   │   └── medicine/                                   Phase 4: → cianleighis (per-vertical)
│   ├── england/, scotland/, wales/, northern_ireland/, jersey/, guernsey/, isle_of_man/
│   │   ├── education/                              ───→ cianfhoghlaim (BI national CURRICULA)
│   │   │   ├── (5 jurisdiction × 3 boards × 2 levels)
│   │   │   ├── subjects/
│   │   │   │   └── english/  (WJEC Welsh-medium = bilingual, stays)
│   │   ├── law/                                       Phase 3: → ciandlíthe (BI jurisdiction law)
│   │   ├── medicine/                                   Phase 4: → cianleighis
│   │   └── law_enforcement/                            Phase 3: → cianchosaint (new vertical)
│
├── european_union/                                    ───→ cianfhoghlaim (Phase 0: stays, reduced)
│   ├── eurostat/                                    ───→ cianfhoghlaim (BI-stat context)
│   ├── eur_lex_celvic/                              ───→ cianfhoghlaim (English-Irish alignment)
│   ├── publications_office/                         ───→ cianfhoghlaim (English-Irish alignment)
│   ├── eur_lex/                                         Phase 3: → ciandlíthe (statute, BI-context)
│   ├── ecdc/                                            Phase 4: → cianleighis
│   ├── ema/                                             Phase 4: → cianleighis
│   ├── ehds/                                            Phase 4: → cianleighis
│   └── (Parliament, Council, Commission, Eurydice,
│      CEDEFOP)                                          Phase 3: → ciandlíthe or ciandlithe-context
│
├── european_nations/                                  ───→ cianfhoghlaim (Phase 0: stays, context)
│   ├── _shared/nation_source.py                      (Phase 1: factory consolidates)
│   ├── albania/, austria/, ..., united_kingdom/, wales/
│   │   ├── education/                                ───→ cianfhoghlaim (context data)
│   │   ├── government/
│   │   ├── statistics/
│   │   ├── law/                                          Phase 3: → ciandlíthe (CONTEXT data — lower priority)
│   │   └── medicine/                                      Phase 4: → cianleighis (CONTEXT data)
│   ├── (40 nations total)                                  Phase 5: this whole subtree demoted to "context" reads only
│   └── united_kingdom/                                ───→ cianfhoghlaim (special; BI + EU member)
│
├── commonwealth/                                      ───→ cianfhoghlaim (Phase 0: stays, context)
│   ├── _shared/nation_source.py
│   ├── australia/, canada/, india/, new_zealand/,
│   │   nigeria/, south_africa/, official/
│   │   ├── education/                                ───→ cianfhoghlaim
│   │   ├── government/
│   │   ├── statistics/
│   │   ├── law/                                          Phase 3: → ciandlíthe (CONTEXT data)
│   │   └── medicine/                                      Phase 4: → cianleighis (CONTEXT data)
│   ├── canada/provinces/                             ───→ cianfhoghlaim
│   └── nigeria/states/                               ───→ cianfhoghlaim
│
├── american_nations/                                  ───→ cianfhoghlaim (Phase 0: stays, context)
│   ├── _shared/nation_source.py
│   ├── united_states/, brazil/, mexico/, venezuela/
│   │   ├── law/                                          Phase 3: → ciandlíthe (CONTEXT data — lowest priority)
│   │   └── medicine/                                      Phase 4: → cianleighis (CONTEXT data — lowest priority)
│   └── united_states/us_ca/                          ───→ cianfhoghlaim
│
├── language/                                              Phase 4: → ciancheiltis (DURING the carve-out)
│   ├── tearma.py + helpers                           ───→ ciancheiltis   (pure Irish-language dataset)
│   ├── logainm.py                                    ───→ ciancheiltis
│   ├── ainm.py                                       ───→ ciancheiltis
│   ├── gaois.py + helpers                            ───→ ciancheiltis   (pure Irish-language dataset)
│   ├── duchas.py + helpers                           ───→ ciancheiltis   (pure Irish-language dataset)
│   ├── duchas_images.py + helpers                    ───→ ciancheiltis
│   ├── canuint.py + 5 submodules                     ───→ ciancheiltis
│   ├── heritage.py, hidden_heritages.py              ───→ ciancheiltis   (heritage)
│   ├── local_documents_by_subject.py,                ───→ ciancheiltis
│   │   local_education_documents.py
│   ├── local_education_documents.py                  ───→ ciancheiltis
│   └── UD/                                           ───→ ciancheiltis (Universal Dependencies / Celtic)
│       ├── ud_irish (canonical)                      ───→ ciancheiltis (canonical owner)
│       │                                                  cianfhoghlaim/tuatha/subjects/gaeilge.py
│       │                                                  references it via `ciar://ciancheiltis/datasets/ud_irish@v<N>`
│       └── (ud_welsh, ud_scots, ud_breton,
│          ud_manx, ud_cornish)                       ───→ ciancheiltis
│
├── media/                                                  Phase 4: split between tuatha + ciancheiltis
│   ├── animation/, comics/, games/                   ───→ tuatha (game-asset-relevant)
│   ├── official/ (gov + NCCA + SEC + duchas_wikipedia)
│   │   ├── duchas_wikipedia                              → split: duchas-as-dataset → ciancheiltis
│   │   └── (rest)                                    ───→ tuatha
│   ├── celtic_history_research/                      ───→ ciancheiltis (Celtic heritage)
│   └── prose/, wheel_of_time/                        ───→ tuatha
│
├── crypteolas/                                            Phase 4: → tuatha (already conceptually there)
└── (9 dead helpers in common/)                        Phase 0: delete
```

---

## B. The strict bilingual-educational carve rule (the rule that resolves every grey area)

The user-confirmed 4-element carve rule (per Q3 + Q5):

> **If a sub-tree is a primary CURATED CURRICULUM for an Irish or British/Celtic-nation educational entity (NCCA / SQA / WJEC / CCEA / IoM / Jersey / Guernsey / UoG / NUI), the sub-tree stays in cianfhoghlaim. If it is a primary IRISH-LANGUAGE-ONLY or CELTIC-LANGUAGE-ONLY DATASET (Duchas, Gaois, Téarma, Logainm, Ainm, Canúint, UD/Irish, UD/Welsh, UD/Scots-Gaelic, UD/Breton, UD/Manx, UD/Cornish), and is not consumed by the LC Gaeilge / WJEC Welsh-medium curricula as source-of-truth curriculum, it moves to ciancheiltis. Cross-language library catalogues that link to UoG module reading lists + LC Gaeilge + WJEC Welsh-medium stay in cianfhoghlaim because they are bilingual + educational.**

This rule resolves 7 grey-area files (see appendix A for the per-file carve table).

---

## C. Phase Plan (0–12+ months)

> **Phases 0 and 1 execute today in this repo (cianfhoghlaim). Phase 2 scaffolds the cross-repo automation. Phases 3 and 4 carve the first 4 sister repos. Phase 5+ deferred past the 12-month horizon with no ETA set.**

### Phase 0 — Strengthen the self-sufficient state (now → 2 weeks)

**Goal**: every `import dlt_sources.<subtree>` succeeds in cianfhoghlaim. No file moves. Internal cleanup + dlt 1.30 + DuckLake 1.0 + Cognee population.

1. **Smoke test every `dlt_sources/<subtree>` import** — write `tests/dlt/test_imports.py` with one `importlib.import_module(dlt_sources.<subtree>)` per subtree. Reference run via the new `mise run dlt:smoke-all`.
2. **Bulk-fix the 873 broken legacy imports** via 6 deterministic `sed` one-liners (one per ISO-3 → snake_case rename wave). No openspec change needed; add a `# noqa` shim wrapper at the new module path for any backward-compat callers.
3. **Delete 9 dead helpers** in `common/` (~1,974 LOC): `pagination.py`, `safety.py`, `observability.py`, `motherduck_options.py`, `named_destinations.py`, `snake_case_contract.py`, `_shared_utils_stub.py`, `ducklake_pool.py`, `batching.py`.
4. **Delete `common/destinations_tuatha.py`** (deprecated shim; its own docstring admits it; namespace is misspelled `"tuath"` not `"tuatha"`).
5. **Rename `_lakehouse/` → `lakehouse/`** (drop the leading underscore so it follows the per-area convention in `DATA_PLATFORM_ROUTER.md`).
6. **Adopt dlt 1.30 features in cianfhoghlaim** (current pin per pyproject.toml: `dlt[duckdb,motherduck,filesystem]>=1.30.0,<2.0.0`):
   - `multischema datasets` (1.25.0): collapse the per-nation DuckLake schemas into one BIEP-schema dataset
   - `cross-destination joins` (1.30.0): enable the BIEP Ireland pipeline to join MotherDuck + R2 + local DuckLake in marimo
   - `.add_limit()` on the `@dlt.source` factory (1.30.0): add to the new smoke test
   - `retry_schema_update` helper (1.30.0): wire into the BIEP v3 jurisdiction pipelines
   - `abort_packages` / `fail_pending_job` / `retry_failed_job` (1.30.0): replace the deprecated `drop_pending_packages` calls
7. **Adopt DuckLake 1.0 best practices**:
   - `metadata_schema` per quadrant (1.25.0): `oideachais`, `tuatha`, `croilar`, `agents`, `media` schemas in the shared `md:cianfhoghlaim` Postgres catalog
   - `SORTED BY (jurisdiction, stage, subject)` on the hot LC tables
   - Nightly Dagster asset: `expire_snapshots()` + `cleanup_old_files()` + `merge_adjacent_files()` + `rewrite_data_files()`
   - `automatic_migration=True` on Postgres catalog attaches
8. **Populate the 8 cianfhoghlaim-scope Cognee clusters** (`openspec_changes`, `baml_schemas`, `dagster_assets`, `agents`, `dlt_sources`, `notebooks`, `stacks`, `firecrawl_concepts`) per the existing `knowledge-sync-loop` skill's `sync:paths` + `sync:cognee` tasks.
9. **Add the `mise run dlt:smoke-all` task** + wire into CI.

**Phase 0 exits when**: `mise run dlt:smoke-all` passes with no `ImportError`; all broken legacy imports fixed; 0 dead helpers in `common/`; `lakehouse/` follows the convention; dlt 1.30 features in use; DuckLake 1.0 best practices in use; Cognee clusters populated.

### Phase 1 — Internal consolidation (2 → 6 weeks)

**Goal**: collapse the per-nation sprawl + merge the 2 base classes. Still no file moves.

1. **Collapse `european_nations/<40>/` → `european_nations/_factory.py`** using the CocoIndex pattern from `cocoindex_flows/european_nations/_factory.py` (per `DATA_PLATFORM_ROUTER.md` §6). Each nation gets a 1-line shim `__init__.py` that calls the factory.
2. **Same for `commonwealth/<6>/` and `american_nations/<4>/`** — one `_factory.py` each.
3. **Merge `_shared/nation_source.py:NationSource` + `_cross/jurisdiction_pipeline_base.py:JurisdictionPipelineBase`** → `british_isles/_cross/jurisdiction_pipeline_base.py:JurisdictionPipelineBase` (keep the better-named one).
4. **Add the openspec/mise/Dagster/CocoIndex glue** for the per-PR reusable workflow scaffold (without the per-sister-repo targets yet):
   - `mise.toml`: add `[tasks."dlt:sister-sync"]` (the reusable workflow stub)
   - `.github/workflows/dlt-sister-sync.yml` — reusable workflow definition (no callers yet)
5. **Validate the smoke test** still passes.
6. **Cut a `v1.0` tag** of `dlt_sources/` — the canonical pre-split shape.

**Phase 1 exits when**: ~12,000 LOC of empty `__init__.py` removed; 2 base classes merged into 1; sub-packages carry factory + 1-line shims only; smoke test still passes; `v1.0` tagged.

### Phase 2 — Multi-repo scaffolding (6 weeks → 3 months)

**Goal**: add sister-repo scaffolding + the per-PR + nightly automation. NO data moves yet.

1. **Create `ciandlíthe/` repo skeleton** at `github.com/cianmacandeisigh/ciandlithe.git`. Copy the `tuatha/` project shape:
   - `pyproject.toml` (uv workspace member, depends on cianfhoghlaim)
   - `mise.toml` (`ciandlithe:<verb>:*` task namespace)
   - `openspec/{specs,changes}/`
   - `dlt_sources/` (empty, with `law/` + `_cross/`)
   - `baml/`, `dagster/`, `cocoindex/`, `notebooks/`, `tests/`, `ci/`, `docs/`
2. **Add `.github/workflows/dlt-sister-sync.yml`** (the **reusable workflow** definition) in cianfhoghlaim. Add `.github/workflows/dlt-sister-sync-call.yml` **in ciandlíthe** that calls it.
3. **Add Cognee clusters for ciandlíthe**: `ciandlithe_dlt_sources`, `ciandlithe_openspec_changes`, `ciandlithe_dagster_assets`. Configure the per-repo `.cocoindex_code/guides.yml`.
4. **Add the intra-Cognee nightly sync**: Dagster sensor in cianfhoghlaim that runs each night and pushes `ciandlíthe.*` cluster changes into the cianfhoghlaim-scope `*` clusters (and vice-versa).
5. **Add the per-PR reciprocal PR flow**: PR opened on `ciandlithe/dlt_sources/...` → CI mirror opens a reciprocal PR on `cianfhoghlaim/dlt_sources/_sister_refs/ciandlithe/...`. Built on `gh api` + the Graphite / `gt` skill's stacked-PR pattern.
6. **Wire the openspec sync** via the existing 6-layer `knowledge-sync-loop` skill's nightly Job 1.
7. **Wire Langfuse + MLflow cross-repo observability** — add `ciandlíthe_*` Langfuse project + per-repo MLflow experiment registry.
8. **Scaffold `cianchosaint/`** skeleton (same shape, no data yet).

**Phase 2 exits when**: `ciandlíthe` skeleton exists; `cianchosaint` skeleton exists; per-PR + nightly automation proven via 1 dummy PR + 1 nightly run; Cognee clusters populated; observability surface wired.

### Phase 3 — First real carve-out (3 → 6 months)

**Goal**: `ciandlíthe` gets its first real content.

1. **Move `british_isles/<jurisdiction>/law/*` into `ciandlíthe/dlt_sources/law/<jurisdiction>/`** via git subtree merge or `gh repo fork` + `git subtree add`. For BI jurisdictions where `law/` doesn't currently exist as a per-jurisdiction subtree, create it from per-nation `european_nations/<country>/law/` (for the European BI nations) + from the BIEP v3 `_cross/` registry data.
2. **Add `british_isles/_cross/legal_registry.py`** to ciandlíthe — WRC + courts + statutory-law registry.
3. **Move `european_union/eur_lex*` + `commonwealth/*/law/*` + `european_nations/*/law/*`** (European BI countries only) into `ciandlíthe/dlt_sources/law/_context/` — EU + Commonwealth context data.
4. **Wire the openspec change** `2026-09-XX-ciandlithe-initial-carveout-v1` (dual openspec change: cianfhoghlaim + ciandlíthe).
5. **Run the smoke test** in both repos.
6. **Verify the per-PR reciprocal PR** opens automatically.
7. **First cianfhoghlaim receives** the legal-pipeline improvements back when ciandlíthe upgrades a source (the cascade).

**Phase 3 exits when**: ciandlíthe has the BI legal content; smoke test passes in BOTH repos; per-PR reciprocal PR proven via 1 real PR; cianfhoghlaim has new law-context data via the nightly sync.

### Phase 4 — The remaining 2 sister repos (6 → 12 months)

**Goal**: `cianchosaint` (defence) + `ciancheiltis` (Celtic languages) carve out.

1. **`cianchosaint` (BI law enforcement)** — same pattern as ciandlíthe. Move `british_isles/<j>/law_enforcement/` (new vertical; add to the BIEP v3 jurisdiction tree per the `JurisdictionPipelineBase` pattern) and EU CIRCIA-style threat feeds from `european_union/`.
2. **`ciancheiltis` (Irish + Celtic languages)** — move the full `language/` subtree + `media/heritage.py`, `media/hidden_heritages.py`, `media/local_*` + `media/celtic_history_research/` + the `media/official/duchas_wikipedia` Irish-language subset + the UD corpora. Add CLARIN-UK alignment per your "will be developed to focus on the types of gaois and duchas irish language and later clarin uk all celtic language resource" guidance. The carve rule (appendix A) ensures LC Gaeilge / WJEC Welsh-medium / UoG bilingual content stays in cianfhoghlaim.
3. **Move `crypteolas/` into `tuatha/`** (finalise what's already conceptually there).
4. **Move the remaining `media/` content** into the appropriate sister repos (most → tuatha; heritage + celtic → ciancheiltis).

**Phase 4 exits when**: ciancheiltis carries the Irish + Celtic language slice; cianchosaint carries the BI law enforcement slice; cianfhoghlaim no longer carries pure-language pipelines.

**NOTE**: `cianleighis` (medicine) is **also Phase 4** but is OUT OF SCOPE for the current plan because the user-confirmed split places **medical-malpractice law** in `ciandlíthe` (Q1 clarification) rather than in cianleighis. Re-scope if user wants it.

### Phase 5+ — Deferred past 12-month horizon (no ETA set, per user Q4)

**Goal**: centralise `bonneagar` + `meaisinfhoghlaim`.

1. **Move `bonneagar/stacks/` + the mise Infisical/Locket contract + the per-stack pangolin.yaml + the 89 stacks to `github.com/cianmacandeisigh/bonneagar.git`**.
2. **Move the 12-agent fleet + the agent-observability stack + the fine-tuning tooling to `github.com/cianmacandeisigh/meaisinfhoghlaim.git`**.
3. **Update cianfhoghlaim pyproject.toml** to depend on the 2 repos via uv workspace + pip.
4. **Re-validate the smoke test** + the per-PR + nightly automation.

**Phase 5+ exits when**: cianfhoghlaim contains only the cross-cutting hub + the education pipelines + per-domain context data; the 8 repos form the final topology.

---

## D. The 6 Cascade Effects on Each Sister Repo

Each cascade names the **push direction** (cianfhoghlaim → sister; sister → cianfhoghlaim; bidirectional) and the **concrete trigger**. All cascades reuse the existing 6-layer `knowledge-sync-loop` skill conventions.

### 1. openspec cascade (bidirectional)

- **Trigger**: Any `openspec/changes/<id>/proposal.md` in any of the 8 repos.
- **Cianfhoghlaim→sister**: nightly Dagster sensor scans cianfhoghlaim `openspec/changes/`; for any change that touches a `<vertical>` the sister owns, opens a `mirror_changes/<id>-<repo>-mirror.md` in the sister repo's `openspec/changes/` queue.
- **Sister→cianfhoghlaim**: same sensor (deployed per repo) for the reverse direction.
- **Conflict resolution**: the sister's `openspec archive/` is authoritative for the sister; cianfhoghlaim's for the main. Cross-cutting specs live in cianfhoghlaim.
- **Stack reuse**: openspec CLI + the Cognee `openspec_changes` cluster + the existing 6-layer `knowledge-sync-loop` skill.

### 2. DLT source cascade (sister → cianfhoghlaim via _sister_refs, then reflected back)

- **Trigger**: A PR modifying `<sister>/dlt_sources/.../*.py`.
- **Per-PR reusable workflow** (`.github/workflows/dlt-sister-sync.yml` in cianfhoghlaim + the call site `.github/workflows/dlt-sister-sync-call.yml` in each sister): opens a reciprocal PR on cianfhoghlaim's `dlt_sources/_sister_refs/<repo>/...` mirror path (read-only).
- **Nightly merge**: a Dagster sensor in cianfhoghlaim once per night merges the accumulated sister-ref changes into `dlt_sources/<sister-context>/` in cianfhoghlaim. The sister gets a successful `dlt:mirror-ack` notification.
- **Stack reuse**: GitHub Actions reusable workflows (`gh api`), Dagster sensor, Cognee `dlt_sources` cluster, the existing `dlt-sync` skill.

### 3. Schema cascade (cianfhoghlaim → sister for compilation; sister → cianfhoghlaim for new fields)

- **Trigger**: A `baml_src/*.baml` change in any repo.
- **Cianfhoghlaim→sister**: existing `baml build` step (per `baml-schema-sync` skill) regenerates the per-repo Pydantic client in the sister's `baml/` directory.
- **Sister→cianfhoghlaim**: a new BAML field added in a sister repo is mirrored back via the per-PR workflow + nightly sync.
- **Stack reuse**: BAML CLI + `baml-schema-sync` skill + Cognee `baml_schemas` cluster (with per-repo twins: `tuatha_baml_schemas`, `ciandlithe_baml_schemas`, `ciancheiltis_baml_schemas`, etc.).

### 4. Destination cascade (cianfhoghlaim → sister; downgrades gated)

- **Trigger**: A change to `dlt_sources/common/destinations_cianfhoghlaim.py` or `dlt_sources/lakehouse/` (Phase 0 rename) or DuckLake options.
- **Cianfhoghlaim→sister**: sister repos depend on cianfhoghlaim as a uv workspace member; `pip install -e ../cianfhoghlaim` exposes the new destination automatically.
- **Versioning**: cianfhoghlaim bumps its minor version on any destination API change; sister's mise.toml pins `cianfhoghlaim >=<minor>,<<next-minor`.
- **Downgrade gating**: a per-sister `mise.toml` `[tasks."dlt:destination-validate"]` runs every CI to verify the current cianfhoghlaim destination version passes the sister's smoke tests.
- **Stack reuse**: uv workspace + mise tasks + the existing destinations factory.

### 5. Observability cascade (bidirectional)

- **Trigger**: Any Langfuse span / MLflow run / Ragas eval that touches a `<sister>` tag.
- **Bidirectional**: Langfuse projects per sister repo + a `cianfhoghlaim_synthesis` project that aggregates. MLflow tracking URIs per repo + a shared tracking URI for cross-repo experiments.
- **Stack reuse**: Langfuse + Logfire + MLflow + Ragas (per `agent-observability` skill).

### 6. Knowledge-graph cascade (bidirectional via the cianfhoghlaim-scope Cognee cluster)

- **Trigger**: Any `cognee_remember()` call in any repo.
- **Per-repo twins**: 6 Cognee clusters per repo (8 repos × 6 = 48 clusters). Sync hourly via the existing 6-layer sync loop.
- **Cluster diffing**: a Dagster sensor in cianfhoghlaim runs the existing `notebooks/24_...sync_health.ipynb` against each sibling cluster; surfaces drift to a `stedding/sync-reports/cognee-{date}.md` summary.
- **Stack reuse**: Cognee + CCC + Dagster + the existing `knowledge-sync-loop` skill.

---

## E. The 12-Component Stack to Reuse (with concrete touchpoints)

For each component: what it does in cianfhoghlaim today → reuse for the multi-repo cascade.

| Component | Reuse for | Skill / location |
|---|---|---|
| **mise tasks** | Per-repo `mise.toml` namespaces (`ciandlithe:*`, `cianchosaint:*`, etc.) + the new `dlt:sister-sync` reusable workflow + `dlt:destination-validate` CI gate + `dlt:smoke-all` smoke test | `mise` skill + existing `tuatha/mise.toml` as the reference pattern |
| **openspec CLI** | Per-repo spec-driven change management + the 6-layer sync loop's `sync:openspec` task + per-repo `openspec/{specs,changes}/` trees | `openspec` skill + `knowledge-sync-loop` skill |
| **Cognee + CCC** | Cross-repo knowledge-graph cascade (48 clusters) + concept guides per repo (`.cocoindex_code/guides.yml`) + the existing `notebooks/24_*sync_health.ipynb` dashboard (extended) | `agent-memory-systems` skill + `ccc` skill + `knowledge-sync-loop` skill |
| **Infisical + Locket + mise** | 3-way secrets contract — `infisical://dev-baile/cianfhoghlaim/...` URIs reused across all 6 sister repos (no `cianfhoghlaim/` prefix per the `secrets-management` skill) | `secrets-management` skill |
| **Dagster (5-layer `defs/` tree)** | Per-repo asset groups + per-PR sensors + nightly sync sensors + cross-repo job DAGs | The existing Dagster asset count (~833 in cianfhoghlaim); per `dagster-asset-sync` skill |
| **CocoIndex (v1 `coco.App`)** | Per-repo embedding pipelines + the shared `BAAI/bge-m3` 1024-d embedder from `_lifespan.py` reused across all 8 repos | `cocoindex` skill + the existing 7 BIEP v1 Apps as reference patterns |
| **Firecrawl MCP (12 tools)** | Cross-repo research + scrape + map for new jurisdiction pipelines + the `firecrawl_agent` deep-research for BI+NCCA syllabus change detection | `firecrawl` skill + `browser-tools` skill |
| **Langfuse + Logfire + MLflow + Ragas** | Cross-repo observability + per-repo trace aggregation + the `@observe` decorator pattern reused in each sister repo's agents | `agent-observability` skill + `logfire-instrumentation` skill |
| **MotherDuck + DuckLake 1.0** | Shared `md:cianfhoghlaim` destination with per-quadrant `metadata_schema` (1.25.0) + the 4 nightly maintenance tasks | `motherduck` skill + `ducklake` skill + the dlt+DuckLake 1.0 destinations |
| **TanStack Start + CopilotKit (4 web surfaces)** | Add 4 sister-repo web surfaces (planned: `ciandlithe-web`, `cianchosaint-web`, `ciancheiltis-web`) using the same `agentic-frontend-frameworks` umbrella + `tuatha-ui/` as the reference pattern | `agentic-frontend-frameworks` skill + the existing `tuatha-ui/` |
| **HTTPX retry v2 + EndpointRecovery v2 + Firecrawl adapter v2** | Each sister repo consumes via `cianfhoghlaim.dlt_sources.common.{endpoint_recovery, firecrawl_source, http_client}` — the 200-importer `endpoint_recovery.py` becomes the cross-repo canonical primitive | `firecrawl-build-scrape` skill + the Cianfhoghlaim-200-importer `common/endpoint_recovery.py` |
| **BAML contracts + `@observe` + Cognee recall + Langfuse trace + DAG lineage** | The full agentic-pipeline observability stack — every per-sister-repo pipeline emits to all 4 | `baml` skill + the 12-agent fleet from `agent-fleet-orchestration` skill |

---

## F. What Cianfhoghlaim Receives When Pipelines Improve in Sister Repos

Concrete mechanisms (the answer to the user's "how cianfhoghlaim being our main repo will later when pipelines improved" question):

1. **Schema-driven improvements propagate back** — when ciandlíthe improves `ExtractStatuteConcept` BAML (e.g. adds a `court_division` field), the field flows back via the per-PR workflow → cianfhoghlaim's `baml_schemas` Cognee cluster → surfaces in the marimo knowledge-graph notebook for the next LC History "Irish legal history" lesson (per `tuatha/subjects/history.py`).
2. **Cross-domain context data gets richer** — new WRC rulings + statutory amendments + court procedural rules from ciandlíthe surface in cianfhoghlaim's BIEP v3 jurisdiction registry (the `british_isles/_cross/` registry) and become context data for the LC History + LC English syllabi (which both cite case law).
3. **Defence-pipeline cross-fertilisation** — when cianchosaint adds a new police-data quality checker, that checker is adapted for LC subject agents' input validation in `tuatha/subjects/` via the per-PR reciprocal mirror.
4. **Celtic-language improvements lift terminology** — when ciancheiltis improves `ExtractTermFrequency` + `ExtractWordAlignment` BAML (the patterns from existing `tearma_search.py` + `gaois.py`), the LC Gaeilge subject agent benefits (the `tuatha/subjects/gaeilge.py` + the `gael_gramadach_review` BAML tool).
5. **UD corpora stay canonical for LC Gaeilge + WJEC Welsh-medium** — ciancheiltis owns the canonical `UD/ud_irish` + `UD/ud_welsh` corpora; cianfhoghlaim's LC Gaeilge + WJEC Welsh-medium pipelines consume via the versioned `ciar://ciancheiltis/datasets/ud_<lang>@v<N>` URI contract (parallel to the existing `infisical://dev-baile/...` secrets contract).
6. **Library catalogue enrichment** — leabharlann_books + leabharlann_education_notes (staying in cianfhoghlaim) benefit when ciancheiltis publishes new Irish-language bibliographic metadata into the Cognee twin cluster.
7. **Infrastructure improvements flow down** (Phase 5+) — when `bonneagar` provisions a new Cognee cluster tier or a faster MotherDuck Duckling instance, all 8 repos benefit immediately via the mise + uv workspace contract.
8. **ML training pipeline improvements** (Phase 5+, future state) — when `meaisinfhoghlaim` trains a new TinyLLaMA + CroilarWeb BERT on the legal / medical / defence corpora, the trained LoRA adapters are served via Hugging Face Inference Endpoints to cianfhoghlaim's BAML `equivalency_generator.baml` for the LC subject agents.

---

## G. Phase-Specific Risks + Mitigations

| Phase | Risk | Severity | Mitigation |
|---|---|---|---|
| 0 | **873 broken legacy imports** that currently fail silently | **CRITICAL** | Phase 0.1 + 0.2: smoke test first, then bulk-fix; never rename-before-test |
| 0 | **~12,000 LOC of empty `__init__.py`** in the per-nation subtrees | HIGH | Phase 1 collapses these; not a Phase 0 risk |
| 0 | **9 dead helpers in `common/`** (~1,974 LOC) | MEDIUM | Delete in Phase 0.3; verify no test fails |
| 0 | **Two competing destination modules** (`destinations_cianfhoghlaim.py` + `destinations_tuatha.py`) | MEDIUM | Delete `destinations_tuatha.py` in Phase 0.4 |
| 1 | **2 base classes for the same pattern** (`NationSource` + `JurisdictionPipelineBase`) | MEDIUM | Phase 1.3: merge into 1 `JurisdictionPipelineBase` |
| 2 | **Per-PR workflow gets out of sync** with the canonical cianfhoghlaim destination version | MEDIUM | Phase 2.7 + downgrade-gate via `dlt:destination-validate` |
| 2 | **Cognee twin cluster naming drift** — sister clusters not consistently suffixed with `_ciandlithe_*`, etc. | LOW | Phase 2.3 standardised cluster naming convention |
| 3 | **`british_isles/<j>/law/` doesn't exist as a per-jurisdiction subtree** for all BI jurisdictions yet — needs creation from per-nation + BIEP cross data | HIGH | Phase 3.1 creates the subtree pattern per the `JurisdictionPipelineBase` |
| 3 | **The 4 BI jurisdiction law-style sources** need new BAML contracts (`ExtractCourtRuling`, `ExtractWRCAdjudication`, etc.) | MEDIUM | Phase 3.2 alongside the move; mirror back via cascade contract 3 |
| 4 | **LC Gaeilge + WJEC Welsh-medium + UoG bilingual data must keep flowing into cianfhoghlaim** post-ciancheiltis carve | HIGH | Appendix A carve rule + the `ciar://ciancheiltis/datasets/ud_irish@v<N>` versioned URI contract |
| 4 | **cianchosaint** has no existing precedent in this codebase (new vertical) | LOW | Use the ciandlíthe skeleton as the reference pattern |
| 5+ | **bonneagar + meaisinfhoghlaim hive-out** is conceptually large | DEFERRED | No ETA; revisit at Phase 4 review |

---

## H. Success Metrics (per Phase)

| Phase | Metric | Before | After target |
|---|---|---|---|
| 0 | `mise run dlt:smoke-all` | fails with 873 ImportErrors | passes |
| 0 | LOC in `common/` | ~8,073 | ≤ 6,100 (9 dead helpers removed) |
| 0 | Destination modules in `common/` + `_lakehouse/` | 4 | 2 (1 in `common/`, 1 in `lakehouse/`) |
| 0 | Bumped dlt feature usage | partial | full (multischema + cross-destination + .add_limit + retry_schema_update + abort_packages) |
| 0 | DuckLake 1.0 best-practice usage | partial | full (metadata_schema + sorted_by + nightly maintenance) |
| 0 | Cognee clusters populated | partial | full 8 / 8 |
| 1 | `.py` files in `dlt_sources/` | ~1,975 | ≤ 1,400 |
| 1 | Total LOC | ~155,506 | ≤ 105,000 (factory consolidation removes ~12,000 LOC empty shims + ~38,000 LOC redundant class defs) |
| 1 | Base classes for per-jurisdiction sources | 2 | 1 |
| 2 | Sister-repo skeletons | 1 (tuatha) | 3 (+ ciandlíthe + cianchosaint) |
| 2 | Per-PR reciprocal workflow proven | 0 | 1 dummy PR + 1 nightly run |
| 2 | Cognee twin clusters | 0 | 6 × 2 (sister-scope) = 12 |
| 3 | CI smoke passes in BOTH repos | not applicable | yes |
| 3 | BI jurisdiction law content in ciandlíthe | 0 | 8 / 8 BI jurisdictions |
| 4 | Irish-language datasets in ciancheiltis | 0 | 11+ sources (tearma + logainm + ainm + gaois + duchas + canuint + heritage + UD variants) |
| 4 | BI law_enforcement surface in cianchosaint | 0 | 8 / 8 BI jurisdictions |
| 5+ | deferred past 12-month horizon | — | — |

---

## Appendix A — The 7 grey-area file-by-file carve decisions

The rule from §B applied to each ambiguous file. Source per row: the user's Q3 + Q5 clarifications.

| File | Carve | Why |
|---|---|---|
| `filesystem/uog_personal_archive.py` | **Stays in cianfhoghlaim** | UoG = educational entity; this is the personal archive of an educational user |
| `filesystem/university_of_galway.py` | **Stays in cianfhoghlaim** | UoG institutional pipeline = educational |
| `filesystem/leabharlann_books.py` | **Stays in cianfhoghlaim** | Cross-language bibliography that links to UoG module reading lists + LC Gaeilge + WJEC Welsh-medium — bilingual + educational |
| `api_sources/leabharlann_education_notes.py` | **Stays in cianfhoghlaim** | Same — links to UoG + NCCA LCs; "education notes" suffix is the educational layer |
| `language/tearma.py` + helpers | **ciancheiltis** | Pure Irish-language dataset, not an educational curriculum |
| `language/logainm.py`, `ainm.py`, `gaois.py` (+ `_gaois_helpers.py`), `duchas.py` (+ `_duchas_images_helpers.py`), `canuint.py` (+ 4 submodules), `duchas_images.py` | **ciancheiltis** | Pure Irish-language datasets |
| `language/heritage.py`, `hidden_heritages.py`, `local_documents_by_subject.py`, `local_education_documents.py` (4 files) | **ciancheiltis** | Celtic-language heritage datasets (not educational) |
| `language/UD/*` (Universal Dependencies) — `ud_irish` canonical + `ud_welsh` + `ud_scots` + `ud_breton` + `ud_manx` + `ud_cornish` | **ciancheiltis** owns the canonical data; **cianfhoghlaim** holds a pinned `ciar://ciancheiltis/datasets/ud_irish@v<N>` reference from `tuatha/subjects/gaeilge.py` and the WJEC Welsh-medium pipeline | LC Gaeilge + WJEC need the UD corpora as ground truth, but the corpora themselves are language research data |
| `british_isles/wales/education/*` (WJEC Welsh-medium pipeline) | **Stays in cianfhoghlaim** | Welsh-medium CURRICULUM = educational surface; sibling to AQA + OCR + Pearson English |
| `british_isles/scotland/education/*` (SQA Gàidhlig-medium pipeline, if/when added) | **Stays in cianfhoghlaim** | Same — bilingual educational |
| `british_isles/ireland/education/subjects/gaeilge/*` (the LC Gaeilge subject) | **Stays in cianfhoghlaim** | LC Gaeilge = NCCA educational surface |
| `tuatha/subjects/gaeilge.py` (the LC Gaeilge subject agent) | **Stays in cianfhoghlaim** (in the already-carved `tuatha/` sub-project) | Educational |

---

## Appendix B — Cross-references

- **Companion openspec change**: [`2026-08-24-dlt-sources-to-multi-repo-scaffold-v1`](../changes/2026-08-24-dlt-sources-to-multi-repo-scaffold-v1/)
- **Companion spec**: [`cianfhoghlaim-dlt-sources-multi-repo`](../changes/2026-08-24-dlt-sources-to-multi-repo-scaffold-v1/specs/cianfhoghlaim-dlt-sources-multi-repo/spec.md)
- **Tuatha precedent**: `openspec/changes/2026-08-25-tuatha-british-isles-mmo-consolidation-v1/`
- **`tuatha/` repo** (the reference sub-project at `/Users/cianmacandeisigh/dev/cianfhoghlaim/tuatha/`): the shape every future sister repo copies
- **Audit trail**: `openspec/plans/STATUS.md`

## Appendix C — Key Skills to Load for Execution

| Phase | Skill to load |
|---|---|
| 0 | `dlt` (the canonical dlt routing skill), `motherduck-ducklake`, `browser-tools` (for the Firecrawl adapter), `secrets-management`, `knowledge-sync-loop` (for the Cognee cluster population) |
| 1 | `cocoindex` (for the `_factory.py` consolidation pattern), `mise` (for the new `dlt:*` tasks), `dagster-asset-sync` (for the asset group alignment) |
| 2 | `gh` (for the per-PR workflow), `mise` (for the per-repo task namespaces), `agent-observability` (for Langfuse + MLflow per-repo projects), `agent-memory-systems` (for the Cognee twin clusters) |
| 3 | `openspec` (for the dual change authorship), `tuatha` (for the per-jurisdiction per-vertical skeleton pattern) |
| 4 | `tuatha`, `openspec`, `mise` |
| 5+ | `bonneagar` (when separated), `agent-fleet-orchestration` (when separated) |

---

**Last updated**: 2026-08-24 (v2; supersedes v1)
**Owner**: build subagent (proposed openspec change `2026-08-24-dlt-sources-to-multi-repo-scaffold-v1`)
