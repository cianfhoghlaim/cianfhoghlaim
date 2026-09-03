# British Isles Endpoint Health Audit — 2026-07-12 snapshot

This is the canonical snapshot of the 39 British Isles endpoints that
the
`2026-07-12-british-isles-endpoint-recovery-v1 <../openspec/changes/2026-07-12-british-isles-endpoint-recovery-v1/>`_
change fixes.

Re-run the audit any time with:

```python
from cianfhoghlaim.dlt.common.endpoint_recovery import probe_all_39
import asyncio, json
print(json.dumps(asyncio.run(probe_all_39()), indent=2))
```

## The 39 endpoints

| # | Nation | Domain | Source | URL | Status (2026-07-12) | Strategy |
|--:|:--|:--|:--|:--|--:|:--|
| 1 | Ireland | education | NCCA | `https://ncca.ie/en/` | **403 → recovers via stealth** | `stealth` |
| 2 | Ireland | education | CurriculumOnline | `https://www.curriculumonline.ie/en/senior-cycle/senior-cycle-subjects` | **403 → recovers via stealth** | `stealth` |
| 3 | Ireland | education | Examinations | `https://www.examinations.ie/` | 200 | `auto` |
| 4 | Ireland | education | gov.ie circulars | `https://www.gov.ie/en/circulars/` | 200 (browser UA required) | `auto` |
| 5 | Ireland | law | courts.ie | `https://www.courts.ie/` | 200 | `auto` |
| 6 | Ireland | law | Irish Statute Book | `https://www.irishstatutebook.ie/` | 200 | `auto` |
| 7 | Ireland | law | justice.ie | `https://www.justice.ie/` | 200 (redirects to gov.ie) | `auto` |
| 8 | Ireland | law | workplace relations | `https://www.workplacerelations.ie/en/` | 200 | `auto` |
| 9 | Ireland | law | citizensinformation | `https://www.citizensinformation.ie/en/` | 200 (browser UA required) | `auto` |
| 10 | Ireland | medicine | HSE | `https://www.hse.ie/eng/` | 200 | `auto` |
| 11 | Ireland | medicine | HPSC | `https://www.hpsc.ie/` | 200 | `auto` |
| 12 | Ireland | medicine | Medical Council | `https://www.medicalcouncil.ie/` | 200 | `auto` |
| 13 | Ireland | statistics | CSO | `https://www.cso.ie/en/index.html` | 200 | `auto` |
| 14 | Ireland | statistics | Met Office | `https://www.met.ie/` | 200 | `auto` |
| 15 | Scotland | education | SQA | `https://www.sqa.org.uk/supporting-others/` | **URL changed (404 → recovers via map discovery)** | `firecrawl_map` |
| 16 | Scotland | education | CfE | `https://education.gov.scot/curriculum-for-excellence/` | 200 | `auto` |
| 17 | Scotland | law | legislation.gov.uk/asp | `https://www.legislation.gov.uk/asp` | 200 | `auto` |
| 18 | Scotland | medicine | NHS Scotland | `https://www.nhsinform.scot/` | 200 (browser UA required) | `auto` |
| 19 | Wales | education | WJEC | `https://www.wjec.co.uk/qualifications` | 200 | `firecrawl_map` |
| 20 | Wales | law | legislation.gov.uk/anaw | `https://www.legislation.gov.uk/anaw` | 200 | `auto` |
| 21 | Wales | medicine | Public Health Wales | `https://phw.nhs.wales/` | 200 | `auto` |
| 22 | England | education | AQA | `https://www.aqa.org.uk/find-past-papers-and-mark-schemes` | **URL changed (404 → recovers via map discovery)** | `firecrawl_map` |
| 23 | England | education | Pearson | `https://qualifications.pearson.com/en/qualifications/edexcel-gcses.html` | 200 | `firecrawl_map` |
| 24 | England | law | legislation.gov.uk/ukpga | `https://www.legislation.gov.uk/ukpga` | 200 | `auto` |
| 25 | England | medicine | NHS England | `https://www.nhs.uk/` | 200 | `auto` |
| 26 | England | medicine | NICE | `https://www.nice.org.uk/` | 200 | `auto` |
| 27 | England | medicine | GMC | `https://www.gmc-uk.org/` | **403 → recovers via stealth** | `stealth` |
| 28 | NI | education | CCEA | `https://ccea.org.uk/about/what-we-do/curriculum` | **403 → recovers via stealth** | `stealth` |
| 29 | NI | education | education-ni | `https://www.education-ni.gov.uk/` | 200 | `auto` |
| 30 | NI | medicine | nidirect | `https://www.nidirect.gov.uk/` | 200 | `auto` |
| 31 | NI | law | legislation.gov.uk/nisr | `https://www.legislation.gov.uk/nisr` | 200 | `auto` |
| 32 | IoM | education | gov.im | `https://www.gov.im/categories/education-training-and-careers/` | **403 → recovers via stealth** | `stealth` |
| 33 | IoM | law | legislation.gov.im | `https://legislation.gov.im/` | 200 | `auto` |
| 34 | Jersey | education | gov.je | `https://www.gov.je/Pages/default.aspx` | 200 (originally 500, fixed by retry) | `auto` |
| 35 | Jersey | law | jerseylaw.je | `https://www.jerseylaw.je/Pages/default.aspx` | 200 (originally 500, fixed by retry) | `auto` |
| 36 | Guernsey | education | gov.gg | `https://www.gov.gg/education` | 200 | `auto` |
| 37 | Guernsey | law | guernseylegalresources.gg | `https://www.guernseylegalresources.gg/legislation` | **403 → recovers via stealth** | `stealth` |
| 38 | Guernsey | medicine | gov.gg health | `https://www.gov.gg/health-social-care` | 200 | `auto` |
| 39 | Ireland | law | courts.ie judgements | `https://www.courts.ie/search/judgements` | 200 (URL fixed from `/judgements` → `/search/judgements`) | `url_fix` |

