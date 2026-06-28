# S09 — gov.je (Jersey Government Education)

**Date:** 2026-06-28
**Phase:** 3 (Live Site Discovery Reports)
**Budget:** ~75 credits
**Subagent:** research

## TL;DR

gov.je is the **Government of Jersey** portal, specifically the Department for Children, Young People, Education and Skills (CYPES). Hosts Jersey Curriculum Framework + exam materials (follows UK GCSE/A-Level with Jersey-specific additions).

## Site structure

| Path | Content |
|:--|:--|
| `/` | Government home |
| `/government/departments/` | Departments list |
| `/government/departments/children-young-people-education-skills/` | CYPES home |

## Dropdown cascade

```
1. Government → Departments → Children, Young People, Education and Skills
2. Section: Schools / Curriculum / Students / Teachers
3. Resource: [Curriculum Document, Exam Materials, Policy]
```

## URL pattern

```
https://www.gov.je/Government/Departments/{department}
```

## Anti-scraping posture

- **Open access** (small site, no rate limit)
- **English-only** (Jèrriais is rare)
- **Wayback Machine** has snapshots

## BAML extraction strategy

```python
function ExtractJerseyEducation(
  html: Html,
) -> JerseyDoc {
  client ExtractEn
  prompt #"
    Extract this Jersey education document.
    Return: title, section, summary, key_points (list[str]).
  "
}
```

## CCC anchors

`oideachais/dlt_sources/crown_dependencies/jey.py`

## Drift log

| Date | Event |
|--:|:--|
| 2026-01 | Initial Jersey corpus |
| 2026-03 | BAML extraction |

## Decision matrix

| Decision | Choice | Rationale |
|:--|:--|:--|
| Source method | dlt REST | Small site |
| Language | English | Standard |
| Refresh | Annual | Stable |
