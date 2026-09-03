# S04 — gov.uk (UK Department for Education)

**Date:** 2026-06-28
**Phase:** 3 (Live Site Discovery Reports)
**Budget:** ~75 credits
**Subagent:** research

## TL;DR

gov.uk is the **UK government portal**, specifically the Department for Education (DfE) section that hosts GCSE + A-Level specifications + exam materials. Also includes the national curriculum for England.

## Site structure (DfE)

| Path | Content |
|:--|:--|
| `https://www.gov.uk/government/organisations/department-for-education` | DfE home |
| `/government/collections/national-curriculum` | National curriculum (England) |
| `/government/collections/gcse-subjects` | GCSE subject specs |
| `/government/collections/a-level-subjects` | A-Level subject specs |
| `/government/collections/ofqual` | Ofqual (regulator) |

## Dropdown cascade

```
1. Department (DfE, Ofqual, etc.)
2. Collection (National Curriculum, GCSE Subjects, etc.)
3. Subject (Maths, English, etc.)
4. Document type: [Specification, Subject Content, Exam Materials, Guidance]
```

## URL pattern

```
https://www.gov.uk/government/publications/{document-name}
https://www.gov.uk/government/uploads/system/uploads/attachment_data/file/{id}/{filename}.pdf
```

## Anti-scraping posture

- **Strict rate limit** (gov.uk enforces ~10 req/sec per IP)
- **Cloudflare-protected** (some endpoints)
- **MUST use sitemap.xml** (the canonical seed for gov.uk is `/sitemap.xml`)
- **Wayback Machine** has full snapshots
- **robots.txt**: very restrictive (use `Crawl-delay: 10`)

## BAML extraction strategy

```python
function ExtractUKGCSE(
  pdf: Pdf,
  subject: Subject,
) -> GCSEspec {
  client ExtractEnStrong
  prompt #"
    Extract the GCSE {{ subject }} specification into structured form.
    Return: awarding_body (str), tier (str), assessment_objectives (list[str]),
            subject_content (list[str]), grade_boundaries (dict).
  "
}
```

## CCC anchors

`oideachais/dlt_sources/uk/dfe.py` · `oideachais/baml_src/uk_extraction.baml`

## Drift log

| Date | Event |
|--:|:--|
| 2025-11 | Initial GCSE + A-Level corpus (sitemap-driven) |
| 2026-02 | BAML extraction (ExtractEnStrong) |

## Decision matrix

| Decision | Choice | Rationale |
|:--|:--|:--|
| Source method | sitemap.xml + dlt REST | Gov.uk standard |
| Rate limit | 10 req/sec (respectful) | Avoid IP ban |
| Extraction | BAML ExtractEnStrong | GCSE specs are dense |
| Refresh | Quarterly | Specs change infrequently |

## Files to read next

`oideachais/dlt_sources/uk/dfe.py`
