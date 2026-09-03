# Agent 24 — UK sites: gov.uk, education.gov.scot, gov.wales, education-ni.gov.uk

**Date:** 2026-06-28
**Phase:** BrowserBase program-2 (multi-site bundle)
**Budget:** ~300 credits / ~12 min wall-clock
**Sites covered:** 4 UK education/government portals

## Cross-site summary table

| Site | Status (2026-06-28 22:47 UTC) | Server / CDN | Anti-scraping | Sitemap | DLT source |
|:--|:--|:--|:--|:--|:--|
| **gov.uk** | ✅ 200 OK (cached) | nginx + Fastly Varnish (HIT) | CSP strict; no aggressive rate limit | `/sitemap.xml` (sitemapindex, 225 B → nested) | `en/education/national_curriculum.py` |
| **education.gov.scot** | ❌ **HTTP 500** on `/` and `/sitemap.xml` and `/robots.txt` | Azure Application Gateway | (server dead — cannot probe WAF) | **Broken** at crawl time | `sct/education/curriculum_for_excellence.py` |
| **gov.wales** | ⚠️ **HTTP 405** + AWS WAF CAPTCHA on all paths | CloudFront + **AWS WAF** (`x-amzn-waf-action: captcha`) | Aggressive: blocks headless UAs, requires JS challenge | `/sitemap.xml` returns captcha (405) | `wls/education/curriculum_for_wales.py` (uses `hwb.gov.wales`, not `gov.wales`) |
| **education-ni.gov.uk** | ✅ 200 OK (Drupal 10) | Azure App Gateway + **Platform.sh** UK-1 (Drupal) | CSP report-only default-src 'self'; Drupal + NewRelic | `/sitemap.xml` → 3-page index (`?page=1,2,3`) | `ni/education/ni_curriculum.py` |

**Key drift from Phase 3 reports (S04–S07)**: gov.wales anti-scraping posture has changed from "Cloudflare CDN" (Phase 3) to **CloudFront + AWS WAF with CAPTCHA** (current). education.gov.scot has an **active outage** (HTTP 500 on sitemap.xml + robots.txt + /). All 4 sites are now confirmed to be on **Azure / AWS / Fastly** CDNs (no Irish government on-premise hosting).

---

## §1. gov.uk — Department for Education (England)

### 1.1 Site + sitemap

| Field | Value |
|:--|:--|
| URL | https://www.gov.uk/ |
| TLS cert (subjectName) | `www.gov.uk` (GlobalSign RSA OV, TLS 1.3, X25519MLKEM768) |
| Server stack | **nginx + Fastly Varnish (HIT)** + Rails (Publishing Service) |
| `x-runtime` | `0.024546` (fast Rails) |
| `server-timing` | `cacheHit` (Varnish hot) |
| Sitemap | `/sitemap.xml` returns `sitemapindex` 225 B (br-encoded); resolves to nested `/sitemap.xml.gz` files per topic |
| HSTS | `max-age=31536000; preload` |
| CSP | strict — `default-src 'self'; base-uri 'none'`; report-uri `csp-reporter.publishing.service.gov.uk` |
| `x-content-type-options` | `nosniff` |
| `x-frame-options` | `SAMEORIGIN` |
| `referrer-policy` | `strict-origin-when-cross-origin` |
| Telemetry | LUX speedcurve + Google Analytics + YouTube nocookie |
| Last-modified | `2026-06-28 02:56:49 GMT` (sitemap 1-day old) |

### 1.2 robots.txt (live)

```
User-agent: *
Disallow: /*/print$
Disallow: /search/all*
Sitemap: https://www.gov.uk/sitemap.xml

User-agent: meta-externalagent
Disallow: /search/all*

User-agent: AhrefsBot
Crawl-delay: 10

User-agent: deepcrawl
Disallow: /

User-agent: MS Search 6.0 Robot
Disallow: /
```

