# Lower Socioeconomic Piracy: A Budget Media Stack

> An honest look at the cheapest, most reliable consumer-grade media stack circa 2026.
> Streaming-service fragmentation has made keeping up with Netflix + Disney+ + Max +
> Paramount+ + Apple TV+ + Prime + Crunchyroll cost more per month than most people's
> grocery bill. This document describes the de-facto replacement that the rest of the
> internet has converged on, and how it works.

---

## TL;DR — The Stack

| Layer | Service | Role | Cost (approx.) |
|---|---|---|---|
| **Browser foundation** | **Firefox + uBlock Origin** | Mandatory before touching any of the sites below | Free |
| Player / UI | **Stremio** | Open-source media centre (Netflix-like front-end) | Free |
| Source / scraper | **Torrentio** (Stremio addon) | Aggregates torrent indexers, hands magnets to the debrid | Free |
| Delivery / cloud cache | **Real-Debrid** | Cached torrents → direct HTTPS streams (video *and* comics via RDT-Client) | ~€3/month (16 days) → ~€4/month (180 days bulk) |
| Comics (parallel stack) | **Mylar3** + GetComics DDL | Sonarr-style automation for comic series (CBR/CBZ), native GetComics support | Free, self-hosted |
| Books / journals | **libgen.li + Z-Library** | World's largest free book and academic-paper repositories | Free |

**Total monthly cost: ~€3–4** for the entire video catalogue of recorded human
cinema and television **plus** a self-hosted comics library **plus** essentially
every book and academic paper ever published — the same one Real-Debrid sub
covers the video and comics layers; the rest is free.

---

## 0. Prerequisite — Firefox + uBlock Origin

**Do not visit any of the sites in this document from Chrome, Safari, or a mobile
browser without an ad blocker.** The sites described here — getcomics.org,
readcomiconline.ru / readcomiconline.li, libgen.li, z-library.bz, the torrent
indexers Torrentio scrapes — survive on aggressive, often malicious advertising:
fake "download" buttons, redirect chains to scam pages, pop-unders, cryptominers,
drive-by malware. **uBlock Origin (uBO) on Firefox neutralises essentially all of
it.** This is non-negotiable.

### Why specifically Firefox + uBlock Origin (as of 2026)

