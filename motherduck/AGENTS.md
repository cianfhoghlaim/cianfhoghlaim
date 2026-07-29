# `motherduck/` — MotherDuck Dives + Flights

> **The 53 MotherDuck Dive definitions + 27 MotherDuck Flight files for the BIEP v1 + BIEP v3 lakehouse.**
>
> The compute substrate (MotherDuck `compose.yaml` + `pangolin.yaml` + `secrets.env`) lives at `bonneagar/stacks/motherduck/`. The Python side — Dives that materialise BIEP dashboards and Flights that schedule the daily `lc_pdf_sync_flight` — lives here in `motherduck.{dives,flights}`.

## Priority quick reference

### Priority skills (2 of 53)

| Skill | When to load |
|:--|:--|
| [`motherduck`](../../.agents/skills/motherduck/SKILL.md) | The master routing skill — load this first for any MotherDuck work (architecture + connections + data-modeling + analytics + create-dive + create-flight) |
| [`motherduck-create-dive`](../../.agents/skills/motherduck-create-dive/SKILL.md) | The Dive authoring recipe (the `DiveSpec` dataclass + `to_dict()` + `save_dive` MCP tool) |

### Priority commands

```bash
# The canonical 4 BIEP v1 Dives (the package entry-point now works post-fix)
python -c "from motherduck import BIEP_DIVES, save_all; print(len(BIEP_DIVES), save_all())"
# -> 4 4

# The canonical daily Flight (the v1 BIEP entry-point)
python -c "from motherduck import lc_pdf_sync_flight_main; lc_pdf_sync_flight_main.__name__"
# -> 'main'

# Dry-run a Flight registration
python -c "from motherduck import run_flight; print(run_flight(name='test', cron='0 4 * * *', dry_run=True))"

# Save all Dives to the MotherDuck workspace (requires MOTHERDUCK_TOKEN)
MOTHERDUCK_TOKEN=$MOTHERDUCK_TOKEN python -c "from motherduck import save_all; print(save_all())"
```

### Priority compose stacks

`motherduck` (the MotherDuck SaaS compute stack — `compose.yaml` + `pangolin.yaml` + `secrets.env`) at `bonneagar/stacks/motherduck/`. The Python `motherduck/` sub-package is the consumer; the stack is the provider.

### Priority openspec specs (1 of 48)

| Spec | One-liner |
|:--|:--|
| [`british-isles-education-pipeline-v3`](../../openspec/specs/british-isles-education-pipeline-v3/spec.md) | The BIEP v3 spec — 14 MotherDuck Dives + 12 MotherDuck Flights across 5 jurisdictions |

### Priority mise tasks

```bash
mise run biep:v3:lakehouse:smoke-test   # The canonical BIEP lakehouse smoke test
mise run biep:v3:status               # Status of the BIEP v3 MotherDuck pipeline
```

## Overview

`motherduck/` is the **Python-side** of the BIEP lakehouse. It
houses:

- **`dives/`** — **49 Dive `.py` files** + **4 Dive `.sql` files** +
  1 `__init__.py`. The 4 BIEP v1 canonical Dives +
  47 jurisdiction-specific BIEP v3 Dives (England + Scotland +
  Wales + NI + Ireland JC + meaisin eval + filesystem +
  corpus overviews).
- **`flights/`** — **20 Flight `.py` files** + **6 Flight `.sql`
  files** + 1 `config.yaml` (the BIEP v3 Flight registry) +
  1 `__init__.py`. The canonical `lc_pdf_sync_flight` (BIEP v1
  daily) + 8 stub Flights (per-region/country) + 4 BIEP v3
  jurisdiction Flights + 5 BIEP v3 corpus Flights + 2 filesystem
  sync Flights.

## The 4 canonical BIEP v1 Dives

| Dive name | File | Tables read |
|:--|:--|:--|
| `lc_syllabus_topics` | `dives/lc_syllabus_topics.py:102` | `md:cianfhoghlaim.leaving_cert.<subject>_topics` (6 subjects) |
| `lc_exam_difficulty` | `dives/lc_exam_difficulty.py:117` | `md:cianfhoghlaim.leaving_cert.<subject>_papers` (6 subjects) |
| `lc_marking_complexity` | `dives/lc_marking_complexity.py:86` | `md:cianfhoghlaim.leaving_cert.<subject>_marking` (6 subjects) |
| `gov_circulars_archive` | `dives/gov_circulars_archive.py:74` | `md:oideachais.government.circulars` + `circular_to_syllabus` |

