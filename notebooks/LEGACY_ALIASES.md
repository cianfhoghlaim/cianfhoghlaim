# LEGACY_ALIASES — notebooks/

Per the
[`2026-07-17-pipeline-directory-consolidation-v1`](../../changes/2026-07-17-pipeline-directory-consolidation-v1/proposal.md)
openspec change. Notebooks are leaf artefacts (no code imports), so
the migration is a directory rename with no deprecation shim required.

## Renamed directories

| Old | New |
|:--|:--|
| `notebooks/01_dev_env/` | `notebooks/dev_env/` |
| `notebooks/02_vision_models/` | `notebooks/vision_models/` |
| `notebooks/03_leaving_cert/` (merged with `leaving_cert/`) | `notebooks/leaving_cert/` |
| `notebooks/04_biep_motherduck/` | `notebooks/data_platform/biep_motherduck/` |
| `notebooks/05_lakehouse_inspect/` | `notebooks/data_platform/lakehouse_inspect/` |
| `notebooks/06_observability/` | `notebooks/observability/` |
| `notebooks/07_educational_stages/` | `notebooks/educational_stages/` |
| `notebooks/08_sources/` | `notebooks/sources/` |
| `notebooks/09_official_media/` | `notebooks/official_media/` |
| `notebooks/10_cognify/` | `notebooks/data_platform/cognify/` |
| `notebooks/10_marimo_dashboards/` + `notebooks/11_marimo_dashboards_v2/` | `notebooks/marimo_dashboards/` (consolidated) |
| `notebooks/10_mmo/` | `notebooks/mmo/` |
| `notebooks/11_speedrun/` | `notebooks/speedrun/` |
| `notebooks/12_ireland_law/` | `notebooks/ireland_law/` |
| `notebooks/12_semantic_search/` | `notebooks/semantic_search/` |
| `notebooks/12_subject_study_tools/` | `notebooks/subject_study_tools/` |
| `notebooks/13_baml_cocoindex_tutorial/` | `notebooks/baml_cocoindex_tutorial/` |
| `notebooks/14_academic_history/` | `notebooks/academic_history/` |
| `notebooks/16_celtic_language/` | `notebooks/celtic_language/` |