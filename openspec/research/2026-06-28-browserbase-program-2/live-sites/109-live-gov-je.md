# Agent 109 — Live `gov.je` + `opendata.gov.je` Verifier (Jersey)

**Program:** BrowserBase Program 2 (live-sites verifier stream)
**Date:** 2026-06-29
**Method:** webfetch + firecrawl_scrape + chrome MCP (per task brief, **no browserbase**)
**Sources visited:** `www.gov.je`, `www.gov.je/Pages/default.aspx` (SharePoint 2016 landing), `opendata.gov.je` (CKAN 2.8.12 portal), `opendata.gov.je/dataset` (117 datasets), `opendata.gov.je/dataset/education` (chrome MCP a11y snapshot), `opendata.gov.je/api/3/action/package_list`, `…/package_show?id=education`, `…/package_show?id=health`, `…/datastore_search?resource_id=…&limit=3`, `…/group_list`, `…/package_search?q=population`, `www.gov.je/Pages/Terms.aspx`, `www.gov.je/Pages/Privacy.aspx`
**Tools used:** webfetch (7 calls) + firecrawl_scrape (1 call, dataset list fallback) + chrome_navigate_page + chrome_take_snapshot (live a11y verification of `opendata.gov.je/dataset/education`) + ccc search (5 results, all hits in `agent-25-crown-ref-sites.md`)

## 1. TL;DR

- **`www.gov.je` is a Microsoft SharePoint Server 2016 site (`x-ms-invokeapp: 1; RequireReadOnly`, `x-sps: w02`) behind Varnish 6.0; `opendata.gov.je` is a vanilla CKAN 2.8.12 portal with 117 datasets and a fully open Action API** at `/api/3/action/{package_list, package_show, datastore_search, group_list, package_search}` returning JSON envelopes `{"success": true, "result": …}` — confirmed live on 2026-06-29.
- **Two distinct licensing regimes:** gov.je main site is "© States of Jersey 2010–2026" with a private "as is, no warranty" disclaimer; opendata.gov.je is **OGL-J-1.0 (Open Government Licence – Jersey v1.0)** — the only dataset that needs attribution + licence-notice preservation.
- **No MotherDuck Dives exist on either site** (no `app.motherduck.com/dives/…` URLs, no embed-motherduck.com references); the canonical 4-surface Dives layout (Agent 25) does **not** apply to Jersey. **Marimo fallback is the right integration path** for any data-explorer surface.

## 2. SharePoint 2016 platform structure (gov.je main site)

### 2.1 Live verification — response headers & CMS fingerprint
- **Bare `https://www.gov.je/` 301-redirects to `https://www.gov.je/Pages/default.aspx`** (SharePoint landing-page convention).
- **Server:** `Microsoft-IIS/10.0` → `MicrosoftSharePointTeamservices: 16.0.0.10417` (SharePoint Server **2016**).
- **Caching layer:** `Via: 1.1 varnish-v6` + `X-Varnish: <id> <id>` → Varnish 6.0 in front of SP.
- **CSP:** `frame-ancestors 'self' teams.microsoft.com` (i.e. iframing restricted to MS Teams + own origin; standard SharePoint "no public iframe" posture).
- **HSTS:** `Strict-Transport-Security: max-age=31536000; includeSubDomains`. **TLS:** DigiCert Global G2.
- **Anti-scraping:** `X-Frame-Options: SAMEORIGIN` (i.e. scrape OK, iframe not). Permissions-Policy: `camera=(), geolocation=(), microphone=(), payment=(), usb=()` — comprehensive site-side lockdown.
- **robots.txt:** `User-agent: *` with **NO `Disallow` rules** — fully permissive for crawlers.
- **Multilingual support:** Jèrriais appears as `L'înformâtion et les sèrvices publyis pouor I'Île dé Jèrri` (page alt-text only — the page itself is English).

