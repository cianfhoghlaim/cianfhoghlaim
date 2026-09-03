# Agent 23 — Ireland sites (curriculumonline.ie + examinations.ie + ncca.ie) (2026-06-28)

**Wave:** Program 2, Agent 23 of 25 (multi-site bundle)
**Sites:** 3 Ireland live education sites (NCCA family + SEC)
**Live findings supersede `phase-3/S01-S03` aspirational URL patterns** — the actual site maps discovered via Firecrawl are different from the earlier Phase 3 sketches (Phase 3 used an LLM-imagined `/en/exam-archive/leaving-certificate/` path that does not exist; the real landing is `https://www.examinations.ie/exammaterialarchive` with a PHP-style checkbox-gated dropdown form).
**Cross-references:** `ireland-primary-jc-dlt-baml` spec, `stedding/stedding/flows/education/dlt_sources/ireland/{curriculum_registry,ncca,examinations,curriculum_source,source_adapters}.py`

---

## §1 curriculumonline.ie (NCCA primary + JC + SC portal)

### TL;DR
NCCA's public-facing curriculum portal. Serves **4 stages** (Early Childhood, Primary, Junior Cycle, Senior Cycle) with **5 primary curriculum areas** (Language, STEM, Wellbeing, Arts Ed, Social & Env Ed) + **21 Junior Cycle subjects** + **38 Senior Cycle subjects** + **24 LCA subjects**. Public content is at the legacy path `/<cycle>/...`; the new 2026 redeveloped primary curriculum is published at `/2026-primary/...` but those routes **redirect to a login wall** (`/User/Signin?ReturnUrl=...`) for the `[TCA]` (Teacher-Only) marker. **Anti-scraping is the real blocker** here: reCAPTCHA on login + CMS-gated content + aggressive Cloudflare CSP.

### Live URL structure (from `firecrawl_map`, `firecrawl_scrape`)

| Path | Content | Status |
|:--|:--|:--|
| `/` | Home (Welcome, age 1-12) | 200 |
| `/primary/` | Primary Curriculum (1999 + 2026 redeveloped) | 200 |
| `/primary/curriculum-areas/mathematics/` | Subject landing | 200 |
| `/primary/primary-curriculum-toolkit/pedagogy/` | Toolkit sub-page | 200 |
| `/primary/1999-primary-school-curriculum/` | Legacy 1999 doc | 200 |
| `/junior-cycle/junior-cycle-subjects/{subject}/` | 21 JC subjects | 200 |
| `/junior-cycle/short-courses/` | 15 short courses | 200 |
| `/senior-cycle/senior-cycle-subjects/{subject}/` | 38 SC subjects | 200 |
| `/senior-cycle/lca/{lca-subject}/` | 24 LCA subjects | 200 |
| `/early-childhood/aistear-2024/` | Aistear (2024 update) | 200 |
| `/ga-ie/...` | Irish-language mirror (path-prefix) | 200 |
| `/2026-primary/curriculum-areas` | **NEW 2026 primary** | **302 → /User/Signin (login wall)** |
| `/User/Signin` | reCAPTCHA login | blocked |
| `/clipboard` | User clipboard (auth required) | blocked |
| `/getmedia/{guid}/{slug}.{ext}?width=&ext=` | **PDF/image pattern** (e.g. `https://www.curriculumonline.ie/getmedia/dc57ef5c-3d13-44a4-b000-c183b43681f3/BJC_Co-opt_Banner.png?ext=.png&width=2000&resizemode=force%202000w`) | 200 |
| `/getfile/{id}` | Old static-PDF pattern (legacy, mostly dead) | 200/404 |
| `/sitemap.xml` | **DOES NOT EXIST** — returns 404 | n/a |

### Dropdown cascade (mobile nav from scraped HTML)
```
Mobile menu (hamburger):
  Home
  Early Childhood
    - Early Childhood Overview
    - Principles and Themes
    - Guidelines for Good Practice
    - Aistear (2024 / 2009)
    - Support Materials
    - Support Videos
  Primary
    - Primary Curriculum
    - The Primary Curriculum Framework
    - Curriculum Areas
        - Arts Education | Language | STEM | Mathematics | Social & Env | Wellbeing
    - Primary Curriculum Toolkit (7 sub-pages)
    - Curriculum Area Toolkits (5 toolkits)
    - 1999 Primary School Curriculum
  Junior Cycle
    - Curriculum | Subjects (21) | Short Courses (15) | JCL1LP | JCL2LP
    - Assessment | Key Skills | Junior Cycle is changing
  Senior Cycle
    - Curriculum | Redevelopment | Subjects (38) | Assessment
    - Transition Year | LCA (24) | LCVP | L1L2 LPs | SPHE
```