Each Dive is a `DiveSpec` dataclass with `name + description + sql +
charts + filters`. The MotherDuck `save_dive` MCP tool consumes the
serialised dict (`DiveSpec.to_dict()`).

## The BIEP v3 Dives (replacement suite)

The 5 BIEP v3 jurisdiction Dives:

- `dives/ireland_lc_syllabus_topics.py` — Ireland LC cohort analysis
  (replaces `lc_syllabus_topics.py` for the v3 namespace)
- `dives/england_a_level_complexity.py` — England A-Level difficulty
  analysis
- `dives/england_aqa_curriculum_dive.sql` — England AQA per-spec
  analysis
- `dives/england_gcse_complexity.py` — England GCSE difficulty
- `dives/england_gcse_difficulty_dive.sql` — England GCSE difficulty
- `dives/jc_curriculum_dive.sql` — Junior Cycle (Ireland) per-spec
  analysis

Plus 3 evaluation/capability Dives:

- `dives/meaisin_evaluation_summary_dive.py` — meaisínfhoghlaim OCR
  evaluation summary (the 19 OCR models × 4 classical backends)
- `dives/filesystem_sources_overview_dive.py` — filesystem DLT
  pipeline summary
- `dives/guernsey_curriculum_dive_v2.py` +
  `dives/isle_of_man_curriculum_dive_v2.py` — Crown Dependencies
- `dives/ireland_jc_curriculum_topics.py` — Ireland Junior Cycle

## The 13 BIEP v3 Flights (in `flights/config.yaml`)

| Flight | Cron | TZ | Description |
|:--|:--|:--|:--|
| `eu_official_daily_sync_flight` | `0 5 * * *` | UTC | Daily BAML backfill for the EU institutional pipeline |
| `eu_nation_daily_sync_flight` | `0 6 * * *` | UTC | EU nations + Ukraine pipeline |
| `commonwealth_daily_sync_flight` | `0 6 * * *` | UTC | Commonwealth pipeline (aus/can/nzl/ind/zaf) |
| `americas_daily_sync_flight` | `0 6 * * *` | UTC | Americas regional pipeline |
| `british_isles_daily_sync_flight` | `0 5 * * *` | UTC | British Isles parity layer |
| `canada_daily_sync_flight` | `0 6 * * *` | UTC | Canada provinces + Quebec/Montreal |
| `nigeria_daily_sync_flight` | `0 6 * * *` | UTC | Nigerian federal + state |
| `eu_multilingual_daily_sync_flight` | `0 5 * * *` | UTC | EU multilingual (en + ga) alignment |
| `ireland_full_coverage_flight` | `0 2 * * *` | UTC | BIEP v3 Ireland full-coverage |
| `england_full_coverage_flight` | `0 3 * * *` | UTC | BIEP v3 England full-coverage |
| `sct_wls_ni_flight` | `0 4 * * *` | UTC | BIEP v3 Scotland + Wales + Northern Ireland |
| `crown_dependencies_flight` | `30 4 * * *` | UTC | BIEP v3 Crown Dependencies (Jersey + Guernsey + IoM) |

Plus the canonical BIEP v1 daily Flight (currently NOT registered
in `config.yaml` — the v1 canonical entry point is the standalone
`lc_pdf_sync_flight.py:177: main()` callable).

## Database URI conventions

| Surface | URI pattern | Example |
|:--|:--|:--|
| BIEP v1 structured rows | `md:cianfhoghlaim.leaving_cert.*` | `md:cianfhoghlaim.leaving_cert.mathematics_topics` |
| BIEP v1 status rows | `md:cianfhoghlaim.lc_ops.daily_sync_status` | (the v1 Flight writes here) |
| BIEP v3 typed + voted rows | `md:cianfhoghlaim.education.<jurisdiction>.<stage>.<subject>.<variant>` | `md:cianfhoghlaim.education.ireland.leaving_cycle.mathematics.untiered_en` |
| BIEP v3 status rows | `md:cianfhoghlaim.education.<jurisdiction>._audit.daily_sync_status` | (the v3 Flights write here) |
| Government circulars | `md:oideachais.government.circulars` + `circular_to_syllabus` | (legacy v1 namespace) |

