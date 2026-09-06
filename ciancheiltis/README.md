# ciancheiltis

**Long-distance Celtic bilingual alignment — a tangential branch of
`cianfhoghlaim`.**

`ciancheiltis` (Irish *[cian]* + *[Cheiltis]* — "long-distance
Celtic-ness") crawls, ingests, extracts, aligns, and surfaces Welsh-,
Irish-, Scottish Gaelic-, and Manx-language government publications
that, **by law**, must exist in both an official majority language
(English) and a recognised Celtic minority or co-official language.

It is a sibling umbrella to `celtic-language-pipeline` (curated corpora
— Gaois, Dúchas, Heritage, Canuint, UD, Local documents, Celtic
curriculum) and `british-isles-education-pipeline` (education-only —
Leaving Cert + A-Level + GCSE + National 5 + WJEC + CCEA).

---

## Why

The existing `dlt_sources/british_isles/**` DLT sources for the
Celtic-language jurisdictions were authored against the pre-v7
Firecrawl tool surface and ship almost no real bilingual content in
the local cache:

| Pair | Local cache rows |
|---|---|
| `en-ga (Republic)` | **richest** (~4,464 pairs — ncca.ie + curriculumonline.ie + LC PDFs) |
| `en-cy (Wales)` | **0 rows** |
| `en-ga (NI)` | 1 EN sample file |
| `en-gd (Scotland)` | 1 EN sample file |
| `en-gv (Isle of Man)` | 0 rows |
| `en-ga (EU)` | 18 placeholder JSONs |

This pipeline fills that gap with the v1 Firecrawl MCP tool surface
(`firecrawl_agent`, `firecrawl_monitor_*`, `firecrawl_interact`,
`firecrawl_parse`, `firecrawl_map`), the content-based lingua-py
language detector (because the metadata `language` tag is *wrong* on
bilingual legislation pages), and a 10-theme taxonomy that lets one
DLT pipeline per jurisdiction cover the full Celtic-nation bilingual
statutory footprint.

---

## The 6-phase priority order

Each phase = one language pair. Phases gate on each other via the
RAGAS ≥ 0.70 bilingual-pair coverage check.

| # | Jurisdiction | Language pair | Canonical example |
|---|---|---|---|
| 1 | 🏴󠁧󠁢󠁷󠁬󠁳󠁿 Wales | `en-cy` | `https://www.legislation.gov.uk/wsi/2007/2044/made/welsh` — *Gorchymyn Ffurfiau Cymraeg Llwon a Chadarnhadau (Deddf Llywodraeth Leol (Cymru) 2012)* |
| 2 | 🇮🇪 Republic of Ireland | `en-ga` | `https://www.irishstatutebook.ie/eli/1937/act/0019/enacted/ga/html` — Constitution Art. 4 (Irish as first official language) |
| 3 | 🇬🇧 Northern Ireland | `en-ga` | `https://www.legislation.gov.uk/uksi/2022/15/contents/made` — *Identity and Language (Northern Ireland) Act 2022* |
| 4 | 🏴󠁧󠁢󠁳󠁣󠁴󠁿 Scotland | `en-gd` | `https://www.gaidhlig.scot/bord-na-gaidhlig/naidheachdan/` — Bòrd na Gàidhlig (Gaelic Language (Scotland) Act 2005) |
| 5 | 🇮🇲 Isle of Man | `en-gv` | `https://www.culturevannin.im/learn-gaelg/` — Culture Vannin (Manx language body) |
| 6 | 🇪🇺 EU (Irish as treaty language) | `en-ga` | `https://eur-lex.europa.eu/legal-content/GA/TXT/?uri=CELEX:12012E` — Treaty on European Union |

## The 10-theme taxonomy

| # | Theme | Example |
|---|---|---|
| T1 | Legislation | WSI / UKSI / uksro / ISB Acts / EU CELEX |
| T2 | Policy / consultations | White papers, Green papers, Senedd / NI Executive consultations |
| T3 | Education | Hwb CfW, CfE, NCCA, CCEA, DESC, language-medium portals |
| T4 | Healthcare | NHS Wales, NHS Scotland, HSE, patient-info PDFs |
| T5 | Language bodies | Welsh Language Commissioner, Bòrd na Gàidhlig, Foras na Gaeilge, Culture Vannin, CnaG |
| T6 | Terminology | Termau Cymru, Téarma, Teanglann, IATE |
| T7 | Courts & Tribunals | HMCTS Welsh, NI Courts Service, Scottish Courts, Courts Service Ireland |
| T8 | Local government | 22 Welsh LAs, NI councils, Scottish councils, Irish councils, IoM councils |
| T9 | Public broadcasting & culture | S4C, BBC ALBA, TG4, RTÉ Raidió na Gaeltachta |
| T10 | Statistics & public records | Bilingual census tables, NISRA Gaeilge, NRS Scottish Gaelic |

---

## Architecture

```
┌── Phase A ──┐  ┌── Phase B ───┐  ┌── Phase C ──┐  ┌── Phase D ──┐
│ Firecrawl   │→ │ BAML         │→ │ CocoIndex   │→ │ ibis +      │
│ MCP suite:  │  │  extraction  │  │  + bge-m3   │  │ MotherDuck  │
│ scrape,map, │  │  suite       │  │  1024-d     │  │  sync_audit │
│ search,     │  │              │  │             │  └──────┬──────┘
│ crawl,      │  │              │  │             │         │
│ agent,      │  │              │  │             │         ▼
│ monitor,    │  │              │  │             │  ┌── Phase E ──┐
│ interact,   │  │              │  │             │  │ marimo +    │
│ parse       │  │              │  │             │  │ motherduck  │
└─────────────┘  └──────────────┘  └─────────────┘  │  Dive       │
                                                  └─────────────┘
```

Ground truth providers (in order of reliability):
1. **CLARIN-UK Celtic resource family** (`https://www.clarin.ac.uk/resource-families/celtic-languages/`)
2. **Akoma Ntoso XML** from `legislation.gov.uk` (8 formats; AKN carries language metadata in the document root)
3. **Bilingual Explanatory Notes** on legislation.gov.uk (English + Welsh side-by-side — same artifact, two `<doc xml:lang="…">` blocks)
4. **`tearma.cymru` / `tearma.ie` / `teanglann.ie`** for terminology
5. **`/cy/`, `/ga-ie/`, `/gd/` prefixed pages** on `gov.wales`, `gov.ie`, `gov.scot`

## File layout

```text
ciancheiltis/
└── README.md (this file)

openspec/
├── changes/2026-09-06-ciancheiltis-v1/    # the v1 change
└── specs/ciancheiltis/                    # canonical umbrella spec

dlt_sources/ciancheiltis/
├── clarin_uk/         # CLARIN-UK + Cadhan Aonair + Foclóir Gàidhlig-Gaeilge
├── en_cy/             # Phase 1 — Wales (en-cy)
├── en_ga_roi/         # Phase 2 — Republic of Ireland (en-ga)
├── en_ga_ni/          # Phase 3 — Northern Ireland (en-ga)
├── en_gd/             # Phase 4 — Scotland (en-gd)
├── en_gv/             # Phase 5 — Isle of Man (en-gv)
├── en_ga_eu/          # Phase 6 — EU (en-ga)
└── _shared/           # content-based language detector, opaque-URL scanner, gov.wales WAF bypass
```

## The firecrawl story

Today's free tier on Firecrawl is exhausted, so this v1 lands the
scaffolding (the spec, the file layout, the README, the openspec
change) and the Phase 0.1 / Phase 0.2 helpers in code form. Live
discovery waits for the next Firecrawl reset — by which time the
canonical `CLARIN-UK → legislation.gov.uk → gov.wales → eur-lex`
discovery checklists can be exercised end-to-end.

The live doc reference for the Firecrawl MCP tool surface used by
this pipeline is at
[`https://docs.firecrawl.dev/mcp-server/tools`](https://docs.firecrawl.dev/mcp-server/tools).

## Cross-references

- [`../openspec/specs/ciancheiltis/spec.md`](../openspec/specs/ciancheiltis/spec.md) — canonical umbrella spec
- [`../openspec/specs/celtic-language-pipeline/spec.md`](../openspec/specs/celtic-language-pipeline/spec.md) — curated Celtic corpora (companion)
- [`../openspec/specs/british-isles-education-pipeline/spec.md`](../openspec/specs/british-isles-education-pipeline/spec.md) — education-only bilingual pipeline (subset)
- [`../openspec/specs/biep-8-jurisdictions/spec.md`](../openspec/specs/biep-8-jurisdictions/spec.md) — 8 BIEP jurisdictions
- [`../.agents/skills/firecrawl/SKILL.md`](../.agents/skills/firecrawl/SKILL.md) — Firecrawl MCP tool surface