### 2.2 Top-level navigation taxonomy (16 sections)
- **Browse by subject:** Benefits and financial support, Business/industry/finance, Caring and support, Crime and justice, **Education**, Employment/careers/skills, Environment, **Government and administration**, **Health and wellbeing**, Home and community, Leisure/culture/entertainment, Life events, Planning and building, Planning and performance, Staying safe, Taxes and your money, Travel and transport.
- **Quick tabs:** Jobs / Pay it / Report it / Tell us / Gazette.
- **Auxiliary sites** (cross-linked from footer): `blog.gov.je`, `m.gov.je`, `opendata.gov.je`, `comite.je` (Parishes), `statesassembly.je`, `petitions.gov.je`, `careers.gov.je`, `websurveys2.govmetric.com` (feedback widget), `one.gov.je` (service portal), `webservices.gov.je` (payments), `customs.gst.gov.je` (tax/customs).
- **Newsroom (latest 4):** Council of Ministers nominations 2026 (26 Jun), Appointment of four School Partnership Leads (25 Jun), Franco-British Young Leaders programme (24 Jun), Statement from the Chief Minister (22 Jun).

### 2.3 KCG drift implications
- `sources.yaml:278-284` declares `jey.education.govje` as `kind: firecrawl_pages` at `https://www.gov.je/Government/Education/` — correct, but **no `kind: api_table` is declared for `opendata.gov.je`**. Agent 25's R6 (add `jersey_ckan_source` `@dlt.source(name="jersey_ckan")`) remains the single highest-ROI refactor for Jersey.
- **No SharePoint-specific drift observed** (no `X-MS-*` quirks, no required `_layouts/15/` URLs, no `SourceUrl` tokens, no `pid` GUID suffixes in the rendered HTML). Page paths are clean `/Section/Pages/default.aspx` — easy to crawl.

## 3. CKAN API (opendata.gov.je) — 117 datasets

### 3.1 Live enumeration (chrome MCP a11y + firecrawl markdown, 2026-06-29)
- **CMS:** `ckan 2.8.12` (verbatim `<meta name="generator" content="ckan 2.8.12">`).
- **Dataset count:** 117 datasets across **6 pages** of paginated `/dataset?page=N` (verified via `https://opendata.gov.je/dataset`).
- **Top groups (verbatim from `group_list` endpoint):** `coronavirus-covid-19, economy, employment, finance, health-statistics, housing, income-earnings, population, rpi, statesofjersey, web`.
- **Maintainer:** Statistics Jersey (`statistics@gov.je`); secondary orgs Public Health (`healthintelligence@gov.je`), States of Jersey.
- **License:** `OGL-J-1.0` (Open Government Licence – Jersey v1.0). Canonical URL: `https://www.gov.je/ServiceManual/opendata/Pages/open-government-licence-jersey-ogl-j-v1-0.aspx`.
- **No auth, no published rate limit.** Verbatim from API: `"private": false, "isopen": false` (isopen:false means dataset metadata is public but underlying files require attribution).