The `gov_circulars_archive.py` Dive is the only one that still
references the pre-v3 `oideachais` namespace.

## The DiveSpec + DiveRegistry contract

```python
from dataclasses import dataclass, field
from typing import Any

@dataclass
class DiveSpec:
    name: str
    description: str
    sql: str
    charts: list[dict[str, Any]] = field(default_factory=list)
    filters: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "description": self.description,
                "sql": self.sql, "charts": self.charts,
                "filters": self.filters}

# A canonical Dive
LC_SYLLABUS_TOPICS_DIVE = DiveSpec(
    name="lc_syllabus_topics",
    description="...",
    sql="WITH syllabus_topics AS (...) SELECT ...",
    charts=[{"type": "line", "title": "..."}, {"type": "bar", "title": "..."}],
    filters=[{"column": "subject", "type": "multi_select", "options": [...]}],
)
```

`DiveRegistry.save_all()` iterates the registry and returns the count
of Dives successfully serialised (network-free by default; consumes
the MotherDuck `save_dive` MCP tool when `MOTHERDUCK_TOKEN` is set).

## The Flight contract

```python
from motherduck.flights import run_flight

# Dry-run (no MotherDuck token required)
result = run_flight(
    name="my_daily_flight",
    cron="0 4 * * *",  # 04:00 UTC
    timezone="UTC",
    module="motherduck.flights.my_daily_flight",
    callable_name="main",
    dry_run=True,
)

# Live registration (requires MOTHERDUCK_TOKEN)
result = run_flight(name="my_daily_flight", cron="0 4 * * *")
```

In dry-run mode, the payload is returned without making the API
call — useful for CI / pre-deployment validation.

## Quick routing — "I want to add X, where do I go?"

| If you want to... | Look at... |
|:--|:--|
| Add a new BIEP v1 Dive | `dives/<name>.py` (model after `lc_syllabus_topics.py`); append to `BIEP_DIVES` in `dives/__init__.py` |
| Add a new BIEP v3 Dive | `dives/<jurisdiction>_<stage>_<topic>.py`; register in the relevant `flights/config.yaml` entry |
| Add a new BIEP v3 Flight | `flights/<jurisdiction>_full_coverage_flight.py`; register in `flights/config.yaml` |
| Add a new MotherDuck table destination | Update `motherduck_options.py` in `dlt_sources/common/` |
| Diagnose a Dive SQL issue | Run the SQL directly against MotherDuck: `duckdb -c "SELECT ..." md:cianfhoghlaim` |
| Deploy the MotherDuck stack | `docker compose -f bonneagar/stacks/motherduck/compose.yaml -f sidecar.yaml up -d` |
| Save all Dives | `python -c "from motherduck import save_all; save_all()"` |

## Cross-references

- [`../README.md`](../README.md) — root README
- [`../AGENTS.md`](../AGENTS.md) — root agent instructions
- [`../openspec/AGENTS.md`](../openspec/AGENTS.md) — openspec workflow
- [`../openspec/specs/british-isles-education-pipeline-v3/spec.md`](../openspec/specs/british-isles-education-pipeline-v3/spec.md) — BIEP v3 spec
- [`../.agents/skills/motherduck/SKILL.md`](../.agents/skills/motherduck/SKILL.md) — MotherDuck master skill
- [`../.agents/skills/motherduck-create-dive/SKILL.md`](../.agents/skills/motherduck-create-dive/SKILL.md) — Dive authoring recipe
- [`../.agents/skills/motherduck-create-flight/SKILL.md`](../.agents/skills/motherduck-create-flight/SKILL.md) — Flight authoring recipe
- [`../dlt_sources/AGENTS.md`](../dlt_sources/AGENTS.md) — the DLT ingestion layer
- [`../cocoindex/AGENTS.md`](../cocoindex/AGENTS.md) — the CocoIndex embedding layer
- [`../orchestration/README.md`](../orchestration/README.md) — the Dagster orchestration layer
- [`../bonneagar/stacks/motherduck/](../bonneagar/stacks/motherduck/) — the IaC stack provider