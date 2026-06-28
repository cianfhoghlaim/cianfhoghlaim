# S02 — examinations.ie (Ireland SEC exam materials)

**Date:** 2026-06-28
**Phase:** 3 (Live Site Discovery Reports)
**Budget:** ~75 credits
**Subagent:** research

## TL;DR

examinations.ie is the **official Irish State Examinations Commission** website — the canonical source for Leaving Cert, Junior Cycle, and Primary Curriculum exam papers + marking schemes. It's a high-priority BAML extraction target (3.4 GB+ of PDFs in our leabharlann from this site).

## Site structure

| Path | Content |
|:--|:--|
| `/en/` | English home (bilingual: `/ga/` for Irish) |
| `/en/educational-resources/` | Curriculum + exam archive |
| `/en/exam-archive/` | Past exam papers by subject + year |
| `/en/exam-archive/leaving-certificate/` | 24 subjects × 30+ years |
| `/en/exam-archive/junior-cycle/` | 24 subjects × 30+ years |
| `/en/specification-and-rubrics/` | Marking schemes + rubrics |
| `/en/sample-papers/` | Sample papers for new curricula |

## Dropdown cascade (Leabharlann ingestion flow)

```
1. Home → "Exam Archive"
2. Exam level dropdown: [Primary, Junior Cycle, Leaving Cert]
3. Subject dropdown: 24 subjects (filtered by level)
4. Year dropdown: 1995-present (30+ years per subject)
5. Component dropdown: [Exam Paper, Marking Scheme, Audio, Video]
6. Result: PDF download (URL pattern below)
```

## URL pattern

```
https://www.examinations.ie/exams/-archive-leaving-cert/-exam-papers-and-materials/{level}/{subject}/{year}/{component}.pdf
```

Examples:
- Leaving Cert Maths 2024 Paper 1: `.../lc/maths/2024/paper-1.pdf`
- Junior Cycle English 2023 Marking Scheme: `.../jc/english/2023/marking-scheme.pdf`

## PDF download endpoints

- **PDF MIME type**: `application/pdf`
- **Filename pattern**: `{subject}-{year}-{component}.pdf`
- **File size**: 100KB - 5MB per PDF
- **Total corpus**: ~15,000 PDFs across all years/subjects/components
- **BAML extraction**: MultiPartitionsDefinition (subject × material_type) in `oideachais/dagster_defs/assets/ingestion/examinations.py`

## Anti-scraping posture

- **No rate limit** observed (extensive download possible)
- **No Cloudflare challenge** (open to direct GET)
- **No JS-rendered content** (server-side HTML)
- **No login required** (public archive)
- **robots.txt**: `/sitemap.xml` exposes full URL space — use that for ingestion seed
- **Backup**: Wayback Machine has snapshots back to 2008

## BAML extraction strategy

```python
# oideachais/baml_src/examinations_extraction.baml
function ExtractExaminationPDF(
  pdf: Pdf,
  exam_level: ExamLevel,  # "primary" | "junior_cycle" | "leaving_cert"
) -> ExamPaper {
  client ExtractEnStrong
  prompt #"
    Extract the structured exam paper from this {{ exam_level }} PDF.
    Return: subject (str), year (int), component (str),
            question_count (int), max_marks (int), duration_minutes (int),
            topics (list[str]), difficulty_breakdown (dict).
  "
}
```

## CCC anchors

| Path | Purpose |
|:--|:--|
| `oideachais/dlt_sources/ireland/examinations.py` | Canonical dlt source (28 sources include this) |
| `oideachais/dagster_defs/assets/ingestion/examinations.py` | MultiPartitionsDefinition asset |
| `oideachais/baml_src/examinations_extraction.baml` | BAML extraction function |
| `cognify/rules/examinations_tables.py` | Dagster asset check |

## Drift log

| Date | Event |
|--:|:--|
| 2024-Q4 | Initial ingestion (batch via dlt filesystem) |
| 2025-Q4 | Switched to dlt REST source with sitemap.xml seed |
| 2026-03 | Added BAML extraction (ExtractEnStrong) |
| 2026-04 | Added MultiPartitionsDefinition (subject × type) |
| 2026-06-28 | v4 consolidation: source moved to `cianfhoghlaim/dlt_sources/ireland/examinations.py` |

## Decision matrix

| Decision | Choice | Rationale |
|:--|:--|:--|
| Source method | dlt REST (with sitemap.xml seed) | Efficient + idempotent |
| Partition | MultiPartitionsDefinition (subject × type) | 24×4 = 96 partitions manageable |
| Extraction | BAML ExtractEnStrong | High-accuracy for exam papers |
| Anti-scraping | None needed | Site is open |
| Refresh | Monthly cron (new exams published quarterly) | Catch new papers |

## Next research

- Compare with curriculumonline.ie (S01) and ncca.ie (S03) for curriculum cross-reference
- Add Wayback Machine snapshots for pre-2008 exams
- Implement content-hash dedup (many re-uploads have same content)
