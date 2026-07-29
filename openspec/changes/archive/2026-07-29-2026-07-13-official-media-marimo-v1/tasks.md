# Tasks — Official Media Marimo Dashboards v1

## 1. Read the spec to understand the 5 requirements

- [x] **1.1** Read `openspec/specs/official-media-marimo/spec.md` and
      identify the 5 requirements: R1 OfficialMediaMissionControl,
      R2 OfficialMediaTanStackRoute, R3 OfficialMediaCogneeDataset,
      R4 Marimo on Cloudflare deployment (KCG),
      R5 Streamlit-compatible layout in marimo.

## 2. Inspect the existing official-media pipeline + marimo work

- [x] **2.1** Identified the existing 2 notebooks at
      `notebooks/09_official_media/`:
      `01_official_media.py` (4-panel mission control, covers R1) and
      `02_email_inbox_triage.py` (inbox triage, out of scope).
- [x] **2.2** Identified the canonical data sources:
      `dlt/official_media/allowlist.py` (Stage-1 filter),
      `dlt/official_media/source_resolver.py` (4-lookup
      resolver), `baml/processing/official_media.baml`
      (Stage-2 BAML fallback), and the Cognee dataset
      `cianfhoghlaim_official_media` with the 4 spec-defined edge types.

## 3. Create the 5 marimo dashboards

- [x] **3.1** Create
      `notebooks/09_official_media/03_post_trends.py`
      (~360 lines; 3 panels: posts per day, per platform, engagement
      heatmap; 1 BAML `ClassifyOfficialMedia` extractor; covers R1
      timeline sub-requirement).
- [x] **3.2** Create
      `notebooks/09_official_media/04_mention_network.py`
      (~345 lines; 3 panels: source platform, mention overlap matrix,
      top-15 mention pairs; 1 BAML extractor; covers R2 TanStack route
      preview).
- [x] **3.3** Create
      `notebooks/09_official_media/05_fediverse_coverage.py`
      (~390 lines; 3 panels: 4 edge-type counts, fediverse instance
      distribution, edge direction; 1 BAML extractor; covers R3 Cognee
      dataset edges).
- [x] **3.4** Create
      `notebooks/09_official_media/06_cross_archive.py`
      (~425 lines; 3 panels: link strength by category, NCCA subject
      coverage, R4 Cloudflare deployment status; 1 BAML extractor;
      covers R4 cross-archive + deployment).
- [x] **3.5** Create
      `notebooks/09_official_media/07_moderation_sentiment.py`
      (~390 lines; 4 tabs (sentiment over time, moderation flags,
      sentiment by category, BAML extractor); 1 BAML extractor;
      covers R5 multi-column tabs layout).
- [x] **3.6** Use the underscore-prefix convention for cell-local
      variables (`_chart_a`, `_rows`, `_rng_seed`, etc.) so each cell
      has a unique reactive variable namespace (the marimo check
      requires this).

## 4. Verify the 5 dashboards AST-parse

- [x] **4.1** Run `ast.parse(open(f).read())` on each of the 5 files —
      all 5 pass without SyntaxError.
- [x] **4.2** Run `marimo check` on each of the 5 files — all 5 have
      no critical issues (only 2 non-fatal warnings per file:
      `general-formatting` for the docstring-before-import order, and
      `markdown-indentation` for the multi-line markdown cells).

## 5. Verify the CLI discovery

- [x] **5.1** Run `uv run cianfhoghlaim-marimo list 09_official_media`
      and confirm all 5 new notebooks (plus the 2 pre-existing ones)
      are discovered.

## 6. Write the openspec change artifacts

- [x] **6.1** Create
      `openspec/changes/2026-07-13-official-media-marimo-v1/proposal.md`
      (this file's parent directory).
- [x] **6.2** Create
      `openspec/changes/2026-07-13-official-media-marimo-v1/tasks.md`
      (this file).
- [x] **6.3** Create
      `openspec/changes/2026-07-13-official-media-marimo-v1/specs/official-media-marimo/spec.md`
      (1 ADDED requirement: 5 dashboards at 03..07 render + CLI
      discoverable).

## 7. Validate + commit + push

- [x] **7.1** Run `openspec validate 2026-07-13-official-media-marimo-v1 --strict`
      and confirm it passes.
- [x] **7.2** Commit the 8 new files (5 dashboards + 3 openspec
      artifacts) with the canonical message and push to
      `origin/pick-4-biep-v1` (NOT `main`).
