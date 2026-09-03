# BIEP v3 — Cron Schedule (the 4-cadence scheduling policy in detail)

> Per the `2026-08-13-biep-v3-systematic-download-ireland-england-v1`
> openspec change + the user's direction (2026-07-28):
> *"all the schedules for these education official documents should be
> yearly for exam papers, marking schemes, syllabus and monthly for
> more regular types like government circulars"*.

## Overview

The BIEP v3 systematic download plan implements a **4-cadence scheduling
policy**:

1. **Yearly** for NCCA + SEC + AQA + OCR + Edexcel + SQA + WJEC + CCEA + IoM + Jersey + Guernsey education content
2. **Monthly** for gov.ie education circulars + the 2 scanner domains (filesystem + language)
3. **Weekly** for the M0 foundation assets
4. **Nightly** for the BIEP v3 RAGAS + audit + asset checks
5. **Event-driven** (eager) for the ChangeDetection.io sensors

The canonical implementation is at `orchestration/automation/biiep_scheduling.py`.

## Yearly cadence (1st September 00:00 UTC)

The yearly cron expression is `0 0 1 9 *`. This fires on the 1st of
September at 00:00 UTC, which corresponds to the start of the UK +
Ireland academic year. The yearly cron triggers the per-jurisdiction
yearly education content refresh.

The 10 yearly Dagster assets (one per jurisdiction + scanner domain):

| Jurisdiction | Asset name | Mise task |
|:--|:--|:--|
| Ireland (LC) | `ireland_documents_ingested` | `biep:v3:m1` |
| Ireland (JC) | `ireland_jc_documents_ingested` | `biep:v3:m2` |
| England (A-Level) | `england_a_level_documents_ingested` | (via m3) |
| England (GCSE) | `england_gcse_documents_ingested` | (via m4) |
| Scotland | `scotland_documents_ingested` | `biep:v3:m5` |
| Wales | `wales_documents_ingested` | `biep:v3:m6` |
| Northern Ireland | `northern_ireland_documents_ingested` | `biep:v3:m7` |
| Jersey | `jersey_documents_ingested` | `biep:v3:m8` |
| Guernsey | `guernsey_documents_ingested` | `biep:v3:m9` |
| Isle of Man | `isle_of_man_documents_ingested` | `biep:v3:m10` |

The yearly cron also triggers the corresponding 30 extraction +
embedding assets (one of each per jurisdiction + scanner domain).

## Monthly cadence (1st of each month 00:00 UTC)

The monthly cron expression is `0 0 1 * *`. This fires on the 1st of
each month at 00:00 UTC, which corresponds to the typical monthly
refresh rate for content that changes more frequently than the annual
education content.

The 2 monthly Dagster assets (one per scanner domain):

| Scanner | Asset name | Mise task |
|:--|:--|:--|
| filesystem | `filesystem_documents_ingested` | `biep:v3:filesystem:monthly:sync` |
| language | `language_documents_ingested` | `biep:v3:language:monthly:sync` |

The monthly cron also triggers the 2 corresponding extraction +
embedding assets + the 2 monthly MotherDuck Flights.

The monthly cadence is also used for the 6 deferred MotherDuck Flights
(sct_wls_ni_flight + crown_dependencies_flight) which call the 6
per-jurisdiction entrypoint scripts (m5 + m6 + m7 + m8 + m9 + m10).

## Weekly cadence (Monday 06:00 UTC)

The weekly cron expression is `0 6 * * 1`. This fires on Monday at
06:00 UTC, which is a low-traffic window. The weekly cron triggers the 4
M0 foundation assets (lakehouse_smoke_test + baml_codegen_gate +
registry_seed_count + lance_namespace_ready) which validate the
lakehouse stack + BAML codegen + registry seed + Lance namespace are
all working.

The 4 weekly Dagster assets:

| M0 asset | Mise task |
|:--|:--|
| `lakehouse_smoke_test` | `mise run biep:v3:m0` (last step) |
| `baml_codegen_gate` | `mise run baml:generate` |
| `registry_seed_count` | `mise run biep:v3:registry:seed` |
| `lance_namespace_ready` | `python3 scripts/create_lance_namespace.py` |

