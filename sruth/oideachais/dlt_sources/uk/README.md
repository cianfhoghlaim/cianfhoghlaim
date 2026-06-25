# `oideachais/dlt_sources/uk/` — UK & Crown Dependencies DLT Sources

**Last updated:** 2026-06-16

DLT sources for the United Kingdom and the Crown Dependencies (Channel Islands, Isle of Man). 16 dlt source files across 5 territories.

## Coverage matrix

Status: ✅ working · ⚠️ partial · 🟡 planned · ❌ missing

| Territory | Cycle | dlt source | BAML extract | Dagster asset | Cognee | CocoIndex |
|:--|:--|:--|:--|:--|:--|:--|
| **England** | DfE statistics | `uk/england/dfe_explore_statistics.py` ✅ | (none) | `uk_education_assets.py:england_dfe_statistics` ✅ | (none) | (none) |
| **England** | National Curriculum | `uk/england/national_curriculum.py` ✅ | (none) | `uk_education_assets.py` (England) ✅ | (none) | (none) |
| **England** | Ofsted | `uk/england/ofsted.py` ✅ | (none) | `uk_education_assets.py` ✅ | (none) | (none) |
| **England** | School info | `uk/england/school_info.py` ✅ | (none) | `uk_education_assets.py` ✅ | (none) | (none) |
| **England** | Key Stage 1-2 (primary) | ❌ missing | (none) | (planned) | (none) | (none) |
| **England** | Key Stage 3-4 (secondary) | ❌ missing | (none) | (planned) | (none) | (none) |
| **Scotland** | Curriculum for Excellence | `uk/scotland/curriculum_for_excellence.py` ✅ | (none) | `uk_education_assets.py` (Scotland) ✅ | (none) | (none) |
| **Scotland** | Gov.scot statistics | `uk/scotland/gov_scot_statistics.py` ✅ | (none) | ✅ | (none) | (none) |
| **Scotland** | Insight benchmarking | `uk/scotland/insight_benchmarking.py` ✅ | (none) | ✅ | (none) | (none) |
| **Scotland** | SIMD | `uk/scotland/simd.py` ✅ | (none) | ✅ | (none) | (none) |
| **Scotland** | CfE Early Level (primary) | ❌ missing | (none) | (planned) | (none) | (none) |
| **Scotland** | CfE First/Second Level (lower secondary) | ❌ missing | (none) | (planned) | (none) | (none) |
| **Wales** | Curriculum for Wales | `uk/wales/curriculum_for_wales.py` ✅ | (none) | `uk_education_assets.py` (Wales) ✅ | (none) | (none) |
| **Wales** | StatsWales | `uk/wales/statswales.py` ✅ | (none) | ✅ | (none) | (none) |
| **Wales** | Estyn (inspections) | `uk/wales/estyn.py` ✅ | (none) | ✅ | (none) | (none) |
| **Wales** | Foundation Phase (primary) | ❌ missing | (none) | (planned) | (none) | (none) |
| **Northern Ireland** | CCEA curriculum | `uk/northern_ireland/ccea_curriculum.py` ✅ | (none) | `uk_education_assets.py` (NI) ✅ | (none) | (none) |
| **Northern Ireland** | Education NI | `uk/northern_ireland/education_ni.py` ✅ | (none) | ✅ | (none) | (none) |
| **Northern Ireland** | ETI (inspections) | `uk/northern_ireland/etini.py` ✅ | (none) | ✅ | (none) | (none) |
| **Northern Ireland** | NISRA (statistics) | `uk/northern_ireland/nisra.py` ✅ | (none) | ✅ | (none) | (none) |
| **Northern Ireland** | Foundation Stage (primary) | ❌ missing | (none) | (planned) | (none) | (none) |
| **Guernsey (GGY)** | All | `crown_dependencies/channel_islands.py` ✅ | (none) | (planned) | (none) | (none) |
| **Jersey (JEY)** | All | `crown_dependencies/channel_islands.py` ✅ | (none) | (planned) | (none) | (none) |
| **Isle of Man (IOM)** | All | `crown_dependencies/isle_of_man.py` ✅ | (none) | (planned) | (none) | (none) |

## Cross-cutting gap

Primary (Key Stage 1-2 / CfE Early-First Level / Foundation Phase / Foundation Stage) and lower-secondary (Key Stage 3 / CfE Second Level / KS3) BAML extraction is **missing for all 5 territories**. See `oideachais/REFACTORING.md` Feature 1 for the queued fix.

## Source URLs (canonical, used by the dlt sources)

- **England**: DfE explore-education-statistics.service.gov.uk, nationalcurriculum.uk, gov.uk/government/organisations/ofsted
- **Scotland**: education.gov.scot, gov.scot/collections/scottish-government-statistics, scotland.shinyapps.io/Insight, simd.scot
- **Wales**: gov.wales/curriculum-wales, statswales.gov.wales, estyn.gov.wales
- **Northern Ireland**: ccea.org.uk, education-ni.gov.uk, etini.gov.uk, nisra.gov.uk
- **Guernsey / Jersey / Isle of Man**: gov.gg, gov.je, gov.im

## How dlt sources are registered

`oideachais/dlt_sources/uk/__init__.py` re-exports `england`, `scotland`, `wales`, `northern_ireland`. The `oideachais/dlt_sources/__init__.py` does NOT re-export these submodules directly — the canonical pattern is `from oideachais.dlt_sources.uk import england`.

## How Dagster assets are registered

`oideachais/dagster_defs/assets/uk_education_assets.py` exports a list of `@asset`s for each nation + cycle. The list is added to `oideachais/dagster_defs/definitions.py:combined_assets` and shows up in the `dg dev` UI under the `uk_education` group.

## Related

- `oideachais/dlt_sources/ireland/README.md` — Ireland coverage matrix.
- `oideachais/dlt_sources/crown_dependencies/` — GG, JE, IM sources.
- `oideachais/dlt_sources/domains/education/{en,sct,wls,ni,ggy,jey,iom}/` — domain-specific cross-nation sources.
- `oideachais/STATUS.md` § 2 — per-nation × per-cycle coverage matrix.
