# 2026-09-06-ciancheiltis-v1

## Why

The existing `dlt_sources/british_isles/**` DLT sources for the
Celtic-language jurisdictions (Wales, Scotland, Northern Ireland,
Isle of Man) were authored against the pre-v7 Firecrawl tool surface
(`firecrawl_scrape` + `firecrawl_search` only) and ship with almost no
**real bilingual content** in the local cache:

- `en-cy (Wales)` — **0 rows cached** anywhere in `stedding/` — the
  biggest gap.
- `en-gd (Scotland)` — 1 EN sample file only.
- `en-ga (NI)` — 1 EN sample file only.
- `en-gv (Isle of Man)` — 0 rows cached.
- `en-ga (EU)` — 18 placeholder JSON files (no real EUR-Lex document).

The only rich bilingual coverage in the codebase is `en-ga (Republic)`
with 2,388 EN + 2,010 GA cached pages from `ncca.ie` and 1,398 EN +
1,000 GA from `curriculumonline.ie`. This change extends that
materialised coverage to the four other Celtic pairs plus the EU-level
`en-ga` dimension (where Irish is a treaty language under Council
Regulation No 1/1958), and re-platforms the work onto the v1
Firecrawl MCP tool surface
(`https://docs.firecrawl.dev/mcp-server/tools`) — including the
currently unused `firecrawl_agent`, `firecrawl_monitor_*`,
`firecrawl_interact`, `firecrawl_parse`, and `firecrawl_map` tools.

The umbrella project name is `ciancheiltis` — Irish *[cian]*
(long) + *[Cheiltis]* (Celtic-ness) — and is a tangential branch of
`cianfhoghlaim`. It is **distinct** from `celtic-language-pipeline`
(curated corpora: Gaois, Dúchas, Heritage, Canuint, UD, Local docs,
Celtic curriculum) and from `british-isles-education-pipeline`
(education-only: Leaving Cert + A-Level + GCSE + National 5 + WJEC
+ CCEA).

Sister-language bodies without any current DLT source include:
Welsh Language Commissioner, Coleg Cymraeg Cenedlaethol (Termau),
Senedd Cymru, Techiaith, Bòrd na Gàidhlig, Stòrlann Nàiseanta, Sabhal
Mòr Ostaig, DASG, BBC ALBA, Culture Vannin, Learn Manx, Bunscoill
Ghaelgagh, Foras na Gaeilge, Gaois, Téarma, Teanglann, Comhairle na
Gaelscolaíochta (CnaG), TED, IATE, EUR-Lex `GA/TXT`, Cadhan Aonair,
Foclóir Gàidhlig-Gaeilge, and CLARIN-UK — none of which currently
exist as DLT sources.

## What changes

### 1. New umbrella spec `ciancheiltis`

Adds `openspec/specs/ciancheiltis/spec.md` as the canonical
umbrella spec. 13 Requirements (covering 6-phase staging,
10-theme taxonomy, canonical file layout, content-based
language detection, opaque-URL scanner, gov.wales WAF bypass,
CLARIN-UK integration, BAML extraction, CocoIndex R1–R4,
Dagster 5-layer, MotherDuck Dive + Flight, cross-pipeline
integration, and a DO NOT section).

### 2. New canonical file layout

Adds `dlt_sources/ciancheiltis/` as a sibling to
`dlt_sources/british_isles/`:

```text
dlt_sources/ciancheiltis/
├── clarin_uk/         # CLARIN-UK Celtic corpora + Cadhan + Foclóir (PR0.1)
├── en_cy/             # Phase 1 — Wales (en-cy)
├── en_ga_roi/         # Phase 2 — Republic of Ireland (en-ga)
├── en_ga_ni/          # Phase 3 — Northern Ireland (en-ga)
├── en_gd/             # Phase 4 — Scotland (en-gd)
├── en_gv/             # Phase 5 — Isle of Man (en-gv)
├── en_ga_eu/          # Phase 6 — EU (en-ga)
└── _shared/           # language_detector, opaque_url_scanner, gov_wales_waf_bypass
```

### 3. PR0.1 — Cross-domain Celtic linguistic bridges

Adds 3 new DLT sources under `dlt_sources/ciancheiltis/clarin_uk/`:
- `corpus_browser.py` — catalogues the CLARIN-UK Celtic resource
  family and ingests 10+ corpora into `lancedb://md:cianfhoghlaim/clarin_uk_corpora`.
- `cadhan_aonair.py` — ingests UD Irish + UD Welsh + UD Scottish
  Gaelic + UD Breton + UD Manx treebanks.
