# `notebooks/` — Marimo dashboards for the BIEP lakehouse

> **The 107 active marimo notebooks for the British-Isles Education Pipeline (BIEP). Each notebook is a reactive dashboard AND a standalone CLI script (dual-mode).**
>
> Post-v7 flattening (2026-07-17) the canonical layout is **flat-numbered** — `notebooks/<NN>_<topic>_<NN>_<slug>.py` files at the repo root, not the 11-group subdirectory layout that older docs describe.

## Quick start

```bash
# Interactive — pick a notebook and open it
uv run marimo edit notebooks/01_overview_setup.py

# CLI — invoke from any cwd (the notebook's @__main__ guard detects <flags>)
uv run notebooks/01_overview_setup.py --query "Dagster asset"

# The 5-tab deployment control panel (Models / Pipelines / Datasets / Stacks / Registry)
mise run notebook:control-panel
# or: marimo edit notebooks/00_control_panel.py

# Discover + run via the CLI wrapper
uv run python notebooks/cli.py list
uv run python notebooks/cli.py run 14_dev_env_tools_01 -- --query "my query"

# Smoke test the canonical nb_utils helpers
mise run notebook:smoke
```

## Layout — flat-numbered

```
notebooks/
├── __init__.py                  # Package marker
├── __marimo__/                  # Marimo session cache (auto-generated)
├── _shared/                     # Canonical helpers (see "Canonical helpers" below)
│   ├── db.py                    # ibis-first lakehouse connection helpers
│   ├── schema.py                # 5 lakehouse introspection helpers (NEW 2026-08-15)
│   ├── deployment_choice.py     # atomic read/write of deployment-choice.yaml (NEW)
│   ├── area_shims/              # Per-area shims (leaving_cert.py for BIEP v3 dashboards)
│   └── ...
├── analysis_plan/               # 5 markdown files (aistear / primary / junior_cycle / senior_cycle / tertiary)
├── subject_study_tools/         # Cloudflare Worker (deploy.sh + Dockerfile + wrangler.jsonc)
├── legacy/                      # 1 README.md + empty __init__.py (the pre-v7 directory is gone)
├── nb_utils.py                  # The legacy canonical helper module (re-exports from _shared/db.py)
├── cli.py                       # The `notebooks` CLI wrapper (list + run + edit + dashboard subcommands)
│
├── 00_control_panel.py                                            # NEW 2026-08-15: the 5-tab deployment control panel
├── 01_overview_setup.py                                              # BIEP overview + setup
├── 02_education_overview.py                                          # Education overview
├── 05_england_aqa_ocr_edexcel.py                                     # England AQA / OCR / Edexcel OCR comparison
├── 06_celtic_languages__shared.py                                     # 1 of 7 — Celtic languages shared
├── 06_celtic_languages_01_gaois_terminology_explorer.py               # Gaois.ie terminology
├── 06_celtic_languages_02_duchas_folklore_with_bboxes.py              # Dúchas folklore with bboxes
├── 06_celtic_languages_03_heritage_sites_map.py                       # Heritage sites map
├── 06_celtic_languages_04_canuint_dialect_player.py                   # Canúint dialect player
├── 06_celtic_languages_05_ud_celtic_treebank_viewer.py                # UD Celtic treebank viewer
├── 06_celtic_languages_06_local_documents_subject_viewer.py           # Local documents subject viewer
├── 06_celtic_languages_07_celtic_curriculum_browser.py                # Celtic curriculum browser
├── 07_junior_cycle_ireland.py                                        # Junior Cycle Ireland
├── 08_ocr_ensemble_audit.py                                          # OCR ensemble audit
│
├── 10_biep_pipeline_lakehouse_01_curriculum_educator.py              # 17 of 17 — BIEP lakehouse (curriculum_educator)
├── 10_biep_pipeline_lakehouse_01_ducklake_explorer.py                # DuckLake explorer
├── 10_biep_pipeline_lakehouse_01_knowledge_graph.py                  # Knowledge graph
├── 10_biep_pipeline_lakehouse_02_lakehouse_inspector.py              # Lakehouse inspector
├── 10_biep_pipeline_lakehouse_02_syllabus_visualizer.py              # Syllabus visualizer
├── 10_biep_pipeline_lakehouse_03_all_nations.py                      # All nations
├── 10_biep_pipeline_lakehouse_03_dlt_pipeline_overview.py            # DLT pipeline overview
├── 10_biep_pipeline_lakehouse_04_cocoindex_embedding_coverage.py     # CocoIndex embedding coverage
├── 10_biep_pipeline_lakehouse_04_university_courses.py               # University courses
├── 10_biep_pipeline_lakehouse_05_marking_scheme_analyzer.py          # Marking scheme analyzer
├── 10_biep_pipeline_lakehouse_06_exam_papers_explorer.py             # Exam papers explorer
├── 10_biep_pipeline_lakehouse_07_subject_full_pipeline.py            # Subject full pipeline
├── 10_biep_pipeline_lakehouse_08_leabharlann_full_stack_demo.py      # Leabharlann full-stack demo
├── 10_biep_pipeline_lakehouse_09_pipeline_e2e_test.py                 # Pipeline E2E test
├── 10_biep_pipeline_lakehouse_10_leabharlann_descriptive.py          # Leabharlann descriptive
├── 10_biep_pipeline_lakehouse_11_dpre_lag_analysis.py               # DPRE lag analysis
├── 10_biep_pipeline_lakehouse_semantic_01_search.py                  # Semantic search
│
├── 11_irish_law_01_personal_injury_journey.py                         # 6 of 6 — Irish law (personal injury)
├── 11_irish_law_02_courts_journey.py                                 # Courts journey
├── 11_irish_law_03_wrc_complaints.py                                # WRC complaints
├── 11_irish_law_04_citizensinformation.py                           # CitizensInformation
├── 11_irish_law_05_unified_cross_source.py                          # Unified cross-source
├── 11_irish_law_06_gov_ie_legal.py                                  # gov.ie legal
│
├── 12_corpus_overview__shared.py                                     # 1 of 21 — Corpus overview shared
├── 12_corpus_overview_01_biep.py                                     # BIEP corpus overview
├── 12_corpus_overview_02_leabharlann.py                             # Leabharlann corpus overview
├── 12_corpus_overview_03_cognee.py                                  # Cognee knowledge graph
├── 12_corpus_overview_04_embedding_coverage.py                      # Embedding coverage
├── 12_corpus_overview_05_baml_extraction_log.py                     # BAML extraction log
├── 12_corpus_overview_06_university_matrix.py                      # University matrix
├── 12_corpus_overview_07_gaeilge_language_coverage.py               # Gaeilge coverage
├── 12_corpus_overview_08_cocoindex_v1_conformance.py                # CocoIndex v1 conformance
├── 12_corpus_overview_09_qqi_nfq_ladder.py                          # QQI NFQ ladder
├── ... (12 more)
│
├── 13_official_media_01_official_media.py                            # 7 of 7 — Official media
├── 13_official_media_02_email_inbox_triage.py
├── 13_official_media_03_post_trends.py
├── 13_official_media_04_mention_network.py
├── 13_official_media_05_fediverse_coverage.py
├── 13_official_media_06_cross_archive.py
├── 13_official_media_07_moderation_sentiment.py
│
├── 14_dev_env_tools_01_ccc_search.py                                # 6 of 6 — Dev-env tools (CCC search)
├── 14_dev_env_tools_02_drift_detect.py                              # Drift detect
├── 14_dev_env_tools_03_firecrawl_refactor.py                        # Firecrawl refactor
├── 14_dev_env_tools_04_hf_best_model.py                             # HuggingFace best model
├── 14_dev_env_tools_05_openspec_list.py                             # OpenSpec list
├── 14_dev_env_tools_06_mise_lint_skills.py                          # mise lint:skills
│
├── 15_observability_01_baml_drift_audit.py                          # 3 of 3 — Observability (BAML drift audit)
├── 15_observability_02_irish_extraction_quality.py                   # Irish extraction quality
├── 15_observability_03_cognee_kg.py                                 # Cognee knowledge graph
│
├── 16_speedrun_mmo__shared.py                                       # 1 of 12 — SpeedRun MMO shared
├── 16_speedrun_mmo_01_*.py ... 12_*.py                              # (12 numbered SpeedRun challenges)
│
├── 17_academic_history__common.py                                   # 1 of 9 — Academic history common
├── 17_academic_history_01_uog_math_corpus.py                         # UoG maths corpus
├── 17_academic_history_02_uog_module_map.py                         # UoG module map
├── ... (7 more — Stats & Numerical Analysis Labs)
│
├── 18_cianfhoghlaim_subject_registry.py                             # 1 — Subject registry (the 544 Ireland rows)
│
├── 19_ireland_pipeline_dashboard.py                                 # 1 — BIEP v3 Ireland jurisdiction dashboard
├── 20_england_pipeline_dashboard.py                                 # 1 — BIEP v3 England jurisdiction dashboard
├── 21_sct_wls_ni_pipeline_dashboard.py                              # 1 — BIEP v3 Scotland + Wales + NI dashboard
├── 22_crown_dependencies_dashboard.py                               # 1 — BIEP v3 Crown Dependencies dashboard
├── 23_8_jurisdiction_overview.py                                    # 1 — BIEP v3 8-jurisdiction overview
│
├── 40_leaving_cert_subject_panel.py                                 # 1 — The canonical 6-subject LC panel
│
└── ie_law_explorer.py                                               # 1 — Irish Law standalone explorer (pre-numbering)
```