## Nightly cadence (00:00 UTC)

The nightly cron expression is `0 0 * * *`. This fires every day at
00:00 UTC. The nightly cron triggers the BIEP v3 RAGAS + audit +
asset checks which validate that the 4-path OCR ensemble + RAGAS voting
+ asset checks are all working.

The nightly cadence also surfaces stale RAGAS scores, missed ingestion
windows, and 4-path ensemble drift.

## Event-driven cadence (eager)

The ChangeDetection.io sensors (per the 2026-08-02 change) trigger
immediately on every external spec change. The sensors are:

- `ncca_registry_sensor.py` — NCCA (Ireland)
- `sqa_registry_sensor.py` — SQA (Scotland)
- `wjec_registry_sensor.py` — WJEC (Wales)
- `ccea_registry_sensor.py` — CCEA (Northern Ireland)
- `jcq_registry_sensor.py` — JCQ (England: AQA + OCR + Edexcel)
- `jersey_registry_sensor.py` — Jersey
- `guernsey_registry_sensor.py` — Guernsey
- `isle_of_man_registry_sensor.py` — Isle of Man

The canonical event-driven trigger flow is:

```
ChangeDetection.io monitor → Dagster webhook → ChangeDetection sensor
→ 4-path OCR ensemble → RAGAS voting → DuckLake landed → MotherDuck Dive
```

## Per-jurisdiction cron schedule table

| Jurisdiction | Cadence | Cron | Mise task | ChangeDetection sensor |
|:--|:--|:--|:--|:--|
| Ireland (LC) | Yearly | `0 0 1 9 *` | `biep:v3:m1` | `ncca_registry_sensor` |
| Ireland (JC) | Yearly | `0 0 1 9 *` | `biep:v3:m2` | `ncca_registry_sensor` |
| England (A-Level) | Yearly | `0 0 1 9 *` | `biep:v3:m3` | `jcq_registry_sensor` |
| England (GCSE) | Yearly | `0 0 1 9 *` | `biep:v3:m4` | `jcq_registry_sensor` |
| Scotland | Yearly | `0 0 1 9 *` | `biep:v3:m5` | `sqa_registry_sensor` |
| Wales | Yearly | `0 0 1 9 *` | `biep:v3:m6` | `wjec_registry_sensor` |
| Northern Ireland | Yearly | `0 0 1 9 *` | `biep:v3:m7` | `ccea_registry_sensor` |
| Jersey | Yearly | `0 0 1 9 *` | `biep:v3:m8` | `jersey_registry_sensor` |
| Guernsey | Yearly | `0 0 1 9 *` | `biep:v3:m9` | `guernsey_registry_sensor` |
| Isle of Man | Yearly | `0 0 1 9 *` | `biep:v3:m10` | `isle_of_man_registry_sensor` |
| filesystem | Monthly | `0 0 1 * *` | `biep:v3:filesystem:monthly:sync` | n/a (filesystem sensors are per-source) |
| language | Monthly | `0 0 1 * *` | `biep:v3:language:monthly:sync` | n/a (language sensors are per-source) |
| M0 foundation | Weekly | `0 6 * * 1` | `biep:v3:m0` | n/a |
| RAGAS + audit | Nightly | `0 0 * * *` | (background) | n/a |

## See also

- `docs/agents/biiep-v3-systematic-download.md` — the canonical newcomer guide
- `docs/agents/biiep-v3-quickstart.md` — the "first 30 minutes" guide
- `docs/agents/biiep-v3-faq.md` — the canonical FAQ
- `docs/agents/biiep-v3-baml-client.md` — how to invoke the 6 new Extract* functions from Python
- `docs/agents/biiep-v3-storage-layout.md` — the DuckLake + Lance + MotherDuck layout
- `docs/agents/biiep-v3-bie-8-jurisdictions.md` — the 8-jurisdiction rollout + the 2 scanner domains