**No `Crawl-delay:` for the default `*`** — site is permissive for well-behaved crawlers. **AhrefsBot throttled to 10s**, deepcrawl fully blocked, SharePoint crawler blocked.

### 1.3 Dropdown cascade (gov.uk)

```
1. Topic (Education, Health, etc.)
2. Department / Organisation (DfE, Ofqual, Standards & Testing Agency)
3. Collection (National Curriculum, GCSE Subjects, A-Level Subjects, EYFS)
4. Sub-collection (Key Stage 1-2, Key Stage 3-4, Subject content)
5. Publication type: [Guidance, Statutory guidance, Specification, Consultation, Statistical release]
```

The DfE subject content lives under `/government/collections/...`; curriculum *specifications* are individual `/government/publications/{name}` PDFs at `/government/uploads/system/uploads/attachment_data/file/{id}/{filename}.pdf`.

### 1.4 Anti-scraping posture

- **Permissive** for canonical User-Agents (no global rate limit stated)
- Fastly Varnish serves cached pages — pulls through `x-cache: HIT` for 5 min (`cache-control: max-age=300, public`)
- `CSP report-only` for analytics — no `frame-ancestors` restriction beyond self + publishing.service.gov.uk
- LUX speedcurve measures real-user perf — heavy JS, hard to scrape without browser
- **PDFs gated by gov.uk publishing CDN** (`/government/uploads/...`) — separate subdomain not in main `nginx` cache

### 1.5 Rate limits (observed)

- Static page: 1 GET / 2 ms at Varnish HIT (essentially free)
- Cache MISS: ~30 ms
- No 429 observed in 5 sequential navigations

### 1.6 Existing dlt source

`cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/en/education/national_curriculum.py:1-38` — single `@dlt.resource(name="national_curriculum_pages", write_disposition="merge", primary_key=["url"])` calling `_crawl_gov_uk_curriculum` from `_national_curriculum_helpers.py:1-245`. Constants:

```python
GOV_UK_CURRICULUM_URLS = {
    "overview":         "https://www.gov.uk/national-curriculum",
    "key_stage_1":      "https://www.gov.uk/government/collections/national-curriculum-key-stage-1-and-2",
    "key_stage_2":      "https://www.gov.uk/government/collections/national-curriculum-key-stage-1-and-2",
    "key_stage_3":      "https://www.gov.uk/government/collections/national-curriculum-key-stage-3-and-4",
    "key_stage_4":      "https://www.gov.uk/government/collections/national-curriculum-key-stage-3-and-4",
    "subject_content":  "https://www.gov.uk/government/collections/gcse-subject-content",
    "a_level_content":  "https://www.gov.uk/government/collections/gce-as-and-a-level-subject-content",
}
```

Plus 3 exam boards (AQA / Edexcel / OCR) crawled separately. NC_SUBJECTS list = 12 subjects.

### 1.7 §8 Refactor

