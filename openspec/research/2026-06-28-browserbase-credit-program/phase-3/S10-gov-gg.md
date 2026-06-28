# S10 — gov.gg (Guernsey Education Services)

**Date:** 2026-06-28
**Phase:** 3 (Live Site Discovery Reports)
**Budget:** ~75 credits
**Subagent:** research

## TL;DR

gov.gg is the **Government of Guernsey** portal, specifically the Committee for Education, Sport & Culture. Hosts Guernsey Curriculum + exam materials (follows UK GCSE/A-Level with Guernsey-specific additions).

## Site structure

| Path | Content |
|:--|:--|
| `/` | Government home |
| `/government/committee-of-the-day/committee-for-education-sport-culture/` | Committee home |

## Dropdown cascade

```
1. Government → Committee for Education, Sport & Culture
2. Section: Schools / Curriculum / Students
3. Resource: [Curriculum Document, Exam Materials]
```

## URL pattern

```
https://www.gov.gg/committee-for-education-sport-culture
```

## Anti-scraping posture

- **Open access** (small site, no rate limit)
- **English-only**
- **Wayback Machine** has snapshots

## BAML extraction strategy

```python
function ExtractGuernseyEducation(
  html: Html,
) -> GuernseyDoc {
  client ExtractEn
  prompt #"
    Extract this Guernsey education document.
    Return: title, section, summary, key_points (list[str]).
  "
}
```

## CCC anchors

`oideachais/dlt_sources/crown_dependencies/ggy.py`

## Drift log

| Date | Event |
|--:|:--|
| 2026-01 | Initial Guernsey corpus |
| 2026-03 | BAML extraction |

## Decision matrix

| Decision | Choice | Rationale |
|:--|:--|:--|
| Source method | dlt REST | Small site |
| Language | English | Standard |
| Refresh | Annual | Stable |