**Total**: 101 active flat-numbered notebooks + 1 legacy dir (`legacy/` with only a README + empty `__init__.py`) + 2 shared helpers.

## Numbering convention

| Prefix | Group | Count |
|:--|:--|--:|
| `00_` | **Deployment control panel** (NEW 2026-08-15: the 5-tab marimo control panel reading `MODEL_REGISTRY` + `notebooks/_shared/schema.py` + writing `deployment-choice.yaml`) | 1 |
| `01_` | Overview + setup | 1 |
| `02_` | Education overview | 1 |
| `05_` | England AQA / OCR / Edexcel OCR comparison | 1 |
| `06_celtic_languages_` | Celtic-language corpus (Gaois / Dúchas / Heritage / Canúint / UD / Local / Curriculum) | 8 |
| `07_` | Junior Cycle Ireland | 1 |
| `08_` | OCR ensemble audit | 1 |
| `10_biep_pipeline_lakehouse_` | BIEP lakehouse (curriculum_educator / ducklake_explorer / knowledge_graph / lakehouse_inspector / syllabus_visualizer / all_nations / dlt_pipeline_overview / cocoindex_embedding_coverage / university_courses / marking_scheme_analyzer / exam_papers_explorer / subject_full_pipeline / leabharlann_full_stack_demo / pipeline_e2e_test / leabharlarn_descriptive / dpre_lag_analysis / semantic_search) | 17 |
| `11_irish_law_` | Irish law (personal_injury / courts / WRC / citizensinformation / gov_ie_legal / unified_cross_source) | 6 |
| `12_corpus_overview_` | Corpus overview (BIEP / Leabharlann / Cognee / embedding_coverage / BAML_extraction_log / university_matrix / QQI_NFQ / Gaeilge_coverage / CocoIndex_v1_conformance / ... + 1 shared) | 21 |
| `13_official_media_` | Official media (official_media / email_inbox_triage / post_trends / mention_network / fediverse_coverage / cross_archive / moderation_sentiment) | 7 |
| `14_dev_env_tools_` | Dev-env tools (ccc_search / drift_detect / firecrawl_refactor / hf_best_model / openspec_list / mise_lint_skills / model_registry) | 7 |
| `15_observability_` | Observability (BAML_drift_audit / Irish_extraction_quality / Cognee_KG) | 3 |
| `16_speedrun_mmo_` | SpeedRunEthereum challenges (12 numbered + 1 shared) | 12 |
| `17_academic_history_` | Academic history (UoG maths + module map + Stats labs) | 9 |
| `18_` | Subject registry (the 544 Ireland rows) | 1 |
| `19_` | BIEP v3 Ireland dashboard | 1 |
| `20_` | BIEP v3 England dashboard | 1 |
| `21_` | BIEP v3 Scotland + Wales + NI dashboard | 1 |
| `22_` | BIEP v3 Crown Dependencies dashboard | 1 |
| `23_` | BIEP v3 8-jurisdiction overview | 1 |
| `40_` | LC subject panel (the canonical 6-subject dashboard) | 1 |
| `ie_law_explorer.py` | Pre-numbering legacy (Irish Law standalone) | 1 |