## Summary

- 28/39 endpoints healthy out-of-the-box.
- 11 endpoints required Phase 1 fixes:
  - **5 endpoints** required URL changes (the page moved): SQA, AQA, courts.ie/judgements, Pearson (stale cache path), WJEC (stale cache path).
  - **5 endpoints** required Firecrawl `stealth` proxy (WAF-blocked): NCCA, CurriculumOnline, GMC, CCEA, gov.im (IoM), guernseylegalresources.gg.
  - **1 endpoint** required browser User-Agent (CitSinfo returns 403 to curl but 200 to Safari UA): `www.citizensinformation.ie`.

## How the recovery ladder works

```python
from cianfhoghlaim.dlt.common.endpoint_recovery import (
    EndpointRecoveryStrategy, fetch, probe_all_39,
)

# Strategy ladder: auto -> stealth -> wayback
page = await fetch("https://ncca.ie/en/")  # strategy="auto"
print(page.status, page.backend_used, page.content_hash)
```

The ladder tries `auto` first, then `stealth` on 403, then the
Wayback Machine on 403 / time-out. The chosen backend is recorded
in the `endpoint_health` DuckLake table + emitted as a `endpoint_status`
structlog event.

## Operational probe

The Dagster L2 asset `endpoint_health_sink` runs every 6 hours:

```bash
# Manual probe
python3 -c "import asyncio, json; from cianfhoghlaim.dlt.common.endpoint_recovery import probe_all_39; print(json.dumps(asyncio.run(probe_all_39()), indent=2))"
```

The asset emits one row per probe to the `cianfhoghlaim.endpoint_health`
DuckLake table. The companion L2 asset `endpoint_health_alerts`
posts a Slack message to `#upstream-endpoints` whenever a source falls
below 200 for 2 consecutive probes.

## References

- `openspec/changes/2026-07-12-british-isles-endpoint-recovery-v1/proposal.md`
- `openspec/changes/2026-07-12-british-isles-endpoint-recovery-v1/tasks.md`
- `cianfhoghlaim/dlt/common/endpoint_recovery.py` (the helper)
- `cianfhoghlaim/orchestration/defs/2_materials/endpoint_health/` (the L2 assets)