### Anti-scraping posture
- **Cloudflare CDN** with HSTS, XSS-protection, nosniff (from response headers)
- **Tight CSP** (`default-src 'self'`, `frame-ancestors 'self' cms.curriculumonline.ie` — admin CMS at `cms.curriculumonline.ie`)
- **reCAPTCHA** on login (Google reCAPTCHA + Privacy Policy/ToS links)
- **`[TCA]` (Teacher-Content Access) gating** — content under `TCA` marker only visible to logged-in teachers. The `/2026-primary/...` new primary curriculum is fully TCA-gated
- **Rate-limit posture:** Not observed in single-shot scrapes; the Phase 1 spec says "sustainable download, but don't parallelize >5 requests"
- **robots.txt:** Phase 1 S01 report claims "allows all standard crawlers" — not re-verified here
- **Bilingual:** `/ga-ie/{path}` for Irish (path-prefix style, not subdir)

### CCC anchors
`stedding/stedding/flows/education/dlt_sources/ireland/curriculum_registry.py:43-485` (registers all 3 sites), `source_adapters.py:104-225` (`CurriculumOnlineAdapter`), `curriculum_source.py:4-762` (3-way URL generator), `agentic_discovery.py:118-302` (Firecrawl + Stagehand fallback for TCA-gated pages), `subjects/{junior_cycle,senior_cycle,base}.py` (subject spec enum + URL patterns)

### §8 Refactor (curriculumonline.ie)
1. **The dlt source `curriculum_source.py:230-238` hard-codes the legacy `/en/Primary/...` URL pattern**, but the live site no longer serves `/en/` (returns 404) and has migrated Primary → `/primary/`. **MUST update to:** `https://www.curriculumonline.ie/{cycle}/{cycle}-subjects/{subject}/` (with `/ga-ie/` prefix for `language="ga"`). The `ga-ie` mapping for primary subjects is still broken — primary subject slugs are English (e.g. `mathematics`), the Irish slug is also `matamaitic` only for JC/SC. Need a per-stage subject-slug table.
2. **`getmedia/` pattern is undocumented** in the existing code. The adapter's `metadata={"description": ..., "links": ...}` block does NOT extract the GUID or the `ext` query param. Add a `getmedia_guid` and `getmedia_width` field to `NormalizedPage.metadata` so we can dedupe by GUID.
3. **TCA gating is a silent data loss bug.** `agentic_discovery.py:273-302` falls back to Stagehand only when Firecrawl returns empty, but Stagehand can't solve reCAPTCHA. We need a teacher-account service account (stored in Infisical under `oideachais/sources/curriculumonline_teacher`) to log in via Stagehand and pull TCA-gated PDFs.
4. **`/sitemap.xml` does NOT exist** — we need a custom URL generator (the 4 stages × 21+38+24+15 subjects × 2 languages ≈ 200 pages) and a Firecrawl `map` call seeded by those URLs instead of a sitemap.
5. **The `/2026-primary/...` migration** is the real event to track. The existing spec `ireland-primary-jc-dlt-baml` calls for "12 curriculum areas × ~3 docs" but the redeveloped primary is now **5 broad areas** (not 12). Spec drift — see Phase 3 S01 "12 curriculum areas" is wrong.

---

## §2 examinations.ie (State Examinations Commission)

### TL;DR
SEC's **legacy PHP site** (`charset=iso-8859-1`, `images/spacer.gif`, `images/arrow_instruct.gif`, frame-table layout) serving Leaving Cert + Junior Cycle + LCA exam papers, marking schemes, and Chief Examiner reports. **The dropdown cascade is gated by a T&Cs checkbox** (`/exammaterialarchive/`) — you MUST click "I have read, understand and accept the Terms and Conditions" before the actual subject/year/component selectors render. This is the only one of the 3 sites with a substantive human-in-the-loop + checkbox gate; the other two are pure navigation. **No anti-scraping beyond the T&Cs click** — `robots: index, follow`, no Cloudflare challenge, no JS-rendered content (server-side HTML).

### Live URL structure