**Total**: 107 active notebooks.

## Dual-mode pattern (`@app.cell` + `if __name__ == "__main__":`)

Every refactored notebook under `01..40_*` supports both execution modes:

| Mode | Command |
|:--|:--|
| **marimo edit** | `marimo edit notebooks/01_overview_setup.py` |
| **marimo run**  | `marimo run  notebooks/01_overview_setup.py` |
| **CLI script**  | `python notebooks/01_overview_setup.py --query "..."` |
| **CLI via uv**  | `uv run notebooks/01_overview_setup.py --query "..."` |

The CLI mode uses each notebook's `if __name__ == "__main__":` guard which parses the BIEP canonical flags (`--subject`, `--level`, `--language`, `--year`, `--limit`) via `nb_utils.cl_argument_parser()` and prints the same data to stdout.

> **Historical note**: The previous documentation claimed `@app.setup` + `@app.function` (the marimo async/streaming pattern). The actual pattern is the standard marimo `@app.cell` (reactive cells) + `if __name__ == "__main__":` guard. These are not even in `_shared/db.py` or `nb_utils.py`.

## Canonical helpers

`_shared/db.py` (403 lines) is the canonical ibis-first lakehouse connection home:

```python
from notebooks._shared.db import (
    connect_md,                  # ibis-first MotherDuck connect (use_md=True|False)
    connect_local,               # in-memory DuckDB
    connect_local_lakehouse,     # local DuckLake
    connect_lance,               # LanceDB vector store
    format_snake_case_cohort_path,# BIEP v3 path helper
    compute_ragas_distribution,  # eval metric
    lakehouse_uri,               # returns 'md:cianfhoghlaim' (or env override)
    LAKEHOUSE_URI_DEFAULT,       # 'md:cianfhoghlaim'
)
```

