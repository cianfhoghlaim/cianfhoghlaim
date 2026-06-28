# S01 — curriculumonline.ie (Ireland SEC primary curriculum)

**Date:** 2026-06-28
**Phase:** 3 (Live Site Discovery Reports)
**Budget:** ~75 credits
**Subagent:** research

## TL;DR

curriculumonline.ie is the **National Council for Curriculum and Assessment (NCCA) primary curriculum portal**. It hosts the primary school curriculum (English, Irish, Maths, etc.) for Junior Infants through 6th Class.

## Site structure

| Path | Content |
|:--|:--|
| `/en/` | English home |
| `/en/Primary/` | Primary curriculum section |
| `/en/Primary/English/` | Subject-specific pages |
| `/en/Primary/English/Strands/` | Strand-level pages |
| `/en/Primary/English/Strands/Developing-English-Literacy/` | Strand units |
| `/en/Primary/Assessment/` | Assessment guidelines |

## Dropdown cascade

```
1. Primary section → Subject (English, Gaeilge, Maths, etc.)
2. Strand (within subject)
3. Strand unit / learning outcome
4. Resource type: [Curriculum Document, Teacher Guidelines, Sample Plan]
```

## URL pattern

```
https://www.curriculumonline.ie/en/Primary/{subject}/{strand}/{unit}
```

PDFs:
```
https://www.curriculumonline.ie/getfile/{id}  # dynamic ID
```

## Anti-scraping posture

- **Mild rate limit** (sustainable download, but don't parallelize >5 requests)
- **No login required** (public)
- **Bilingual**: `/en/` and `/ga/` mirror each other
- **robots.txt**: allows all standard crawlers

## BAML extraction strategy

```python
function ExtractCurriculumStrand(
  html: Html,
  subject: Subject,
  classLevel: ClassLevel,  # "junior_infants" | "senior_infants" | ... | "sixth_class"
) -> CurriculumStrand {
  client ExtractEn
  prompt #"
    Extract the curriculum strand from this {{ subject }} {{ classLevel }} page.
    Return: strand_name, learning_outcomes (list[str]),
            assessment_criteria (list[str]), examples (list[str]).
  "
}
```

## CCC anchors

`oideachais/dlt_sources/ireland/curriculum_online.py` · `oideachais/baml_src/curriculum_extraction.baml`

## Drift log

| Date | Event |
|--:|:--|
| 2025-09 | Initial ingestion (dlt filesystem, HTML extraction) |
| 2026-02 | Switched to dlt REST with sitemap.xml |
| 2026-04 | BAML extraction (ExtractEn for structured curriculum) |

## Decision matrix

| Decision | Choice | Rationale |
|:--|:--|:--|
| Source method | dlt REST (sitemap.xml seed) | Efficient + idempotent |
| Extraction | BAML ExtractEn | Standard extraction |
| Refresh | Quarterly cron | NCCA updates curriculum ~2x/year |
| Bilingual | Process both /en/ and /ga/ | Cross-corpus search needs both |

## Files to read next

`oideachais/dlt_sources/ireland/curriculum_online.py` · `oideachais/baml_src/curriculum_extraction.baml`
