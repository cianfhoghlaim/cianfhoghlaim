# Lateralise British Isles Domains — Sources, Parity & Lakehouse Centralisation

## Why

The `sruth/oideachais/` data platform today is **deep on Ireland education** and **shallow everywhere else**. The `dlt_sources/` tree carries 30+ Irish sources plus 4 UK nations' education sources and 3 crown‑dependency sources, but:

- There are **no DLT sources** for `medicine` (HSE, Medical Council, GMC‑UK, NHS England/Scotland/Wales), `law` (irishstatutebook.ie, legislation.gov.uk, workplacerelations.ie, courts.ie, ACAS), or `statistics` beyond the four UK census endpoints already documented in `sruth/oideachais/firecrawl_configs/scraping_config.yaml`.
- The existing `sruth/oideachais/sources.md` lists 5 Irish education sources + 1 medicine row + 1 law row (and the law row is the wrong shape — `medicalcouncil.ie`, `gmc-uk.org`, `hse.ie` are listed under "medicine" but the value `https://www.gov.ie/en/department-of-health/` is the Department of Health, not the GMC).
- There is **no canonical `sources.yaml`** that the DLT pipeline factory, the Dagster asset factory, the CocoIndex embedder, the Cognee cognify step and the marimo dashboards all read from. Instead, each layer hand‑codes its own understanding of which sources exist.
- The firecrawl + browserbase MCP servers in `opencode.json` and the `sruth_browser` stack at `infrastructure/browser/sruth_browser/` are wired but **not** exercised by any production asset. The only consumer is the legacy `sruth/oideachais/dagster_defs/assets/ireland/firecrawl_assets.py` which writes a JSON dump to a hard‑coded `/app/storage/data/scrapes/` path and is bypassed by the production assets.
- The Dagster × DLT integration has **no automated test coverage**. The four `sruth/oideachais/test_crawl*.py` files are ad‑hoc smoke scripts run from a venv, not in CI, and they break whenever the local `stedding/ingest_queue/` cache is empty.
- The Leaving Cert reader (`sruth/oideachais/api/ducklake_reader.py`) opens 7 separate DLT datasets and globs 7 S3 prefixes; there is no shared "one big DB with schemas" model. Per the user's decision (this conversation) we converge on **`md:oideachais` with `oideachais.{domain}.{nation}` schemas**.

This change centralises, lateralises, and tests that existing surface, without adding new product features outside the data platform.

## What

1. **Canonical `sruth/oideachais/sources.yaml`** — single source of truth listing every DLT source across the four domains (`education`, `medicine`, `law`, `statistics`) and the eight nations (`ie, ni, en, sct, wls, iom, jey, ggy`). Pydantic‑validated by `SourceFactory.from_yaml()`.
2. **`SourceFactory`** in `sruth/oideachais/dlt_utils/source_factory.py` — 7‑method contract that turns a YAML ID into a DLT source / `@dlt_assets` decorator / Dagster `@asset` / LanceDB table name / Cognee dataset / marimo notebook path / pytest path.
3. **Toolchain bump** — Python 3.13 in `mise.toml`, `Dockerfile.dagster`, all `pyproject.toml` files; `uv lock --upgrade` to pull latest stable `dagster`, `dlt`, `duckdb`, `lancedb`, `cognee`, `marimo`, `firecrawl-py`, `playwright`, `pydantic`, `boto3`, `httpx`; refresh `bun.lock` on the TS side.
4. **Asset‑key rename** — old `["ireland", …]` / `["uk", "education", "northern_ireland", …]` keys move to `["ie", …]` / `["ni", "education", …]`. A one‑shot backwards‑compat alias table in `definitions.py` keeps the old keys resolvable in the Dagster UI for the rest of the LC 2026 cycle.
5. **One big `oideachais` DB with schemas** — DLT `dataset_name` stays per‑source, but the DuckLake schema is unified to `oideachais.{domain}.{nation}`. The LC reader (7 glob calls) is replaced by a single `duckdb.attach("oideachais")`.
6. **16 pytests** in `sruth/oideachais/tests/`, `sruth/tuatha/tests/`, `sruth/croilar/tests/`, `tests/sources/` — exercise the existing DLT/Dagster asset graph with `USE_LOCAL_SCRAPES=true` and a temp DuckLake; no live network, no new features.
7. **Existing source re‑organisation** — `sruth/oideachais/dlt_sources/ireland/*` and `sruth/oideachais/dlt_sources/uk/{england,scotland,wales,northern_ireland}/*` and `sruth/oideachais/dlt_sources/crown_dependencies/*` are re‑export shimmed to the new `sruth/oideachais/dlt_sources/domains/education/{nation}/*` package layout. Same behaviour, new address.
8. **New medicine + statutory‑law DLT sources for Ireland** (Phase 4a/4b). `law/` is **statutory only** per user decision; case law is explicitly out of scope and reserved for a future `case-law-and-precedent` change.
9. **Lateralise to NI / EN / SCT / WLS** — new medicine + statutory‑law DLT sources for each of the 4 UK nations, plus education parity for the 3 crown dependencies.
10. **`sruth/oideachais/site_analysis/`** package that drives **firecrawl + browserbase MCP** to produce a `SiteAnalysis` BAML record (software fingerprint, layout fingerprint, page description, screenshot path) for every public source, written to `oideachais.site_analysis` in DuckLake, embedded in LanceDB, cognified in Cognee.
11. **Three new marimo dashboards** (education all‑nations, medicine registers, law statute book) under the existing `infrastructure/stacks/engineering/marimo/` stack, scheduled by Dagster.

