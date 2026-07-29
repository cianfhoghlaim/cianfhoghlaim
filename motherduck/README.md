# `motherduck/` — MotherDuck Dives + Flights

> **The 53 MotherDuck Dive definitions + 27 MotherDuck Flight files for the BIEP v1 + BIEP v3 lakehouse.**

## Quick start

```bash
# The canonical 4 BIEP v1 Dives are accessible via the package entry-point
python -c "from motherduck import BIEP_DIVES; print([d.name for d in BIEP_DIVES])"
# -> ['lc_syllabus_topics', 'lc_exam_difficulty', 'lc_marking_complexity', 'gov_circulars_archive']

# Save all 4 Dives to the MotherDuck workspace
python -c "from motherduck import save_all; save_all()"
# -> 4

# Run the canonical v1 daily Flight (locally; no MotherDuck auth needed)
python -c "from motherduck import lc_pdf_sync_flight_main; print(lc_pdf_sync_flight_main.__name__)"
# -> 'main'

# Dry-run a Flight registration
python -c "from motherduck import run_flight; print(run_flight(name='test', cron='0 4 * * *', dry_run=True))"
```

## Layout — 2 sub-trees

```
motherduck/
├── __init__.py               # The canonical entry-point (BIEP_DIVES, DiveRegistry,
│                             # DiveSpec, save_all, lc_pdf_sync_flight_main, run_flight)
├── dives/                    # 53 Dive definitions
│   ├── __init__.py           # BIEP_DIVES tuple + DiveRegistry class + re-exports
│   ├── lc_syllabus_topics.py     # BIEP v1 canonical
│   ├── lc_exam_difficulty.py     # BIEP v1 canonical
│   ├── lc_marking_complexity.py  # BIEP v1 canonical
│   ├── gov_circulars_archive.py  # BIEP v1 canonical (gov.ie circulars)
│   ├── ireland_lc_syllabus_topics.py  # BIEP v3 Ireland LC (replaces v1)
│   ├── ireland_jc_curriculum_topics.py # BIEP v3 Ireland JC
│   ├── england_a_level_complexity.py  # BIEP v3 England A-Level
│   ├── england_aqa_curriculum_dive.sql # BIEP v3 England AQA
│   ├── england_gcse_complexity.py     # BIEP v3 England GCSE
│   ├── england_gcse_difficulty_dive.sql # BIEP v3 England GCSE
│   ├── jc_curriculum_dive.sql          # BIEP v3 JC (Ireland)
│   ├── meaisin_evaluation_summary_dive.py # meaisínfhoghlaim OCR eval
│   ├── filesystem_sources_overview_dive.py # filesystem DLT summary
│   ├── guernsey_curriculum_dive_v2.py # Crown Dependencies
│   ├── isle_of_man_curriculum_dive_v2.py # Crown Dependencies
│   └── ... (39 more jurisdiction/v3 Dives)
└── flights/                  # 27 Flight files + registry
    ├── __init__.py           # run_flight() + lc_pdf_sync_flight_main re-export
    ├── config.yaml           # The 13 BIEP v3 Flight registry
    ├── lc_pdf_sync_flight.py # The canonical v1 daily Flight (CocoIndex + Dagster)
    ├── ireland_lc_daily_sync_flight.py # BIEP v3 Ireland LC (real impl)
    ├── ireland_full_coverage_flight.py # BIEP v3 Ireland (13-line stub)
    ├── england_full_coverage_flight.py # BIEP v3 England (13-line stub)
    ├── sct_wls_ni_flight.py             # BIEP v3 Scotland + Wales + NI (66-line real)
    ├── crown_dependencies_flight.py    # BIEP v3 Crown (66-line real)
    ├── filesystem_monthly_sync_flight.py
    ├── language_monthly_sync_flight.py
    ├── eu_official_daily_sync_flight.py    # stub
    ├── eu_nation_daily_sync_flight.py      # stub
    ├── british_isles_daily_sync_flight.py  # stub
    ├── commonwealth_daily_sync_flight.py   # stub
    ├── americas_daily_sync_flight.py       # stub
    ├── canada_daily_sync_flight.py         # stub
    ├── nigeria_daily_sync_flight.py        # stub
    ├── eu_multilingual_daily_sync_flight.py # stub
    └── ireland_full_coverage_flight.sql
        # (plus 5 sibling .sql Flights + 4 jurisdiction_full_coverage_flight.sql)
```

