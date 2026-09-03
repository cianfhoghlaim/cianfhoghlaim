# S06 — gov.wales (Wales Curriculum for Wales)

**Date:** 2026-06-28
**Phase:** 3 (Live Site Discovery Reports)
**Budget:** ~75 credits
**Subagent:** research

## TL;DR

gov.wales (Hwb + Welsh Government Education) hosts the **Curriculum for Wales** — a progression-based curriculum for ages 3-16, with Welsh language as the primary medium.

## Site structure

| Path | Content |
|:--|:--|
| `/education-and-skilling/` | Education home |
| `/curriculum-for-wales/` | Curriculum for Wales main page |
| `/curriculum-for-wales/curriculum-guidance-for-3-16-year-olds/` | The core curriculum guidance |
| `/curriculum-for-wales/progression-references/` | Progression steps |

## Dropdown cascade

```
1. Curriculum for Wales
2. Area: [Languages, Literacy + Communication, Mathematics + Numeracy, Science + Technology, ...]
3. Progression step: [Progression Step 1, 2, 3, 4, 5]
4. Resource type: [Curriculum Guidance, Progression Reference, Code of Practice]
```

## URL pattern

```
https://www.gov.wales/curriculum-for-wales/{area}
https://www.gov.wales/{document-slug}
```

## Anti-scraping posture

- **Open access** (bilingual Welsh/English)
- **No strict rate limit**
- **Welsh language**: full bilingual site (Cymraeg + English)
- **Wayback Machine** has snapshots

## BAML extraction strategy

```python
function ExtractCurriculumWales(
  html: Html,
  area: Area,
  language: Language,  # "en" | "cy"
) -> CurriculumWalesArea {
  client ExtractEn
  prompt #"
    Extract this Curriculum for Wales {{ area }} page ({{ language }}).
    Return: area_name, statements_of_what_matters (list[str]),
            progression_steps (list[ProgressionStep]),
            cross_curricular_responsibilities (list[str]).
  "
}
```

## CCC anchors

`oideachais/dlt_sources/uk/wales_cfW.py` · `oideachais/baml_src/cfw_extraction.baml`

## Drift log

| Date | Event |
|--:|:--|
| 2026-01 | Initial CfW corpus |
| 2026-03 | Bilingual extraction (English + Welsh) |

## Decision matrix

| Decision | Choice | Rationale |
|:--|:--|:--|
| Language | Both English + Welsh | Multilingual required |
| Source method | dlt REST | Standard |
| Refresh | Annual | CfW is stable |