## Impact

### Affected specs
- `MODIFIED` `oideachais-pipeline/spec.md` — new domain‑first asset keys; new SourceFactory reference.
- `MODIFIED` `data-pipeline/spec.md` — new `sources.yaml` + `SourceFactory` capability; toolchain bumped to Python 3.13 / latest pins.
- `MODIFIED` `knowledge-graph/spec.md` — Cognee datasets keyed by `domain` (not by `nation`) with a `oideachais_cross_nation` cross‑domain dataset.
- `ADDED` `domain-source-registry/spec.md` — the `sources.yaml` + `SourceFactory` capability spec.
- `ADDED` `site-analysis-mcp/spec.md` — the firecrawl + browserbase MCP side‑analysis capability spec.

### Affected files / directories
- `sruth/oideachais/sources.yaml` (new)
- `sruth/oideachais/dlt_utils/source_factory.py` (new)
- `sruth/oideachais/dlt_utils/{firecrawl_source.py, destinations.py, batching.py, mixins.py, safety.py}` (extended; no new behaviour)
- `sruth/oideachais/dlt_sources/domains/education/{ie,ni,en,sct,wls,iom,jey,ggy}/*` (new package layout; existing sources moved)
- `sruth/oideachais/dlt_sources/domains/medicine/{ie,ni,en,sct,wls}/*` (new)
- `sruth/oideachais/dlt_sources/domains/law/{ie,ni,en,sct,wls}/*` (new, statutory only)
- `sruth/oideachais/dlt_sources/{ireland,uk,crown_dependencies}/*` (re‑export shims)
- `sruth/oideachais/dagster_defs/definitions.py` (asset key aliases; SourceFactory integration)
- `sruth/oideachais/dagster_defs/assets/ie/education/*` (moved from `assets/ireland/`)
- `sruth/oideachais/dagster_defs/assets/ie/education/leaving_cert/*` (moved)
- `sruth/oideachais/dagster_defs/assets/{ni,en,sct,wls,iom,jey,ggy}/education/*` (new asset directories)
- `sruth/oideachais/dagster_defs/assets/{domain}/{nation}/*` for medicine + law (new)
- `sruth/oideachais/dagster_defs/assets/site_analysis/*` (new)
- `sruth/oideachais/api/ducklake_reader.py` (refactored to single attach)
- `sruth/oideachais/site_analysis/` (new package)
- `sruth/oideachais/baml_src/site_analysis.baml` (new)
- `sruth/oideachais/cocoindex_flows/site_analysis_embedding.py` (new)
- `sruth/oideachais/cognee_integration/site_analysis_cognify.py` (new)
- `sruth/oideachais/notebooks/dashboards/{education,medicine,law,site_analysis}/*` (new)
- `sruth/oideachais/tests/**` (new pytest tree)
- `sruth/tuatha/tests/test_definitions_loads.py` (new)
- `sruth/croilar/tests/dlt_assets/test_spotify_soundcloud_labels.py` (new)
- `tests/sources/test_cross_namespace.py` (new)
- `mise.toml`, `sruth/oideachais/pyproject.toml`, `sruth/croilar/pyproject.toml`, `sruth/tuatha/pyproject.toml`, `sruth/oideachais/Dockerfile.dagster`, `infrastructure/stacks/engineering/sruth/oideachais/Dockerfile.dagster` (toolchain bump)
- `package.json`, `bun.lock` (refresh)

