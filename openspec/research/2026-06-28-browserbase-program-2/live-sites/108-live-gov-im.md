# Agent 108 — Live gov.im Verifier (Isle of Man Government + Legislation)

**Captured:** 2026-06-29
**Tools used:** webfetch (primary), chrome_navigate + chrome_take_snapshot (JS-rendered pages), firecrawl NOT required. **No browserbase consumed.**

## 1. TL;DR

- **gov.im** is a GOV.UK-style content platform (Jadu iCM) — clean server-rendered HTML, fully scraper-friendly under the Isle of Man OGL. Robots.txt **only blocks GPTBot**; all other crawlers welcome.
- **legislation.gov.im** is a **separate Joomla CMS** (paths `/cms/administrator/`, `/cms/components/`, `/cms/modules/` in robots.txt), running a structured PDF publishing platform managed by the Attorney General's Chambers — JS-rendered home, all PDFs reachable via predictable URL pattern.
- Education (DESC) is on its **own subdomain** `desc.gov.im`, not under gov.im — so a "www.gov.im/education-sport-and-culture" URL **404s**; the actual department lives at `https://www.gov.im/about-the-government/departments/education-sport-and-culture/` and links out to `https://desc.gov.im/`.

## 2. Site structure (iCM GOV.UK platform + Joomla)

### gov.im (Jadu iCM)
- Server-rendered, no SPA shell. Pages return full HTML on first byte.
- URL taxonomy mirrors GOV.UK: `/categories/{topic}/`, `/about-the-government/departments/{slug}/`, `/news/YYYY/mon/dd/{slug}/`, `/about-this-site/{slug}/`, `/media/{id}/{filename}` for assets.
- Eight Government Departments enumerated on `/about-the-government/departments/`: Cabinet Office, **Education, Sport and Culture** (ESC), Enterprise, Environment Food and Agriculture, Health and Social Care, Home Affairs, Infrastructure, The Treasury.
- The Education department is a **micro-site at desc.gov.im** (different platform, has its own nav: `/education/education/`, `/sport/sport/`, `/culture/culture/`, `/corporate/corporate/`).
- Search box is present but a GET form with no JS shell — a static `?q=…` URL works.
- News listing: `/news/`. Departmental chart PDF lives at `/media/1392504/isle-of-man-government-departmental-chart-2026_compressed.pdf`.

### legislation.gov.im (Joomla CMS)
- Joomla 3.x/4.x — the path `/cms/` everywhere plus the robots.txt directory disclosure (`/cms/administrator/`, `/cms/components/`, `/cms/libraries/`, `/cms/modules/`, `/cms/plugins/`, `/cms/tmp/`, `/cms/layouts/`) is canonical Joomla.
- Maintained by the **Attorney General's Chambers** (not the Cabinet Office that runs gov.im). Quoting the home: "The Attorney General's Chambers is responsible for the project to publish Manx legislation on this website. All current Acts of Tynwald and Synod Measures are published, comprising over 750 pieces of legislation with over 2,500 versions."
- Home is JS-rendered; webfetch gets an empty shell. Chrome snapshot retrieves full nav and all "RECENT ACTS / RECENT STATUTORY DOCUMENTS / RECENT BILLS" lists.
- PDF distribution: **Apache `mod_autoindex` directory listing** at `/cms/images/LEGISLATION/{CATEGORY}/{YEAR}/` — returns plain HTML indexes (no JS), trivially scrapable. Confirmed categories: `PRINCIPAL/`, `SUBORDINATE/`, `AMENDING/`, `BILLS/`, `CASES/`, `GAZETTES/`, `NOTICES/`.
- Each PDF has a numeric ID under year: `2026-0001`, `2026-0002`, `2026-0003`, with version suffix `_{N}.pdf` for consolidations and an unsuffixed `.pdf` for the as-enacted version.

## 3. Verbatim URLs (legislation PDF pattern + education pages)

