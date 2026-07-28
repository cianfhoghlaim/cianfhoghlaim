# BIEP v3 — Systematic Download & Iteration (the canonical newcomer guide)

> Per the `2026-08-13-biep-v3-systematic-download-ireland-england-v1`
> openspec change. The 5-milestone plan that systematically downloads,
> extracts, embeds, logs, and analyses all 8 British Isles jurisdictions
> + the 2 scanner domains.

## What is the BIEP v3 systematic download & iteration plan?

The **British-Isles Education Pipeline v3 (BIEP v3)** is the canonical
Cianfhoghlaim data platform capability that systematically downloads,
extracts, embeds, logs, and analyses all 8 British Isles jurisdictions +
the 2 general-purpose scanner domains. The plan is structured as **5
sequential milestones** (M0 → M4) that can only be run in order:

1. **M0** — Foundation unblock (lakehouse + BAML + registry + namespace)
2. **M1** — Ireland Leaving Cycle (12 cohorts, EN+GA)
3. **M2** — Ireland Junior Cycle (88 cohorts, EN+GA)
4. **M3** — England A-Level (147 cohorts, AQA + OCR + Edexcel)
5. **M4** — England GCSE (129 cohorts, AQA + OCR + Edexcel)

After M0-M4, the **6 deferred jurisdictions** are picked up by:

6. **M5** — Scotland (150 cohorts, SQA)
7. **M6** — Wales (160 cohorts, WJEC)
8. **M7** — Northern Ireland (70 cohorts, CCEA)
9. **M8** — Jersey (120 cohorts)
10. **M9** — Guernsey (120 cohorts)
11. **M10** — Isle of Man (120 cohorts)

Plus the **2 general-purpose scanner domains** (filesystem + language)
are picked up by **monthly** flights (separate cadence because they
change more frequently than the annual education content).

## The 4-cadence scheduling policy

Per the user's direction (2026-07-28): *"all the schedules for these
education official documents should be yearly for exam papers, marking
schemes, syllabus and monthly for more regular types like government
circulars"*.

| Document class | Cadence | Cron |
|:--|:--|:--|
| NCCA + SEC + AQA + OCR + Edexcel + SQA + WJEC + CCEA education content | **Yearly** | `0 0 1 9 *` (1st September 00:00 UTC = start of academic year) |
| gov.ie education circulars | **Monthly** | `0 0 1 * *` (1st of each month) |
| M0 foundation assets (smoke test, BAML codegen, registry seed, lance namespace) | **Weekly** | `0 6 * * 1` (Monday 06:00 UTC) |
| BIEP v3 RAGAS + audit + asset checks | **Nightly** | `0 0 * * *` (00:00 UTC) |
| ChangeDetection.io sensors (NCCA, SEC, AQA, OCR, Edexcel, WJEC, CCEA, IoM, Jersey, Guernsey) | **Event-driven** (eager) | n/a |

## The 5-phase pattern (applied to every milestone)

Every milestone (M0-M10) follows the same canonical 5-phase pattern:

1. **Phase A — Ingestion** — DLT sources land raw PDFs + scraped HTML into `s3://garage/cianfhoghlaim/<jurisdiction>/<stage>/<subject>/<language>/<year>/<file>.pdf` with snake_case metadata sidecar
2. **Phase B — Extraction** — `EnsembledExtractor.extract()` runs the 4-path OCR ensemble (BAML/Docling + Unstract + qwen3-vl-8b + gemma-4-26B-A4B) + RAGAS `biiep_extraction_consensus` vote
3. **Phase C — Embedding** — per-jurisdiction CocoIndex v1 Apps chunk + embed via `BAAI/bge-m3` 1024-d multilingual embedder + write to LanceDB
4. **Phase D — ibis logging** — 1 audit row per cohort in `cianfhoghlaim.education.<jurisdiction>._audit.daily_sync_status`
5. **Phase E — Analytics** — marimo notebook renders the per-jurisdiction cohort matrix + MotherDuck Dive

## Canonical contracts

### Snake_case file naming

Every BIEP v3 PDF + metadata sidecar MUST land at:

```text
s3://garage/cianfhoghlaim/<jurisdiction>/<stage>/<subject>/<language>/<year>/<file>.pdf
```

with a sibling `<file>.meta.json` sidecar carrying the 14 metadata fields
(`source_id`, `jurisdiction`, `stage`, `subject_slug`, `board`,
`qualification_level`, `language`, `year`, `source_url`, `crawled_at`,
`byte_size`, `page_count`, `content_hash_sha256`, `publisher`).

The `source_id` matches the regex `^[a-z0-9]+(\.[a-z0-9]+){3,}$` per the
`cross-region-pipeline` spec.

### ibis-first contract

Every Dagster asset + marimo notebook + MotherDuck Dive MUST use
`ibis.duckdb.connect("md:cianfhoghlaim")` (or the local lakehouse
fallback) for ALL data access. Raw `duckdb.connect()` is forbidden in
the BIEP v3 paths. Run `mise run biep:v3:lint` to validate.

### RAGAS voting contract

Every BAML extraction is followed by a 4-path ensemble + RAGAS
`biiep_extraction_consensus` vote. The consensus row lands in
`*.voted_canonical` and the per-path rows land in
`*.baml_canonical`, `*.unstract_json`, `*.qwen3_vl`, `*.gemma4`. The
`ragas_score >= 0.70` asset check MUST pass before the voted_canonical
row is committed.