### LLM stack
- Unchanged. BAML extraction (DeepSeek V4 Pro) and Bge‑m3 embeddings (CocoIndex) continue. No new model registrations.

### Hosting / infra
- No new Docker Compose stacks. Existing `infrastructure/stacks/engineering/dagster/`, `…/marimo/`, `…/sruth/oideachais/`, `…/crawl4ai/`, and `infrastructure/stacks/storage/lakehouse/` already host the required services.

### Cost
- The new sources are mostly read‑only Firecrawl / Browserbase / API calls against public endpoints, all cached by `USE_LOCAL_SCRAPES=true` in CI and dev. Production only spends on real (non‑cached) runs. Estimate: ≤$10/month additional Firecrawl credits for the new `medicine` + `law` endpoints at current crawl rates.

## Non‑Goals

- **No case law** — courts.ie, ACAS decisions, BAILII, etc. are explicitly out of scope. Reserved for a future `case-law-and-precedent` change.
- **No authenticated medical register lookups** — GMC‑UK / Medical Council public search endpoints only. Full register download behind auth is reserved for `domain-source-registry/v2`.
- **No new external scraping beyond the source list** in `sources.yaml`. The source list is the contract.
- **No new DLT destination** — DuckLake is the only destination. The `use_ducklake=True|False` toggle in `curriculum_dlt_assets.py` is preserved for local dev.
- **No product‑side UI changes** — TanStack Start, Convex, CopilotKit untouched. Only the data platform underneath.

## Per‑Phase Build Order

| # | Phase | What ships | Risk |
|--:|:--|:--|:--|
| 1a | Toolchain bump | Python 3.13, latest pins, lockfile refresh. No behaviour change. | Transitive pin conflicts → fallback to Python 3.12. |
| 1b | Pytest suite (16 tests) | All under `USE_LOCAL_SCRAPES=true` + temp DuckLake. | Existing fragility points surface — we don't fix them in this phase, just guard. |
| 2 | `sources.yaml` + `SourceFactory` stub | YAML schema, pydantic validation, 7‑method contract; no real sources hooked. | None. |
| 3 | Re‑organisation | Move existing DLT sources into `domains/education/{nation}/*`; legacy re‑export shims. Asset keys renamed; one‑shot alias table. | Backwards‑compat breaks a `dagster asset list` consumer. |
| 4a | Ireland medicine | HSE, Medical Council, DoH, HPSC. | Endpoints not yet mapped. |
| 4b | Ireland law (statutory) | irish_statute_book (XML API), doj, lawreform. | `irishstatutebook.ie` is high‑volume; rate limit. |
| 5 | Lateralise | medicine + law (statutory) + education parity to NI/EN/SCT/WLS/IOM/JEY/GGY. | Per‑nation config burden. |
| 6 | `site_analysis/` + dashboards | Firecrawl + Browserbase MCP via new BAML schema; LanceDB embed; Cognee cognify; 3 marimo dashboards. | Screenshot storage cost. |
| 7 | Archive | `openspec archive lateralise-british-isles-domains` + `domain-source-registry` + `site-analysis-mcp` added to `openspec/project.md`. | None. |

## Risks

1. **3.13 + Dagster 1.13 + dlt 1.x triple bump** — see Phase 1a. Mitigation: it is a pure upgrade PR; rollback is `git revert`.
2. **Single `md:oideachais` DB schema mapping** — DLT `dataset_name` is per‑source; the DuckLake *schema* must be `oideachais.{domain}.{nation}`. The factory must emit both. The existing reader glob() calls must be replaced by `attach('oideachais')`; if not, we leak N schemas.
3. **Asset key rename is breaking** — `definitions.py` carries a one‑shot alias table for the LC 2026 cycle; after archive, that alias table goes in a follow‑on `drop-asset-key-aliases` change.
4. **`irishstatutebook.ie` is high‑volume** — ~30k acts / 3k SIs / 30k statutory instruments; the new DLT source MUST use `dlt.sources.incremental` on `act_id` and a `dlt.config["data_writer.file_max_items"]=1000` to avoid one huge parquet.
5. **BAML `SiteAnalysis` schema** — must validate against the actual responses from firecrawl's `/extract` endpoint; expected to need 1–2 iterations.
6. **Brittle `dlt_utils/destinations.py`** — currently uses `DuckLakeCredentials` constructor kwargs that may have shifted in dlt 1.x. The Phase 1a toolchain bump is the moment this surfaces; if it breaks, the 1a PR becomes "fix DuckLakeCredentials for dlt 1.x" instead of "no behaviour change".