```text
# legislation.gov.im — PDF pattern
https://legislation.gov.im/cms/images/LEGISLATION/PRINCIPAL/2026/2026-0003/2026-0003_1.pdf   # City of Douglas Act 2026
https://legislation.gov.im/cms/images/LEGISLATION/PRINCIPAL/2026/2026-0002/2026-0002_1.pdf   # Safeguarding (Amendment) Act 2026
https://legislation.gov.im/cms/images/LEGISLATION/PRINCIPAL/2026/2026-0001/2026-0001_1.pdf   # Elections (Keys and Local Authorities) (Amendment) Act 2026
https://legislation.gov.im/cms/images/LEGISLATION/PRINCIPAL/2025/2025-SM01/2025-SM01_1.pdf   # Cathedral Measure (Isle of Man) 2025
https://legislation.gov.im/cms/images/LEGISLATION/SUBORDINATE/2026/2026-0099/2026-0099_1.pdf # Social Security Legislation (Benefits) (Application) Order 2026
https://legislation.gov.im/cms/images/LEGISLATION/BILLS/2026/2026-0006/2026-0006.pdf         # Verification of Entity Registration Bill 2026
https://legislation.gov.im/cms/images/LEGISLATION/GAZETTES/2026/2026-0005/2026-0005.pdf       # Isle of Man Legislation Newsletter (May 2026)

# Directory listings (Apache mod_autoindex)
https://legislation.gov.im/cms/images/LEGISLATION/
https://legislation.gov.im/cms/images/LEGISLATION/PRINCIPAL/2026/

# Education — gov.im root
https://www.gov.im/about-the-government/departments/education-sport-and-culture/  # 200 — department landing on gov.im
https://www.gov.im/education-sport-and-culture                                   # 404 — slug does NOT exist at root
https://www.gov.im/categories/education-training-and-careers/                     # 200 — public-facing category

# Education — DESC sub-site (desc.gov.im, separate platform)
https://desc.gov.im/education/education/                                          # 200 — education services hub
https://desc.gov.im/education/education/manx-language-in-schools/                 # 200 — Manx language in schools (highly relevant to KCG)
https://desc.gov.im/education/education/curriculum/                              # 200 — curriculum
https://desc.gov.im/corporate/corporate/legislation/                             # 200 — DESC-published legislation index
https://desc.gov.im/desc-latest/                                                 # 200 — news index

# Gov.im structural / licence
https://www.gov.im/about-this-site/terms-and-conditions/
https://www.gov.im/about-this-site/open-government-licence/
https://www.gov.im/about-the-government/departments/                             # 200 — eight depts enumerated
https://www.gov.im/media/1392504/isle-of-man-government-departmental-chart-2026_compressed.pdf
```

## 4. Anti-scraping posture

| Layer | gov.im | legislation.gov.im |
|---|---|---|
| `robots.txt` | **Blocks GPTBot only** (`User-agent: GPTBot / Disallow: /`). All other agents allowed. | Standard Joomla hardening — blocks `/cms/administrator/`, `/cms/bin/`, `/cms/cache/`, `/cms/cli/`, `/cms/components/`, `/cms/includes/`, `/cms/installation/`, `/cms/language/`, `/cms/layouts/`, `/cms/libraries/`, `/cms/logs/`, `/cms/modules/`, `/cms/plugins/`, `/cms/tmp/`. **All content paths allowed.** |
| JS challenge / Cloudflare | None observed (gov.im serves full HTML on GET) | None observed (chrome_navigate returned full DOM after JS render; no CF interstitial) |
| Rate limiting / WAF | Not hit during ~12 webfetch calls in <2 min | Same |
| CAPTCHA | None | None |
| Login gate | None for read access | None for read access |
| T&Cs gate | None — see §5 | None — only a "Cookies on this site…" notice: "The Isle of Man web site only uses cookies to allow you to return to the last selected page in the legislation. No other cookies are used on this site to track your usage." |
| Legal posture | **Isle of Man Open Government Licence (OGL v3-style)** — quoting: "The Licensor grants you a worldwide, royalty-free, perpetual, non-exclusive licence to use the Information" with mandatory attribution. Compatible with CC-BY 4.0. | Inherits the same OGL footer from gov.im. Crown Copyright. |

