# 102 - Zotero Web API v3 (deferred site)

**Status:** Researched 2026-06-29 via firecrawl MCP
**Canonical source:** https://www.zotero.org/support/dev/web_api/v3/start
**Cianfhoghlaim footprint:** 1 leabharlann DLT source at
`cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/leabharlann/zotero.py`
+ 1 v1 CocoIndex App `leabharlann_zotero_embedding` + 2 cross-archive
edge types in Cognee.

## TL;DR

Zotero Web API v3 is the REST API for Zotero's personal + group
libraries. The cianfhoghlaim platform uses it to ingest the
researcher's PDF + citation corpus into the leabharlann lakehouse.

**The 5 endpoints we use:**

1. **Read items** — `GET /users/{userID}/items?format=json,data,bib,citation`
2. **Read full-text** — `GET /items/{itemKey}/file` (returns PDF bytes)
3. **Get metadata** — `GET /item/{itemKey}` (title, authors, abstract)
4. **Search** — `GET /users/{userID}/items?q={query}&qmode=titleCreatorYear`
5. **Collections** — `GET /users/{userID}/collections`

The Python client `pyzotero` (https://github.com/urschrei/pyzotero)
wraps all 5 endpoints with a clean iterator API and is the
canonical ingestion pattern for the leabharlann corpus.

## Code

```python
from pyzotero import zotero
zot = zotero.Zotero(
    library_id=os.environ["ZOTERO_USER_ID"],
    library_type="user",
    api_key=os.environ["ZOTERO_API_KEY"],
)
for item in zot.everything(zot.items()):
    # item["data"]["title"], item["data"]["creators"], item["data"]["abstractNote"]
    yield {"key": item["key"], **item["data"]}
```

The DLT source at `leabharlann/zotero.py` wraps this with
MultiPartitions (collection × year) and writes to
`oideachais.leabharlann.zotero` in DuckLake.

## Env

- `ZOTERO_USER_ID` — set in `.infisical.env` to
  `infisical://dev-baile/zotero/user_id`
- `ZOTERO_API_KEY` — set in `.infisical.env` to
  `infisical://dev-baile/zotero/api_key`

## ccc anchors

- `leabharlann` skill (planned; not yet created)
- `cocoindex` skill (v1 App pattern for embeddings)
- `cognee` skill (cross-archive edge types)

## Anti-patterns

- **Polling `/items` in a tight loop** — Zotero returns 304 Not
  Modified for unchanged items; use `If-Mod-Since-Version` header
- **Storing full PDFs in DLT** — store the `itemKey` + download
  the PDF on-demand via the dedicated file endpoint
- **Hitting `/items` for 1M+ items without pagination** — use
  the `everything()` iterator (handles pagination internally)

## Decision matrix

| Use Zotero API when | Use Firecrawl when | Use pyzotero when |
|:--|:--|:--|
| Researcher's own library | Web scraping Zotero.org pages | Python integration |
| Need full-text content | Need PDF download from URL | Both (canonical pattern) |
| Citation export (BibTeX, CSL) | Web archives / snapshots | Bulk ingestion |
| Group library sharing | Public Zotero library pages | Local library sync |
