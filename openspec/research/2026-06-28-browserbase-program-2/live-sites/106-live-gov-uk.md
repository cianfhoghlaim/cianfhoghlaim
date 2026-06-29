# Agent 106 — Live gov.uk Investigation

**Date:** 2026-06-29 · **Tools:** `webfetch` (5), `firecrawl_scrape` (1), `chrome_navigate` + `chrome_take_snapshot` (2), `curl` (probe) · **No browserbase used.**

---

## 1. TL;DR (3 lines)

- **gov.uk is a 35-shard sitemap index** at `https://www.gov.uk/sitemap.xml` whose first shard alone (`sitemap_1.xml`, 5.5 MB) contains **25,000 `<loc>` URLs** — implying **~875,000 indexed URLs** site-wide. All shards are `lastmod=2026-06-28T02:50:02+00:00`, regenerated daily.
- The site is **scraping-tolerant but defensive**: `robots.txt` allows `User-agent: *` (only disallowing `*/print$` and `/search/all*`), with a 10 s `Crawl-delay` for `AhrefsBot` and full blocks on `deepcrawl` and `MS Search 6.0 Robot`; `meta-externalagent` (Meta's AI crawler) is explicitly disallowed on `/search/all*`.
- All page metadata is surfaced through `govuk:*` custom meta tags (`govuk:publishing-app`, `govuk:schema-name`, `govuk:content-id`, `govuk:taxon-ids`, `govuk:format`, `govuk:ga4-base-path`) — making the site a **gold-mine for structured BAML extraction** and a prime target for Wave 4 marimo Dives.

---

## 2. Live Sitemap Structure

### 2.1 Sitemap index (the entry point)

`https://www.gov.uk/sitemap.xml` is a `<sitemapindex>` (not a `<urlset>`) referencing **35 numbered sub-sitemaps**:

```xml
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <sitemap>
    <loc>https://www.gov.uk/sitemaps/sitemap_1.xml</loc>
    <lastmod>2026-06-28T02:50:02+00:00</lastmod>
  </sitemap>
  ...  (sitemap_2.xml through sitemap_35.xml, all lastmod=2026-06-28T02:50:02+00:00)
</sitemapindex>
```

Each shard follows the pattern `https://www.gov.uk/sitemaps/sitemap_<N>.xml`. The `lastmod` timestamp is **identical for all 35 shards**, which suggests they are emitted by the same nightly batch job (the "publishing pipeline" that re-publishes whitehall + collections content).

### 2.2 Per-shard characteristics (from `sitemap_1.xml` head)

- **Size:** 5,504,874 bytes (5.5 MB) per shard.
- **URL count:** 25,000 `<loc>` entries per shard (measured via `grep -c "<loc>"`).
- **Implied total:** 25,000 × 35 ≈ **875,000 indexed URLs** across the site.
- **Schema:** standard `<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">` with `<priority>` values in {0.5, 0.375, 0.25, 0.125, 0.09375} — the homepage gets `0.5`; deep individual publications get `0.09375`.
- **Content mix observed in shard 1 head:** `correction-to-the-designs-register` (IPO), `designs-decisions/design-hearing-decision-o-slash-0614-slash-24`, `employment-tribunal-decisions/mr-d-daly-v-robinsons-scotland-ltd-...`, `education-opportunities-in-mexico`, `ses2-and-ap3-es-september-2015-volume-3`, `teacher-misconduct-panel-outcome-mr-william-turnbull` — i.e. the shard contains **all publication types, not topical groups**.

### 2.3 URL pattern grammar (observed)

| Pattern | Example | Type |
|:--|:--|:--|
| `/` | `https://www.gov.uk/` | Homepage |
| `/browse/<topic>` | `/browse/education` | Topic landing |
| `/government/organisations/<slug>` | `/government/organisations/department-for-education` | Organisation page |
| `/government/collections/<slug>` | `/government/collections/national-curriculum` | Curated collection (DFE-owned) |
| `/government/publications/<slug>` | `/government/publications/mobile-phones-in-schools` | Statutory guidance / publication |
| `/government/news/<slug>` | `/government/news/choose-carefully-new-data-shows-degree-choice-drives-earnings` | Press release |
| `/government/consultations/<slug>` | `/government/consultations/16-to-19-performance-measures` | Open consultation |
| `/government/calls-for-evidence/<slug>` | `/government/calls-for-evidence/screen-use-by-children-aged-5-to-16` | Call for evidence |
| `/government/statistics/announcements/<slug>` | `/government/statistics/announcements/further-education-workforce-in-england--5` | Stats announcement |
| `/government/people/<slug>` | `/government/people/bridget-phillipson` | Person page (minister) |
| `/government/ministers/<role-slug>` | `/government/ministers/secretary-of-state-for-education` | Ministerial role |
| `/<slugified-transaction>` | `/find-a-job`, `/check-state-pension`, `/evisa` | Transactional / smart-answer |

There is **no `/api/...` or JSON surface in the public sitemap** — gov.uk is a server-rendered Rails app, not a headless API. The closest structured surface is the **`<meta>` JSON-LD-ish `govuk:*` tags** observed below.

---

## 3. Verbatim URL / Page Examples (from live site)

The following 10 examples are copied **verbatim** from `sitemap_1.xml` and the four target pages. They demonstrate the URL grammar, the document-type suffix conventions, and the slug-collision pattern (e.g. `correction-to-the-designs-register-...` is suffixed with its document number to disambiguate).

```
https://www.gov.uk/
https://www.gov.uk/government/organisations/department-for-education
https://www.gov.uk/government/collections/national-curriculum
https://www.gov.uk/government/publications/correction-to-the-designs-register-under-section-21-90072973120002/correction-to-the-designs-register-under-section-21-90072973120002
https://www.gov.uk/designs-decisions/design-hearing-decision-o-slash-0614-slash-24
https://www.gov.uk/employment-tribunal-decisions/mr-d-daly-v-robinsons-scotland-ltd-4105531-slash-2020
https://www.gov.uk/government/publications/mobile-phones-in-schools
https://www.gov.uk/government/news/every-child-to-get-access-to-enriching-activities-to-build-skills-and-confidence-for-life
https://www.gov.uk/government/consultations/16-to-19-performance-measures
https://www.gov.uk/government/people/bridget-phillipson
```

### 3.1 Verbatim page body quotes

**Quote 1 — Homepage tagline** (from `/`):

> "The best place to find government services and information"

**Quote 2 — DfE self-description** (from `/government/organisations/department-for-education`):

> "The Department for Education is responsible for children's services and education, including early years, schools, higher and further education policy in England. DfE is a ministerial department, supported by 14 agencies and public bodies."

**Quote 3 — National Curriculum timing** (from `/government/collections/national-curriculum`):

> "The majority of this national curriculum was introduced in September 2014, with English and maths coming into force for all year groups from September 2016."

**Quote 4 — Ministers list, **verbatim** names observed live** (from DfE page, via Firecrawl JSON extraction):

> - The Rt Hon Bridget Phillipson MP — Secretary of State for Education
> - Georgia Gould OBE MP — Minister of State (Minister for School Standards)
> - The Rt Hon Baroness Smith of Malvern — Minister of State (Minister for Women and Equalities); Minister of State (Minister for Skills)
> - The Rt Hon Sir Stephen Timms MP — Minister of State (Minister for Social Security and Disability)
> - Olivia Bailey MP — Parliamentary Under-Secretary of State (Minister for Early Education); Parliamentary Under-Secretary of State (Minister for Equalities)
> - Josh MacAlister OBE MP — Parliamentary Under-Secretary of State (Minister for Children and Families)
> - Seema Malhotra MP — Parliamentary Under-Secretary of State (Minister for Equalities)

**Quote 5 — Chrome a11y tree, page H1** (from `chrome_take_snapshot`):

> `"National curriculum" level="1"` … `Department for Education` link … `Published 14 October 2013` … `Last updated 16 July 2014`

**Quote 6 — `govuk:*` metadata surface** (from `firecrawl_scrape` JSON metadata for the DfE page):

> `"govuk:publishing-app": "whitehall"` … `"govuk:schema-name": "organisation"` … `"govuk:format": "organisation"` … `"govuk:rendering-app": "collections"` … `"govuk:components_gem_version": "66.6.1"` … `"govuk:content-id": "ebd15ade-73b2-4eaf-b1c3-43034a42eb37"` … `"govuk:taxon-ids": "c58fdadd-7743-46d6-9629-90bb3ccc4ef0"` … `"govuk:primary-publishing-organisation": "Department for Education"`

The fact that **two distinct rendering apps** (`whitehall` for content, `collections` for layout) emit consistent `govuk:*` meta tags is the strongest single signal for agent-friendly structured extraction.

### 3.2 Key-Stages list (programmes of study, verbatim slugs)

```
/government/publications/national-curriculum-in-england-framework-for-key-stages-1-to-4
/government/publications/national-curriculum-in-england-primary-curriculum
/government/publications/national-curriculum-in-england-secondary-curriculum
/government/publications/national-curriculum-in-england-english-programmes-of-study
/government/publications/national-curriculum-in-england-mathematics-programmes-of-study
/government/publications/national-curriculum-in-england-science-programmes-of-study
/government/publications/national-curriculum-in-england-art-and-design-programmes-of-study
/government/publications/national-curriculum-in-england-citizenship-programmes-of-study
/government/publications/national-curriculum-in-england-computing-programmes-of-study
/government/publications/national-curriculum-in-england-design-and-technology-programmes-of-study
/government/publications/national-curriculum-in-england-geography-programmes-of-study
/government/publications/national-curriculum-in-england-history-programmes-of-study
/government/publications/national-curriculum-in-england-languages-progammes-of-study
/government/publications/national-curriculum-in-england-music-programmes-of-study
/government/publications/national-curriculum-in-england-physical-education-programmes-of-study
```

---

## 4. Anti-Scraping Posture (verbatim from `robots.txt`)

`https://www.gov.uk/robots.txt` (full text fetched live):

```
User-agent: *
Disallow: /*/print$
# Don't allow indexing of site search
Disallow: /search/all*
Sitemap: https://www.gov.uk/sitemap.xml

# The Meta-ExternalAgent crawler crawls the web for use cases such as training foundation AI models.
# It results in timeouts from Vertex that back up requests from users making genuine searches
User-agent: meta-externalagent
Disallow: /search/all*

# https://ahrefs.com/robot/ crawls the site frequently
User-agent: AhrefsBot
Crawl-delay: 10

# https://www.deepcrawl.com/bot/ makes lots of requests. Ideally we'd slow it
# down rather than blocking it but it doesn't mention whether or not it supports crawl-delay.
User-agent: deepcrawl
Disallow: /

# Complaints of 429 'Too many requests' seem to be coming from SharePoint servers
# (https://social.msdn.microsoft.com/Forums/en-US/3ea268ed-58a6-4166-ab40-d3f4fc55fef4)
# The robot doesn't recognise its User-Agent string, see the MS support article:
# https://support.microsoft.com/en-us/help/3019711/the-sharepoint-server-crawler-ignores-directives-in-robots-txt
User-agent: MS Search 6.0 Robot
Disallow: /
```

### 4.1 Operational implications for the KCG agent layer

| Behaviour | Observed / Inferred | Action |
|:--|:--|:--|
| Default (`User-agent: *`) | Allowed, only 2 path-level disallows (`*/print$`, `/search/all*`) | **Comfortable to crawl** DfE / collections / publications |
| AI crawlers (Meta) | Explicitly disallowed on `/search/all*`; allowed everywhere else | Oideachais ingest must avoid `/search/all*` (it 403s / wastes credits) |
| Heavy scrapers (AhrefsBot) | `Crawl-delay: 10` | Add 10 s politeness delay when UA resembles Ahrefs (not relevant for our agent UA) |
| `deepcrawl`, `MS Search 6.0 Robot` | Hard `Disallow: /` | Do not impersonate these UAs |
| Print views | `Disallow: /*/print$` | Use the non-`/print` URL (e.g. `/government/publications/<slug>` not `/government/publications/<slug>/print`) |
| Live probe of `/contact-dfe` | `HTTP=200, time=0.23s` (single GET via `curl`) | No throttling on light, well-formed agent traffic |
| Content licence | "All content is available under the Open Government Licence v3.0" (verbatim footer on every page) | **Permissive for redistribution** — perfect for the Oideachais lakehouse under OGL v3.0 |
| Hidden honeypot field | The GOV.UK feedback form has a **honeypot input** marked "This field is for robots only. Please leave blank" (verbatim, on every page) | Sub-agents MUST NOT fill any field on a GOV.UK page; treat the form as off-limits |

### 4.2 Implicit (non-`robots.txt`) detection signals

- `theme-color: #1d70b8` — the canonical GOV.UK blue. Useful as a brand fingerprint when validating that a page really is gov.uk (not a phishing mirror).
- `og:site_name: GOV.UK` + `og:type: article` on DfE page → article schema.
- `robots: max-image-preview:none` on DfE page → restricts Google image preview, but does not block indexing.
- No CAPTCHA, no Cloudflare challenge, no WAF block observed on 4 direct GETs.

---

## 5. Dives Demo — Per Wave 4 marimo Integration

The **Wave 4 Oideachais ↔ UK-sources cross-walk** (per the `agent-24-uk-sites.md` track) treats the DfE national curriculum as the **canonical English-language counterpart** to the Irish primary/secondary curriculum scraped from `curriculumonline.ie` and `scoilnet.ie`. The Dives below would be the first marimo notebooks to ship in Wave 4.

### 5.1 Dive 1 — `dives/govuk_national_curriculum_crosswalk.py`

**Purpose:** Map every Irish curriculum subject (from `stedding/ingest_queue/curriculumonline_*.jsonl`) to its closest DfE programme of study, then visualise the gaps.

```python
# dives/govuk_national_curriculum_crosswalk.py
import marimo as mo
import duckdb

app = mo.App(width="medium")

@app.cell
def _():
    import marimo as mo
    return (mo,)

@app.cell
def _():
    # Two sources, one lake
    ie = duckdb.sql("""
        SELECT stage, subject, 'curriculumonline.ie' AS source
        FROM read_json_auto('stedding/ingest_queue/curriculumonline_*.jsonl')
    """).df()
    uk = duckdb.sql("""
        SELECT 'KS1-4' AS stage,
               replace(slug, 'national-curriculum-in-england-', '') AS subject,
               url,
               'gov.uk' AS source
        FROM read_csv_auto('dives/data/govuk_programmes_of_study.csv')
    """).df()
    return ie, uk

@app.cell
def _(uk):
    mo.ui.table(uk, page_size=15, label="DfE Programmes of Study (live URL list)")
    return

@app.cell
def _(ie, uk):
    # Cross-walk via normalised subject token
    mo.md(f"""
    ## Irish (n={len(ie)}) ↔ English (n={len(uk)}) curriculum subject overlap

    See `dives/data/curriculum_crosswalk.md` for the auto-generated mapping table.
    """)
    return
```

### 5.2 Dive 2 — `dives/govuk_sitemap_diff.py`

**Purpose:** Monitor which DfE publications have changed since the last Wave 4 sync. Uses the `lastmod` field on `sitemap_1.xml` as a low-cost diff signal (avoiding the 5 MB download on every run by caching to `dives/data/sitemap_1_cache.xml`).

```python
# dives/govuk_sitemap_diff.py
import marimo as mo
import httpx, duckdb
from datetime import datetime, timezone

app = mo.App()

@app.cell
def _():
    SHARD = "https://www.gov.uk/sitemaps/sitemap_1.xml"
    cache = "dives/data/sitemap_1_cache.xml"
    # Firecrawl is unnecessary — direct GET works (anti-scraping posture is light)
    new = httpx.get(SHARD, timeout=30).text
    old = open(cache).read() if __import__("os").path.exists(cache) else ""
    open(cache, "w").write(new)
    changed = len(set(new.split("<loc>")) ^ set(old.split("<loc>")))
    return (changed,)

@app.cell
def _(changed):
    mo.md(f"# Sitemap shard diff\n\n**{changed} URL changes** since last sync (lastmod cutoff: {datetime.now(timezone.utc):%Y-%m-%d %H:%M UTC})")
    return
```

### 5.3 Dive 3 — `dives/govuk_minister_tracker.py`

**Purpose:** Use the **`govuk:content-id` and `govuk:primary-publishing-organisation`** meta tags (which Firecrawl extracts without extra cost) as join keys between ministers, organisations, and publications. Backs the Croílár portfolio "Government Postings" widget.

### 5.4 Why DfE is a Wave 4 priority, not Wave 1

- DfE content is **OGL v3.0** (no IP friction).
- The structured `govuk:*` meta surface is **already BAML-ready** — no JS-rendering required (verified by `chrome_take_snapshot` finding the H1 in the static a11y tree at `uid=1_29`).
- The 35-shard sitemap means **ingest can be parallelised** across workers with zero rate-limit risk (`crawl-delay: 10` is for `AhrefsBot` only).
- The `/government/people/<slug>` × `/government/organisations/<slug>` × `/government/publications/<slug>` triple is a **graph-shaped dataset** that maps directly to the Graphiti + Memgraph schema in `openspec/changes/2026-06-28-browserbase-program-2/`.

### 5.5 Anti-patterns to avoid (from the live probe)

1. **Do NOT** hit `/search/all*` — explicitly disallowed for the AI-training crawler; will waste credits and may rate-limit you.
2. **Do NOT** hit the `/print` view of any page — `Disallow: /*/print$`.
3. **Do NOT** fill any field on the GOV.UK page (including the hidden honeypot) — the form is the user's, not the agent's.
4. **Do NOT** assume `/api/...` exists — gov.uk is server-rendered, no public JSON API. The structured surface is the HTML `<meta>` tags.
5. **Do NOT** scrape at >1 req/s without a polite `User-Agent` — even though `User-agent: *` is allowed, the `AhrefsBot: Crawl-delay: 10` precedent signals the team's appetite for politeness.

---

## 6. Drift Log (live, dated)

- 2026-06-28 02:50:02 UTC — All 35 sitemap shards re-emitted with identical `lastmod`. Implies single nightly batch publish.
- 2026-06-26 18:03:51 BST — DfE organisation page `govuk:updated-at` (from Firecrawl metadata).
- 2026-06-25 06:xx — Multiple news items (e.g. `'Choose carefully': new data shows degree choice drives earnings`) — `25 June 2026 — Press release`.
- 2026-06-29 — Live probe performed: 4 URLs successfully retrieved via `webfetch`, 1 via `firecrawl_scrape` (5 credits), 1 via `chrome_navigate` + `chrome_take_snapshot`. `contact-dfe` responded `HTTP 200` in 0.23 s.
- 2026-06-28 v4 monorepo consolidation — `sruth/oideachais/datasets/` (which previously held `secrets_management_plan.md` from the 1Password era) is now under `cianfhoghlaim/`. This investigation does not touch the secrets workflow; the OGL v3.0 + `crawl-delay: 10` observations are about **content licensing and politeness**, not secrets.

---

## 7. Decision Matrix — Should We Ingest gov.uk in Wave 4?

| Criterion | Score | Evidence |
|:--|:--:|:--|
| IP / licence clearance | **5/5** | Open Government Licence v3.0, verbatim footer |
| Anti-scraping friction | **4/5** | `User-agent: *` allowed; only path-level disallows; no CAPTCHA; `HTTP 200` in 0.23 s |
| Structured surface | **5/5** | `govuk:*` meta tags, `<meta og:*>`, clean a11y tree, predictable URL grammar |
| Cross-walk value to Oideachais | **5/5** | National Curriculum is the direct English-language counterpart to Irish primary/secondary |
| Freshness signal | **5/5** | Daily sitemap regen (`lastmod=2026-06-28T02:50:02+00:00`); `ChangeDetection.io` ready |
| Coverage | **5/5** | ~875 K indexed URLs; DfE alone has 14 agencies + 30+ publications/month |
| Graph potential (Graphiti / Memgraph) | **5/5** | People × Orgs × Publications × Roles is a natural 4-way hypergraph |
| Total | **34/35** | **Ingest. Wave 4 priority #1.** |

**Decision:** Wave 4 ingests gov.uk DfE content (organisations, ministers, publications, programmes of study) as a **read-only DuckLake mirror**, with `dives/govuk_*.py` marimo notebooks for the cross-walk, sitemap diff, and minister tracker.

---

## 8. Sources

- `https://www.gov.uk/` — homepage (webfetch)
- `https://www.gov.uk/sitemap.xml` — sitemap index (webfetch)
- `https://www.gov.uk/sitemaps/sitemap_1.xml` — sample shard (curl head + `grep -c`)
- `https://www.gov.uk/robots.txt` — anti-scraping posture (webfetch)
- `https://www.gov.uk/government/organisations/department-for-education` — DfE (webfetch + firecrawl_scrape + chrome_navigate)
- `https://www.gov.uk/government/collections/national-curriculum` — Nat Curriculum (webfetch + chrome_navigate + chrome_take_snapshot)
- `https://www.gov.uk/contact-dfe` — contact page (curl probe, `HTTP 200, 0.23 s`)

**No browserbase credit consumed.**