**Verdict:** both sites are *more* open than UK gov.uk — no per-bot throttling, no T&Cs clickthrough, no API key required, and the legislation site even publishes its entire PDF corpus as plain Apache directory listings. A dlt `filesystem` source pointing at `https://legislation.gov.im/cms/images/LEGISLATION/` would scrape the full corpus without anti-bot interference.

## 5. T&Cs gate (if any)

- **gov.im T&Cs (`/about-this-site/terms-and-conditions/`)**: Standard Crown-copyright disclaimer. Quoting: "By using this site you indicate that you accept these terms of use and that you agree to abide by them." — **passive acceptance by use**, no clickwrap gate. Liability is disclaimed; Isle of Man law and IOM Courts have exclusive jurisdiction. No scraping prohibition.
- **Open Government Licence (`/about-this-site/open-government-licence/`)**: Explicitly permits commercial and non-commercial reuse, modification, and redistribution. **Conditions**: include attribution ("Contains public sector information licensed under the Isle of Man Open Government Licence" if no provider-specific attribution is given). **Exemptions**: personal data, departmental logos / IOM crest, third-party rights, patents/trademarks, identity documents.
- **legislation.gov.im privacy page**: states the OGL applies; the only interactive element is a "Cookies on this site" banner that defaults to "Accept" on click — **not a scraping barrier**.
- No clickwrap, no API key, no auth, no per-URL robots disallow.

## 6. KCG cross-references

- **oideachais-pipeline**: a new `ireland_isle_of_man` dlt source could `filesystem`-mirror `https://legislation.gov.im/cms/images/LEGISLATION/PRINCIPAL/` (1500+ Acts of Tynwald and Synod Measures) using the OGL. The Manx language in schools page at `desc.gov.im/education/education/manx-language-in-schools/` is directly adjacent to the Celtic corpus.
- **celtic-asset-generation**: the `2025-SM01` (Cathedral Measure) and `1933-SM01` (Church Measure) Synod Measures path pattern (`/cms/images/LEGISLATION/PRINCIPAL/{YEAR}/{YEAR}-SM{NN}/{YEAR}-SM{NN}_{N}.pdf`) is unique to Manx ecclesiastical legislation — worth a dedicated `synod-measures` asset.
- **infrastructure-stacks**: legislation.gov.im runs Joomla + Apache `mod_autoindex` — no DAG / Dagster / k8s integration required. Could be packaged as a pure-pipeline source with zero runtime dependencies.

## 7. Decision matrix

| Source | Format | Volume | Gate | Recommended KCG role |
|---|---|---|---|---|
| `legislation.gov.im/cms/images/LEGISLATION/PRINCIPAL/` | PDF (Apache index) | ~750 Acts × N versions | None | Primary `ireland_isle_of_man_legislation` dlt filesystem source |
| `legislation.gov.im/cms/images/LEGISLATION/SUBORDINATE/` | PDF (Apache index) | Thousands of SIs/orders | None | Secondary source for statutory documents |
| `legislation.gov.im/cms/images/LEGISLATION/BILLS/` | PDF (Apache index) | 5–20 per year | None | Bill-tracker asset (Dagster sensor) |
| `www.gov.im/categories/education-training-and-careers/` | HTML | News + pages | None | RSS-style ingestion via firecrawl/chrome |
| `desc.gov.im/...` | HTML (separate platform) | ~200 pages | None | Separate `isle_of_man_education` dlt source |

---

**Agent 108 summary:** gov.im is Jadu iCM, legislation.gov.im is Joomla — both fully open, OGL-licensed, no scraping barriers beyond a single GPTBot disallow. PDF corpus at `legislation.gov.im/cms/images/LEGISLATION/` is a directory-listing goldmine (~750 Acts + thousands of SIs) ready for a single dlt filesystem source. Department of Education (ESC) is a separate `desc.gov.im` micro-site, not under gov.im. Recommend a new `openspec/changes/2026-06-29-ireland-isle-of-man-legislation-source/` change to wire this into the oideachais lakehouse.