`_shared/schema.py` (NEW 2026-08-15) is the canonical **lakehouse introspection** home — 5 helpers that walk the BIEP + LanceDB + BAML surface:

```python
from notebooks._shared.schema import (
    schema_introspect,               # every BIEP DuckDB table + column metadata
    schema_introspect_table,         # the canonical column metadata for any table
    schema_introspect_full,          # DuckDB + LanceDB + BAML union (Tab 3 in 00_control_panel)
    list_dlt_sources,                # all 920 @dlt.source decorated functions + their primary keys
    list_cocoindex_apps,             # all 94+ CocoIndex Apps + their LanceDB mount targets
    list_baml_classes,               # all 838 BAML class definitions + their parent files
    read_deployment_choice,          # read deployment-choice.yaml (atomic + fcntl.flock)
    write_deployment_choice,         # write deployment-choice.yaml (atomic + fcntl.flock)
    deployment_choice_path,          # canonical path to deployment-choice.yaml
)
```

`_shared/deployment_choice.py` (NEW 2026-08-15) is the atomic write layer for `deployment-choice.yaml` — the canonical enablement file consumed by the 00_control_panel notebook, the web UI, and the CLI.

`_shared/db.py` + `_shared/schema.py` + `_shared/deployment_choice.py` are the three canonical helpers. Every notebook in this directory uses one or more of these.

