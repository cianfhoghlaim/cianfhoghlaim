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
| Player / UI | **Stremio** | Open-source media centre (Netflix-like front-end) | Free |
| Source / scraper | **Torrentio** (Stremio addon) | Aggregates torrent indexers, hands magnets to the debrid | Free |
| Delivery / cloud cache | **Real-Debrid** | Cached torrents served as direct HTTPS streams | ~€3/month (16 days) → ~€4/month (180 days bulk) |
| Comics (parallel stack) | **Mylar3** | Sonarr-style automation for comic series (CBR/CBZ) | Free, self-hosted |

**Total monthly cost: ~€3–4** for the entire video catalogue of recorded human cinema and television, plus a self-hosted comics library.

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

Mylar3 does **not** use Real-Debrid — comics piracy economics are different. The
recommended pairing is:

- **Indexer:** a paid Usenet indexer (e.g. NZBgeek, DrunkenSlug — ~$15/year flat)
  *or* a Newznab-compatible torrent indexer.
- **Download client:** **SABnzbd** (Usenet) or your existing torrent client
  (`qbittorrent`, Deluge, Transmission).
- **Storage:** local NAS or a directory on the same machine.
- **Reader:** [Komga](https://komga.org) or [Kavita](https://www.kavitareader.com) —
  both are self-hosted comic servers with web + mobile readers, and both consume
  Mylar3's `series.json` natively.

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

## 6. Architecture at a Glance

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

   ┌─────────────┐   queues   ┌──────────┐   downloads   ┌──────────┐
   │   Mylar3    ├───────────►│ SABnzbd  ├──────────────►│  Komga   │
   │ (watchlist) │            │ /qbit    │               │  /Kavita │
   └─────────────┘            └──────────┘               └──────────┘
```

---

## 7. Risks, Costs, Reality Check

**Financial:** ~€3–4/month Real-Debrid + ~$15/year Usenet indexer (optional, for
comics) = under €50/year total. For reference, that is one month of Sky.

**Legal:** This stack relies on accessing copyrighted content via unauthorised
intermediaries. Real-Debrid itself is a legal company providing a generic
file-hosting service; the legality of the *content* you stream through it is on you
and depends entirely on your local jurisdiction. Irish copyright law treats personal
non-commercial copying differently from redistribution, but enforcement against
individual end-users via debrid services has been effectively zero to date because
no swarm participation occurs.

**Technical:**

- Real-Debrid going down (rare, but it happens) takes your video library with it.
- Torrentio is a single point of failure — keep a backup addon (e.g. Comet, MediaFusion)
  configured but disabled, ready to swap in.
- The Real-Debrid API key is bearer-token-style — anyone with it has full access to
  your account. Treat it like a credit card number.

**Operational hygiene:**

- Do not share your Real-Debrid API key.
- Do not connect Real-Debrid to public-facing self-hosted services without auth.
- If you also self-host an *arr stack (Sonarr/Radarr/Prowlarr), the same
  Real-Debrid account can power those via Prowlarr indexers — one subscription,
  many consumers.

---

## 8. References (sources used to write this document)

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
- [mylarcomics.com](https://mylarcomics.com/) — official documentation.