| Path | Content | Notes |
|:--|:--|:--|
| `/` | Home (SEC, Athlone, Co. Westmeath) | 200 |
| `/?l=en&mc=se&sc=sh` | Section nav pattern (l=lang, mc=main category, sc=sub category) | 200 |
| `/?l=en&mc=ex&sc=sp` | Examination Information | 200 |
| `/?l=en&mc=ex&sc=e26` | Examinations 2026 landing | 200 |
| `/?l=en&mc=en&sc=cr` | Chief Examiner Reports (submenu) | 200 |
| `/?l=en&mc=en&sc=sy` | Syllabus Changes | 200 |
| `/?l=en&mc=en&sc=mc` | Music Practicals | 200 |
| `/exammaterialarchive/` | **THE archive landing** (T&Cs checkbox gate) | 200 |
| `/tmp/{unix_ts}_{id}.pdf` | **PDF pattern for archived papers** (e.g. `/tmp/1577565768_3089625.pdf`, `/tmp/1601624140_4495962.pdf`) | 200 |
| `/misc-doc/EN-EX-{id}.pdf` | Circulars pattern (e.g. `EN-EX-83626587.pdf`, `EN-CA-97149561.pdf`, `EN-SE-80819185.pdf`) | 200 |
| `/docs/schoolscirculars/EN-{id}.pdf` | School circulars (e.g. `EN-1011-4236490.pdf`) | 200 |
| `/?l=ir&mc=se&sc=sh` | **Irish** version of every page (query-param, not subdir) | 200 |
| `/exammaterialarchive/?l=ir&...` | Irish archive | 200 |
| `/?v={view-id}` | Legacy "view" routing (e.g. `?v=2100201`) | 200/404 |
| `https://fees.examinations.ie/` | Separate subdomain for fee payment | out-of-scope |
| `https://secexaminer.ie/` | External link to examiner recruitment | out-of-scope |
| `/robots.txt` | Returns content but `robots: index, follow` (non-blocking) | 200 |

### Dropdown cascade (post-T&Cs-accept)
```
1. /exammaterialarchive/ — Click T&Cs checkbox
2. Exam Level: [Leaving Certificate, Junior Cycle, LCA, LCVP, L1LP, L2LP]
3. Subject: dynamic (24 LC / 24 JC / 24 LCA subjects)
4. Year: 1995-present (30 years)
5. Component: [Paper 1, Paper 2, Marking Scheme, Chief Examiner Report, Audio, Modified Paper]
6. Result: download PDF via /tmp/{timestamp}_{id}.pdf
```

### PDF pattern (live, NOT the Phase 3 sketch)
- `https://www.examinations.ie/tmp/{unix_ts}_{id}.pdf` — primary archive
- `https://www.examinations.ie/misc-doc/EN-{XX}-{id}.pdf` — circulars (XX = EX/CA/SC/AU/etc)
- `https://www.examinations.ie/docs/schoolscirculars/EN-{id}.pdf` — school circulars
- `https://www.examinations.ie/RACEwebinar/` — webinar landing (not a PDF)

### Anti-scraping posture
- **T&Cs checkbox gate** on `/exammaterialarchive/` (legal gate, must accept before subject/year selector appears)
- **No Cloudflare challenge** observed
- **No rate limit** observed (Firecrawl + dlt downloads cleanly)
- **Server-side HTML** (no JS SPA)
- **Mixed content encoding** (`iso-8859-1` legacy)
- **robots.txt: index, follow** (non-blocking) — but the T&Cs click is the effective rate limit
- **Subdomain isolation:** `fees.examinations.ie` is separate (do not crawl)

### CCC anchors
`stedding/stedding/flows/education/dlt_sources/ireland/examinations.py:30-465` (3 dlt sources: `sec_examinations_crawl`, `sec_examinations_browser_source` for Stagehand), `source_adapters.py:372-525` (`ExaminationsAdapter`), `parallel_corpus.py:582-585` (URL normalization `re.search(r'examinations\.ie(/.+)$', url)`), `agentic_discovery.py:155-218` (Firecrawl agent search "Find exam papers on examinations.ie" with `exammaterialarchive` as seed)