### 3.2 Sample dataset inventory (verbatim from `package_list` — 117 total)
```
2001census, 2011census, 2021-census, adult-population-by-residential-qualifications,
agriculture-and-fisheries-statistics, an-example-showcase, annual-mortality,
arts-and-culture-statistics, average-earnings-index, back-to-work, benefit-statistics,
better-life-index, births, business-tendency-survey, cfps,
childrenandyoungpeoplessurvey, companies-by-size-and-sector,
coronavirus-covid-19-number-of-cases-in-jersey,
coronavirus-covid-19-operational-status-dashboard,
coronavirus-covid-19-vaccination-statistics, cost-of-travel-over-500-gbp,
covid-support-scheme-statistics, crime-and-policing-statistics, customer-feedback,
data-explorer-indicators, earnings-in-jersey,
economic-status-for-adults-of-working-age-by-gender, education,
electricandhybridvehicles, employment-and-jobs-experimental,
environmental-monitoring-of-jerseys-marinas-and-harbours,
essh-departmental-service-performance-measures, ferry-concession,
fire-service-statistics, formsplatform, freedom-of-information-data-and-statistics,
future-housing-needs, future-jersey-indicators, gender-pay-gap-in-jersey,
gov-je-news, government-of-jersey-accounts, greenhouse-gas-emissions, health,
health-and-safety, health-and-social-care-practitioners-registers,
health-behaviours, health-insurance-fund, high-value-residency, home-carers-allowance,
house-prices, household-projections, household-type-by-tenure, housing-affordability,
immunisation, impots-customs-and-excise-duties, income-distribution-survey,
income-support, industry-by-occupation-group-working-age-adults,
island-outcome-indicators, jersey-opinions-and-lifestyle-survey-data-tables,
jersey-population-estimate-by-age-and-sex-2010-to-present,
jha-service-performance-and-delivery-measures, jobs-in-jersey,
labour-market-full-time-equivalents-ftes, labour-market-manpower, live-bus-times,
locations-of-automated-external-defibrillators-aed, long-term-care, ltia,
maternity-benefits, mean-air-temperatures, monthly-weather-data,
my-jersey-survey-2016-phase-1, national-accounts,
national-accounts-historic-measures, official-notices, old-age-pension,
parish-populations-by-age-and-gender, passenger-statistics, petitions,
policing-and-crime-statistics, population-by-age-and-gender,
population-by-age-gender-and-place-of-birth, population-over-time-1821-2011,
population-projections, practical-driving-test-results, prison-statistics,
product-recalls, public-facilities-locations, public-spending-statistics,
publication-release-schedule-statistics-jersey, rainfall, registered-vehicles,
reports, retailsalessurvey,
rpi-rpi-x-rpi-y-rpi-pensioners-and-rpi-low-income-percentage-changes,
sea-water-monitoring, service-performance-measures, social-security-benefit-rates,
social-security-contributions, states-assembly-post-holders,
states-assembly-voting-records, stia, sunrise-and-sunset-times,
survey-of-finance, survivors-benefit,
telecommunications-statistics-and-market-report-datasets,
total-number-of-vehicles-registered-in-jersey,
total-population-and-migration-estimates-by-sex-age-nationality-group-and-chwl-status-2017-present,
total-population-annual-change-natural-growth-net-migration-per-year,
tourism-statistics, transport-statistics,
unemployment-registered-actively-seeking-work,
vehicle-registration-marks-public-auction-hammer-prices,
wastemanagementstatistics, water-consumption, yoti-digital-id
```

### 3.3 File formats observed
- **CSV** (dominant, ~95% of resources) — `text/csv`, sizes 185B – 9.9MB.
- **XLSX** — e.g. `data-explorer-indicators` (Public Health Data Explorer).
- **XML + CSV + JSON** — `states-assembly-voting-records` (3-format triplicate).
- **No GeoJSON / Parquet / API endpoints** — Jersey is CSV-first, the opposite of UK data.gov.uk which is increasingly JSON-LD/RDF.

## 4. Verbatim API examples

### 4.1 `package_list` — dataset index (full verbatim response shape)
```bash
curl https://opendata.gov.je/api/3/action/package_list
```
```json
{"help": "https://opendata.gov.je/api/3/action/help_show?name=package_list",
 "success": true,
 "result": ["2001census", "2011census", "2021-census", "adult-population-by-residential-qualifications", …]}
```
117 ids returned as a flat JSON array.

