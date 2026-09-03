# S07 — education-ni.gov.uk (Northern Ireland CCEA)

**Date:** 2026-06-28
**Phase:** 3 (Live Site Discovery Reports)
**Budget:** ~75 credits
**Subagent:** research

## TL;DR

education-ni.gov.uk is the **Department of Education Northern Ireland (DENI) + Council for the Curriculum, Examinations & Assessment (CCEA)** portal. Hosts Northern Ireland Curriculum + GCSE specifications (same as England, but distinct administration).

## Site structure

| Path | Content |
|:--|:--|
| `/` | DENI home |
| `/schools-and-colleges/` | Schools + colleges |
| `/managing-schools/` | School management |
| `/topics/` | Topics (curriculum, exams, etc.) |

## Dropdown cascade

```
1. Section (Schools, Curriculum, Exams)
2. Sub-section (e.g., Curriculum → Primary / Post-primary)
3. Document type: [Curriculum, Specification, Guidance]
```

## URL pattern

```
https://www.education-ni.gov.uk/articles/{article-name}
https://www.education-ni.gov.uk/publications/{publication-name}
```

## Anti-scraping posture

- **Open access** (no login)
- **Strict rate limit** (gov.uk standard)
- **Cross-jurisdiction**: CCEA specs often link to AQA/OCR/Edexcel (UK awarding bodies)
- **Wayback Machine** has snapshots

## BAML extraction strategy

```python
function ExtractNorthernIrelandCurriculum(
  pdf: Pdf,
  level: Level,  # "primary" | "post_primary"
) -> NICurriculum {
  client ExtractEn
  prompt #"
    Extract this Northern Ireland {{ level }} curriculum document.
    Return: stage (str), subjects (list[str]),
            assessment_objectives (list[str]), cross_curricular_skills (list[str]).
  "
}
```

## CCC anchors

`oideachais/dlt_sources/uk/ni_ccea.py`

## Drift log

| Date | Event |
|--:|:--|
| 2025-12 | Initial NI corpus |
| 2026-03 | BAML extraction |

## Decision matrix

| Decision | Choice | Rationale |
|:--|:--|:--|
| Source method | dlt REST + sitemap.xml | Standard gov.uk pattern |
| Cross-ref | Link to AQA/OCR/Edexcel awarding bodies | NI uses English awarding bodies |
| Refresh | Annual | Stable |
