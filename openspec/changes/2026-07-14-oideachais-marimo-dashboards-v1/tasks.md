# Tasks — Oideachais Marimo Dashboards v1

## 1. Read the spec to understand the 10 requirements

- [x] **1.1** Read `openspec/specs/oideachais-marimo-dashboards/spec.md`
      and identify the 10 requirements: R1 5-stage education
      dashboards, R2 Leabharlann full-stack demo,
      R3 Cross-domain + lakehouse + ducklake,
      R4 Marimo on Cloudflare Workers + Container,
      R5 PEP 723 inline dependency blocks, R6 Multi-column layout,
      R7 DLT + LanceDB pipeline pattern in notebooks,
      R8 University courses dashboard,
      R9 BIEP Notebooks Wire to Local Lakehouse (ibis-first),
      R10 BIEP Notebooks — ibis-first refactor of all 11 files.

- [x] **1.2** Audit existing dashboard infrastructure:
      - `notebooks/04_biep_motherduck/{01..11}_*.py` — the 11 BIEP
        subject + leabharlann + full-pipeline notebooks (covers
        most of R9 + R10)
      - `notebooks/leaving_cert/{chemistry,mathematics,gaeilge,...}.py`
        — the 6 per-subject notebooks (covers R6 + R9 for the per-subject
        half)
      - `notebooks/06_observability/03_cognee_knowledge_graph.py` —
        the per-subject cognify dashboard (partial R2)
      - `notebooks/06_observability/02_irish_extraction_quality.py`
        — the per-corpus Irish quality audit (partial R2/R7)
      - `notebooks/05_lakehouse_inspect/01_ducklake_explorer.py` —
        the DuckLake explorer (partial R3)
      - `notebooks/13_baml_cocoindex_tutorial/{01..05}_*.py` —
        the 5 BAML + CocoIndex tutorials (reference patterns for
        R7 + R9)
      - `notebooks/09_official_media/{03..07}_*.py` — the canonical
        follow-up-dashboards precedent for openspec change
        `2026-07-13-official-media-marimo-v1`

## 2. Add the new dashboards group to the CLI

- [x] **2.1** Edit `ciolanza/notebooks/cli.py` GROUPS tuple to
      register `10_marimo_dashboards` between `09_official_media`
      and `10_mmo` so the CLI's `list 10_marimo_dashboards` matches
      the convention used by the other 12 functional groups.

## 3. Create the 10 marimo dashboards

- [x] **3.1** Create
      `ciolanza/notebooks/10_marimo_dashboards/01_biep_corpus_overview.py`
      (~343 lines; 5 charts: subject×level heatmap, per-year stacked
      area, EN/GA grouped bar, per-subject depth bar, engine health
      banner; covers R1 + R9 corpus matrix).
- [x] **3.2** Create
      `ciolanza/notebooks/10_marimo_dashboards/02_cognee_knowledge_graph.py`
      (~376 lines; 5 charts: nodes-per-subject×type bar, edges-per-type
      grouped bar, subject-pair relation matrix, island detection, live
      `cognee.search` query box; covers R2 cognify cohort view).
- [x] **3.3** Create
      `ciolanza/notebooks/10_marimo_dashboards/03_cross_archive_navigation.py`
      (~346 lines; 5 charts: book×subject heatmap, join-strength by
      subject×language bar, top-15 strongest edges horizontal bar,
      per-level distribution stacked bar, orphan detection; covers R3).
- [x] **3.4** Create
      `ciolanza/notebooks/10_marimo_dashboards/04_lakehouse_table_browser.py`
      (~339 lines; 5 charts: tables-per-schema bar, top-15 row counts
      log-scale bar, row-size histogram, full table list (table-md),
      live `mo.sql` SQL console against `md:oideachais`; covers R3
      lakehouse + ducklake half).
- [x] **3.5** Create
      `ciolanza/notebooks/10_marimo_dashboards/05_baml_extraction_log_viewer.py`
      (~349 lines; 5 charts: call counts per function, latency boxplot
      per function, success-rate over time line, retry/timeout counts
      per function, live `b.ExtractCurriculumSyllabus` invocation +
      typed Pydantic dump; covers R7).
- [x] **3.6** Create
      `ciolanza/notebooks/10_marimo_dashboards/06_per_subject_analytics.py`
      (~311 lines; 5 charts + ibis-first canonical R9 wiring
      (`ibis.duckdb.connect("md:oideachais")` first cell), subject×year
      heatmap, level distribution stacked bar, language per-year line,
      YoY-growth per subject grouped bar, live BAML `ExtractExamPaperLayout`;
      covers R6 + R9).