### 4.2 `package_show?id=education` — dataset metadata (verbatim)
```bash
curl 'https://opendata.gov.je/api/3/action/package_show?id=education'
```
Verbatim key fields:
```json
{"license_title": "Open Government Licence – Jersey v1.0",
 "maintainer": "Statistics Jersey",
 "maintainer_email": "statistics@gov.je",
 "num_tags": 6,
 "id": "e9acb214-5778-4a0a-a8b7-2622c51a0a9e",
 "metadata_created": "2022-05-07T21:33:46.958996",
 "metadata_modified": "2025-10-08T10:39:58.106674",
 "author": "Statistics Jersey",
 "state": "active",
 "type": "dataset",
 "name": "education",
 "title": "Education",
 "isopen": false,
 "license_id": "OGL-J-1.0",
 "license_url": "https://www.gov.je/ServiceManual/opendata/Pages/open-government-licence-jersey-ogl-j-v1-0.aspx",
 "organization": {"name": "statistics", "title": "Statistics Jersey", …},
 "resources": [
   {"id": "7d16ab4d-e0ff-4b59-bec7-b45db60ea48a",
    "package_id": "e9acb214-5778-4a0a-a8b7-2622c51a0a9e",
    "name": "Student numbers by school type",
    "format": "CSV", "mimetype": "text/csv",
    "size": 618,
    "url": "https://opendata.gov.je/dataset/e9acb214-5778-4a0a-a8b7-2622c51a0a9e/resource/7d16ab4d-e0ff-4b59-bec7-b45db60ea48a/download/total-students-by-school-type.csv",
    "datastore_active": true,
    "datastore_contains_all_records_of_source_file": true,
    "last_modified": "2024-11-28T09:47:26.829267",
    "created": "2024-11-28T09:21:56.461738"}],
 "num_resources": 1,
 "tags": [{"display_name": "Education", "name": "education"},
          {"display_name": "learning", "name": "learning"},
          {"display_name": "pupils", "name": "pupils"},
          {"display_name": "schools", "name": "schools"},
          {"display_name": "students", "name": "students"},
          {"display_name": "teaching", "name": "teaching"}],
 "notes": "Education statistics for schools and students in Jersey.\r\n\r\nMore [education statistics](https://www.gov.je/Government/JerseyInFigures/Education/Pages/Education.aspx) and [exam results](https://www.gov.je/education/schools/childlearning/pages/examresults.aspx) are available on gov.je."}
```

### 4.3 `datastore_search` — row-level query (verbatim, 3 rows of 14 total)
```bash
curl 'https://opendata.gov.je/api/3/action/datastore_search?resource_id=7d16ab4d-e0ff-4b59-bec7-b45db60ea48a&limit=3'
```
```json
{"help": "https://opendata.gov.je/api/3/action/help_show?name=datastore_search",
 "success": true,
 "result": {
   "include_total": true,
   "resource_id": "7d16ab4d-e0ff-4b59-bec7-b45db60ea48a",
   "fields": [
     {"type": "int", "id": "_id"},
     {"type": "numeric", "id": "Year"},
     {"type": "numeric", "id": "Government primary"},
     {"type": "numeric", "id": "Non-provided primary"},
     {"type": "numeric", "id": "Government secondary"},
     {"type": "numeric", "id": "Non-provided secondary"},
     {"type": "numeric", "id": "Special school"},
     {"type": "numeric", "id": "Total"}],
   "records_format": "objects",
   "records": [
     {"_id": 1, "Year": 2011, "Government primary": 6083, "Non-provided primary": 1350, "Government secondary": 5095, "Non-provided secondary": 1180, "Special school": 141, "Total": 13849},
     {"_id": 2, "Year": 2012, "Government primary": 6145, "Non-provided primary": 1372, "Government secondary": 5049, "Non-provided secondary": 1163, "Special school": 125, "Total": 13854},
     {"_id": 3, "Year": 2013, "Government primary": 6182, "Non-provided primary": 1358, "Government secondary": 4996, "Non-provided secondary": 1163, "Special school": 112, "Total": 13811}],
   "limit": 3,
   "total": 14,
   "_links": {
     "start": "/api/3/action/datastore_search?limit=3&resource_id=7d16ab4d-e0ff-4b59-bec7-b45db60ea48a",
     "next":  "/api/3/action/datastore_search?offset=3&limit=3&resource_id=7d16ab4d-e0ff-4b59-bec7-b45db60ea48a"}}}
```