### §8 Refactor (examinations.ie)
1. **Phase 3 S02 URL pattern is WRONG.** S02 claims `https://www.examinations.ie/exams/-archive-leaving-cert/...` — this path does not exist (returns 404). The real path is **`/tmp/{unix_ts}_{id}.pdf`** for archived papers. The dlt source `examinations.py:135-194` for `_map_examiner_report_pdf_urls` should be refactored to extract `(unix_ts, id)` from the `/tmp/` URL pattern, NOT from a hypothetical `/exams/-archive-leaving-cert/` path.
2. **T&Cs click is the critical missing step.** `sec_examinations_browser_source` (`examinations.py:306-399`) opens the archive but does NOT click the T&Cs checkbox — so the subject dropdown never renders. Add a `stagehand_act("click", selector="input[type='checkbox'][name='accept-terms']")` call before any subject interaction. Use the persisted-context feature so we don't have to re-accept every session.
3. **No Irish URL prefix** — bilingual is via `?l=ir&...` query param, NOT `/ga/...`. `source_adapters.py:391-466` has a `language` field but does NOT swap the URL when language changes. Add a `to_url_with_lang(base, lang)` helper.
4. **Bypass the T&Cs gate with the static PDF index.** Many circulars and reports are directly linked from the SEC home page (e.g. `S39_26`, `S29_26`, `JC Engineering Project 2026`) with absolute `/misc-doc/...` URLs. Add a separate dlt source `sec_circulars_source()` that scrapes the home + `/about-us` + `/schools` for direct PDF links — this avoids the T&Cs gate entirely and gets us ~40 docs without Stagehand.
5. **Subject slug table is incomplete.** `examinations.py` references `ALL_LC_SUBJECTS` and `ALL_JC_SUBJECTS` (constants not in the file slice seen) but the live site uses **English slugs** like `mathematics` (matches the menu) AND **legacy slugs** like `english` for old papers. The SEC archive also has subjects like `applied-mathematics`, `physics-and-chemistry`, `classical-studies` that have non-obvious mappings. Build a per-subject `(slug, irish_slug, year_first, year_last)` table.
6. **The `/exammaterialarchive` page is the right seed** for Firecrawl `map` instead of `agentic_discovery`'s generic prompt. Once the T&Cs are accepted, the dynamic dropdowns can be enumerated with `map(search="exammaterialarchive", limit=200)`.

---

## §3 ncca.ie (National Council for Curriculum and Assessment)

### TL;DR
NCCA's **policy / strategy / research / curriculum-development portal** — sister site to curriculumonline.ie (curriculumonline hosts the actual spec documents; ncca.ie hosts the **frameworks, background papers, consultation reports, and research** that drove those specs). **Dublin Core metadata throughout** (DC.Title, DC.Identifier, DC.Rights, DC.Format, etc) — rare in 2026, useful for BAML extraction. **`googlebot: noindex,indexifembedded`** is the most interesting anti-scraping posture: Google should NOT index, but if content is embedded it can be. This means the site explicitly does NOT want its research pages appearing in search results.

### Live URL structure

| Path | Content | Notes |
|:--|:--|:--|
| `/en/` | English home (news, consultations, publications tiles) | 200 |
| `/ga/` | Irish home (mirror) | 200 |
| `/en/primary/primary-curriculum-framework-and-curriculum-areas/` | **Primary curriculum framework landing** | 200 |
| `/en/early-childhood/` | Aistear, Síolta | 200 |
| `/en/junior-cycle/` | Junior cycle policy | 200 |
| `/en/senior-cycle/` | Senior cycle redevelopment | 200 |
| `/en/updates-and-events/latest-news/` | News | 200 |
| `/en/updates-and-events/latest-news/2026/april/...` | Date-archived news | 200 |
| `/en/updates-and-events/consultations/` | Open consultations | 200 |
| `/en/publications-and-research/publications/` | Publications index | 200 |
| `/en/resources/{slug}/` | Resource pages (long-form content) | 200 |
| `/media/{short-id}/{slug}.pdf` | **PDF pattern** (e.g. `/media/5gfbsf4c/generalprimary_faq_website.pdf`, `/media/oruhzueb/information-note-for-the-primary-curriculum-framework-en.pdf`) | 200 |
| `/media/{id}/{filename}.png?rmode=crop&width=600&height=600&v=...` | **Image pattern** with cache-bust `v=...` query | 200 |
| `/media/{id}/{filename}.jpg?rmode=crop&width=500&height=250&mode=crop` | Same with `mode=crop` | 200 |
| `/images/{name}.{ext}` | Static site assets | 200 |
| `/favicon.ico` | Favicon | 200 |
| `/sitemap.xml` | **NOT tested** — Phase 3 S03 didn't confirm; need a fresh fetch | tbd |

