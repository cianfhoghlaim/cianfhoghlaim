# S08 — gov.im (Isle of Man Department of Education)

**Date:** 2026-06-28
**Phase:** 3 (Live Site Discovery Reports)
**Budget:** ~75 credits
**Subagent:** research

## TL;DR

gov.im is the **Isle of Man Government** portal, specifically the Department of Education, Sport and Culture (DESC). Hosts Manx curriculum + exam materials.

## Site structure

| Path | Content |
|:--|:--|
| `/` | Government home |
| `/government/departments/` | Departments list |
| `/government/departments/education-sport-culture/` | DESC home |
| `/services/` | Services |

## Dropdown cascade

```
1. Government → Departments → Education, Sport and Culture
2. Section: Curriculum / Schools / Students / Teachers
3. Resource: [Curriculum Document, Exam Materials, Policy]
```

## URL pattern

```
https://www.gov.im/education-sport-and-culture/{section}
```

## Anti-scraping posture

- **Open access** (very small site, no rate limit)
- **English-only** (Manx Gaelic is rare)
- **Wayback Machine** has snapshots

## BAML extraction strategy

```python
function ExtractManxEducation(
  html: Html,
) -> ManxDoc {
  client ExtractEn
  prompt #"
    Extract this Isle of Man education document.
    Return: title, section, summary, key_points (list[str]).
  "
}
```

## CCC anchors

`oideachais/dlt_sources/crown_dependencies/iom.py`

## Drift log

| Date | Event |
|--:|:--|
| 2026-01 | Initial IoM corpus |
| 2026-03 | BAML extraction |

## Decision matrix

| Decision | Choice | Rationale |
|:--|:--|:--|
| Source method | dlt REST | Small site |
| Language | English (Manx Gaelic optional) | Limited Manx content |
| Refresh | Annual | Stable |