- `focloir_gd_ga.py` — ingests the cross-Celtic dictionary at
  `https://kevinscannell.com/files/gd2ga.pdf`.

Adds `notebooks/_shared/firecrawl_corpus_loader.py` key
`clarin_uk_corpora` (weekly cadence).

### 4. PR0.2 — Shared _shared/ helpers

Adds 4 new modules under `dlt_sources/ciancheiltis/_shared/`:
- `language_detector.py` — lingua-py content-based detection
  (never trust `metadata["language"]`)
- `opaque_url_scanner.py` — discovers numeric/slug-only URLs that
  hide their language pair
- `gov_wales_waf_bypass.py` — gov.wales CloudFront + WAF + CAPTCHA
  fallback (firecrawl_interact + hwb.gov.wales mirror)
- `bilingual_page_validator.py` — checks "is this the same article
  in two languages?"

### 5. PR0.3 — Phase 1 (en-cy / Wales) minimum-viable pipeline

Adds 8 new DLT sources under `dlt_sources/ciancheiltis/en_cy/`,
one per theme that ships bilingual content for Wales:
- `legislation.py` (T1) — legislation.gov.uk/uksi + /wsi dual crawl
- `education.py` (T3) — Hwb + WJEC/CBAC
- `language_commissioner.py` (T5) — welshlanguagecommissioner.wales
- `termau_cymru.py` (T6) — colegcymraeg.ac.uk/termau/
- `local_government.py` (T8) — 22 Welsh LAs
- `healthcare.py` (T4) — NHS Wales patient info
- `court_service.py` (T7) — HMCTS Welsh
- `policy_consultations.py` (T2) — gov.wales consultations

### 6. PR0.4 — Phase 1 BAML + CocoIndex + Dagster integration

Adds 1 new BAML extraction function
`ExtractCiancheiltisBilingualPage` in
`baml_src/british_isles/_shared/ciancheiltis.baml`. Adds 1 new
CocoIndex v1 App under `cocoindex_flows/british_isles/uk/`.
Adds 1 new Dagster 5-layer asset group under
`orchestration/defs/2_materials/ciancheiltis/en_cy/`.

### 7. PR0.5 — Phase 1 MotherDuck Dive + marimo

Adds `motherduck/dives/ciancheiltis_en_cy_dive.py` showing per-theme
coverage and metadata-language-mismatch rates. Adds
`notebooks/ciancheiltis_en_cy.py` marimo notebook (dual-mode).

### 8. Phases 2–6

Replicates the Phase 1 template for `en-ga (Republic)`, `en-ga (NI)`,
`en-gd (Scotland)`, `en-gv (Isle of Man)`, `en-ga (EU)`. Each phase
gates the next on the RAGAS ≥ 0.70 bilingual-pair coverage gate.

### 9. 1 MODIFIED + 1 MODIFIED spec deltas

- ADDED Requirements on `ciancheiltis/spec.md` (new umbrella — 13
  Requirements including DO NOT).
- ADDED Requirement on `bilingual_concept_registry.py` to extend the
  registry writer with `stedding/education/bilingual_concepts/ciancheiltis_<phase>__<theme>.jsonl`
  paths without overwriting the existing Ireland (en-ga) JSONL files.

## Dependencies

```yaml
Blocked by:        none
Blocked by (soft): 2026-09-15-celtic-language-corpus-extension-v1
Affected repos:    cianfhoghlaim (single-repo change)
Push target:       origin/main
```

## Acceptance gates

- `openspec validate 2026-09-06-ciancheiltis-v1 --strict` passes
- `dg check yaml` passes on all new `defs.yaml` files
- `mise run lint:skills` still passes
- `mise run baml:generate` shows 0 errors
- Phase 1 RAGAS ≥ 0.70 bilingual-pair coverage gate fires (green)
- Phase 1 metadata-language-mismatch log demonstrates at least
  one success on `legislation.gov.uk/uksi/2007/1484/made`

## Cross-references

- [`celtic-language-pipeline`](../../specs/celtic-language-pipeline/spec.md) — curated corpora (companion spec)
- [`british-isles-education-pipeline`](../../specs/british-isles-education-pipeline/spec.md) — education-only bilingual pipeline
- [`centralized-model-registry`](../../specs/centralized-model-registry/spec.md) — LlamaSwap routing table
- [`dagster-5-layer-component-architecture`](../../specs/dagster-5-layer-component-architecture/spec.md) — asset graph pattern
- `ciancheiltis/README.md` — user-facing orientation
- `.agents/skills/firecrawl/SKILL.md` — Firecrawl MCP tool surface
- `.agents/skills/dlt/SKILL.md` — DLT conventions