### Tab structure (jQuery UI tabs)
The Primary Curriculum Framework page uses URL-fragment-based tabs (`#panel-{uuid}`):
```
- Vision (#panel-5e9d3e74-7ea7-4662-b525-c7f52e52855b)
- Principles of Learning, Teaching and Assessment
- Key Competencies
- Language
- STEM Education
- Wellbeing
- Arts Education
- Social and Environmental Education
- Time Allocations
```

### Anti-scraping posture
- **`googlebot: noindex,indexifembedded`** — explicit Google-blocking of index (but allow embed). Use `firecrawl_scrape` not Google
- **No rate limit** observed
- **No Cloudflare challenge** observed
- **Dublin Core metadata** in `<head>` — friendlier for BAML extraction
- **Bilingual** via `/en/` + `/ga/` subdir prefix (NOT path-tail like curriculumonline's `/ga-ie/`)
- **Cross-domain links to curriculumonline.ie** for the actual specs — this is a SISTER-SITE relationship that dlt must model

### CCC anchors
`stedding/stedding/flows/education/dlt_sources/ireland/ncca.py:1-399` (3 dlt sources: `ncca_crawl`, `ncca_resources`, `ncca_publication_index` — none currently wire Dublin Core), `source_adapters.py:227-370` (`NCCAAdapter` with `ncca.ie` as base, NO `www.`, no `https://` — minor bug), `parallel_corpus.py` (uses `ncca.ie/en/{cycle}/curriculum-developments/{subject}/` as canonical URL), `curriculum_source.py:244-250` (URL generator), `content_deduplication.py:87-88` (mentions `Mathematics specification appearing on both curriculumonline.ie and ncca.ie`)

### §8 Refactor (ncca.ie)
1. **`NCCAAdapter.get_base_url` is wrong** (`source_adapters.py:262-263`): `return "ncca.ie"` (no scheme). Every other adapter returns `https://www.{domain}`. Fix to `return "https://ncca.ie"` (NCCA uses bare `ncca.ie` not `www.ncca.ie` — confirmed from response headers `subjectName: ncca.ie` and the live site `og:url` is `https://ncca.ie/en/...`).
2. **Dublin Core metadata is not extracted.** `ncca.py:149-308` dlt sources scrape the page body but discard the `<meta name="DC.Title">`, `DC.Identifier`, `DC.Date.Created`, `DC.Rights`, `DC.Format`, `DC.Language` fields. These would give us `publication_date`, `copyright_holder`, `document_format` "for free" — should be a `metadata.dublin_core` block in `NormalizedPage`.
3. **Image cache-bust `v=` query param** (e.g. `?v=1db62a9b183edd0`) is breaking content-dedup. Two fetches of the same image will get different URLs. Add a `normalize_media_url(url)` that strips `?v={hash}` before hashing.
4. **Tab URL fragments are missed by dlt filesystem scrapes.** The Primary Curriculum Framework has 5 in-page tabs but the dlt source only yields the landing page. Add a `extract_tab_panels(html, tab_urls)` step that scrapes each `#panel-{uuid}` panel as a separate `NormalizedPage` (with `tab_name` metadata).
5. **Cross-site dedup with curriculumonline.ie is documented but not implemented** (`content_deduplication.py:87-88`). The `Mathematics` spec on ncca.ie and the same spec on curriculumonline.ie should be dedup'd on `(cycle, subject, year, language)` — but the dlt sources run independently. Need a Dagster asset_check that flags duplicates.
6. **`/media/` paths are inconsistent.** Some are `/media/{id}/{slug}.pdf` (5+ char IDs like `5gfbsf4c`, `oruhzueb`, `ghilbg5j`), others are `/media/{numeric_id}/{filename}` (e.g. `/media/1085/ncca_annual_report_2007.pdf`, `/media/1504/transition_to_primary_research_report_19.pdf`). Two ID formats coexist — likely legacy migration. The dlt source should treat them as opaque tokens.

---

## Cross-site synthesis (Agent 23 → other agents)

### Common patterns
- **3 sites = 3 URL conventions:** curriculumonline uses `/ga-ie/` path-prefix + legacy `/en/` (now 404), examinations uses `?l=en&mc=...&sc=...` query params + Irish via `?l=ir`, ncca uses clean `/en/` + `/ga/` subdirs. **Bilingual handling is the most important interop problem.**
- **PDF patterns are all different:** curriculumonline=`/getmedia/{guid}/{slug}.{ext}?ext=...&width=...`, examinations=`/tmp/{unix_ts}_{id}.pdf` or `/misc-doc/EN-{cat}-{id}.pdf`, ncca=`/media/{id}/{slug}.pdf` (or `.png?rmode=crop&width=...` for images). Need 3 URL normalizers in `parallel_corpus.py`.
- **No 2 of the 3 have an actual `/sitemap.xml`** — Phase 3 S01/S03 assumed sitemap discovery, but real ingestion must use Firecrawl `map` with a URL seed (the stage/subject index for curriculumonline, the archive page for examinations, the news/consultations index for ncca).
- **Teacher-only `[TCA]` gating** is a curriculumonline-only anti-pattern; the other 2 are open.

### To Agent 5 (motherduck) + Agent 8 (ducklake)
The 3 sites produce ~3,000 PDFs total (estimated from map: 1,000 curriculumonline + 1,500 examinations + 500 ncca). Each PDF should land in a separate `leabharlann/ireland/{site}/{stage}/{subject}/` S3 prefix. Recommend a `MultiPartitionsDefinition(year, site, stage, subject, language)` instead of the current 2-axis partition.

### To Agent 4 (lancedb) + Agent 11 (graphiti)
The bilingual parallel corpus (en+ga) for the same content is a textbook use case for BGE-M3 + Graphiti temporal edges. Add `bilingual_pair_id` to the `NormalizedPage` schema so we can do embedding-based cross-language dedup.

### To Agent 15 (baml) + Agent 9 (cognee)
Curriculum content is **multi-stage, multi-language, multi-version** (1999 Primary + 2026 redeveloped Primary + 2024 Aistear). Cognee graph edges should be `OldVersion -superseded_by-> NewVersion` + `English -translated_to-> Irish` + `CurriculumOnline -publishes_spec_for-> NCCAFramework`. Suggest adding a `BAML function ClassifyCurriculumVersion(text) -> VersionTag` to disambiguate.

### To Agent 17 (komodo) + Agent 18 (infisical)
The TCA-gated curriculumonline content needs a teacher-account credential stored in Infisical at `oideachais/sources/curriculumonline_teacher/{email,password}`. Add a `komodo` procedure `rotate-curriculumonline-teacher-creds` that re-accepts T&Cs and re-stores the session cookie.

---

## Drift log (vs `phase-3/S01-S03`)

| Phase 3 claim | Reality (this agent) |
|:--|:--|
| S01: `/en/Primary/{subject}/{strand}/{unit}` | Returns **404** — old `/en/` prefix is dead; live pattern is `/primary/curriculum-areas/{subject}/` |
| S01: 12 curriculum areas | Reality: **5 broad areas** (Language, STEM, Wellbeing, Arts Ed, Social & Env Ed) |
| S01: `/getfile/{id}` PDF pattern | Reality: **`/getmedia/{guid}/{slug}.{ext}?ext=...`** is the live pattern |
| S02: `/en/educational-resources/` | **DOES NOT EXIST** — Phase 3 hallucinated this path |
| S02: `/en/exam-archive/leaving-certificate/` | **DOES NOT EXIST** — real landing is `/exammaterialarchive/` with T&Cs gate |
| S02: `/en/exams/-archive-leaving-cert/{level}/{subject}/{year}/{component}.pdf` | **DOES NOT EXIST** — real PDF pattern is `/tmp/{unix_ts}_{id}.pdf` |
| S03: `/en/Publications/` etc | The actual top-nav uses `/en/updates-and-events/{latest-news,consultations}/` and `/en/publications-and-research/publications/` — different |
| S03: `/en/Senior-Cycle/` (capitalised) | Lowercase: `/en/senior-cycle/` |
| S03: `/getfile/{id}` PDF pattern | Reality: `/media/{id}/{slug}.pdf` with two ID formats (5-char alnum + numeric) |

## Decision matrix

| Question | Answer |
|:--|:--|
| Best site to ingest first? | **ncca.ie** (open, no auth, Dublin Core metadata, smallest corpus) |
| Best site for parallel-corpus demo? | **curriculumonline.ie** (bilingual `/ga-ie/` mirror is the cleanest, en+ga side-by-side) |
| Most expensive site to ingest? | **examinations.ie** (T&Cs gate + Stagehand + 30 years × 24 subjects × 5 components = ~3,600 PDFs) |
| Can we ingest without browser automation? | Yes for **ncca.ie** + **curriculumonline.ie** (public nav); NO for **examinations.ie** (T&Cs click is the blocker) |
| Wayback fallback viable? | Yes for all 3 — Wayback has snapshots back to 2008 for ncca.ie |
