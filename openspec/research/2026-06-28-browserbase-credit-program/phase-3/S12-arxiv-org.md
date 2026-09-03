# S12 — arxiv.org (Leabharlann Research Papers Source)

**Date:** 2026-06-28
**Phase:** 3 (Live Site Discovery Reports)
**Budget:** ~75 credits
**Subagent:** research

## TL;DR

arxiv.org is the **open-access scientific paper repository** — the primary source for ML/AI/NLP research papers cited in the Leabharlann corpus. The Cianfhoghlaim corpus ingests arxiv papers via the OAI-PMH API + arxiv API.

## Site structure

| Path | Content |
|:--|:--|
| `/` | Home |
| `/list/{category}/recent` | Recent papers by category |
| `/list/{category}/{YYMM}` | Papers by month |
| `/abs/{paper_id}` | Abstract page |
| `/pdf/{paper_id}` | PDF download |
| `/api` | API docs |

## Dropdown cascade (for API)

```
1. Category: [cs.LG, cs.CL, cs.AI, cs.CV, ...]  (40+ categories)
2. Date range: from/to
3. Max results: limit (default 10, max 2000)
4. Sort: [relevance, lastUpdatedDate, submittedDate]
5. Result: list of papers with metadata + abstracts
```

## URL pattern

```
https://arxiv.org/abs/{paper_id}        # e.g., 2501.12345
https://arxiv.org/pdf/{paper_id}       # e.g., 2501.12345v2
https://arxiv.org/list/cs.LG/2606       # category + month
https://export.arxiv.org/oai2           # OAI-PMH endpoint
https://export.arxiv.org/api/query      # arxiv API (REST-ish)
```

## Anti-scraping posture

- **Mild rate limit** (~1 req/sec recommended; arxiv asks for `Crawl-delay: 20`)
- **No login required** (open access)
- **API requires User-Agent** (must identify as a research project)
- **Wayback Machine** has full snapshots back to 1991

## BAML extraction strategy

```python
function ExtractArxivPaper(
  pdf: Pdf,
  arxiv_id: str,  # "2501.12345v2"
) -> ArxivPaper {
  client ExtractEnStrong
  prompt #"
    Extract this arxiv paper {{ arxiv_id }} into structured form.
    Return: title, authors (list[str]), abstract (str),
            primary_category (str), all_categories (list[str]),
            key_contributions (list[str]), methodology (str),
            benchmark_results (dict), cited_papers (list[str]).
  "
}
```

## CCC anchors

| Path | Purpose |
|:--|:--|
| `oideachais/dlt_sources/leabharlann/arxiv.py` | Canonical arxiv dlt source |
| `oideachais/baml_src/arxiv_extraction.baml` | BAML extraction |
| `oideachais/dagster_defs/assets/ingestion/arxiv_assets.py` | Dagster asset |
| `cognify/rules/arxiv_corpus.py` | Lists 600+ arxiv papers in leabharlann |

## Drift log

| Date | Event |
|--:|:--|
| 2025-07 | Initial arxiv API ingestion (cs.LG, cs.CL) |
| 2025-11 | Expanded to 10+ categories |
| 2026-02 | BAML extraction (ExtractEnStrong for methodology extraction) |
| 2026-04 | Added OAI-PMH fallback (for older papers) |

## Decision matrix

| Decision | Choice | Rationale |
|:--|:--|:--|
| Source method | arxiv API (REST) + OAI-PMH (legacy) | Both supported |
| Categories | cs.LG, cs.CL, cs.AI, cs.CV, cs.NE, ... | ML/AI focus |
| Refresh | Daily (incremental) | New papers every day |
| Rate limit | 1 req/sec | Respect arxiv TOS |
| User-Agent | `Cianfhoghlaim/1.0 (research; mailto:cian@cianfhoghlaim.ie)` | Required by arxiv |
| Extraction | BAML ExtractEnStrong | Dense academic text |