- [x] **3.7** Create
      `ciolanza/notebooks/10_marimo_dashboards/07_gaeilge_language_coverage.py`
      (~346 lines; 5 charts: EN vs GA per subject, GA-by-level line,
      fada-preservation + síneadh-fada heatmap, punctum-delens
      coverage bar (ḃ ċ ḋ ġ ṁ ṗ ṡ ṫ), quality-ratio histogram; covers R2
      bilingual arm).
- [x] **3.8** Create
      `ciolanza/notebooks/10_marimo_dashboards/08_cocoindex_v1_conformance_dashboard.py`
      (~329 lines; 5 charts: per-App v1-conformance table-grid,
      embedder×App matrix, LanceDB row coverage per App, Apps-not-
      using-BAAI/bge-m3 highlight list, log-scaled per-App row count
      bar; covers R10).
- [x] **3.9** Create
      `ciolanza/notebooks/10_marimo_dashboards/09_agent_memory_dashboard.py`
      (~389 lines; 5 charts: per-backend counts grouped bar (Cognee /
      Graphiti / LanceDB / Letta), `cognee.search()` query box,
      Graphiti temporal episode fan-out timeline, LanceDB subject-pair
      similarity heatmap, agent ↔ memory-backend wiring matrix; covers
      R2 + R7).
- [x] **3.10** Create
      `ciolanza/notebooks/10_marimo_dashboards/10_dagster_asset_lineage.py`
      (~374 lines; 5 charts: per-asset success rate bar, top-15 slowest
      assets bar, asset group × status stacked bar, pending
      re-materialisation flag list, Dagster SDA sensor health banner
      (live `dg sensor list` subprocess + simulated fallback);
      covers R7 + R9).

- [x] **3.11** All 10 notebooks use:
  - PEP 723 inline dependency header (`requires-python = ">=3.12"`
    + `dependencies = ["marimo>=0.13.0", ...]`)
  - `__generated_with = "0.13.0"`
  - The underscore-prefix convention (`_intro`, `_viz_*`, etc.) for
    cell-local variables
  - 3-5 altair `Chart().mark_*()...` visualisations per notebook
  - MotherDuck + DuckDB connection with graceful local-DuckDB
    fallback (or ibis.duckdb.connect() for `06_per_subject_analytics.py`)
  - try/except-wrapped BAML `b.ExtractCurriculumSyllabus` /
    `b.ExtractExamPaperLayout` invocations (when BAML client is
    available) so the notebooks render offline

## 4. Verify the 10 dashboards AST-parse

- [x] **4.1** Run `ast.parse(open(f).read())` on each of the 10 files
      — all 10 pass without SyntaxError.
- [x] **4.2** Run `python3 -m py_compile <file>` on each of the 10
      files — all 10 compile cleanly.

## 5. Verify CLI discovery + reference-notebook regression

- [x] **5.1** Run `uv run cianfhoghlaim-marimo list 10_marimo_dashboards`
      — discovers all 10 dashboards, reports "10 notebooks in
      10_marimo_dashboards/".
- [x] **5.2** AST-parse the 5 reference notebooks to confirm the
      change does not break existing
      `ciolanza/notebooks/{03_leaving_cert/01_chemistry_analysis,
      04_biep_motherduck/07_subject_full_pipeline,
      leaving_cert/chemistry,
      13_baml_cocoindex_tutorial/01_baml_post_v4_syntax,
      09_official_media/03_post_trends}.py` — all 5 pass.

## 6. Write the openspec change

- [x] **6.1** Create `proposal.md` (Why + What + Dependencies +
      Cross-repo sync).
- [x] **6.2** Create `tasks.md` (the 6 task groups above).
- [x] **6.3** Create `specs/oideachais-marimo-dashboards/spec.md`
      delta — 1 MODIFIED requirement "Phase 1 complete: 10
      requirements all functional; 10 marimo dashboards at
      `notebooks/10_marimo_dashboards/0[1-9]_*.py` + `10_*.py`
      exist + AST-parse cleanly + render via
      `uv run cianfhoghlaim-marimo list 10_marimo_dashboards`".

## 7. Commit + push

- [x] **7.1** Stage the 10 dashboards + cli.py GROUPS tuple + the
      3 openspec change artifacts.
- [x] **7.2** Commit with the conventional message
      `feat(dashboards): ship 10 oideachais marimo dashboards`.
- [x] **7.3** Push to `origin/pick-4-biep-v1` (NOT `main`).