The ad-blocking landscape changed materially in the last two years. The
[ublockorigin.com](https://ublockorigin.com/) homepage (updated January 2026)
states it directly:

| Browser | uBlock Origin status |
|---|---|
| **Firefox (recommended)** | Full uBO works. Mozilla committed to keeping Manifest V2 support. |
| **Brave** | Full uBO works. Brave engineered workarounds. |
| Chrome / Chromium | **Full uBO removed from the Chrome Web Store in late 2024. All remaining MV2 extensions permanently disabled by Google in July 2025.** Only **uBO Lite** is available — and Lite cannot do cosmetic filtering by default, has hard rule limits (declarativeNetRequest API), no scriptlet injection by default, and no dynamic per-site filtering. It is meaningfully weaker on exactly the kinds of sites this document discusses. |
| Edge | Full uBO currently works but is expected to follow Chrome's deprecation path since Edge is Chromium-based. |
| Safari / iOS WebKit | **Not supported since Safari 13.** Apple's content-blocker API (`WKContentRuleList`) is sandboxed, capped at 150,000 rules, and cannot do scriptlet injection, dynamic filtering, or response-body filtering. The full uBO simply cannot exist on Safari/iOS even if the author wanted to ship it. Every iOS browser (Chrome iOS, Firefox iOS, Brave iOS, etc.) is forced by App Store policy to use WebKit underneath, so this limitation extends to every browser on iPhone and iPad. |

The two failure modes have **different causes**:

- **Safari/iOS** is *technically* unable to host a real content blocker. Apple's
  argument is that the sandbox protects users; the side effect is that no
  third-party blocker can match uBO's capabilities on the platform.
- **Chrome** is *politically* unwilling. Google's Manifest V3 transition was
  positioned as a security improvement, but the practical outcome is that
  Google — the world's largest advertising company — has restricted the
  capabilities of the most effective ad blocker on the world's most-used
  browser. uBO's author Raymond Hill maintained throughout that the Lite
  version is a worse product, not a "modernised" one.

The conclusion is uncomfortable but simple: **if you want a fully functional ad
blocker in 2026, you need Firefox** (or Brave). Firefox is the only mainstream
browser whose vendor's commercial interests are not in direct conflict with
content blocking.

### Why this matters for everything else in this document

- **getcomics.org** serves real CBR/CBZ downloads but the page is saturated with
  ad networks. The actual download button is often surrounded by 3–5 fake ones.
  uBO removes them all.
- **readcomiconline.ru / readcomiconline.li** are excellent free in-browser
  comic readers but the page DOM is full of pop-under triggers, redirect
  iframes, and "your computer has a virus" overlays. Without uBO they are
  basically unusable; with uBO they are quiet, clean reading apps.
- **libgen.li and z-library.bz** are comparatively clean, but mirrors and clone
  domains run by impersonators are not — uBO's malicious-domain filter
  (URLhaus) blocks the worst of them outright.
- **Real-Debrid, Stremio, Torrentio** themselves are clean; uBO is still
  recommended because it speeds up every other site you visit in a day.

### Universal benefits of uBO (not just on piracy sites)

uBO is the single highest-impact change you can make to your browsing
experience. From the official site and project README:

- **YouTube** — blocks all video pre-roll, mid-roll, and overlay ads, full
  effectiveness on Firefox. (Chrome's uBO Lite is noticeably weaker here and
  YouTube actively fights back; Firefox + full uBO is still the only reliable
  configuration.) Also removes Shorts shelf, "people also watched" injections,
  and home-page ad rows if you enable the appropriate annoyance lists.
- **Twitch** — blocks in-stream ads.
- **News sites** — kills paywalls that rely on client-side overlays, removes
  newsletter pop-ups, cookie banners, "related stories" chumboxes.
- **Reddit** — removes promoted posts and sidebar ads.
- **Privacy** — blocks tracker scripts (Google Analytics, Facebook Pixel,
  hotjar, segment, etc.) on every site you visit by default.
- **Performance** — pages load measurably faster and use less CPU/RAM. A 2020
  [MDPI energy-conservation study](https://www.mdpi.com/2227-7080/8/2/18/htm)
  cited on the uBO site estimated the global savings from ad blocking at over
  **$1.8 billion/year** in energy alone.
- **Safety** — the default lists include the
  [Online Malicious URL Blocklist (URLhaus)](https://gitlab.com/malware-filter/urlhaus-filter#malicious-url-blocklist),
  which blocks known malware and phishing domains before they can load. This
  is the part that matters when navigating fringe sites.
- **No business model conflict** — uBO is GPL-3.0, has no "acceptable ads"
  programme (unlike AdBlock Plus), and **refuses donations** as a matter of
  policy. Raymond Hill instead asks users to support filter-list maintainers.

### Install (one minute)

1. Install Firefox: [mozilla.org/firefox](https://www.mozilla.org/firefox/).
2. Install uBlock Origin from
   [addons.mozilla.org/addon/ublock-origin](https://addons.mozilla.org/addon/ublock-origin/).
3. Open the uBO toolbar icon → dashboard → *Filter lists* tab. The defaults
   (EasyList, EasyPrivacy, Peter Lowe's, uBO filters, URLhaus) are already
   tuned correctly. Optionally enable:
   - **Annoyances → AdGuard Annoyances** (kills cookie banners and newsletter
     pop-ups).
   - **Annoyances → uBlock filters – Annoyances** (kills overlay videos, social
     widgets).
   - **Regions, languages → uBlock filters – Badware risks** (extra blocklist
     for shady file-sharing sites — strongly recommended given the rest of
     this document).
4. That is it. Do not install any other ad blocker alongside uBO; per the
   project README, stacking blockers actively breaks uBO's anti-anti-blocker
   features.

---

## 1. Stremio — The Front-End

**What it is:** An open-source media centre. Think of it as a Netflix-style UI with no
content of its own — content arrives via *addons*. The official desktop, Android,
Android TV, and LG webOS apps are first-class; a Stremio Web client at
`web.stremio.com` works for iOS / iPadOS where the native app is restricted.

**Key facts** (from the official site):

- Available on Windows, macOS, Linux, Android, Android TV, LG TV, web.
- 4K HDR playback supported.
- Library/progress syncs across devices once you sign in.
- Open-source: [stremio-shell](https://github.com/stremio/stremio-shell) and the
  [Stremio GitHub org](https://github.com/Stremio).
- **Addons run server-side** — they expose a manifest to the player, so they cannot
  execute code on your device. This is the basis of Stremio's safety model.
- Plays magnet links, raw HTTP URLs, and torrent files via drag-and-drop.
- Chromecast supported from desktop and Android.
- Guest mode signup is available if you do not want an account.

**Web vs native:** `web.stremio.com` requires the user to install a local *streaming
server* helper for many addons to work — it shows the "Streaming server is not
available" banner until you do. The desktop app bundles this. For TV/laptop use,
install the native app. For iPhone/iPad, the web client is the only practical option.

**Install:** [stremio.com/downloads](https://www.stremio.com/downloads)

---

## 2. Torrentio — The Source Addon

`https://torrentio.strem.fun/configure` is the configuration page for a Stremio addon
that aggregates an enormous list of public torrent indexers and turns them into
clickable stream options on every movie / series page in Stremio.

**Indexers it scrapes** (verbatim from the configure page):

> YTS, EZTV, RARBG, 1337x, ThePirateBay, KickassTorrents, TorrentGalaxy, MagnetDL,
> HorribleSubs, NyaaSi, TokyoTosho, AniDex, Rutor, Rutracker, Comando, BluDV,
> MicoLeaoDublado, Torrent9, ilCorSaRoNeRo, MejorTorrent, Wolfmax4k, Cinecalidad,
> BestTorrents.

**Coverage:** Movies, Series, Anime, plus a generic "Other" bucket.

**Configuration knobs that matter:**

- **Sorting:** by quality then seeders / by quality then size / by seeders / by size.
- **Priority foreign language:** 40+ language flags — useful for native-audio
  preference on dubs.
- **Exclude qualities/resolutions:** can blacklist CAM / Screener / Unknown /
  3D / 480p etc. *Always exclude CAM and Screener.*
- **Max results per quality** and **Video size limit** — keep the UI clean.
- **Debrid provider:** the critical field. Options are:
  `None`, `RealDebrid`, `Premiumize`, `AllDebrid`, `DebridLink`, `EasyDebrid`,
  `Offcloud`, `TorBox`, `Put.io`.

**Without a debrid configured**, Torrentio returns raw magnet links which Stremio
will torrent peer-to-peer on your own connection — slow, exposes your IP to the
swarm, and is the fastest route to an ISP letter. **With a debrid configured**,
Torrentio asks the debrid service if the torrent is already cached on their servers
and, if so, returns a direct HTTPS URL that streams instantly. This is the entire
point of the stack.

**Install URL:** `stremio://torrentio.strem.fun/manifest.json` — clicking
`INSTALL` from the configure page after pasting your debrid API key wires it all
together.

---

## 3. Real-Debrid — The Delivery Layer

**What it is:** A French "unrestricted downloader" service. They describe themselves as:

> *An unrestricted downloader that allows you to quickly download files hosted on the
> Internet or instantly stream them into an innovative web player.*

In practice, Real-Debrid runs a large pool of seedboxes that pre-download popular
torrents into their cache. When you (via Torrentio) ask "do you have this magnet?",
the answer is almost always yes for anything mainstream, and they hand you a direct
HTTPS URL backed by their gigabit infrastructure. The user never touches the
BitTorrent swarm — only an HTTPS GET request to a French CDN.

**Three selling points** (verbatim from real-debrid.com homepage):

- *Economic* — "A lower price than the majority of file hosters while still offering
  more features and hosters."
- *Speed* — removes the artificial waits and throttling of free file hosters.
- *Many hosters* — wide range of unrestricted file hosts in addition to torrents
  (1fichier, Rapidgator, Mega, MediaFire, Uptobox, Fikper, etc. — the full list is
  on their homepage and is enormous).

**Pricing (verify before paying):** Roughly €3 for 15 days, ~€4/month effective rate
on a 180-day bundle. Pricing is on the Premium page; check
[real-debrid.com/premium](https://real-debrid.com/premium) for current numbers.

**API key:** Once you have a Premium account, generate the API key at
[real-debrid.com/apitoken](https://real-debrid.com/apitoken) — this is what you paste
into Torrentio's "RealDebrid API Key" field.

**Why this is the magic:**

- No torrent client running locally.
- No BitTorrent traffic on your home connection — just HTTPS to a CDN, the same as
  Netflix.
- Stream starts in 1–2 seconds, not minutes.
- 4K HDR works out of the box, with seeking, because it is a direct file URL.
- Your home IP never enters a swarm, so the standard DMCA/ISP-letter risk is removed.

**Caveats:**

- Real-Debrid is a French company; legal exposure for the *user* depends on local
  jurisdiction. Pay attention to your own country's laws regarding the consumption
  of copyrighted content via unauthorised channels.
- If a torrent is not already in their cache, Torrentio will mark it as a "download
  to debrid" link rather than an instant stream. For obscure/niche content this can
  take a few minutes the first time someone in the world requests it.
- One Real-Debrid account is officially one user. Sharing the API key across many
  devices/people can get the account flagged.

---

## 4. Putting It Together (10-Minute Setup)

1. Install Stremio: [stremio.com/downloads](https://www.stremio.com/downloads).
2. Create a Stremio account (or use guest mode).
3. Buy a Real-Debrid premium subscription at [real-debrid.com](https://real-debrid.com).
4. Get your Real-Debrid API token: [real-debrid.com/apitoken](https://real-debrid.com/apitoken).
5. Open [torrentio.strem.fun/configure](https://torrentio.strem.fun/configure).
6. Set:
   - **Debrid provider:** RealDebrid
   - **RealDebrid API Key:** paste your token
   - **Sorting:** *By quality then seeders*
   - **Exclude qualities/resolutions:** tick `CAM`, `Screener`, `Unknown`
   - Leave the rest at defaults
7. Click **INSTALL** — Stremio will open and ask to confirm the addon.
8. Pick any movie or series episode in Stremio. The stream list should show entries
   prefixed with `[RD+]` (Real-Debrid cached). Pick a 1080p / 4K entry. It should
   begin playing within ~2 seconds.

**Recommended additional addons to install alongside Torrentio:**

- **Cinemeta** (default) — IMDb metadata.
- **OpenSubtitles v3** — subtitles in any language, including Irish where available.
- **Trakt** — sync watchlist/history with trakt.tv for cross-device progress.

---

## 5. Comics — Mylar3

**Repo:** [github.com/mylar3/mylar3](https://github.com/mylar3/mylar3) — 1.4k stars,
GPL-3.0, Python 3, actively maintained (last release v0.8.3, August 2025).

**What it is:** The Sonarr/Radarr equivalent for comic books. You curate a watchlist
of series; Mylar3 monitors them and automatically grabs new issues from your
configured providers, then sorts, renames, and metatags them into a clean library.

**Feature highlights** (from the official README):

- Cross-platform — Windows, Linux, macOS, Raspberry Pi.
- Download client support: **SABnzbd, NZBGet** (Usenet), and **various torrent
  clients**, plus a generic blackhole.
- Multiple **Newznab** indexers, a raw indexer, and direct-download (DDL) support
  including GetComics-style sources.
- Pull-list view up to 4 weeks ahead, plus historical months — see what is coming
  out and queue it in advance.
- TPBs (Trade Paperbacks) and GNs (Graphic Novels) supported for monitoring and
  post-processing.
- **Existing-library scan** — point it at an existing collection of CBR/CBZ files
  and it will fill in the gaps automatically.
- Failed-download handling — auto-retries with a different release if one fails.
- Configurable file/folder renaming.
- Metatagging via an embedded modified `ComicTagger`, either during post-processing
  or in a manual batch run.
- Generates `series.json` sidecar files so downstream readers (Komga, Kavita,
  Mylar's own UI, mobile readers) all see the same metadata.
- Story-arc tracking — group issues into reading-order arcs.
- Push notifications on snatch / download.

**Where Mylar3 fits in the same household:**

You do **not** need Usenet for comics. Mylar3 has first-class support for
**GetComics DDL** (direct-download) and that single source alone covers the vast
majority of mainstream and back-catalogue comics. No paid indexer, no SABnzbd, no
extra subscription. The recommended pairing is:

- **Primary source: GetComics DDL** — enabled directly in Mylar3 under
  *Settings → Search Providers → DDL (GetComics)*. Mylar3 ships with this built in,
  scrapes [getcomics.org](https://getcomics.org), and downloads CBR/CBZ files
  straight to your library. Most series, single issues, TPBs, and OmniBus volumes
  resolve on the first try.
- **Fallback / torrent path (optional): Real-Debrid + RDT-Client.**
  [`RDT-Client`](https://github.com/rogerfar/rdt-client) is a small Docker service
  that exposes a qBittorrent-compatible API to Mylar3 (and Sonarr/Radarr/etc.) but
  routes everything through your existing Real-Debrid account. You point Mylar3 at
  RDT-Client as a "torrent client", paste a torrent indexer (or a Newznab/Jackett
  proxy), and any magnet Mylar3 grabs is sent to Real-Debrid, cached, and pulled
  back as a clean HTTPS download — the same trick the video stack uses. **One
  Real-Debrid subscription powers both video and comics.**
- **Skip Usenet entirely** unless you already have a Usenet provider — between
  GetComics DDL and the optional Real-Debrid fallback there is nothing left for it
  to do.
- **Storage:** local NAS or a directory on the same machine.
- **Reader:** [Komga](https://komga.org) or [Kavita](https://www.kavitareader.com) —
  both are self-hosted comic servers with web + mobile readers, and both consume
  Mylar3's `series.json` natively.

### No-setup alternative — in-browser comic readers

If you do not want to self-host anything, two web readers cover essentially the
entire DC + Marvel + indie catalogue with a browser-only reading experience:

- **[readcomiconline.ru](https://readcomiconline.ru) / [readcomiconline.li](https://readcomiconline.li)** —
  same operator, different mirror domains. Search any series, click an issue,
  read it in a built-in reader. No download, no account required.

**Warning:** these sites are *unusable* without uBlock Origin. The pages
trigger pop-unders, "your device has been infected" overlays, and fake-VPN
redirect chains the moment you click anywhere. **With uBO on Firefox the site
is silent and the reader works flawlessly.** This is the single best
demonstration of why §0 of this document exists. If you find yourself fighting
pop-ups on `readcomiconline.*`, you have either not installed uBO or you are
not using Firefox — go back and fix that first.

**Install (Docker, recommended):**

```bash
docker run -d \
  --name=mylar3 \
  -e PUID=1000 \
  -e PGID=1000 \
  -e TZ=Europe/Dublin \
  -p 8090:8090 \
  -v /path/to/config:/config \
  -v /path/to/comics:/comics \
  -v /path/to/downloads:/downloads \
  --restart unless-stopped \
  lscr.io/linuxserver/mylar3:latest
```

Then open `http://localhost:8090` and walk the setup wizard. Documentation at
[mylarcomics.com](https://mylarcomics.com/) and community support at
[forum.mylarcomics.com](https://forum.mylarcomics.com/) /
[Discord](https://discord.gg/6UG94R7E8T).

---

## 6. Books, Textbooks, and Academic Papers — libgen.li + Z-Library

Video and comics are the visible top of the iceberg. The thing that
*disproportionately* matters for someone shut out of paid access is **books and
academic journals**, where a single textbook can run €60–120, a paywalled
journal article can run €40 for a 24-hour rental, and a full subscription to
the Big Five academic publishers is priced for university libraries, not
individuals. Two services have made this a non-issue for a generation of
self-taught learners, students in countries without university access, and
researchers outside institutional walls.

### Library Genesis (libgen)

**Current primary domain:** [libgen.li](https://libgen.li/)
**Active mirrors:** `libgen.li`, `libgen.vg`, `libgen.la`, `libgen.bz`,
`libgen.gl`
**Dead/seized mirrors (do not use):** `libgen.lc`, `libgen.gs`

Library Genesis is an open repository of books, scientific articles, comics,
fiction, magazines, and academic standards. As of 2026 the site exposes a
search across:

- **Topics:** Libgen (general non-fiction & textbooks), Comics, Fiction,
  Scientific Articles, Magazines, Russian Fiction, Standards.
- **Object types:** Files, Editions, Series, Authors, Publishers, Works.
- **Search fields:** Title, Author, Series, Year, Publisher, ISBN.
- **Bibliographic integration:** verbatim from the libgen.li front page —
  *"20.10.2025 Added bibliography search in local databases of the Worldcat.org
  and the Russian State Library"*, *"02.09.2025 Bibliography search from
  Openlibrary.org added to loader"*. So an ISBN that does not directly hit a
  libgen file can still resolve via OCLC/OpenLibrary metadata.
- **Database dumps:** *"21.09.2025 Added database dumps by sections"* — the
  entire catalogue is downloadable as section-by-section dumps. Libgen is
  designed to be irreducibly distributed; you can mirror it yourself.

Coverage is, in practice, the majority of every English-language textbook ever
printed, plus several million Sci-Hub-sourced academic papers, plus the
Russian, German, French, and Chinese non-fiction back catalogues.

### Z-Library

**Current primary domain:** [z-library.bz](https://z-library.bz/)
**Active community mirror landing page:** the .bz domain lists current working
mirrors — at time of writing: `z-library.im`, `z-lib.gs`, `z-lib.fm`. Domains
rotate; the landing page is the authoritative source.

Z-Library (often `zlib`, `z-lib`) describes itself on its project homepage as:

> *Your gateway to knowledge and culture. Accessible for everyone.*

The numbers it publishes:

- **~15,000,000 books** in EPUB, PDF, MOBI, AZW, AZW3, FB2, DJVU, DJVU, LIT,
  CBZ, RTF, TXT formats (Kindle-compatible).
- **~80,000,000 articles** (scientific papers, journal articles, conference
  proceedings).
- **~250,000 booklists** — curated reading lists by community members,
  searchable and forkable.
- **24 top-level categories** covering fiction, nonfiction, children's
  literature, medical, history, mathematics, law, economics, business,
  religion, programming, and academic subjects.
- **Languages:** English, Russian, Chinese, Japanese, Korean, Spanish, French,
  Arabic, Italian, Portuguese, Urdu, Pashto, Turkish, German, Malay, and
  others. This is one of the few services where a Welsh-, Tamil-, or Vietnamese-
  speaking learner can actually find first-language educational material.

**Z-Library was not shut down.** The 2022 FBI domain seizure took two domains
(`z-lib.org` and `b-ok.cc`); the project itself rebuilt on rotating domains
and a TOR-aware desktop launcher. From the current `z-library.bz` homepage:

> *Contrary to popular belief, Z-Library (Z-Lib) has not shut down and is still
> working. You just need to find the right Z-Lib website, as there are plenty
> of copy-cat websites and even fake sites out there.*

Use the `.bz` landing page or the official desktop app to find the current
working domain. Avoid randomly Googled "Z-Library" results — the impersonator
sites are aggressive and full of malware. **(This is the single highest-payoff
use case for uBO's URLhaus filter.)**

**Z-Library Desktop App:** Windows / macOS / Linux launchers exist that route
through Tor automatically; this both insulates you from domain blocks and
provides plausible-deniability traffic patterns. Available from
[go-to-library.sk](https://go-to-library.sk/#desktop_app_tab).

### What to use libgen vs Z-Library for

| Need | Better choice |
|---|---|
| Specific textbook, you have the ISBN | **libgen.li** — ISBN search is excellent |
| English-language popular fiction | Either; **Z-Library** has nicer UX and better cover art |
| Academic paper / journal article | **libgen.li** (Scientific Articles topic) or [sci-hub.se](https://sci-hub.se) directly |
| Non-English educational material | **Z-Library** — vastly better language coverage |
| Audiobook / multi-format need | **Z-Library** — exposes AZW3, MOBI, EPUB, PDF for the same title |
| You want a TOR-routed desktop app | **Z-Library** — has an official one |
| You want to mirror the whole archive | **libgen.li** — section-by-section database dumps |
| You hit a "this title was removed" page | Try the other one — overlap is partial but the union covers almost everything |

### Practical workflow

1. Browse to the site on Firefox (with uBO active — *always*).
2. Search by title / author / ISBN / DOI.
3. Click the result, choose a format (EPUB is best for fiction; PDF for
   textbooks with diagrams; DJVU for old scans).
4. Download. The file is yours; back it up. For books, [Calibre](https://calibre-ebook.com)
   is the de-facto open-source library manager. For papers,
   [Zotero](https://www.zotero.org) handles citations alongside the PDF.

---

## 7. Architecture at a Glance

```
                      ┌──────────────────────┐
                      │       Stremio        │  (your TV / phone / laptop)
                      │  (player + library)  │
                      └──────────┬───────────┘
                                 │  addon manifest
                                 ▼
                      ┌──────────────────────┐
                      │      Torrentio       │  (server-side scraper)
                      │  scrapes 23 indexers │
                      └──────────┬───────────┘
                                 │  "is this magnet cached?"
                                 ▼
                      ┌──────────────────────┐
                      │     Real-Debrid      │  (French CDN/seedbox)
                      │  cache + HTTPS srv   │
                      └──────────┬───────────┘
                                 │  direct HTTPS, like Netflix
                                 ▼
                              YOUR TV



           ── separate, parallel stack for comics ──

   ┌─────────────┐ queues  ┌──────────────────┐ DDL/HTTPS  ┌──────────┐
   │   Mylar3    ├────────►│ GetComics (DDL)  ├───────────►│  Komga   │
   │ (watchlist) │         │  ── or ──        │            │  /Kavita │
   │             │         │ RDT-Client ──► RD│            │          │
   └─────────────┘         └──────────────────┘            └──────────┘


           ── browser-only stack for books / papers ──

   ┌─────────────┐         ┌──────────────────┐  EPUB/PDF  ┌──────────┐
   │  Firefox    ├────────►│ libgen.li        ├───────────►│ Calibre  │
   │  + uBO      │         │  or              │            │ /Zotero  │
   │             │         │ z-library.bz     │            │          │
   └─────────────┘         └──────────────────┘            └──────────┘
```

---

## 8. The Ethics — Why This Document Exists

This section is not technical. Skip it if the rest of the document is enough.
It exists because the framing of "piracy" in mainstream discourse is so
poisoned by a century of rights-holder lobbying that it is worth saying clearly
what the moral situation actually is.

### Copying is not theft

The legal fiction that copying a file is equivalent to stealing a physical
object was invented in the late 1970s by the US Motion Picture Association as a
rhetorical strategy. It is not how property has been understood for any of the
preceding 5,000 years of human civilisation, and it is not how copyright law
itself defines the act — copyright infringement and theft are distinct
offences with distinct elements, distinct penalties, and distinct remedies,
and have been throughout the entire history of the statute.

When a person streams a film through Real-Debrid, no original is removed. The
rights-holder retains exactly the same number of copies, the same master, the
same distribution rights, and the same ability to sell to everyone else. The
physical universe has one more copy in it than it did a minute ago. The
appropriate analogy is closer to *singing a song someone else wrote in the
shower* than to *stealing their car* — both are technically copyright
violations in the strictest reading of the statute, and both are non-rivalrous
acts that cost the rights-holder nothing absent a separate counterfactual
sale.

The "lost sale" counterfactual is the entire moral argument the industry leans
on, and for the population this document is aimed at, **it is empirically
false**. A nursing student in Ireland cannot afford the €110 list price of
*Robbins Basic Pathology*. A teenager whose family is on social welfare
cannot afford a €15.99/month Disney+ subscription on top of food, rent, and
ESB. A researcher in Nigeria cannot afford a €38 paywalled Elsevier article.
**These people are not lost sales.** They are people who would simply not
read the book, not watch the film, not learn the science. The rights-holder
loses nothing they would otherwise have gained. The reader, viewer, or
student gains everything.

### The right to read

There is a well-developed body of thought on this — Cory Doctorow's writing on
*"adversarial interoperability"*, Aaron Swartz's *"Guerilla Open Access
Manifesto"*, the Library Genesis project's own foundational documents, and the
Z-Library community's "knowledge accessible for everyone" framing all converge
on the same point: in an age where the marginal cost of distributing a book is
effectively zero, **gatekeeping knowledge behind paywalls that exceed the means
of the people who most need it is itself an ethical violation** — one orders
of magnitude more serious than the act of routing around it.

The UN Universal Declaration of Human Rights, Article 27, states that:

> *Everyone has the right freely to participate in the cultural life of the
> community, to enjoy the arts and to share in scientific advancement and its
> benefits.*

It does not say *"everyone who can afford €110 per textbook"*. It does not
condition the right on a credit card.

### Socioeconomic equality, not opportunism

This document is written for people who would otherwise be locked out. It is
not a how-to for someone with a €120k salary to dodge a Netflix bill — that
person should just pay for Netflix; doing otherwise is freeloading on the
people who actually need these tools to exist. The moral character of this
stack is conditioned entirely on **who is using it**:

- A student paying their own way through college, using libgen to access
  their reading list — yes, unambiguously.
- A retiree on a fixed pension who would otherwise watch nothing because Sky
  Sports doubled in price — yes.
- A teenager in a household where Netflix and Spotify combined cost more than
  the family's weekly food budget — yes.
- A non-anglophone immigrant trying to learn English through TV — yes.
- A researcher whose university dropped its Elsevier subscription — yes.
- A €200k-a-year software engineer who simply doesn't want to pay for
  Disney+ — that is freeloading, do better.

The tools described in this document are morally neutral; what gives them
their moral weight is that, for the first category of users, **the only
alternative to using them is not paying — it is not consuming at all**, and
that has its own real cost to a person's education, cultural participation,
and basic dignity.

### Practical considerations

- **Buy the things you can afford.** When you have the money for a Stremio
  donation, a Real-Debrid sub, a paperback novel, an academic journal you
  rely on, a Bandcamp album, a cinema ticket — buy them. This stack is for
  the gap between what your circumstances allow and what a full participation
  in modern culture would otherwise cost. It is not a license to never
  contribute.
- **Support the maintainers.** uBlock Origin refuses donations and asks you
  to support filter-list maintainers instead. Mylar3 is volunteer-developed.
  Libgen and Z-Library run on donations. Kiwix (offline Wikipedia, often
  paired with this stack in rural deployments) runs on donations. Pick one
  and contribute when you can.
- **Don't redistribute commercially.** The line that matters in most
  jurisdictions, and the line that matters ethically, is *commercial*
  redistribution — selling someone else's work as your own. Personal use,
  even at scale, has never been the actual target of copyright enforcement.
- **Don't be smug.** The people who maintain this infrastructure do so at
  real personal risk in some cases. Use the tools quietly, share them
  privately with people who need them, and don't post screenshots on social
  media bragging about not paying for things.

---

## 9. Risks, Costs, Reality Check

**Financial:** ~€3–4/month Real-Debrid, covering **both** video (Stremio/Torrentio)
**and** comics (Mylar3 via GetComics DDL is free; Real-Debrid only kicks in via
RDT-Client for torrent fallbacks). Total under €50/year for the entire stack. For
reference, that is one month of Sky.

**Legal:** This stack relies on accessing copyrighted content via unauthorised
intermediaries. Real-Debrid itself is a legal company providing a generic
file-hosting service; libgen and Z-Library operate outside any one
jurisdiction; the legality of the *content* you stream or download is on you
and depends entirely on your local jurisdiction. Irish copyright law treats
personal non-commercial copying differently from redistribution, and
enforcement against individual end-users for personal-use streaming, debrid
consumption, or book downloading has been effectively zero to date — the
prosecutions that *do* exist target uploaders, seeders, and commercial
redistributors, not readers. (See §8 for the ethical framing; this is the
narrow legal note.)

**Technical:**

- Real-Debrid going down (rare, but it happens) takes your video library with it.
- Torrentio is a single point of failure — keep a backup addon (e.g. Comet, MediaFusion)
  configured but disabled, ready to swap in.
- The Real-Debrid API key is bearer-token-style — anyone with it has full access to
  your account. Treat it like a credit card number.

**Operational hygiene:**

- Do not share your Real-Debrid API key.
- Do not connect Real-Debrid to public-facing self-hosted services without auth.
- One Real-Debrid account legitimately covers Stremio/Torrentio, Mylar3 (via
  RDT-Client), and a self-hosted *arr stack (Sonarr/Radarr/Prowlarr/Readarr) all
  at the same time — one subscription, many consumers.

---

## 10. References (sources used to write this document)

- [ublockorigin.com](https://ublockorigin.com/) — official site, Manifest V3
  explainer (updated January 2026), browser support matrix, FAQ.
- [github.com/gorhill/uBlock](https://github.com/gorhill/uBlock) — uBO source,
  README ("uBO works best on Firefox"), MANIFESTO.md, default filter lists
  (EasyList, EasyPrivacy, Peter Lowe's, URLhaus), 1.71.0 release (May 2026),
  GPL-3.0, 65.2k stars.
- [addons.mozilla.org/addon/ublock-origin](https://addons.mozilla.org/addon/ublock-origin/)
  — install page for Firefox desktop and Firefox for Android.
- [stremio.com](https://www.stremio.com/) — feature list, supported platforms, FAQ.
- [web.stremio.com](https://web.stremio.com/) — browser client behaviour.
- [torrentio.strem.fun/configure](https://torrentio.strem.fun/configure) — indexer
  list, configuration options, debrid providers supported, install URL.
- [real-debrid.com](https://real-debrid.com/) — service description, hoster list,
  three pillars (economic / speed / many hosters).
- [real-debrid.com/apitoken](https://real-debrid.com/apitoken) — API token
  generation.
- [github.com/mylar3/mylar3](https://github.com/mylar3/mylar3) — README, feature
  list, installation paths (git clone or
  [linuxserver/mylar3](https://hub.docker.com/r/linuxserver/mylar3) Docker image),
  v0.8.3 latest release (Aug 2025), GPL-3.0 licence, Python 3.
- [getcomics.org](https://getcomics.org) — primary DDL source consumed natively by
  Mylar3's built-in GetComics provider.
- [readcomiconline.ru](https://readcomiconline.ru) /
  [readcomiconline.li](https://readcomiconline.li) — in-browser comic reader
  mirrors; require uBlock Origin.
- [github.com/rogerfar/rdt-client](https://github.com/rogerfar/rdt-client) —
  qBittorrent-compatible bridge to Real-Debrid; lets Mylar3 (and Sonarr/Radarr)
  use one Real-Debrid subscription for everything.
- [mylarcomics.com](https://mylarcomics.com/) — official documentation.
- [libgen.li](https://libgen.li/) — Library Genesis primary domain (2026);
  mirrors `libgen.vg / la / bz / gl`; provides ISBN/Worldcat/OpenLibrary
  bibliographic search and section-by-section database dumps.
- [z-library.bz](https://z-library.bz/) — Z-Library community landing page
  listing current working mirrors (`z-library.im`, `z-lib.gs`, `z-lib.fm` at
  time of writing); ~15M books, ~80M articles, multi-format downloads,
  TOR-aware desktop launcher.
- [calibre-ebook.com](https://calibre-ebook.com) — open-source book library
  manager.
- [zotero.org](https://www.zotero.org) — open-source citation/PDF manager for
  academic reading.
- [MDPI energy-conservation study](https://www.mdpi.com/2227-7080/8/2/18/htm)
  — cited by ublockorigin.com for the ~$1.8 billion/year global energy
  savings figure from ad blocking.