`nb_utils.py` (269 lines) is the legacy module that re-exports from `_shared/db.py` + adds the BIEP-specific helpers:

```python
from notebooks.nb_utils import (
    connect_biep_lakehouse,       # MotherDuck + graceful local-DuckDB fallback
    connect_md_oideachais,        # bare MotherDuck connect (raises on failure)
    lc_subject_query,             # per-subject topic query
    leabharlann_join_to_lc,       # cross-archive join
    cl_argument_parser,           # argparse factory with BIEP canonical flags
    run_as_script,                # dual-mode CLI helper
    import_dev_env_tool,          # convenience helper for the dev_env tool module
    BIEP_SUBJECTS,                # The 6 LC priority subjects
    BIEP_LEVELS,                  # 'higher' / 'ordinary' / 'foundation'
    BIEP_LANGUAGES,               # 'en' / 'ga'
    REPO_ROOT,                    # The cianfhoghlaim monorepo root
)
```

> **Historical note**: The README used to claim `from cianfhoghlaim.notebooks import ...` for these helpers. Post-v7, the canonical import is `from notebooks._shared.db import ...` or `from notebooks.nb_utils import ...`. The pre-v7 path would fail with `ModuleNotFoundError`.

## Deployment choice + the control panel

`deployment-choice.yaml` (repo root) is the **canonical enablement file** — every model, pipeline, dataset, and stack is recorded here as `enabled_<key>: bool`. It is read and written by 3 surfaces:

