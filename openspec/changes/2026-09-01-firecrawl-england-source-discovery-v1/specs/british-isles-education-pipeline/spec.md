## ADDED Requirements

### Requirement: The Firecrawl MCP server MUST be used to discover the official PDF URLs for each jurisdiction

The Cianfhoghlaim british-isles-education-pipeline capability MUST
use the canonical Firecrawl MCP server at
`agents/meaisinfhoghlaim/firecrawl_mcp/client.py` to discover the
official PDF URLs for each British Isles jurisdiction before DLT
sources are written.

The 8 jurisdictions and their canonical sources:

1. **IE (Ireland)** — NCCA.ie + examinations.ie + curriculumonline.ie + gov.ie circulars + Tusla + NCSE
2. **EN (England)** — DfE + Ofqual + AQA + OCR + Pearson Edexcel + Cambridge + UCAS
3. **SC (Scotland)** — SQA + Education Scotland + Scottish Government
4. **WL (Wales)** — WJEC + CBAC + Welsh Government
5. **NI (Northern Ireland)** — CCEA + DENI (Department of Education NI)
6. **IM (Isle of Man)** — IoM Government Education
7. **JE (Jersey)** — States of Jersey Education
8. **GG (Guernsey)** — States of Guernsey Education

The canonical MCP client is `FirecrawlMCPClient` (keyless tier
exposes `firecrawl_search` + `firecrawl_scrape` + `firecrawl_parse`;
authenticated tier exposes the full 12-tool surface).

#### Scenario: A new jurisdiction is added

- **WHEN** a developer adds a new DLT source for a new jurisdiction
  (e.g. Scotland SQA)
- **THEN** the developer SHALL first use `FirecrawlMCPClient.search(...)`
  to discover the canonical PDF URLs for that jurisdiction
- **AND** the developer SHALL record the discovered URLs in
  `data/bi_ep/syllabi_raw/<jurisdiction>/README.md`
- **AND** the DLT source SHALL use the discovered URLs as the
  source of truth (NOT hardcoded URLs from memory)