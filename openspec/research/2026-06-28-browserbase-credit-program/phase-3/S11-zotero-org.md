# S11 — zotero.org (Leabharlann Corpus Source)

**Date:** 2026-06-28
**Phase:** 3 (Live Site Discovery Reports)
**Budget:** ~75 credits
**Subagent:** research

## TL;DR

zotero.org is the **academic reference manager** that powers the Leabharlann corpus's `zotero` subdirectory (1,800+ research papers). The Cianfhoghlaim corpus ingests user-created Zotero libraries via the Zotero Web API v3.

## Site structure

| Path | Content |
|:--|:--|
| `/` | Zotero home |
| `/groups/{group_id}` | Public group libraries |
| `/library` | Personal library |
| `/style` | Citation styles (CSL) |

## Dropdown cascade (for API)

```
1. Choose: Personal / Group library
2. Library ID (from URL)
3. API key (generated at https://www.zotero.org/settings/keys)
4. Top-level collection (or "All Items")
5. Item type: [book, journalArticle, thesis, conferencePaper, ...]
6. Result: items with metadata + attachments
```

## URL pattern

```
Web UI: https://www.zotero.org/{user|group}/{library_id}/{item_key}
API: https://api.zotero.org/{user|group}/{library_id}/items?since={version}
PDF: https://api.zotero.org/{user|group}/{library_id}/items/{item_key}/file
```

## Anti-scraping posture

- **API rate limit**: 10 req/sec (free tier), 100 req/sec (paid institutional)
- **OAuth 1.0a required** (or API key)
- **PDF attachments**: behind Zotero File Storage (free tier = 300 MB)
- **Wayback Machine**: limited (auth required)

## BAML extraction strategy

```python
function ExtractZoteroItem(
  json: Json,  # Zotero API response
) -> ZoteroItem {
  client ExtractEn
  prompt #"
    Extract this Zotero item into structured form.
    Return: title, authors (list[str]), year, publication,
            item_type, abstract (str), tags (list[str]).
  "
}
```

## CCC anchors

| Path | Purpose |
|:--|:--|
| `oideachais/dlt_sources/leabharlann/zotero.py` | Canonical Zotero dlt source |
| `oideachais/baml_src/zotero_extraction.baml` | BAML extraction |
| `oideachais/dagster_defs/assets/ingestion/zotero_assets.py` | Dagster asset |
| `cognify/rules/zotero_corpus.py` | Lists 1,800+ items in zotero subdir |

## Drift log

| Date | Event |
|--:|:--|
| 2025-08 | Initial Zotero API v3 ingestion |
| 2025-11 | Switched from public groups to personal library (per Zotero TOS) |
| 2026-02 | BAML extraction |
| 2026-04 | Increased refresh rate (weekly) for new papers |

## Decision matrix

| Decision | Choice | Rationale |
|:--|:--|:--|
| Source method | Zotero Web API v3 | Official + stable |
| Auth | OAuth 1.0a (or API key) | Per Zotero docs |
| Rate limit | 10 req/sec (free tier) | Within TOS |
| Refresh | Weekly cron | New papers added regularly |
| Extraction | BAML ExtractEn | Citation metadata is structured |