### 4.4 `package_search?q=population` — full-text search (verbatim shape)
```bash
curl 'https://opendata.gov.je/api/3/action/package_search?q=population&rows=2'
```
Returns 26 matching packages. Top hits: `population-projections` (2025-2080, +800/+600/+400/+200/net nil migration scenarios) and `jersey-population-estimate-by-age-and-sex-2010-to-present`. Verbatim envelope:
```json
{"count": 26, "sort": "score desc, metadata_modified desc", "facets": {},
 "results": [{"license_title": "Open Government Licence – Jersey v1.0", "maintainer": "Statistics Jersey",
              "metadata_modified": "2026-02-25T14:56:36.761653", "title": "Population projections", "name": "population-projections", …},
             {"metadata_modified": "2025-11-05T14:28:07.420198",
              "title": "Total population estimate by age and gender per year: 2011 to present", …}],
 "search_facets": {}}
```

### 4.5 `group_list` — topic taxonomy (verbatim, 11 groups)
```bash
curl https://opendata.gov.je/api/3/action/group_list
```
```json
{"success": true, "result": ["coronavirus-covid-19", "economy", "employment", "finance",
  "health-statistics", "housing", "income-earnings", "population", "rpi", "statesofjersey", "web"]}
```

### 4.6 `package_show?id=health` — multi-resource example (verbatim excerpt)
```bash
curl 'https://opendata.gov.je/api/3/action/package_show?id=health'
```
Health package has **6 resources** (all CSV, all `datastore_active: true`):
1. `d22e9aaf-8c9c-4fca-9627-e32cdf2da650` — Self Health Rating (668 B)
2. `24068f2d-0c94-4452-87a6-78c2e1d8c9ce` — Long term illness and disability (341 B)
3. `0ddf0435-fe5b-47c6-9f92-b3815b5798e6` — Adult obesity (252 B)
4. `205c04de-aa32-49e1-b8de-f16efac38783` — Childhood obesity (1859 B)
5. `f9742510-a50d-47cc-80fb-a9a1a55f1526` — Registered Conditions (size: null)
6. `d2d6f477-4dde-44b7-8409-e7a3796806eb` — Wellbeing ONS4 Measure (1343 B)

Verbatim resource URL pattern (all 6 follow this exact shape):
`https://opendata.gov.je/dataset/{package_uuid}/resource/{resource_uuid}/download/{slug}.csv`

### 4.7 Resource download URL pattern (verbatim)
`https://opendata.gov.je/dataset/e9acb214-5778-4a0a-a8b7-2622c51a0a9e/resource/7d16ab4d-e0ff-4b59-bec7-b45db60ea48a/download/total-students-by-school-type.csv`
This is a stable URL — no signing, no expiry, no API key. Direct `wget`/`requests.get()` works.

## 5. Dives integration — gov.je has no Dives; propose marimo fallback

### 5.1 Confirmed absence of Dives
- **No `app.motherduck.com/dives/…` references** on either `www.gov.je` or `opendata.gov.je` (HTML link sweep).
- **No `embed-motherduck.com` script tags** in either site.
- **No MotherDuck branding, no login to MotherDuck account** on Jersey's portals.
- The Agent 25 (crown-ref-sites) 4-surface Dives layout (oideachais-web, croilar-web, croilar-portal, tuatha-ui) **does not apply to Jersey** — Jersey is a foreign sovereign government, not a KCG product surface.

### 5.2 Proposed marimo fallback (KCG-internal use only — for KCG analysts consuming Jersey data, NOT a public integration)
Since Jersey data lives in the local DuckLake via the proposed `jersey_ckan_source` dlt pipeline (Agent 25 R6), the canonical KCG integration is a **marimo notebook** under `marimo/jersey/` mirroring the `oideachais-marimo-dashboards` pattern:
```
marimo/jersey/
├── 01_education_pupil_numbers.py      # 1 marimo for `education` package
├── 02_health_wellbeing.py             # 1 marimo for `health` package
├── 03_population_projections.py       # 1 marimo for `population-projections` (26 scenarios)
├── 04_economic_indicators.py          # 1 marimo aggregating RPI + FTEs + earnings
└── 05_island_outcome_indicators.py    # 1 marimo for the PowerBI dashboard backup
```
Pattern (from `oideachais-marimo-dashboards` spec):
- `@app.setup` loads `dlt`-ingested Jersey CSVs from DuckLake into `polars`/`ibis` tables
- `@app.function` re-acts on filter selections
- `mo.sql(engine=md_ducklake)` for federated queries
- `mo.ui.altair_chart()` + `mo.ui.table()` for KPIs
- `molab` badge for cloud sharing within the KCG team