**Total:** 49 `.py` Dives + 4 `.sql` Dives + 20 `.py` Flights + 6 `.sql`
Flights + 1 `config.yaml` + 1 root `__init__.py` + 2 sub-tree
`__init__.py`s = **83 files**.

## The 4 canonical BIEP v1 Dives

| Dive | SQL surface |
|:--|:--|
| `lc_syllabus_topics` | Topic frequency per LC subject per year (filterable by level + language) |
| `lc_exam_difficulty` | Average marks per question per paper (with difficulty band classification) |
| `lc_marking_complexity` | Descriptor word count + grade-band distribution per marking scheme |
| `gov_circulars_archive` | Gov.ie circulars + syllabus links (DES/NCCA/SEC/DOE_NI) |

Each Dive is a `DiveSpec` dataclass with `name + description + sql +
charts + filters`. The MotherDuck `save_dive` MCP tool consumes the
serialised dict via `DiveSpec.to_dict()`.

## The 13 BIEP v3 Flights (in `flights/config.yaml`)

| Flight | Cron | TZ |
|:--|:--|:--|
| `eu_official_daily_sync_flight` | `0 5 * * *` | UTC |
| `eu_nation_daily_sync_flight` | `0 6 * * *` | UTC |
| `commonwealth_daily_sync_flight` | `0 6 * * *` | UTC |
| `americas_daily_sync_flight` | `0 6 * * *` | UTC |
| `british_isles_daily_sync_flight` | `0 5 * * *` | UTC |
| `canada_daily_sync_flight` | `0 6 * * *` | UTC |
| `nigeria_daily_sync_flight` | `0 6 * * *` | UTC |
| `eu_multilingual_daily_sync_flight` | `0 5 * * *` | UTC |
| `ireland_full_coverage_flight` | `0 2 * * *` | UTC |
| `england_full_coverage_flight` | `0 3 * * *` | UTC |
| `sct_wls_ni_flight` | `0 4 * * *` | UTC |
| `crown_dependencies_flight` | `30 4 * * *` | UTC |

## Database URI conventions

| Surface | URI pattern |
|:--|:--|
| BIEP v1 structured rows | `md:cianfhoghlaim.leaving_cert.*` |
| BIEP v1 status rows | `md:cianfhoghlaim.lc_ops.daily_sync_status` |
| BIEP v3 typed + voted rows | `md:cianfhoghlaim.education.<jurisdiction>.<stage>.<subject>.<variant>` |
| BIEP v3 status rows | `md:cianfhoghlaim.education.<jurisdiction>._audit.daily_sync_status` |
| Government circulars (legacy v1 namespace) | `md:oideachais.government.circulars` |

## Cross-references

- [`AGENTS.md`](AGENTS.md) — the canonical quadrant overview (the agent-facing entry point)
- [`../.agents/skills/motherduck/SKILL.md`](../.agents/skills/motherduck/SKILL.md) — MotherDuck master skill
- [`../.agents/skills/motherduck-create-dive/SKILL.md`](../.agents/skills/motherduck-create-dive/SKILL.md) — Dive authoring recipe
- [`../.agents/skills/motherduck-create-flight/SKILL.md`](../.agents/skills/motherduck-create-flight/SKILL.md) — Flight authoring recipe
- [`../dlt_sources/AGENTS.md`](../dlt_sources/AGENTS.md) — the DLT ingestion layer
- [`../cocoindex/AGENTS.md`](../cocoindex/AGENTS.md) — the CocoIndex embedding layer
- [`../orchestration/README.md`](../orchestration/README.md) — the Dagster orchestration layer
- [`../bonneagar/stacks/motherduck/`](../bonneagar/stacks/motherduck/) — the IaC stack provider
- [`../openspec/specs/british-isles-education-pipeline-v3/spec.md`](../openspec/specs/british-isles-education-pipeline-v3/spec.md) — BIEP v3 spec