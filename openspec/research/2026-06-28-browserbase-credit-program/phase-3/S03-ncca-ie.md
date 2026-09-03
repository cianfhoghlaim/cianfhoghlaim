# S03 — ncca.ie (Ireland NCCA)

**Date:** 2026-06-28
**Phase:** 3 (Live Site Discovery Reports)
**Budget:** ~75 credits
**Subagent:** research

## TL;DR

ncca.ie is the **National Council for Curriculum and Assessment (NCCA) main portal** — the source of truth for all curriculum + assessment policy in Ireland. Different from curriculumonline.ie (S01) which is the primary-specific portal.

## Site structure

| Path | Content |
|:--|:--|
| `/en/` | English home |
| `/en/Publications/` | Reports + frameworks |
| `/en/Curriculum/` | Curriculum overview (post-primary) |
| `/en/Assessment/` | Assessment policy + frameworks |
| `/en/Senior-Cycle/` | Senior cycle (Leaving Cert) redevelopment |

## Dropdown cascade

```
1. Section (Curriculum, Assessment, Publications, Senior Cycle)
2. Sub-section (e.g., Curriculum → Senior Cycle → Subjects)
3. Document type: [Framework, Specification, Background Paper, Consultation]
4. Year (publication year)
```

## URL pattern

```
https://ncca.ie/en/{section}/{subsection}/{document-name}
https://ncca.ie/getfile/{id}
```

## Anti-scraping posture

- **Open access** (no login)
- **No rate limit**
- **No robots.txt restrictions** for standard crawlers
- **PDF + HTML mixed** (many resources are PDFs)

## BAML extraction strategy

```python
function ExtractNCCAPolicy(
  pdf: Pdf,
  document_type: DocumentType,
) -> PolicyDocument {
  client ExtractEnStrong
  prompt #"
    Extract this NCCA {{ document_type }} into structured form.
    Return: title, publication_date, scope, key_recommendations (list[str]),
            affected_subjects (list[str]), implementation_timeline.
  "
}
```

## CCC anchors

`oideachais/dlt_sources/ireland/ncca.py` · `oideachais/baml_src/ncca_extraction.baml`

## Drift log

| Date | Event |
|--:|:--|
| 2025-10 | Initial NCCA policy corpus (dlt REST) |
| 2026-03 | BAML extraction (ExtractEnStrong for policy docs) |

## Decision matrix

| Decision | Choice | Rationale |
|:--|:--|:--|
| Source method | dlt REST + sitemap.xml | Open + structured |
| Extraction | BAML ExtractEnStrong | Policy docs need high accuracy |
| Refresh | Monthly | Policy changes infrequently |

## Files to read next

`oideachais/dlt_sources/ireland/ncca.py`