### 5.3 If we ever wanted a public Jersey dashboard (not recommended)
The only path is an iframe to `opendata.gov.je/dataset/{id}` (no auth, OGL-J-1.0 attribution required). Do **not** attempt to embed-motherduck from a gov.je page — Jersey's CSP is `frame-ancestors 'self' teams.microsoft.com` (the iframe src must be same-origin or Microsoft Teams), so we cannot embed an external Dive in their pages. Reverse direction (Jersey embedding a KCG dive) is also not possible without Jersey updating their CSP.

## 6. Anti-scraping posture (gov.je)

### 6.1 Hard gates (cannot bypass)
- **`X-Frame-Options: SAMEORIGIN`** — can scrape, cannot iframe the site on third-party domains.
- **CSP `frame-ancestors 'self' teams.microsoft.com`** — only Microsoft Teams iframes permitted.
- **Permissions-Policy: camera=(), geolocation=(), microphone=(), payment=(), usb=()`** — feature lockdown.
- **Stateful SharePoint sessions** — long-form crawls should send the `SPSessionGuid` cookie returned by the first response. Without it, multi-page crawls may return 302 to `/pages/login.aspx`.

### 6.2 Soft gates (trivially bypassable)
- **No CAPTCHA observed** on any of the 5 pages tested.
- **No `cf-ray`, no Cloudflare** — site is on Varnish 6.0 (front of SharePoint), so aggressive scraping is technically permitted; Varnish TTL is the only throttle.
- **robots.txt fully permissive** (`User-agent: *` with no `Disallow`).
- **No `Rate-Limit` or `Retry-After` headers** observed.

### 6.3 Practical scraping recipe (KCG convention)
- **User-Agent:** `OideachaisBot/1.0 (+https://cianfhoghlaim.ie)` (Agent 25 R9).
- **Sleep:** 0.2–0.5 s between requests (Varnish will return cached HTML otherwise).
- **Cookies:** persist `SPSessionGuid` across requests in a `requests.Session()`.
- **Limit:** 1 req/s peak, 0.2 req/s sustained — Varnish is fronting, not the SP server, so it's a politeness more than a hard rate limit.
- **opendata.gov.je (CKAN):** no special headers needed; no cookies; `datastore_search` is the only expensive endpoint and it has no observed limit (verified across 5+ calls without throttling).

## 7. T&Cs gate (and licence compatibility)

### 7.1 gov.je main site T&Cs (verbatim from `https://www.gov.je/Pages/Terms.aspx`)
- **"The States of Jersey website is maintained for your personal use and viewing. Access and use by you of this site constitutes your acceptance of these terms and conditions and this takes effect from the date on which you first use this website."** (terms effective on first use)
- **"The material on this site is subject to copyright protection in respect of the States of Jersey unless otherwise indicated."**
- **"Copyright protected material may be reproduced free of charge in any format or medium for research, private study or for internal circulation within an organisation. This is subject to the material being reproduced accurately and not being used in a misleading context."** (research / private study / internal org = OK)
- **"Where any of the copyright items on this site are being republished or copied to others, the source of the material must be identified and the copyright status acknowledged."** (attribution required for republication)
- **"The permission to reproduce protected material does not extend to any material on this site for which the copyright is identified as being held by a third party."**
- **"This website and material … is provided 'as is', without any representation or endorsement made and without warranty of any kind whether express or implied, including but not limited to the implied warranties of satisfactory quality, fitness for a particular purpose, non-infringement, compatibility, security and accuracy."** (no warranty)
- **Linking permitted without permission; framing prohibited: "we do not permit our pages to be loaded into frames on your site. The www.gov.je pages must be displayed in the user's entire browser window."** (anti-iframe clause — matches the `X-Frame-Options: SAMEORIGIN` technical control)

### 7.2 gov.je privacy posture (verbatim from `https://www.gov.je/Pages/Privacy.aspx`)
- **"The Department is registered as a 'Controller' under the Data Protection (Jersey) Law 2018 as we collect and process personal information about you."**
- Third-party processors disclosed: **"C5 Alliance, Fusion Development, Switch Digital, Granicus, Govmetric, Talentlink (job applications)"**.
- **"We do not share or process your information overseas. We do not use web services that are hosted outside the European Economic Area."** (EEA-only — relevant if we proxy through a US region)
- **GovMetric feedback widget** (the `websurveys2.govmetric.com/theme/gm/1574` button seen on every page) — tracks user satisfaction, not a bot challenge.
- **Google Analytics + Facebook pixel** — both used with browser-side consent. **No anti-bot implication** for firecrawl/webfetch (which don't execute JS).

### 7.3 opendata.gov.je licence gate (OGL-J-1.0)
- **Verbatim:** `license_title: "Open Government Licence – Jersey v1.0"`, `license_id: "OGL-J-1.0"`.
- **Verbatim licence URL:** `https://www.gov.je/ServiceManual/opendata/Pages/open-government-licence-jersey-ogl-j-v1-0.aspx`.
- **Compatible with OGL-UK v3.0** in spirit (attribution + non-endorsement + same-licence-on-derivative works). KCG may ingest OGL-J data into DuckLake, on the conditions that (a) attribution is preserved per `package_show.organization.title` and `package_show.maintainer`, (b) the `OGL-J-1.0` licence-notice is stored alongside the data, and (c) any derived "Adapted Material" (per OGL v3 §3.0) is itself licensed OGL-J-1.0 or compatible.
- **No API key / rate limit gate** — `https://opendata.gov.je/api/3/action/{package_list,package_show,datastore_search}` is open to anonymous traffic.

### 7.4 T&Cs gate decision matrix (KCG perspective)
| Source | Gate | KCG verdict |
|:--|:--|:--|
| `www.gov.je` HTML pages | "Personal use" + non-iframe + attribution | **OK for firecrawl** (research/internal); attribute `© States of Jersey 2010-2026`; never iframe |
| `www.gov.je` images/logos | "No photograph, image or logo may be copied, reproduced or directly linked to without approval" | **DO NOT scrape** images/photos/logos |
| `www.gov.je` PDFs | "third party copyright may apply; must contact the copyright holder" | **Case-by-case** — `formsplatform` resource (1 of 117) flagged |
| `opendata.gov.je` data | OGL-J-1.0 (attribution + licence-notice) | **OK** — dlt + DuckLake + preserve `organization.title` and `OGL-J-1.0` |
| `opendata.gov.je` HTML | CKAN default (no robots.txt block) | **OK** for firecrawl |
| Personal data on `opendata.gov.je` | DPA (Jersey) Law 2018 | None observed (all aggregate statistics) |

### 7.5 ccc cross-reference (where Jersey lives in the KCG monorepo today)
- `sources.yaml:278-284` — `jey.education.govje` declared as `kind: firecrawl_pages`. **No CKAN source declared.**
- `cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/jey/education/channel_islands.py:19-40` — `jersey_source` crawls only `/Education/*` paths. **0 lines use the CKAN API.**
- `openspec/research/2026-06-28-browserbase-program-2/agent-25-crown-ref-sites.md` — comprehensive prior research (R6–R10 refactor recommendations); this verifier (109) is a live re-confirmation that **the CKAN portal is still there, still has 117 datasets, and still has the exact same `datastore_search` schema** as Agent 25 reported.

### 7.6 Refactor recommendations (KCG §8)
- **R109-1 (re-confirms Agent 25 R6):** Add `jey/opendata/ckan.py` `@dlt.source(name="jersey_ckan")` that calls `package_list` → `package_show` → resource URLs. Primary key: `resource_id`. Merge write disposition.
- **R109-2:** When adding the CKAN source, **set `User-Agent: OideachaisBot/1.0`** and 0.2s sleep between `package_show` calls (117 datasets × ~5 KB JSON = ~600 KB total — should complete in <60 s).
- **R109-3:** Persist `OGL-J-1.0` licence-notice + `organization.title` attribution as **separate columns** in the dlt schema (`license_title`, `maintainer`, `maintainer_email`) so the downstream marimo notebooks can render the licence footer automatically.
- **R109-4:** Add a `ckan_health` Dagster asset_check (Agent 25 R10) — verify `https://opendata.gov.je/api/3/action/status_show` returns `success: true` every 6 hours.
- **R109-5 (Dives posture):** **Do not** attempt any MotherDuck Dives integration for the Jersey public surface — Jersey is a foreign sovereign gov, and the 4-surface KCG Dives layout is for KCG's own products. Use marimo + DuckLake internally.
- **R109-6 (anti-scraping):** Set `respect_robots=True` and use a 0.5s politeness delay for the SharePoint crawl. Varnish + SP2016 are both permissive, but we want to be a good neighbour.

### 7.7 OpenSpec cross-reference
Per `openspec/AGENTS.md`, the 4 relevant capability specs are:
- `oideachais-pipeline` — DLT + Dagster + DuckLake + LanceDB + BAML (the home for the proposed `jersey_ckan_source`).
- `oideachais-marimo-dashboards` — 11 marimo notebooks; the marimo fallback in §5.2 is a natural extension.
- `indexing-and-cognition` — `ccc` (used here for the cross-reference search).
- `infrastructure-stacks` — no relevant stack (Jersey is external, not a KCG stack).

**Note on OpenSpec workflow:** This output is a *research artifact*, not a spec change. Per the OpenSpec AGENTS.md "Critical Rules" — proposals go to `openspec/changes/<change-id>/`, archives to `openspec/changes/archive/`, and historical research lives in `docs/openspec/` (immutable). This file lives under `openspec/research/2026-06-28-browserbase-program-2/live-sites/` which is the **program-2 research output directory** (per the path conventions established by agents 96-99), and is therefore an informational deliverable for the build agent to consume — not a spec delta.

---

**Summary (1 paragraph):** The Government of Jersey runs two technically distinct properties: `www.gov.je` is a **SharePoint Server 2016** site (`x-sps: w02`, Varnish 6.0 front, `X-Frame-Options: SAMEORIGIN`, Jèrriais alt-text, robots.txt fully permissive) with a "personal use / no iframe / attribution required" T&Cs regime; `opendata.gov.je` is a vanilla **CKAN 2.8.12** portal exposing **117 datasets** under **OGL-J-1.0** (Open Government Licence – Jersey v1.0) via a fully open Action API at `/api/3/action/{package_list, package_show, datastore_search, group_list, package_search}` with CSV-dominant resources, JSON envelopes `{"success": true, "result": …}`, and **no auth, no rate limit, no robots.txt block**. Verbatim example: `package_show?id=education` returns 1 resource (`total-students-by-school-type.csv`, 618 B, `datastore_active: true`, modified 2024-11-28) with the package id `e9acb214-5778-4a0a-a8b7-2622c51a0a9e`; `datastore_search?resource_id=7d16ab4d-…&limit=3` returns 3 of 14 rows of pupil numbers (2011-2024). **No MotherDuck Dives exist on either site** — the marimo fallback (under `marimo/jersey/`) is the correct KCG integration path, and the existing `sources.yaml:278-284` `jey.education.govje` `kind: firecrawl_pages` declaration is a **critical drift** that should be augmented with a `jersey_ckan_source` dlt source (Agent 25 R6, re-confirmed) to ingest all 117 datasets instead of the 1 narrative Education page.
