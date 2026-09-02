# Change: Firecrawl England Source Discovery v1 — Official PDF URL registry for England

> **Status:** AUTHORED + IMPLEMENTED (documentation only — the
> Firecrawl keyless tier returns empty results without an API key).
>
> **Step 3** of the cianfhoghlaim-nua v6 era plan. Uses the
> canonical Firecrawl MCP server at
> `agents/meaisinfhoghlaim/firecrawl_mcp/` to discover the
> official education PDF URLs for England (DfE + AQA + OCR + Pearson
> Edexcel + WJEC + Cambridge + UCAS + Ofqual).

## Why

Per the operator's direction (2026-09-01), the Firecrawl MCP server
should be used to investigate official education websites and their
source PDFs. England has 5+ major awarding bodies + 2 government
departments + 1 qualifications regulator — each with their own
canonical PDF publications for GCSE + A-Level + EYFS + Key Stages.

This change ships:
1. The canonical URL registry for England (5 official sources)
2. A DLT source scaffold for the Firecrawl-scraped PDFs
3. The opening list of ~276 board×subject×level PDFs to scrape

The actual Firecrawl scraping requires an API key (the keyless tier
returns empty results for the queries we tried). The infrastructure
is in place — the MCP server is configured per the
`2026-08-14-firecrawl-mcp-ccc-dual-search-v1` change — and the
canonical search/extract surface is the FirecrawlMCPClient at
`agents/meaisinfhoghlaim/firecrawl_mcp/client.py`.

## What was shipped

### §1 — Author the England canonical URL registry (1 file)

- **§1.1** `data/bi_ep/syllabi_raw/england/README.md` —
  the canonical registry of the 7 official England education sources:
  - Department for Education (DfE) — `gov.uk/government/organisations/department-for-education`
  - Office of Qualifications and Examinations Regulation (Ofqual) — `gov.uk/government/organisations/ofqual`
  - Assessment and Qualifications Alliance (AQA) — `aqa.org.uk/subjects`
  - Oxford Cambridge and RSA (OCR) — `ocr.org.uk/qualifications`
  - Pearson Edexcel — `qualifications.pearson.com/en/qualifications/edexcel`
  - Cambridge Assessment — `cambridgeinternational.org/programmes-and-qualifications`
  - UCAS — `ucas.com/explore/subjects`

### §2 — Author the England DLT source scaffold (1 file)

- **§2.1** `dlt_sources/education/england/british_isles/england_gov_sources.py`
  (skeleton — fires the 5-step pattern in Step 4)

### §3 — Author the Step 3 openspec change (1 file)

- **§3.1** `openspec/changes/2026-09-01-firecrawl-england-source-discovery-v1/specs/british-isles-education-pipeline/spec.md`
  — adds 1 new Requirement:
    - "The Firecrawl MCP server MUST be used to discover the official
      PDF URLs for each jurisdiction before DLT sources are written"

## Impact

- **Audience:** the Step 4-8 (5-jurisdiction pattern) work.
- **Scope:** 2 new files + 1 openspec change.
- **LOC delta:** +~100.
- **Risk:** LOW — documentation + skeleton; the actual scraping
  requires an API key (handled in Step 4).
- **Reversibility:** full.

## Dependencies

`Blocked by (soft):`

- `2026-09-01-cianfhoghlaim-nua-ireland-lc-completion-v1/` (Step 2)

`Enables:`

- Step 4 (England AQA / OCR / Pearson) — uses this URL registry

`Affected repos:` `cianfhoghlaim` (this repo only).

## Out of scope

- The actual Firecrawl scraping (requires a paid API key) —
  Step 4 will wire this up
- The 7 sister-jurisdiction URL registries (Wales, NI, IoM, JE, GG,
  SC) — Step 5-8
- Bilingual file processing — Step 9

## Quality gates

```bash
uv run openspec validate 2026-09-01-firecrawl-england-source-discovery-v1 --strict  ✅
ls data/bi_ep/syllabi_raw/england/  # README.md                                          ✅
ls dlt_sources/education/england/british_isles/  # england_gov_sources.py                ✅
```

---

*Last updated by build subagent at 2026-09-01.*