1. **`notebooks/00_control_panel.py`** — the 5-tab marimo notebook (Models / Pipelines / Datasets / Stacks / Registry).
2. **The web UI** (deferred to issue #143) — at `web/apps/cianfhoghlaim-web/control-panel/` (planned).
3. **The CLI** — `bun run cianfhoghlaim models list` / `models enable <key>` / `pipelines list` / etc.

Open the control panel:

```bash
mise run notebook:control-panel
# or
marimo edit notebooks/00_control_panel.py
```

The control panel reads from `MODEL_REGISTRY` (52 entries / 7 families) + `notebooks/_shared/schema.py` introspection helpers, and writes the toggle state back to `deployment-choice.yaml` (atomic + `fcntl.flock`).

## BIEP canonical constants

| Constant | Value | Notes |
|:--|:--|:--|
| `BIEP_SUBJECTS` | `(mathematics, applied_mathematics, english, gaeilge, biology, chemistry)` | The 6 LC priority subjects (matches the spec claim) |
| `BIEP_LEVELS` | `('higher', 'ordinary', 'foundation')` | The 3 LC qualification levels |
| `BIEP_LANGUAGES` | `('en', 'ga')` | The 2 working languages |
| `LAKEHOUSE_URI_DEFAULT` | `'md:cianfhoghlaim'` | The MotherDuck database |

## The BIEP v3 jurisdiction dashboards

5 notebooks cover the BIEP v3 jurisdiction dashboards (per `2026-08-01-biep-v3-iac-pangolin-hostnames-v1`):

| Notebook | Purpose |
|:--|:--|
| `19_ireland_pipeline_dashboard.py` | BIEP v3 Ireland (the first jurisdiction; the canonical reference) |
| `20_england_pipeline_dashboard.py` | BIEP v3 England |
| `21_sct_wls_ni_pipeline_dashboard.py` | BIEP v3 Scotland + Wales + Northern Ireland |
| `22_crown_dependencies_dashboard.py` | BIEP v3 Crown Dependencies (Jersey + Guernsey + IoM) |
| `23_8_jurisdiction_overview.py` | BIEP v3 8-jurisdiction overview |

## The CLI wrapper (`notebooks/cli.py`)

```bash
# List all 101 active notebooks
uv run python notebooks/cli.py list

# Edit a notebook (marimo edit)
uv run python notebooks/cli.py edit 01_overview_setup

# Run a notebook as a CLI script
uv run python notebooks/cli.py run 14_dev_env_tools_01 -- --query "my query"

# Run a notebook's marimo dashboard server
uv run python notebooks/cli.py dashboard 10_biep_pipeline_lakehouse_01_ducklake_explorer
```

> **Historical note**: The CLI was originally designed to work with subdirectory groups (`01_dev_env/`, `02_vision_models/`, etc.). Those directories do NOT exist post-v7 — the layout is flat-numbered. The CLI now uses fallback glob patterns to discover notebooks by their flat-numbered prefix.

## Environment variables

| Variable | Default | Notes |
|:--|:--|:--|
| `MOTHERDUCK_TOKEN` | _required for MD_ | Read from Infisical `dev-baile` via mise |
| `MOTHERDUCK_ENABLED` | `false` | Set `true` to opt-in to `md:cianfhoghlaim` |
| `USE_LOCAL_SCRAPES` | `false` | Set `true` for the curated `stedding/ingest_queue/` snapshot fallback |
| `CIANFHOGHLAIM_LEAVING_CERT_ROOT` | `~/dev/.../leaving_certificate` | Override for the BIEP corpus directory |
| `CIANFHOGHLAIM_LAKEHOUSE_DUCKDB` | `md:cianfhoghlaim` | DuckDB attach string |
| `CIANFHOGHLAIM_ROOT` | `~/dev/kings_college_galway` | Repo root (overridden by `nb_utils.REPO_ROOT`) |

## Common issues

**`ModuleNotFoundError: No module named 'cianfhoghlaim'` when running a notebook as a CLI script.**

The notebook's `_cli_main` adds `<repo>/` to `sys.path` via
`Path(__file__).parents[2]`. If you've moved the notebook, update that
reference. Or run via `uv run` from the repo root — the venv already
has the package on `sys.path`.

**`marimo edit` opens but the cell errors with `ImportError` for the `dev_env` tool module.**

The 6 `14_dev_env_tools/*.py` notebooks compute the tool path via
`Path(__file__).resolve().parents[1] / 'agents' / 'adk' / 'tools' / 'dev_env.py'`.
If you move a notebook outside `14_dev_env_tools_*`, update that reference too.

## Cross-references

- [`AGENTS.md`](../AGENTS.md) — the agents sub-package overview
- [`../openspec/specs/oideachais-marimo-dashboards/spec.md`](../openspec/specs/oideachais-marimo-dashboards/spec.md) — the canonical spec
- [`../.agents/skills/dlt/SKILL.md`](../.agents/skills/dlt/SKILL.md) — DLT conventions used by notebooks
- [`../.agents/skills/baml/SKILL.md`](../.agents/skills/baml/SKILL.md) — BAML extraction patterns
- [`../.agents/skills/cocoindex/SKILL.md`](../.agents/skills/cocoindex/SKILL.md) — CocoIndex embedding patterns
- [`../.agents/skills/motherduck/SKILL.md`](../.agents/skills/motherduck/SKILL.md) — MotherDuck Dives + Flights
- [`../.agents/skills/marimo/SKILL.md`](../.agents/skills/marimo/SKILL.md) — marimo reactive notebooks
- [`../dlt_sources/AGENTS.md`](../dlt_sources/AGENTS.md) — the DLT ingestion layer (consumed by `notebooks/cli.py list`)
- [`../cocoindex/AGENTS.md`](../cocoindex/AGENTS.md) — the CocoIndex embedding layer (consumed by `10_biep_pipeline_lakehouse_*`)
- [`../motherduck/README.md`](../motherduck/README.md) — the MotherDuck Dives + Flights (consumed by `10_biep_pipeline_lakehouse_03_dlt_pipeline_overview.py`)
- [`../orchestration/README.md`](../orchestration/README.md) — the Dagster orchestration layer (consumed by `10_biep_pipeline_lakehouse_09_pipeline_e2e_test.py`)