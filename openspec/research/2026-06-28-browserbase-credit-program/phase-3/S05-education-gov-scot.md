# S05 — education.gov.scot (Scotland Education Scotland)

**Date:** 2026-06-28
**Phase:** 3 (Live Site Discovery Reports)
**Budget:** ~75 credits
**Subagent:** research

## TL;DR

education.gov.scot is the **Scottish Government Education Directorate portal** — hosts Curriculum for Excellence (CfE) for early years through Senior Phase (S4-S6, equivalent to GCSE/A-Level).

## Site structure

| Path | Content |
|:--|:--|
| `/` | Home |
| `/curriculum-for-excellence/` | CfE main page |
| `/curriculum-for-excellence/expressive-arts/` | Subject areas (8 + RME) |
| `/national-improvements/` | National improvements framework |
| `/learning-and-teaching/` | Pedagogy resources |

## Dropdown cascade

```
1. Curriculum for Excellence
2. Level: [Early Years, First Level (P1-P3), Second Level (P4-P7), Third/Fourth Level (S1-S3), Senior Phase (S4-S6)]
3. Subject (8 + RME)
4. Resource type: [Experiences and Outcomes, Benchmarks, Assessment Materials]
```

## URL pattern

```
https://education.gov.scot/curriculum-for-excellence/{subject}/
https://education.gov.scot/media/{document-id}
```

## Anti-scraping posture

- **Open access** (no login)
- **No strict rate limit** observed
- **Scottish Gaelic**: `/curriculum-for-excellence/.../gd/` for Gaelic versions
- **Wayback Machine** has full snapshots

## BAML extraction strategy

```python
function ExtractCfESubject(
  html: Html,
  subject: Subject,
  level: Level,
) -> CfESubject {
  client ExtractEn
  prompt #"
    Extract the CfE {{ subject }} {{ level }} experiences and outcomes.
    Return: experiences (list[str]), outcomes (list[str]),
            benchmarks (list[str]), cross_curricular_links (list[str]).
  "
}
```

## CCC anchors

`oideachais/dlt_sources/uk/scotland_cfe.py` · `oideachais/baml_src/cfe_extraction.baml`

## Drift log

| Date | Event |
|--:|:--|
| 2026-01 | Initial CfE corpus (dlt REST) |
| 2026-03 | BAML extraction |

## Decision matrix

| Decision | Choice | Rationale |
|:--|:--|:--|
| Source method | dlt REST (sitemap.xml) | Standard |
| Language | English + Gaelic | Multilingual support |
| Refresh | Annual | CfE is stable |