## Canonical canonical namespaces

### DuckLake namespaces (MotherDuck + DuckDB)

```text
md:cianfhoghlaim.education.<jurisdiction>.<stage>.<subject>.<level>_<lang>.baml_canonical
md:cianfhoghlaim.education.<jurisdiction>.<stage>.<subject>.<level>_<lang>.unstract_json
md:cianfhoghlaim.education.<jurisdiction>.<stage>.<subject>.<level>_<lang>.qwen3_vl
md:cianfhoghlaim.education.<jurisdiction>.<stage>.<subject>.<level>_<lang>.gemma4
md:cianfhoghlaim.education.<jurisdiction>.<stage>.<subject>.<level>_<lang>.voted_canonical
md:cianfhoghlaim.education.filesystem._audit.daily_sync_status
md:cianfhoghlaim.education.language._audit.daily_sync_status
md:cianfhoghlaim.education.ireland._audit.daily_sync_status
md:cianfhoghlaim.education.england._audit.daily_sync_status
md:cianfhoghlaim.education.scotland._audit.daily_sync_status
md:cianfhoghlaim.education.wales._audit.daily_sync_status
md:cianfhoghlaim.education.northern_ireland._audit.daily_sync_status
md:cianfhoghlaim.education.jersey._audit.daily_sync_status
md:cianfhoghlaim.education.guernsey._audit.daily_sync_status
md:cianfhoghlaim.education.isle_of_man._audit.daily_sync_status
```

### LanceDB namespaces

```text
cianhoghlaim.ireland.leaving_cycle.<subject>.<level>_<lang>_chunks
cianhoghlaim.ireland.junior_cycle.<subject>.<year>_<lang>_chunks
cianhoghlaim.england.a_level.<board>.<subject>_a_level_chunks
cianhoghlaim.england.gcse.<board>.<subject>_gcse_chunks
cianhoghlaim.scotland.<level>.<subject>_chunks
cianhoghlaim.wales.<level>.<subject>_chunks
cianhoghlaim.northern_ireland.<level>.<subject>_chunks
cianhoghlaim.jersey.<level>.<subject>_chunks
cianhoghlaim.guernsey.<level>.<subject>_chunks
cianhoghlaim.isle_of_man.<level>.<subject>_chunks
cianhoghlaim.biep.ga.education_chunks
cianhoghlaim.biep.ireland.education_chunks
```

## Canonical operator surface

| What | Where | How |
|:--|:--|:--|
| Setup | `scripts/biiep_v3_setup.py` | `mise run biep:v3:setup` |
| Status | `scripts/biiep_v3_status.py` | `mise run biep:v3:status` |
| Foundation | `scripts/m0_foundation_unblock.py` | `mise run biep:v3:m0` |
| Ireland LC | `scripts/m1_ireland_lc.py` | `mise run biep:v3:m1` |
| Ireland JC | `scripts/m2_ireland_jc.py` | `mise run biep:v3:m2` |
| England A-Level | `scripts/m3_england_a_level.py` | `mise run biep:v3:m3` |
| England GCSE | `scripts/m4_england_gcse.py` | `mise run biep:v3:m4` |
| Scotland | `scripts/m5_scotland.py` | `mise run biep:v3:m5` |
| Wales | `scripts/m6_wales.py` | `mise run biep:v3:m6` |
| Northern Ireland | `scripts/m7_northern_ireland.py` | `mise run biep:v3:m7` |
| Jersey | `scripts/m8_jersey.py` | `mise run biep:v3:m8` |
| Guernsey | `scripts/m9_guernsey.py` | `mise run biep:v3:m9` |
| Isle of Man | `scripts/m10_isle_of_man.py` | `mise run biep:v3:m10` |
| Filesystem | (monthly) | `mise run biep:v3:filesystem:monthly:sync` |
| Language | (monthly) | `mise run biep:v3:language:monthly:sync` |
| Asset check | `scripts/milestone_gate.py` | `mise run biep:v3:gate --milestone=m<N>` |
| Lint | `scripts/check_ibis_first.py` | `mise run biep:v3:lint` |
| Snake_case | `scripts/validate_snake_case_filenames.py` | `mise run biep:v3:filename-validate` |

## Canonical openspec changes

- `2026-08-13-biep-v3-systematic-download-ireland-england-v1` — the umbrella change
- `2026-07-30-biep-v3-sct-wls-ni-v1` — Scotland + Wales + Northern Ireland
- `2026-07-31-biep-v3-crown-dependencies-v1` — Jersey + Guernsey + Isle of Man
- `2026-08-13-biep-v3-filesystem-and-language-pipelines-v1` — filesystem + language

## See also

- `docs/agents/biiep-v3-quickstart.md` — the "first 30 minutes" guide for newcomers
- `docs/agents/biiep-v3-faq.md` — the canonical FAQ
- `docs/agents/biiep-v3-baml-client.md` — how to invoke the 6 new Extract* functions from Python
- `docs/agents/biiep-v3-storage-layout.md` — the DuckLake + Lance + MotherDuck layout
- `docs/agents/biiep-v3-cron-schedule.md` — the 4-cadence scheduling policy in detail
- `docs/agents/biiep-v3-bie-8-jurisdictions.md` — the 8-jurisdiction rollout + the 2 scanner domains