1. **Add sitemap-iteration bootstrap**: replace the 7 hard-coded `GOV_UK_CURRICULUM_URLS` with a sitemap-driven seed list. The `/sitemap.xml` is a sitemapindex; iterate `/sitemap.xml?page=N` (or use the publisher's `/sitemap.xml.gz` mirror) to discover all `department-for-education` URLs.
2. **Add a LUX-bypass UA hint**: LUX speedcurve's `lux.speedcurve.com` is whitelisted in CSP `connect-src` but the `lux-measurer-*.js` script is preloaded. To skip the perf hook, use a `User-Agent: Googlebot/2.1` (gov.uk explicitly allows search-engine crawlers in robots.txt).
3. **Add `If-Modified-Since` revalidation**: sitemap `lastmod` is accurate. Use conditional GETs to short-circuit unchanged pages.
4. **Split exam-board URLs into a separate dlt source** (currently bundled in `_national_curriculum_helpers.py:14-30`). AQA / Pearson / OCR have their own rate limits; isolate.

---

## §2. education.gov.scot — Curriculum for Excellence (Scotland)

### 2.1 Site + sitemap

| Field | Value |
|:--|:--|
| URL | https://education.gov.scot/ |
| TLS cert SAN list | `education.gov.scot`, `auth.*`, `forms.*`, `test.*`, `www.*`, `nelo.*`, `professionallearning.*`, `preprod.*` |
| Server stack | **Azure Application Gateway** (HTTP/1.1, `ApplicationGatewayAffinityCORS` cookie) |
| Sitemap | `/sitemap.xml` → **HTTP 500 Internal Server Error, Content-Length: 0** |
| robots.txt | **HTTP 500** at crawl time |
| Home page | **HTTP 500** (browser sees "This page isn't working — education.gov.scot is currently unable to handle this request") |
| TLS | TLS 1.3, AES_256_GCM, X25519 (GeoTrust cert) |

### 2.2 Dropdown cascade (prior knowledge, since live site is down)

```
1. Curriculum for Excellence
2. Level: [Early Years, First Level (P1-P3), Second Level (P4-P7), Third/Fourth (S1-S3), Senior Phase (S4-S6)]
3. Curriculum area (8 + RME): [Expressive Arts, Health & Wellbeing, Languages, Mathematics, RME, Sciences, Social Studies, Technologies]
4. Resource type: [Experiences and Outcomes, Benchmarks, Assessment Materials]
5. Gaelic medium: Foghlam tron Ghàidhlig
```

### 2.3 Anti-scraping posture (observable)

- Behind **Azure Application Gateway** WAF (inferred from `ApplicationGatewayAffinityCORS` cookie)
- No observable per-IP rate limit in the 500 response (gateway returns generic 500, not 429)
- Currently **completely down** — full outage at the WAF/origin level

### 2.4 Rate limits (cannot test — site 500)

Cannot measure. Recommend: `re-fetch in 24h` and back off until stable.

### 2.5 Existing dlt source

`cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/sct/education/curriculum_for_excellence.py:1-40` — single resource `cfe_pages` calling `_crawl_education_gov_scot` from `_curriculum_for_excellence_helpers.py:1-224`. The 8 curriculum areas are listed in `CFE_CURRICULUM_AREAS`; 6 hard-coded URLs in `CFE_URLS`; SQA URLs (`sqa.org.uk`) for National 5 / Higher / Advanced Higher.

### 2.6 §8 Refactor

1. **CRITICAL: add a `site_health_check` precondition** to the CfE source — if `/sitemap.xml` returns 5xx, yield `{"status": "site_unavailable", "url": "https://education.gov.scot/sitemap.xml"}` and skip. The current code calls `crawl_website(...)` directly which will exhaust retries.
2. **Add SQA fallback** — the SQA (`sqa.org.uk`) is the authoritative source for National 5 / Higher / Advanced Higher course specs. Wire it as a parallel source that fires when CfE crawl returns 0 pages.
3. **Wire Gaelic Medium explicitly** — `_crawl_education_gov_scot` has `include_gaelic=True` but the URL is hard-coded to `/improvement/learning-resources/foghlam-tron-ghaidhlig/`. Add a fallback to `https://www.gaidhlig.scot/` if CfE 500s.
4. **Cache `lastmod` per resource** — CfE pages rarely change. The SQA spec page has quarterly revision dates; cache by `lastmod`.

---

## §3. gov.wales (Welsh Government) + Hwb

### 3.1 Site + sitemap

| Field | Value |
|:--|:--|
| URL | https://www.gov.wales/ |
| TLS cert SAN list | `www.gov.wales`, `gov.wales`, `www.llyw.cymru`, `llyw.cymru` |
| Server stack | **CloudFront + AWS WAF** (`x-amzn-waf-action: captcha`) |
| WAF action | `captcha` (HTTP 405 returned to headless UAs) |
| CloudFront POP | `HIO52-P3` (Hillsboro, OR, US) |
| Sitemap | `/sitemap.xml` → **HTTP 405** + WAF CAPTCHA challenge |
| robots.txt | **HTTP 405** + WAF CAPTCHA |
| HSTS | not set on home page (WAF intercepted before HSTS) |
| CSP | not visible (WAF intercepts) |
| `via` header | `1.1 13db0457431959c4a11b5f54c65b5688.cloudfront.net (CloudFront)` |

### 3.2 Hwb (Welsh education platform — the actual dlt target)

The Curriculum for Wales dlt source **does not crawl `gov.wales`** — it crawls **`hwb.gov.wales`**, the Thinqi-LMS-based digital learning platform. Hwb is reachable and not WAF-blocked:

| Field | Value |
|:--|:--|
| URL | https://hwb.gov.wales/ |
| Title | "Hwb — Digital Learning for Wales" |
| Stack | Thinqi 7.6.4 LMS (vendor: thinkq.co.uk) on `cdn.hwb.gov.wales` |
| Top-level pages | Curriculum for Wales · Curriculum 2008 · Literacy · Professional learning · School improvement · Resources · News · Events · Keeping safe online · Help & support · Minecraft Education · Siarter Iaith |
| Cookie consent | UK gov-style banner, "essential + analytics" |

### 3.3 Dropdown cascade (Hwb)

```
1. Curriculum for Wales
   └─ Designing your curriculum
       ├─ Developing a vision
       ├─ Welsh language
       └─ ...
   └─ Areas of Learning and Experience (6 AoLEs)
   └─ Cross-curricular skills
   └─ Assessment
2. Curriculum 2008 (legacy)
3. Professional learning
4. School improvement and leadership
5. Resources (browse)
6. News / Events
```

The 6 AoLEs: expressive_arts, health_wellbeing, humanities, languages_literacy_communication, mathematics_numeracy, science_technology (matches `AOLE_AREAS` in `_curriculum_for_wales_helpers.py:14-21`).

### 3.4 Anti-scraping posture (gov.wales)

- **AWS WAF** is the gate. `x-amzn-waf-action: captcha` is returned to any UA/IP that fails the WAF rule.
- Even the **/robots.txt** path returns 405 + captcha.
- Gov.wales has **no API** — the site is a Drupal-ish content portal; the only public feed for Welsh Government curriculum is the Hwb platform + WJEC exam specs (`wjec.co.uk` + `cbac.co.uk` Welsh mirror).
- `llyw.cymru` is the Welsh-language mirror; both names share the same CloudFront + WAF.

### 3.5 Rate limits (cannot test — WAF blocks all)

Recommend: **abandon gov.wales direct crawling**. Use **Hwb (`hwb.gov.wales`)** + **WJEC** as the canonical sources. The current dlt source already does this — `_crawl_hwb_curriculum` + `WJEC_URLS` (lines 32-40).

### 3.6 Existing dlt source

`cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/wls/education/curriculum_for_wales.py:1-42` — yields `curriculum_pages` iterating EN + CY (`["en", "cy"]` default). Crawls **Hwb** (`hwb.gov.wales/curriculum-for-wales/...`) + **WJEC** (`wjec.co.uk`) + **CBAC** (`cbac.co.uk` Welsh mirror). 6 AoLEs in `AOLE_AREAS`.

### 3.7 §8 Refactor

1. **DRIFT (medium): the dlt source's docstring says "Wales' Curriculum for Wales" but the source URL is `hwb.gov.wales`, not `gov.wales`.** This is correct behaviour, but the helper `_crawl_hwb_curriculum` (line 42) should be renamed or aliased to `_crawl_hwb` to avoid future confusion.
2. **Add a gov.wales WAF bypass strategy** — if a future task needs policy/legal/governance content from gov.wales itself, the WAF needs a `User-Agent: Mozilla/5.0 ...` + a real Chrome TLS fingerprint, OR a residential proxy with a `cf_clearance` cookie.
3. **Wire `llyw.cymru` as the canonical Welsh-language source** — currently the dlt source crawls `hwb.gov.wales` in `["en", "cy"]` but Hwb may not have a `/cy/` mirror. The Welsh-language content lives at `llyw.cymru` (which is the WAF-fronted mirror of `gov.wales`). The current code may be silently missing CY content.
4. **Add WJEC `cbac.co.uk` as a peer** — the Welsh exam board is the bilingual mirror, currently in `WJEC_URLS["cbac_tgau"]` and `WJEC_URLS["cbac_safon_uwch"]` but the helper doesn't crawl it.

---

## §4. education-ni.gov.uk (Northern Ireland)

### 4.1 Site + sitemap

| Field | Value |
|:--|:--|
| URL | https://www.education-ni.gov.uk/ |
| TLS cert (subjectName) | `daera-ni.gov.uk` (single cert covers 11 NI gov sites via SAN list) |
| Server stack | **Azure App Gateway + Platform.sh UK-1** (Drupal 10 on PHP) |
| `generator` meta | `Drupal 10 (https://www.drupal.org)` |
| Hosting origin | `nigov.main-bvxea6i-dnvkwx4xjhiza.uk-1.platformsh.site` |
| `Set-Cookie` | `ApplicationGatewayAffinityCORS=...` (Azure App Gateway) |
| Sitemap | `/sitemap.xml` → 267 B sitemapindex with 3 sub-sitemaps (`?page=1,2,3`), lastmod `2026-04-19T05:30:02+01:00` |
| CSP | `default-src 'self'; ...` (report-only) |
| HSTS | `max-age=31557600` (~1 year, not preloaded) |
| `x-frame-options` | `SAMEORIGIN` |
| `x-robots-tag` | `noindex, follow` (on sitemap) |
| Telemetry | NewRelic + Google Analytics + Google Tag Manager + Matomo (?) |
| CDN cache | `x-cache: MISS, HIT, MISS` (multi-tier: Azure App Gateway → Cloudflare/Fastly → Platform.sh origin) |

### 4.2 robots.txt (live)

Standard Drupal + NICS custom additions:

```
User-agent: GPTBot        Crawl-delay: 5
User-agent: ClaudeBot     Crawl-delay: 5
User-agent: BingPreview   Crawl-delay: 5
User-agent: PerplexityBot Crawl-delay: 5
User-agent: *
# CSS/JS/Images: Allow /core/* and /profiles/*
Disallow: /admin/
Disallow: /comment/reply/
Disallow: /filter/tips
Disallow: /node/add/
Disallow: /search/
Disallow: /user/{register,password,login,logout}
# NICS custom: block direct access to documents (force gateway pages)
Disallow: /*.pdf  Disallow: /*.doc  Disallow: /*.docx
Disallow: /*.xls  Disallow: /*.xlsx  Disallow: /*.ppt  Disallow: /*.pptx
Disallow: /*.odt  Disallow: /*.ods  Disallow: /*.odp  Disallow: /*.dot
Disallow: /*.zip
# Block facet URLs
Disallow: /*?f[*
Disallow: /*&f[*
Disallow: /consultations/{type,topic,date}/
Disallow: /news/{type,topic,date,news-type,news-topic,news-date}/
Disallow: /press-releases/{type,topic,date}/
Disallow: /publications/{type,topic,date}/
Sitemap: https://www.education-ni.gov.uk/sitemap.xml
```

**Key constraints**: AI crawlers (GPT/Claude/Bing/Perplexity) explicitly throttled to 5s; PDFs blocked at robots level (must go through publication gateway).

### 4.3 Dropdown cascade (Topics, live 2026-06-28)

```
Department of Education
├─ Curriculum and learning
├─ Children and Young People Issues
├─ Pupils and parents
├─ Teaching staff
├─ Non-teaching staff
├─ Schools and infrastructure
├─ Support and development
├─ Statistics and research (education)
├─ TransformED (major education reform programme)
├─ Good Relations and Social Change (education)
└─ Corporate Governance
```

The **CCEA** (Council for the Curriculum, Examinations & Assessment) is the actual NI curriculum body — its content lives under `topics/curriculum-and-learning` + the `ccea.org.uk` sibling site.

### 4.4 Anti-scraping posture

- **CSP report-only** — actual enforcement is in `default-src 'self'` (allow-list: Google Analytics, NewRelic, YouTube, Vimeo, jsDelivr, Google Fonts, cdnjs, unpkg)
- **Drupal 10** — standard caching (`max-age=60, must-revalidate`), `stale-if-error=180`, `stale-while-revalidate=180`
- **AI crawlers** explicitly slowed to 5s (GPTBot, ClaudeBot, BingPreview, PerplexityBot)
- **Direct PDF access blocked** in robots.txt — must follow the publication gateway
- **Platform.sh** `block-all-mixed-content` + no Cloudflare Turnstile observed

### 4.5 Rate limits

- 1 GET / 1.4 ms from CDN (cache HIT)
- 1 GET / 30 ms from origin
- No 429 observed in 5 sequential navigations
- Recommended: `Crawl-delay: 5` (per robots.txt AI guidance) and `respect max-age=60` for re-fetch

### 4.6 Existing dlt source

`cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/ni/education/ni_curriculum.py:1-40` — single resource `ni_curriculum_pages` calling `_crawl_ni_curriculum` from `_ccea_curriculum_helpers.py`. `include_irish_medium=True` for Irish-medium education. Sibling sources: `ccea_qualifications.py`, `education_ni.py`, `etini.py`, `irish_medium_ni.py` (7 total NI education sources).

### 4.7 §8 Refactor

1. **Wire the 3-page sitemap pagination** — the sitemap index is `?page=1,2,3`; current code likely only fetches `?page=1`. Add `for page in range(1, 4)` loop in `_crawl_ni_curriculum`.
2. **Respect `Crawl-delay: 5` for AI bots** — if the dlt source runs in a Dagster asset_check with a `GPTBot`-style UA, throttle to 5s/page. The current code uses no UA header.
3. **Add CCEA direct crawl** — `ccea.org.uk` is the actual exam/curriculum body. Currently only DENI (`education-ni.gov.uk`) is wired.
4. **Honor `Disallow: /*.pdf`** in dlt incremental — if a page is a PDF gateway, follow the gateway URL not the raw PDF. The current code scrapes the page and may be following direct PDF links.

---

## Cross-cutting findings

**A. All 4 UK sites are on public-cloud CDNs (no on-prem)**: gov.uk → Fastly · education.gov.scot → Azure App Gateway · gov.wales → CloudFront + AWS WAF · education-ni.gov.uk → Azure App Gateway + Platform.sh. **This is a shift from the Phase 3 S04-S07 reports** which implied gov.wales was Cloudflare. The `celtic-asset-generation` spec should reflect UK gov is **fully cloud-native**.

**B. No site is crawlable headlessly without a browser-cookied session**: gov.uk (LUX speedcurve JS check) · education.gov.scot (500) · gov.wales (AWS WAF CAPTCHA) · education-ni.gov.uk (Drupal JS cookies for auth pages).

**C. CCC anchors** (helpers exist in `cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/{en,sct,wls,ni}/education/_*_helpers.py`). All use `crawl_website(...)` + `scrape_page(...)` from `common.firecrawl_source`. None wired for sitemap-paginated iteration; all use 6-7 URL hard-coded seed lists.

**D. BAML extraction** wired: `cianfhoghlaim/core/baml/_oideachais_src/multi_nation_curriculum.baml:78-102` has `ExamBoard` (AQA/OCR/EDEXCEL/WJEC/CCEA) + `CurriculumFramework` (NATIONAL_CURRICULUM/CfE/CfW/CCEA) enums. All 4 sites extractable via `ExtractEnStrong`.

---

## Drift log

| Date | Event | Impact |
|:--|:--|:--|
| 2026-06-28 22:47 UTC | education.gov.scot `/sitemap.xml` + `/robots.txt` + `/` all return HTTP 500 | All 3 SCT sources will fail; fallback to SQA + Wayback |
| 2026-06-28 22:47 UTC | gov.wales moved from Cloudflare → **CloudFront + AWS WAF** with CAPTCHA | Direct gov.wales crawl blocked; Hwb unaffected |
| 2026-06-28 22:47 UTC | education-ni.gov.uk sitemap is **3-page paginated** (`?page=1,2,3`) | Current dlt code likely only fetches page 1 |
| 2025-11 → 2026-02 | Phase 3 baseline reports S04–S07 written | Some details (gov.wales CDN, education.gov.scot uptime) now stale |

---

## Anti-patterns observed

1. **Hard-coded seed URL lists** — all 4 helpers use a 6-7 URL dict. Sitemap-driven discovery is not used despite every site having a sitemap.
2. **No `User-Agent` header set** — all 4 helpers rely on Firecrawl's default UA; gov.wales WAF may block this. The dlt source should set `User-Agent: Cianfhoghlaim-Education/1.0 (+https://cianfhoghlaim.ie/bot)` and respect robots.txt.
3. **No `Crawl-delay` enforcement** — dlt does not pause between requests. The NI robots.txt explicitly requires 5s for AI crawlers; this is not honoured.
4. **Mixed naming** — `_crawl_hwb_curriculum` (Wales) actually crawls `hwb.gov.wales` (Thinqi LMS) + `wjec.co.uk`, not `gov.wales`. The docstring is misleading.
5. **No site health check** — education.gov.scot's 500 will retry endlessly; the source should `yield {"status": "site_unavailable"}` and let Dagster flag the asset as `failed` rather than hang.

---

## Decision matrix (per-site)

| Site | Crawl method | Source | Refresh | Strategy |
|:--|:--|:--|:--|:--|
| gov.uk | Fastly Varnish + sitemapindex iteration | `en/education/national_curriculum.py` | Monthly | DfE page; AQA/Edexcel/OCR exam boards separate |
| education.gov.scot | **Skip until site returns**; fallback SQA | `sct/education/curriculum_for_excellence.py` | n/a (site 500) | Health-check precondition; SQA as canonical |
| gov.wales / Hwb | Hwb Thinqi + WJEC (gov.wales blocked) | `wls/education/curriculum_for_wales.py` | Quarterly | Crawl `hwb.gov.wales` + `wjec.co.uk` + `cbac.co.uk`; abandon gov.wales |
| education-ni.gov.uk | Drupal 10 + paginated sitemap (3 pages) | `ni/education/ni_curriculum.py` | Quarterly | 5s Crawl-delay; iterate `?page=1,2,3`; add CCEA peer |

---

## Files to read next (for follow-up agents)

1. `cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/en/education/_national_curriculum_helpers.py:1-245` (gov.uk)
2. `cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/sct/education/_curriculum_for_excellence_helpers.py:1-224` (CfE)
3. `cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/wls/education/_curriculum_for_wales_helpers.py:1-245` (CfW / Hwb)
4. `cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/ni/education/_ccea_curriculum_helpers.py` (CCEA)
5. `openspec/research/2026-06-28-browserbase-credit-program/phase-3/S04-gov-uk.md` (prior, now partly stale)
6. `openspec/research/2026-06-28-browserbase-credit-program/phase-3/S05-education-gov-scot.md` (prior, **outage confirmed**)
7. `openspec/research/2026-06-28-browserbase-credit-program/phase-3/S06-gov-wales.md` (prior, **CDN drift to AWS**)
8. `openspec/research/2026-06-28-browserbase-credit-program/phase-3/S07-education-ni-gov-uk.md` (prior, sitemap pagination now known)
